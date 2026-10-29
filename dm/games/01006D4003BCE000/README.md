# Guns, Gore & Cannoli 2 (`01006D4003BCE000`)

One package, build v0; its control data says display version 1.0.0 although the dump's file name says 1.0.4. SDK 3.8.0, NVN. Unity 5.6.6f2 IL2CPP, FMOD. Modules `main`, `subsdk0` (the movie module, `NintendoSDK_movie`) and `sdk`. Plays on the Mac. Brought up on the Mac: the title, its menu, the difficulty sheet, the opening movie and the first chapter at 60 fps with no red line. The rest is not walked through yet, and it was not tried on an iPhone.

## What it needs

| Setting | Where | Why |
|---|---|---|
| `SHADER_5_6`, the Unity 5.6.6f2 `Shader` layout | [`unityfs.py`](../../../dm/gfx/tools/unityfs.py) | every serialized file that holds this game's shaders (`Data/*.assets`, `Data/Resources/unity default resources`) carries no type trees, and no bundle of the game supplies one, so the split stopped with `no bundle has a Shader type tree of the same hash to borrow` |
| `mem_used 0x4600000` (70 MB) | [`game.tsv`](game.tsv) | the rewritten modules take 70 MB (`main` 46.9, `sdk` 14.2, `subsdk0` 5.5), more than the default 64 MB of used memory |
| 4 GB layout: `mem_reserve 0x100000000`, `mem_alias 0x10000000`, `mem_stack 0x10000000`, `app_pool 0xCD500000`, `sys_resource 0x0` | [`game.tsv`](game.tsv) | the NPDM declares no system resource, so no virtual address memory: 256 MB in front + 256 MB alias region + 256 MB stack region + 3.25 GB heap region |
| `shader_groups /Data/=data` | [`game.tsv`](game.tsv) | its shaders are all under `Data` |
| SDK 3's `movie::Decoder` take-over | host, `hle_movie.c` `h_movie_Decoder3` ([entry](../../../docs/reference/movies.md#sdk-3s-two-argument-constructor-with-its-own-output-format-numbering)) | its constructor is the two-argument form the host did not take over, so the SDK's own decoder died in ACodec on the opening movie; that SDK numbers NV12 as output format 3, which the newer numbering calls ABGR |

## Memory

- No system resource: Unity sets a heap of the application pool minus the used memory — the host reports `heap 3.14 GB (heap region 3.25 GB)`.
- On the Mac about 1.06 GB resident and 830 MB of Metal allocations once the title is up; the heap itself is mostly untouched by the menus.

## Rendering

- 395 shaders: 190 pixel, 193 vertex, 12 compute; 379 of them from the `Data` files, 16 of the player's own in `main`. One variation pair and one pixel-input cover (`shader_pairs.tsv`, `pso_pairs.tsv` with 191 legacy pass-input covers). All 395 translate and compile.
- Unity 5.6 is older than 2019.3, so each blob entry is one stage and the stage comes from the parsed form (`unity_stages`); the pass's pixel-input cover supplies the vertex padding pairs (`unity_pass_pairs`).
- 162 draws a frame at the title; GPU p50 1.1–1.5 ms, CPU 22–27% of one core, no dropped frames.
- Built here with Xcode 26.6's Metal compiler rather than the one `dmsh_chain.lock` records (`--allow-other-metal`): the picture was right in the sessions run so far, but issue #242's cause is still unconfirmed.

## Saves

- Nothing unusual found: the save lives in `run/save` on the Mac (the app's `Documents/save` on iOS) and the game writes it without a host change.

## Mac routes

- Not scripted yet: from the title, A opens **NEW GAME** and the difficulty sheet (easy / normal / hard / very hard / back); D-pad moves, A picks.
- Keys: arrow keys are the D-pad, `J` A, `K` B, `U` X, `I` Y, `Return` +, `Tab` − (the Mac front end's keyboard map).

## Found on this game

- **SDK 3's two-argument `movie::Decoder` constructor and its own `DecoderOutputFormat` numbering**: [SDK 3's two-argument constructor, with its own output format numbering](../../../docs/reference/movies.md#sdk-3s-two-argument-constructor-with-its-own-output-format-numbering).
- **The Unity 5.6.6f2 `Shader` layout** (`SHADER_5_6`, hash `a70f7abc…`), derived from AssetRipper's TypeTreeDumps for 5.6.4f1 and 5.6.6f2 (identical node for node) and checked on this game's 56 stripped `Shader` objects in 51 serialized files, each reading to its exact end: [Unity Shader layouts written out for players without bundles](../../../docs/reference/shaders.md#unity-shader-layouts-written-out-for-players-without-bundles).

## Open

- The iPhone: no build was made. The profile's warm-up manifest was seeded from the host's own `pso_user.tsv` after a short manual session (the title, the difficulty sheet, the first frames of a level), so it is thin.
- The dump this profile was brought up on is a Chinese-localised release: its UI strings are Chinese in `Data/resources.assets` (the new-game, start-game and options items among them) and no English counterpart of them, while its control data declares nine languages (en-US ja fr de es it nl pt ru) and no Chinese. Whether the language row changes anything on such a dump is not checked.
- Gameplay beyond the first chapter, and the rest of the survey's warnings about SDK 3 object sizes, are unchecked: nothing of the game's own rendering needed a host change so far, and the movie fix is the only host change it asked for.
