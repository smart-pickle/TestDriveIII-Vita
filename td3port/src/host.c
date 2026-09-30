#include "host.h"

#include <SDL.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <dirent.h>
#include <sys/stat.h>

#if defined(__psp2__) || defined(__vita__)
#include <psp2/ctrl.h>
#include <psp2/power.h>
#include <psp2/io/stat.h>
#endif

#include "opl3.h"

#define AUDIO_RATE 44100
#define SPEAKER_AMPLITUDE 5000

static SDL_Window *window;
static SDL_Renderer *renderer;
static SDL_Texture *texture;
static SDL_AudioDeviceID audio_dev;
static SDL_GameController *gamepad;
static char *game_dir;

static int aspect_mode = HOST_ASPECT_4_3; /* Default: Mode 1 (4:3 pillarbox, 725x544) */

#if defined(__psp2__) || defined(__vita__)
static uint32_t last_vita_buttons = 0;
#endif

static void (*tick_handler)(void);
static void (*kbd_handler)(u8);
static void (*focus_lost_handler)(void);
static bool (*frame_source)(u32 *);
static u32 frame[HOST_FRAME_MAX_W * HOST_FRAME_MAX_H];
static int frame_w = 320, frame_h = 200;

/* High-resolution clock in nanoseconds */
static Uint64 perf_freq = 0;
static Uint64 clock_start_ns;
static Uint64 ticks_run;

static inline Uint64 host_ticks_ns(void)
{
    if (perf_freq == 0) perf_freq = SDL_GetPerformanceFrequency();
    return (SDL_GetPerformanceCounter() * 1000000000ULL) / perf_freq;
}

/* Audio: the OPL2 (as one OPL3 in OPL2 mode) and the speaker's square wave, mixed to stereo. */
static opl3_chip opl;
static u16 spk_div;
static bool spk_on;
static double spk_phase;
static double samples_per_tick_frac;

/* Mouse: position in screen units and accumulated relative motion. */
static float mouse_x = 160.0f, mouse_y = 100.0f;
static float mouse_dx, mouse_dy;

static int frame_ticks = HOST_DEFAULT_FRAME_TICKS;

static void process_events(void);

void host_cycle_aspect_ratio(void)
{
    aspect_mode = (aspect_mode + 1) % 3;
}

int host_aspect_ratio(void)
{
    return aspect_mode;
}

static void compute_dst_rect(SDL_Rect *dst)
{
    int win_w = 960, win_h = 544;
    if (renderer) {
        SDL_GetRendererOutputSize(renderer, &win_w, &win_h);
    }
    if (aspect_mode == HOST_ASPECT_STRETCH) {
        /* Fullscreen 16:9 stretch across the display */
        dst->x = 0;
        dst->y = 0;
        dst->w = win_w;
        dst->h = win_h;
    } else if (aspect_mode == HOST_ASPECT_4_3) {
        /* 4:3 aspect ratio centered (725x544 on PS Vita) */
        int target_w = win_h * 4 / 3;
        if (target_w > win_w) {
            target_w = win_w;
            int target_h = win_w * 3 / 4;
            dst->x = 0;
            dst->y = (win_h - target_h) / 2;
            dst->w = target_w;
            dst->h = target_h;
        } else {
            dst->x = (win_w - target_w) / 2;
            dst->y = 0;
            dst->w = target_w;
            dst->h = win_h;
        }
    } else {
        /* 2x integer scale centered (640x480 on PS Vita) */
        int target_w = 640;
        int target_h = 480;
        if (target_w > win_w) target_w = win_w;
        if (target_h > win_h) target_h = win_h;
        dst->x = (win_w - target_w) / 2;
        dst->y = (win_h - target_h) / 2;
        dst->w = target_w;
        dst->h = target_h;
    }
}

