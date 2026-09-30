/* Test Drive III: The Passion PS Vita / SDL2 port — entry point. */
#define SDL_MAIN_HANDLED
#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "host.h"
#include "mem.h"
#include "portcfg.h"
#include "platform/vga.h"
#include "game/game.h"

static int usage(const char *prog)
{
    fprintf(stderr,
            "usage: %s [--game-dir DIR] [--scale N] [--fullscreen] [--frame-ticks N] [--sound adlib|speaker]\n"
            "          [--car CODE] [--course CODE] [--skill N] [--check]\n", prog);
    return 2;
}

int main(int argc, char **argv)
{
    const char *dir = "Game";
    int scale = 3;
    bool check = false, fullscreen = false;
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i], *v = i + 1 < argc ? argv[i + 1] : NULL;
        if (!strcmp(a, "--game-dir") && v) { dir = v; i++; }
        else if (!strcmp(a, "--scale") && v) { scale = atoi(v); i++; }
        else if (!strcmp(a, "--fullscreen")) fullscreen = true;
        else if (!strcmp(a, "--frame-ticks") && v) { host_set_frame_ticks(atoi(v)); i++; }
        else if (!strcmp(a, "--sound") && v) {
            if (!strcasecmp(v, "adlib")) portcfg.sound = 4;
            else if (!strcasecmp(v, "speaker")) portcfg.sound = 0;
            else return usage(argv[0]);
            i++;
        }
        else if (!strcmp(a, "--car") && v) {
            strncpy(portcfg.car, v, sizeof(portcfg.car) - 1);
            portcfg.car[sizeof(portcfg.car) - 1] = '\0';
            i++;
        }
        else if (!strcmp(a, "--course") && v) {
            strncpy(portcfg.course, v, sizeof(portcfg.course) - 1);
            portcfg.course[sizeof(portcfg.course) - 1] = '\0';
            i++;
        }
        else if (!strcmp(a, "--skill") && v) { portcfg.skill = atoi(v); i++; }
        else if (!strcmp(a, "--check")) check = true;
        else return usage(argv[0]);
    }

    /* Probe candidate executable names: TDIII.EXE, tdiii.exe, TD3.EXE, td3.exe */
    static const char *candidates[] = { "TDIII.EXE", "tdiii.exe", "TD3.EXE", "td3.exe" };
    char *resolved_exe = NULL;
    for (size_t i = 0; i < sizeof(candidates) / sizeof(candidates[0]); i++) {
        char *p = host_game_path(candidates[i], false);
        if (p) {
            FILE *tf = fopen(p, "rb");
            if (tf) {
                fseek(tf, 0, SEEK_END);
                long len = ftell(tf);
                fclose(tf);
                if (len > 0) {
                    resolved_exe = p;
                    break;
                }
            }
            host_free(p);
        }
    }

    if (!resolved_exe) {
        /* Fall back to direct path */
        char direct_path[512];
        snprintf(direct_path, sizeof direct_path, "%s/%s", dir, TD_EXE_NAME);
        resolved_exe = strdup(direct_path);
    }

    char err[512];
    if (!mem_load_exe(resolved_exe, err, sizeof err)) {
        fprintf(stderr, "%s\n", err);
        SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, "Test Drive III", err, NULL);
        host_free(resolved_exe);
        return 1;
    }
    host_free(resolved_exe);

    if (check) {
        printf("Test Drive III executable ok: image %u bytes at %04X:0000, DGROUP %04X, frame pacing %d ticks\n",
               mem_image_size, LOAD_SEG, DGROUP, host_frame_ticks());
        return 0;
    }

    if (!host_init(dir, scale, fullscreen)) return 1;
    vga_init();      /* mode 13h model: frame source, DAC, CRTC start */
    modules_init();  /* host handlers, code-pointer tables (modules.c) */
    int rc = game_main();
    host_shutdown();
    return rc;
}
