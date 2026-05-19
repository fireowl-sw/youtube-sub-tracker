#!/usr/bin/env python3
"""Parse SRT subtitle files and update videos.json with transcript data."""
import json
import os
import re

SRT_DIR = "subtitles"
VIDEOS_JSON = "videos.json"

def parse_srt(filepath):
    """Parse an SRT file into [{time, text}, ...] format."""
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\n+", content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        # Line 1: index (skip)
        # Line 2: timestamp range
        # Lines 3+: text
        time_range = lines[1]
        text = " ".join(lines[2:]).strip()

        # Parse start time: 00:01:23,456 -> "1:23"
        match = re.match(r"(\d+):(\d+):(\d+)[,.]\d+", time_range)
        if match:
            h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if h > 0:
                time_str = f"{h}:{m:02d}:{s:02d}"
            else:
                time_str = f"{m}:{s:02d}"
        else:
            time_str = "0:00"

        entries.append({"time": time_str, "text": text})

    return entries

def main():
    subtitles_dir = os.path.join(os.path.dirname(__file__), SRT_DIR)
    videos_path = os.path.join(os.path.dirname(__file__), VIDEOS_JSON)

    with open(videos_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for video in data["videos"]:
        video_id = video["video_id"]
        srt_path = os.path.join(subtitles_dir, f"{video_id}.en.srt")
        if os.path.exists(srt_path):
            transcript = parse_srt(srt_path)
            video["transcript"] = transcript
            print(f"  {video_id}: {len(transcript)} entries")
            updated += 1

    with open(videos_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Updated {updated} videos with transcript data.")

if __name__ == "__main__":
    main()