bool host_init(const char *dir, int window_scale, bool fullscreen)
{
#if defined(__psp2__) || defined(__vita__)
    scePowerSetArmClockFrequency(444);
    scePowerSetBusClockFrequency(222);
    scePowerSetGpuClockFrequency(222);
    scePowerSetGpuXbarClockFrequency(166);
    sceCtrlSetSamplingMode(SCE_CTRL_MODE_ANALOG);
    sceIoMkdir("ux0:data", 0777);
    sceIoMkdir("ux0:data/TestDrive3", 0777);
#endif

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_GAMECONTROLLER) < 0) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        return false;
    }
    game_dir = strdup(dir);
    if (window_scale < 1) window_scale = 3;

#if defined(__psp2__) || defined(__vita__)
    window = SDL_CreateWindow("Test Drive III: The Passion", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              960, 544, 0);
#else
    window = SDL_CreateWindow("Test Drive III: The Passion", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              320 * window_scale, 240 * window_scale, SDL_WINDOW_RESIZABLE);
    if (fullscreen) SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN_DESKTOP);
#endif

    if (!window) {
        fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
        return false;
    }

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!renderer) {
        renderer = SDL_CreateRenderer(window, -1, 0);
    }
    if (!renderer) {
        fprintf(stderr, "SDL_CreateRenderer failed: %s\n", SDL_GetError());
        return false;
    }

    host_set_frame_source(NULL, 320, 200);

    OPL3_Reset(&opl, AUDIO_RATE);
    SDL_AudioSpec want, have;
    memset(&want, 0, sizeof(want));
    want.freq = AUDIO_RATE;
    want.format = AUDIO_S16SYS;
    want.channels = 2;
    want.samples = 1024;
    want.callback = NULL;

    audio_dev = SDL_OpenAudioDevice(NULL, 0, &want, &have, 0);
    if (audio_dev > 0) {
        SDL_PauseAudioDevice(audio_dev, 0);
        static s16 silence[AUDIO_RATE / 20 * 2];
        SDL_QueueAudio(audio_dev, silence, sizeof silence);
    } else {
        fprintf(stderr, "audio unavailable: %s\n", SDL_GetError());
    }

    perf_freq = SDL_GetPerformanceFrequency();
    clock_start_ns = host_ticks_ns();
    ticks_run = 0;
    return true;
}

void host_shutdown(void)
{
    if (gamepad) SDL_GameControllerClose(gamepad);
    if (audio_dev > 0) SDL_CloseAudioDevice(audio_dev);
    if (texture) SDL_DestroyTexture(texture);
    if (renderer) SDL_DestroyRenderer(renderer);
    if (window) SDL_DestroyWindow(window);
    free(game_dir);
    SDL_Quit();
}

void host_set_tick_handler(void (*handler)(void)) { tick_handler = handler; }
void host_set_kbd_handler(void (*handler)(u8)) { kbd_handler = handler; }
void host_set_focus_lost_handler(void (*handler)(void)) { focus_lost_handler = handler; }

void host_set_frame_source(bool (*compose)(u32 *), int w, int h)
{
    frame_source = compose;
    if (w < 1) w = 1;
    if (w > HOST_FRAME_MAX_W) w = HOST_FRAME_MAX_W;
    if (h < 1) h = 1;
    if (h > HOST_FRAME_MAX_H) h = HOST_FRAME_MAX_H;

    frame_w = w;
    frame_h = h;

    if (texture) SDL_DestroyTexture(texture);
    texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, frame_w, frame_h);
    SDL_SetTextureScaleMode(texture, SDL_ScaleModeNearest);
}

static inline Uint64 tick_due_ns(Uint64 n)
{
    return clock_start_ns + n * (Uint64)PIT_DIV_GAME * 1000000000ULL / PIT_HZ;
}

