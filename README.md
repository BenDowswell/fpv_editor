# FPV Editor

Generates EDL timeline files from a simple timestamps text file for import into DaVinci Resolve (free version).

## How it works

1. Log your best clips in `timestamps.txt` organised by section
2. Run `make_edl.py` to generate one EDL per section
3. Import each EDL into DaVinci Resolve as a ready-made timeline

## timestamps.txt format

```
Bloopers
Vid000005 02:36
Vid000013 00:40

Candidates
Vid000005 00:40 - 01:38
Vid000008 00:47 - 01:57

Spins
Vid000008 00:12 - 00:32
```

- **Section headers** are plain text lines (Bloopers, Candidates, Spins, etc.)
- **Single timestamp** — grabs 10 seconds from that point
- **Timestamp range** — grabs exactly that span

## Usage

```bash
python make_edl.py
```

Outputs one `.edl` file per section into the same folder.

## Importing into DaVinci Resolve

1. Create a new project set to **1920×1080 @ 60fps**
2. **File → Import Timeline → Import EDL** and select an EDL file
3. When prompted to relink media, point Resolve to your footage folder

## Config

Edit the top of `make_edl.py` to change paths or settings:

| Variable | Description |
|---|---|
| `TIMESTAMPS_FILE` | Path to your timestamps.txt |
| `OUTPUT_FOLDER` | Where EDL files are saved |
| `FRAME_RATE` | 60 by default |
| `SINGLE_DUR` | Seconds grabbed for single timestamps (default 10) |
