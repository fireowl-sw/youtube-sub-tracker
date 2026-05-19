#!/usr/bin/env bash
# Batch download subtitles for all videos without transcripts
set -e

COOKIES="/root/.openclaw/workspace/.secrets/youtube-cookies.txt"
SCRIPT_DIR="/root/youtube-sub-tracker"
VIDEOS=("4nQnhjimB4Y" "EWvNQjAaOHw" "QLu_ZsRc_G0" "4wC8hnQawiA" "zduSFxRajkE" "zjkBMFhNj_g" "Y7ImxZ_YhJk" "4h5BEALuh44" "Gz0Zv9Y5HsI" "SQm1GVOOSJM" "p7K3xfViWCE" "TnlY1YXSRK0" "qqavVebkXH0")

cd "$SCRIPT_DIR"
mkdir -p subtitles

for vid in "${VIDEOS[@]}"; do
    echo "=== Downloading $vid ==="
    if yt-dlp --js-runtimes node --cookies "$COOKIES" \
        --write-auto-subs --sub-langs en --sub-format srt \
        --skip-download -o "subtitles/%(id)s" \
        "https://www.youtube.com/watch?v=$vid" 2>&1; then
        echo "=== $vid OK ==="
    else
        echo "=== $vid FAILED ==="
    fi
    echo ""
    sleep 3
done

echo "=== All done ==="