static void audio_for_one_tick(void)
{
    if (audio_dev <= 0) return;
    samples_per_tick_frac += (double)AUDIO_RATE * PIT_DIV_GAME / PIT_HZ;
    int n = (int)samples_per_tick_frac;
    samples_per_tick_frac -= n;

    if (SDL_GetQueuedAudioSize(audio_dev) > AUDIO_RATE / 4 * 2 * (Uint32)sizeof(s16)) return;
    s16 buf[2 * 512];
    if (n > 512) n = 512;
    OPL3_GenerateStream(&opl, buf, (uint32_t)n);
    double freq = (double)PIT_HZ / (spk_div ? spk_div : 65536);
    double step = freq / AUDIO_RATE;
    for (int i = 0; i < n; i++) {
        int s = 0;
        if (spk_on) {
            s = spk_phase < 0.5 ? SPEAKER_AMPLITUDE : -SPEAKER_AMPLITUDE;
            spk_phase += step;
            spk_phase -= (int)spk_phase;
        }
        for (int c = 0; c < 2; c++) {
            int v = buf[2 * i + c] + s;
            if (v < -32768) v = -32768;
            if (v > 32767) v = 32767;
            buf[2 * i + c] = (s16)v;
        }
    }
    SDL_QueueAudio(audio_dev, buf, (Uint32)n * 2 * (Uint32)sizeof(s16));
}

void host_opl_write(u8 reg, u8 value) { OPL3_WriteReg(&opl, reg, value); }

void host_speaker(u16 divisor, bool on)
{
    spk_div = divisor;
    spk_on = on;
}

static void present(void)
{
    if (!texture) return;
    SDL_UpdateTexture(texture, NULL, frame, frame_w * (int)sizeof(u32));
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);
    SDL_Rect dst;
    compute_dst_rect(&dst);
    SDL_RenderCopy(renderer, texture, NULL, &dst);
    SDL_RenderPresent(renderer);
}

void host_pump(void)
{
    process_events();

    bool worked = false;
    Uint64 now = host_ticks_ns();
    int budget = 73;
    while (tick_due_ns(ticks_run + 1) <= now && budget-- > 0) {
        ticks_run++;
        if (tick_handler) tick_handler();
        audio_for_one_tick();
        worked = true;
    }
    if (budget < 0) {
        clock_start_ns = now - (tick_due_ns(ticks_run) - clock_start_ns);
    }

    static Uint64 last_present_ns;
    if (frame_source && now - last_present_ns >= 8000000ULL) {
        if (frame_source(frame)) {
            present();
            last_present_ns = host_ticks_ns();
            worked = true;
        }
    }
    if (!worked) {
        Uint64 next = tick_due_ns(ticks_run + 1);
        now = host_ticks_ns();
        if (next > now) {
            Uint32 ms = (Uint32)((next - now) / 1000000ULL);
            if (ms > 0) SDL_Delay(ms);
        }
    }
}

/* VGA 320x200 (mode 13h) refresh: 25.175 MHz / (800 x 449) = 70.086 Hz. */
#define VRETRACE_NUM (800ull * 449ull * 1000000000ull)
#define VRETRACE_DEN (25175000ull)

void host_wait_vretrace(void)
{
    Uint64 since = host_ticks_ns() - clock_start_ns;
    Uint64 next = (since * VRETRACE_DEN / VRETRACE_NUM + 1) * VRETRACE_NUM / VRETRACE_DEN;
    while (host_ticks_ns() - clock_start_ns < next) host_pump();
}

void host_set_frame_ticks(int ticks) { frame_ticks = ticks < 1 ? 1 : ticks; }
int  host_frame_ticks(void) { return frame_ticks; }

/* ---------------------------------------------------------------- keyboard */

