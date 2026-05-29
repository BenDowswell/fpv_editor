#!/usr/bin/env python3
"""
Generates a CMX 3600 EDL from timestamps.txt.
Import into DaVinci Resolve: File -> Import Timeline -> Import EDL
"""

import os
import re

# ================================================================
# CONFIG
# ================================================================
TIMESTAMPS_FILE = r"C:\Users\BenDowswell\OneDrive - Joseph Talbot\Desktop\FPV_Editor\timestamps.txt"
OUTPUT_FOLDER   = r"C:\Users\BenDowswell\OneDrive - Joseph Talbot\Desktop\FPV_Editor"
VIDEO_EXT       = ".MOV"
FRAME_RATE      = 60
SINGLE_DUR      = 10   # seconds for single-timestamp clips
EDL_TITLE       = "FPV_Combined"
# ================================================================


def parse_timecode(s):
    parts = [int(p) for p in s.strip().split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def parse_timestamps(filepath):
    clips, section = [], None
    with open(filepath, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            m = re.match(r'^(Vid\d+)\s+([\d:]+)\s*(?:-\s*([\d:]+))?$', line)
            if m:
                vid, t1, t2 = m.group(1), m.group(2), m.group(3)
                start_s = parse_timecode(t1)
                end_s   = parse_timecode(t2) if t2 else start_s + SINGLE_DUR
                clips.append({"name": vid, "start_s": start_s, "end_s": end_s, "section": section})
            else:
                section = line
    return clips


def secs_to_tc(seconds, fps):
    total_frames = round(seconds * fps)
    ff  = total_frames % fps
    rem = total_frames // fps
    ss  = rem % 60
    mm  = (rem // 60) % 60
    hh  = rem // 3600
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def write_edl(clips, filepath, fps):
    title = clips[0]["section"] if clips else EDL_TITLE
    record_s = 0
    lines = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]

    for i, c in enumerate(clips, 1):
        dur_s   = c["end_s"] - c["start_s"]
        src_in  = secs_to_tc(c["start_s"], fps)
        src_out = secs_to_tc(c["end_s"],   fps)
        rec_in  = secs_to_tc(record_s,     fps)
        rec_out = secs_to_tc(record_s + dur_s, fps)

        # Reel name must be <=8 chars for CMX 3600; use last 8 chars of name (unique part)
        reel = c["name"][-8:].upper()
        lines.append(f"{i:03d}  {reel}  V     C        {src_in} {src_out} {rec_in} {rec_out}")
        lines.append(f"* FROM CLIP NAME: {c['name']}{VIDEO_EXT}")
        lines.append(f"* SECTION: {c['section']}")
        lines.append("")

        record_s += dur_s

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print("=== FPV EDL Generator ===\n")

    all_clips = parse_timestamps(TIMESTAMPS_FILE)
    sections  = list(dict.fromkeys(str(c["section"]) for c in all_clips))
    print(f"Loaded {len(all_clips)} clips across {len(sections)} sections\n")

    for section in sections:
        clips = [c for c in all_clips if str(c["section"]) == section]
        total_s = sum(c["end_s"] - c["start_s"] for c in clips)

        for c in clips:
            dur = c["end_s"] - c["start_s"]
            print(f"  [{section:10}] {c['name']}  {c['start_s']//60:02d}:{c['start_s']%60:02d} -> {c['end_s']//60:02d}:{c['end_s']%60:02d}  ({dur}s)")

        edl_path = os.path.join(OUTPUT_FOLDER, f"{section}.edl")
        write_edl(clips, edl_path, FRAME_RATE)
        print(f"  -> {edl_path}  ({total_s//60}m {total_s%60}s)\n")

    print("Done. In DaVinci Resolve, import each EDL as its own timeline:")
    print("  File -> Import Timeline -> Import EDL")

if __name__ == "__main__":
    main()
