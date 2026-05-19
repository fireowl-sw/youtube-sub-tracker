#!/usr/bin/env python3
"""
添加新视频到追踪系统
用法: python3 add_video.py <YouTube_URL>
"""
import sys
import json
import os
import re
import subprocess
from datetime import datetime

VIDEOS_JSON = "videos.json"

def extract_video_id(url):
    """从URL提取video_id"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info(video_id):
    """获取视频信息（标题、频道）"""
    cmd = [
        'yt-dlp',
        '--js-runtimes', 'node',
        '--cookies-from-browser', 'chromium',
        '--print', '%(title)s|||%(channel)s|||%(uploader)s',
        '--skip-download',
        '--no-warnings',
        'https://www.youtube.com/watch?v=' + video_id
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split('|||')
        return {
            'title': parts[0] if len(parts) > 0 else '',
            'channel': parts[1] if len(parts) > 1 else '',
            'uploader': parts[2] if len(parts) > 2 else ''
        }
    return None

def download_subtitle(video_id):
    """下载字幕，返回解析后的transcript数组"""
    srt_path = f"subtitles/{video_id}.en.srt"
    os.makedirs("subtitles", exist_ok=True)

    cmd = [
        'yt-dlp',
        '--js-runtimes', 'node',
        '--cookies-from-browser', 'chromium',
        '--write-auto-subs', '--sub-langs', 'en',
        '--sub-format', 'srt', '--skip-download',
        '--no-warnings',
        '-o', f"subtitles/{video_id}",
        'https://www.youtube.com/watch?v=' + video_id
    ]
    subprocess.run(cmd, capture_output=True)

    if os.path.exists(srt_path):
        return parse_srt(srt_path)
    return []

def parse_srt(filepath):
    """解析SRT文件"""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r"\n\n+", content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        time_range = lines[1]
        text = " ".join(lines[2:]).strip()
        match = re.match(r"(\d+):(\d+):(\d+)[,.]\d+", time_range)
        if match:
            h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
            time_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
        else:
            time_str = "0:00"
        entries.append({"time": time_str, "text": text})
    return entries

def load_data():
    with open(VIDEOS_JSON, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(VIDEOS_JSON, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 add_video.py <YouTube_URL>")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)
    if not video_id:
        print("错误: 无法从URL提取video_id")
        sys.exit(1)

    print(f"📹 视频 ID: {video_id}")

    # 检查是否已存在
    data = load_data()
    existing = next((v for v in data['videos'] if v['video_id'] == video_id), None)
    if existing:
        print(f"⚠️  视频已存在: {existing.get('video_title', '未知')}")
        sys.exit(0)

    # 获取视频信息
    print("📡 获取视频信息...")
    info = get_video_info(video_id)
    if not info:
        print("   ⚠️  无法自动获取信息，请手动填写")
        info = {'title': '', 'channel': '', 'uploader': ''}
    else:
        print(f"   标题: {info['title']}")
        print(f"   频道: {info['channel']}")

    # 下载字幕
    print("📥 下载字幕...")
    transcript = download_subtitle(video_id)
    if transcript:
        print(f"   ✅ {len(transcript)} 条字幕")
    else:
        print("   ⚠️  无字幕可用")

    # 创建视频条目
    new_video = {
        "video_id": video_id,
        "video_title": info['title'],
        "video_link": f"https://www.youtube.com/watch?v={video_id}",
        "channel_name": info['channel'],
        "speaker_name": info['uploader'] or info['channel'],
        "primary_topic": "",
        "specific_topics": [],
        "transcript": transcript,
        "ai_analysis": "",
        "created_at": datetime.now().isoformat() + "Z",
        "analyzed_at": None,
        "related": []
    }

    data['videos'].insert(0, new_video)
    save_data(data)

    print(f"\n✅ 已添加到 {VIDEOS_JSON}")
    if not info['title']:
        print("⚠️  请手动填写: video_title, channel_name, speaker_name")
    print("⚠️  请手动填写: primary_topic, specific_topics, ai_analysis, related")

if __name__ == "__main__":
    main()