#define GREY 0x100
static u16 xt_scan(SDL_Scancode sc)
{
    if (sc >= SDL_SCANCODE_A && sc <= SDL_SCANCODE_Z) {
        static const u8 letter_scan[26] = { 0x1E,0x30,0x2E,0x20,0x12,0x21,0x22,0x23,0x17,0x24,0x25,0x26,0x32,
                                            0x31,0x18,0x19,0x10,0x13,0x1F,0x14,0x16,0x2F,0x11,0x2D,0x15,0x2C };
        return letter_scan[sc - SDL_SCANCODE_A];
    }
    if (sc >= SDL_SCANCODE_1 && sc <= SDL_SCANCODE_0) return (u16)(0x02 + (sc - SDL_SCANCODE_1));
    if (sc >= SDL_SCANCODE_F1 && sc <= SDL_SCANCODE_F10) return (u16)(0x3B + (sc - SDL_SCANCODE_F1));
    switch (sc) {
    case SDL_SCANCODE_F11:          return 0x57;
    case SDL_SCANCODE_F12:          return 0x58;
    case SDL_SCANCODE_ESCAPE:       return 0x01;
    case SDL_SCANCODE_MINUS:        return 0x0C;
    case SDL_SCANCODE_EQUALS:       return 0x0D;
    case SDL_SCANCODE_BACKSPACE:    return 0x0E;
    case SDL_SCANCODE_TAB:          return 0x0F;
    case SDL_SCANCODE_LEFTBRACKET:  return 0x1A;
    case SDL_SCANCODE_RIGHTBRACKET: return 0x1B;
    case SDL_SCANCODE_RETURN:       return 0x1C;
    case SDL_SCANCODE_KP_ENTER:     return GREY | 0x1C;
    case SDL_SCANCODE_LCTRL:        return 0x1D;
    case SDL_SCANCODE_RCTRL:        return GREY | 0x1D;
    case SDL_SCANCODE_SEMICOLON:    return 0x27;
    case SDL_SCANCODE_APOSTROPHE:   return 0x28;
    case SDL_SCANCODE_GRAVE:        return 0x29;
    case SDL_SCANCODE_LSHIFT:       return 0x2A;
    case SDL_SCANCODE_BACKSLASH:    return 0x2B;
    case SDL_SCANCODE_COMMA:        return 0x33;
    case SDL_SCANCODE_PERIOD:       return 0x34;
    case SDL_SCANCODE_SLASH:        return 0x35;
    case SDL_SCANCODE_KP_DIVIDE:    return GREY | 0x35;
    case SDL_SCANCODE_RSHIFT:       return 0x36;
    case SDL_SCANCODE_KP_MULTIPLY:  return 0x37;
    case SDL_SCANCODE_LALT:         return 0x38;
    case SDL_SCANCODE_RALT:         return GREY | 0x38;
    case SDL_SCANCODE_SPACE:        return 0x39;
    case SDL_SCANCODE_CAPSLOCK:     return 0x3A;
    case SDL_SCANCODE_NUMLOCKCLEAR: return 0x45;
    case SDL_SCANCODE_SCROLLLOCK:   return 0x46;
    case SDL_SCANCODE_KP_7:         return 0x47;
    case SDL_SCANCODE_KP_8:         return 0x48;
    case SDL_SCANCODE_KP_9:         return 0x49;
    case SDL_SCANCODE_KP_MINUS:     return 0x4A;
    case SDL_SCANCODE_KP_4:         return 0x4B;
    case SDL_SCANCODE_KP_5:         return 0x4C;
    case SDL_SCANCODE_KP_6:         return 0x4D;
    case SDL_SCANCODE_KP_PLUS:      return 0x4E;
    case SDL_SCANCODE_KP_1:         return 0x4F;
    case SDL_SCANCODE_KP_2:         return 0x50;
    case SDL_SCANCODE_KP_3:         return 0x51;
    case SDL_SCANCODE_KP_0:         return 0x52;
    case SDL_SCANCODE_KP_PERIOD:    return 0x53;
    case SDL_SCANCODE_HOME:         return GREY | 0x47;
    case SDL_SCANCODE_UP:           return GREY | 0x48;
    case SDL_SCANCODE_PAGEUP:       return GREY | 0x49;
    case SDL_SCANCODE_LEFT:         return GREY | 0x4B;
    case SDL_SCANCODE_RIGHT:        return GREY | 0x4D;
    case SDL_SCANCODE_END:          return GREY | 0x4F;
    case SDL_SCANCODE_DOWN:         return GREY | 0x50;
    case SDL_SCANCODE_PAGEDOWN:     return GREY | 0x51;
    case SDL_SCANCODE_INSERT:       return GREY | 0x52;
    case SDL_SCANCODE_DELETE:       return GREY | 0x53;
    default:                        return 0;
    }
}

static void feed(const u8 *bytes, int n)
{
    if (!kbd_handler) return;
    for (int i = 0; i < n; i++) kbd_handler(bytes[i]);
}

