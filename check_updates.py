#!/usr/bin/env python3
"""
检查 YouTube 频道是否有新视频
使用 yt-dlp 获取频道最新视频（RSS 已失效）
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path


SUBSCRIPTIONS_FILE = Path(__file__).parent / "subscriptions.json"
VIDEOS_FILE = Path(__file__).parent / "videos.json"
COOKIES_FILE = Path(__file__).parent / ".secrets/youtube-cookies.txt"
PROXY = os.environ.get("HTTP_PROXY", "http://127.0.0.1:7890")


def load_subscriptions():
    """加载订阅数据"""
    with open(SUBSCRIPTIONS_FILE, 'r') as f:
        return json.load(f)


def save_subscriptions(data):
    """保存订阅数据"""
    with open(SUBSCRIPTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_latest_video(channel_id):
    """
    用 yt-dlp 获取频道最新视频（flat-playlist，不下载）
    返回 dict 或 None
    """
    url = f"https://www.youtube.com/channel/{channel_id}"
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(upload_date)s",
        "--playlist-end", "1",
        "--proxy", PROXY,
        "--cookies", str(COOKIES_FILE),
        "--no-warnings",
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"yt-dlp exit {result.returncode}: {stderr}")
        line = result.stdout.strip()
        if not line:
            return None
        parts = line.split("\t", 2)
        video_id = parts[0]
        title = parts[1] if len(parts) > 1 else "Unknown"
        upload_date = parts[2] if len(parts) > 2 else ""
        return {
            "video_id": video_id,
            "title": title,
            "published": upload_date,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        }
    except subprocess.TimeoutExpired:
        raise Exception("yt-dlp timeout (30s)")


def check_channel(channel_data):
    """检查单个频道是否有新视频"""
    print(f"\n📺 检查: {channel_data['name']}")

    try:
        latest = fetch_latest_video(channel_data['channel_id'])
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return "error", None

    if latest is None:
        print("   ❌ 无法获取视频信息")
        return "error", None

    print(f"   最新视频: {latest['title']}")
    print(f"   视频 ID: {latest['video_id']}")
    print(f"   发布日期: {latest['published']}")

    # 检查是否有新视频
    last_seen = channel_data.get('last_seen_video_id')

    if last_seen is None:
        print("   ✨ 首次检查，记录此视频")
        return "new", latest

    if last_seen == latest['video_id']:
        print("   ✓ 没有新视频")
        return "ok", None

    print(f"   🆕 发现新视频！上次的: {last_seen}")
    return "new", latest


def main():
    print("=" * 50)
    print("YouTube 订阅更新检查")
    print("=" * 50)

    subs_data = load_subscriptions()

    # 获取已存在的视频 ID
    try:
        with open(VIDEOS_FILE, 'r') as f:
            videos_data = json.load(f)
        existing_ids = {v['video_id'] for v in videos_data.get('videos', [])}
    except Exception:
        existing_ids = set()

    new_videos = []
    errors = []
    ok_channels = []

    for channel in subs_data['channels']:
        status, latest = check_channel(channel)

        if status == "error":
            errors.append(channel['name'])
            continue

        if latest:
            channel['last_seen_video_id'] = latest['video_id']
            channel['last_check_time'] = datetime.utcnow().isoformat() + 'Z'

            if latest['video_id'] not in existing_ids:
                new_videos.append({
                    'channel': channel['name'],
                    'channel_id': channel['channel_id'],
                    **latest
                })
            else:
                ok_channels.append(f"{channel['name']} — 最新视频「{latest['title']}」，无更新")
        else:
            ok_channels.append(f"{channel['name']} — 无变化")

    save_subscriptions(subs_data)

    # 报告结果
    print("\n" + "=" * 50)
    if new_videos:
        print(f"🎉 发现 {len(new_videos)} 个新视频：")
        for v in new_videos:
            print(f"\n  - {v['channel']}: {v['title']}")
            print(f"    URL: {v['url']}")
        print("\n💡 运行添加新视频:")
        for v in new_videos:
            print(f"   python3 add_video.py '{v['url']}'")
    else:
        print("✓ 没有发现新视频。")
    print("=" * 50)

    return {
        "new_videos": new_videos,
        "errors": errors,
        "ok_channels": ok_channels,
    }


if __name__ == '__main__':
    main()
