#!/bin/bash
COOKIES="/root/.openclaw/workspace/.secrets/youtube-cookies.txt"
VIDEOS="7qO8-kx3gW8 kCc8FmEb1nY t3YJ5hKiMQ0 q8SA3rM6ckI P6sfmUTpUmc TCH_1BHY58I ldxFjLJ3rVY Qoes9bTJtn0 fsLh-NYhOoU d0ai33oqqDE 7gG91SZwBoE BHdbsHFs2P0 t3jZ2xGOvYg eCw33snvoNI QzZ4VwDHAT4 yzajLZXh9JU Xf_v62TQOx4 Sk9tvyRSCgY Ersv1ogj7Jo mFSFvKquXwI"

mkdir -p subtitles
cd /root/youtube-sub-tracker

count=0
success=0
failed=0

for vid in $VIDEOS; do
    count=$((count + 1))
    echo "[$count/20] $vid"

    if yt-dlp --js-runtimes node --cookies "$COOKIES" \
        --write-auto-subs --sub-langs en --sub-format srt \
        --skip-download -o "subtitles/%(id)s" \
        "https://www.youtube.com/watch?v=$vid" 2>&1 | grep -q "Writing video subtitles"; then
        echo "  ✓ OK"
        success=$((success + 1))
    else
        echo "  ✗ FAILED"
        failed=$((failed + 1))
    fi

    sleep 3
done

echo ""
echo "完成: $success 成功, $failed 失败"