static void send_xt_key(u16 x, bool down)
{
    if (!x || !kbd_handler) return;
    u8 seq[2];
    int n = 0;
    if (x & GREY) seq[n++] = 0xE0;
    seq[n++] = (u8)(down ? (x & 0x7F) : (x & 0x7F) | 0x80);
    feed(seq, n);
}

static void key_event(SDL_Scancode sc, bool down)
{
    if (sc == SDL_SCANCODE_PAUSE) {
        static const u8 pause[] = { 0xE1, 0x1D, 0x45, 0xE1, 0x9D, 0xC5 };
        if (down) feed(pause, sizeof pause);
        return;
    }
    if (sc == SDL_SCANCODE_PRINTSCREEN) {
        static const u8 make[] = { 0xE0, 0x2A, 0xE0, 0x37 }, brk[] = { 0xE0, 0xB7, 0xE0, 0xAA };
        if (down) feed(make, sizeof make); else feed(brk, sizeof brk);
        return;
    }
    u16 x = xt_scan(sc);
    send_xt_key(x, down);
}

static void process_events(void)
{
    SDL_Event ev;
    while (SDL_PollEvent(&ev)) {
        switch (ev.type) {
        case SDL_QUIT:
            host_shutdown();
            exit(0);
        case SDL_KEYDOWN:
            if (ev.key.keysym.sym == SDLK_RETURN && (ev.key.keysym.mod & KMOD_ALT)) {
                if (!ev.key.repeat) {
                    Uint32 flags = SDL_GetWindowFlags(window);
                    SDL_SetWindowFullscreen(window, (flags & SDL_WINDOW_FULLSCREEN) ? 0 : SDL_WINDOW_FULLSCREEN);
                }
                break;
            }
            key_event(ev.key.keysym.scancode, true);
            break;
        case SDL_KEYUP:
            key_event(ev.key.keysym.scancode, false);
            break;
        case SDL_WINDOWEVENT:
            if (ev.window.event == SDL_WINDOWEVENT_FOCUS_LOST) {
                if (focus_lost_handler) focus_lost_handler();
            }
            break;
        case SDL_CONTROLLERDEVICEADDED:
            if (!gamepad) gamepad = SDL_GameControllerOpen(ev.cdevice.which);
            break;
        case SDL_CONTROLLERDEVICEREMOVED:
            if (gamepad) {
                SDL_GameControllerClose(gamepad);
                gamepad = NULL;
            }
            break;
        case SDL_CONTROLLERBUTTONDOWN:
            if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_BACK) {
                host_cycle_aspect_ratio();
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_START) {
                send_xt_key(0x01, true); /* Esc */
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_A) {
                send_xt_key(0x1C, true); /* Enter */
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_B) {
                send_xt_key(0x39, true); /* Space */
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_Y) {
                send_xt_key(0x1E, true); /* A (Shift Up) */
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_X) {
                send_xt_key(0x2C, true); /* Z (Shift Down) */
            }
            break;
        case SDL_CONTROLLERBUTTONUP:
            if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_START) {
                send_xt_key(0x01, false);
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_A) {
                send_xt_key(0x1C, false);
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_B) {
                send_xt_key(0x39, false);
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_Y) {
                send_xt_key(0x1E, false);
            } else if (ev.cbutton.button == SDL_CONTROLLER_BUTTON_X) {
                send_xt_key(0x2C, false);
            }
            break;
        default:
            break;
        }
    }

