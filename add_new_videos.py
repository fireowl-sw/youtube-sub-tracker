#!/usr/bin/env python3
"""
将 check_updates.py 发现的新视频添加到 videos.json
只填充基础字段，分析字段留空后续补充
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime


SUBSCRIPTIONS_FILE = Path(__file__).parent / "subscriptions.json"
VIDEOS_FILE = Path(__file__).parent / "videos.json"


def load_data():
    """加载所有数据文件"""
    with open(SUBSCRIPTIONS_FILE) as f:
        subscriptions = json.load(f)
    with open(VIDEOS_FILE) as f:
        videos_data = json.load(f)
    return subscriptions, videos_data


def save_videos(data):
    """保存 videos.json"""
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_existing_video_ids(videos_data):
    """获取已存在的视频 ID"""
    return {v['video_id'] for v in videos_data['videos']}


def fetch_latest_video_title(rss_url):
    """从 RSS 获取最新视频标题"""
    try:
        with urllib.request.urlopen(rss_url, timeout=10) as response:
            xml_text = response.read().decode('utf-8')

        root = ET.fromstring(xml_text)
        ns = {
            '': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015',
            'media': 'http://search.yahoo.com/mrss/'
        }

        entry = root.find('entry', ns)
        if entry is not None:
            title = entry.find('title', ns).text
            video_id = entry.find('yt:videoId', ns).text
            return title, f'https://www.youtube.com/watch?v={video_id}'
    except Exception as e:
        print(f"    ⚠️ 获取失败: {e}")

    return None, None


def find_new_videos(subscriptions, existing_ids):
    """找出需要添加的新视频"""
    new_videos = []

    for channel in subscriptions['channels']:
        last_seen = channel.get('last_seen_video_id')
        if not last_seen:
            continue

        # 检查是否已存在
        if last_seen in existing_ids:
            continue

        # 从 RSS 获取视频标题
        print(f"\n📡 获取: {channel['name']}")
        title, url = fetch_latest_video_title(channel['rss_url'])

        new_videos.append({
            "video_id": last_seen,
            "video_title": title or f"Video {last_seen}",
            "video_link": url or f'https://www.youtube.com/watch?v={last_seen}',
            "channel_name": channel['name'],
            "speaker_name": "",
            "primary_topic": "",
            "specific_topics": [],
            "content_summary": "",
            "related_channel": "",
            "related_topic": "",
            "topic_connection": [],
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "analyzed_at": None
        })

    return new_videos


def main():
    print("=" * 50)
    print("添加新视频到 videos.json")
    print("=" * 50)

    subscriptions, videos_data = load_data()
    existing_ids = get_existing_video_ids(videos_data)

    new_videos = find_new_videos(subscriptions, existing_ids)

    if not new_videos:
        print("\n✓ 没有新视频需要添加")
        return

    print(f"\n📋 发现 {len(new_videos)} 个新视频：")
    for v in new_videos:
        print(f"\n  - {v['channel_name']}: {v['video_title']}")
        print(f"    ID: {v['video_id']}")

    # 添加到 videos.json
    videos_data['videos'].extend(new_videos)
    save_videos(videos_data)

    print(f"\n✅ 已添加 {len(new_videos)} 个视频到 videos.json")
    print("\n💡 下一步：填充分析字段（speaker_name, topics, summary...）")
    print("=" * 50)


if __name__ == '__main__':
    main()