#if defined(__psp2__) || defined(__vita__)
    SceCtrlData pad;
    if (sceCtrlPeekBufferPositive(0, &pad, 1) > 0) {
        uint32_t pressed = pad.buttons & ~last_vita_buttons;
        uint32_t released = ~pad.buttons & last_vita_buttons;
        last_vita_buttons = pad.buttons;

        if (pressed & SCE_CTRL_SELECT) {
            host_cycle_aspect_ratio();
        }

        bool l_held = (pad.buttons & (SCE_CTRL_LTRIGGER | SCE_CTRL_L1)) != 0;

        /* Press events */
        if (pressed & SCE_CTRL_START) {
            if (l_held) send_xt_key(0x40, true); /* F6 (Return to road) */
            else        send_xt_key(0x01, true); /* Esc */
        }
        if (pressed & SCE_CTRL_CROSS) {
            if (l_held) send_xt_key(0x44, true); /* F10 (Instant replay) */
            else        send_xt_key(0x1C, true); /* Enter */
        }
        if (pressed & SCE_CTRL_CIRCLE) {
            if (l_held) send_xt_key(0x23, true); /* H (Headlights) */
            else        send_xt_key(0x39, true); /* Space */
        }
        if (pressed & SCE_CTRL_TRIANGLE) {
            if (l_held) send_xt_key(0x3F, true); /* F5 (Chase view) */
            else        send_xt_key(0x1E, true); /* A (Shift Up) */
        }
        if (pressed & SCE_CTRL_SQUARE) {
            if (l_held) send_xt_key(0x13, true); /* R (Mirror) */
            else        send_xt_key(0x2C, true); /* Z (Shift Down) */
        }
        if (pressed & SCE_CTRL_UP) {
            if (l_held) send_xt_key(0x32, true); /* M (Radio) */
            else        send_xt_key(GREY | 0x48, true); /* Up */
        }
        if (pressed & SCE_CTRL_DOWN) {
            if (l_held) send_xt_key(0x11, true); /* W (Wipers) */
            else        send_xt_key(GREY | 0x50, true); /* Down */
        }
        if (pressed & SCE_CTRL_LEFT) {
            send_xt_key(GREY | 0x4B, true); /* Left */
        }
        if (pressed & SCE_CTRL_RIGHT) {
            send_xt_key(GREY | 0x4D, true); /* Right */
        }

        /* Release events */
        if (released & SCE_CTRL_START) {
            send_xt_key(0x40, false);
            send_xt_key(0x01, false);
        }
        if (released & SCE_CTRL_CROSS) {
            send_xt_key(0x44, false);
            send_xt_key(0x1C, false);
        }
        if (released & SCE_CTRL_CIRCLE) {
            send_xt_key(0x23, false);
            send_xt_key(0x39, false);
        }
        if (released & SCE_CTRL_TRIANGLE) {
            send_xt_key(0x3F, false);
            send_xt_key(0x1E, false);
        }
        if (released & SCE_CTRL_SQUARE) {
            send_xt_key(0x13, false);
            send_xt_key(0x2C, false);
        }
        if (released & SCE_CTRL_UP) {
            send_xt_key(0x32, false);
            send_xt_key(GREY | 0x48, false);
        }
        if (released & SCE_CTRL_DOWN) {
            send_xt_key(0x11, false);
            send_xt_key(GREY | 0x50, false);
        }
        if (released & SCE_CTRL_LEFT) {
            send_xt_key(GREY | 0x4B, false);
        }
        if (released & SCE_CTRL_RIGHT) {
            send_xt_key(GREY | 0x4D, false);
        }
    }
#endif
}

/* ---------------------------------------------------------------- mouse, joystick */

void host_mouse_read(s16 *x, s16 *y, u8 *buttons)
{
    process_events();
    if (x) *x = (s16)mouse_x;
    if (y) *y = (s16)mouse_y;
    if (buttons) *buttons = 0;
}

void host_mouse_motion(s16 *dx, s16 *dy)
{
    process_events();
    if (dx) *dx = (s16)mouse_dx;
    if (dy) *dy = (s16)mouse_dy;
    mouse_dx = 0;
    mouse_dy = 0;
}

bool host_joy_read(s16 *x, s16 *y, u8 *buttons)
{
#if defined(__psp2__) || defined(__vita__)
    SceCtrlData pad;
    if (sceCtrlPeekBufferPositive(0, &pad, 1) > 0) {
        s16 ax = (s16)(((int)pad.lx - 128) * 256);
        s16 ay = (s16)(((int)pad.ly - 128) * 256);
        if (pad.buttons & SCE_CTRL_LEFT)  ax = -32768;
        if (pad.buttons & SCE_CTRL_RIGHT) ax = 32767;
        if (pad.buttons & SCE_CTRL_UP)    ay = -32768;
        if (pad.buttons & SCE_CTRL_DOWN)  ay = 32767;
        u8 b = 0;
        if (pad.buttons & (SCE_CTRL_CROSS | SCE_CTRL_RTRIGGER | SCE_CTRL_R1)) b |= 1;
        if (pad.buttons & (SCE_CTRL_SQUARE | SCE_CTRL_CIRCLE | SCE_CTRL_LTRIGGER | SCE_CTRL_L1)) b |= 2;
        if (x) *x = ax;
        if (y) *y = ay;
        if (buttons) *buttons = b;
        return true;
    }
#endif

    if (!gamepad) return false;
    s16 ax = SDL_GameControllerGetAxis(gamepad, SDL_CONTROLLER_AXIS_LEFTX);
    s16 ay = SDL_GameControllerGetAxis(gamepad, SDL_CONTROLLER_AXIS_LEFTY);
    if (SDL_GameControllerGetButton(gamepad, SDL_CONTROLLER_BUTTON_DPAD_LEFT))  ax = -32768;
    if (SDL_GameControllerGetButton(gamepad, SDL_CONTROLLER_BUTTON_DPAD_RIGHT)) ax = 32767;
    if (SDL_GameControllerGetButton(gamepad, SDL_CONTROLLER_BUTTON_DPAD_UP))    ay = -32768;
    if (SDL_GameControllerGetButton(gamepad, SDL_CONTROLLER_BUTTON_DPAD_DOWN))  ay = 32767;
    u8 b = 0;
    if (SDL_GameControllerGetButton(gamepad, SDL_CONTROLLER_BUTTON_A)) b |= 1;
    if (SDL_GameControllerGetButton(gamepad, SDL_CONTROLLER_BUTTON_B)) b |= 2;
    if (x) *x = ax;
    if (y) *y = ay;
    if (buttons) *buttons = b;
    return true;
}

/* ---------------------------------------------------------------- files, errors */

static char *search_dir_case_insensitive(const char *dir, const char *name)
{
    DIR *d = opendir(dir);
    if (!d) return NULL;
    struct dirent *ent;
    char *found = NULL;
    while ((ent = readdir(d)) != NULL) {
        if (strcasecmp(ent->d_name, name) == 0) {
            size_t len = strlen(dir) + 1 + strlen(ent->d_name) + 1;
            found = malloc(len);
            if (found) snprintf(found, len, "%s/%s", dir, ent->d_name);
            break;
        }
    }
    closedir(d);
    return found;
}

char *host_game_path(const char *name, bool create)
{
#if defined(__psp2__) || defined(__vita__)
    if (create) {
        char *path = malloc(256);
        if (path) snprintf(path, 256, "ux0:data/TestDrive3/%s", name);
        return path;
    }
    /* Check ux0:data/TestDrive3 first for user mod/save files */
    char *user_path = search_dir_case_insensitive("ux0:data/TestDrive3", name);
    if (user_path) return user_path;
    /* Check app0:Game (VPK bundled assets) */
    char *app_path = search_dir_case_insensitive("app0:Game", name);
    if (app_path) return app_path;
#endif

    if (create) {
        size_t len = strlen(game_dir) + 1 + strlen(name) + 1;
        char *path = malloc(len);
        if (path) snprintf(path, len, "%s/%s", game_dir, name);
        return path;
    }

    /* Direct path check */
    size_t direct_len = strlen(game_dir) + 1 + strlen(name) + 1;
    char *direct = malloc(direct_len);
    if (direct) {
        snprintf(direct, direct_len, "%s/%s", game_dir, name);
        struct stat st;
        if (stat(direct, &st) == 0) return direct;
        free(direct);
    }

    return search_dir_case_insensitive(game_dir, name);
}

void host_free(void *p)
{
    free(p);
}

_Noreturn void host_fatal(const char *fmt, ...)
{
    char msg[512];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(msg, sizeof msg, fmt, ap);
    va_end(ap);
    fprintf(stderr, "fatal: %s\n", msg);
    SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, "Test Drive III", msg, window);
    host_shutdown();
    exit(3);
}
