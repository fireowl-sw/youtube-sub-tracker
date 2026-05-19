#!/usr/bin/env python3
"""
获取每个频道最新 5 个视频，合并到 videos.json
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime


SUBSCRIPTIONS_FILE = Path(__file__).parent / "subscriptions.json"
VIDEOS_FILE = Path(__file__).parent / "videos.json"


def load_data():
    with open(SUBSCRIPTIONS_FILE) as f:
        subscriptions = json.load(f)
    with open(VIDEOS_FILE) as f:
        videos_data = json.load(f)
    return subscriptions, videos_data


def save_videos(data):
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_recent_videos(rss_url, limit=5):
    """从 RSS 获取最近 N 个视频"""
    with urllib.request.urlopen(rss_url, timeout=10) as response:
        xml_text = response.read().decode('utf-8')

    root = ET.fromstring(xml_text)
    ns = {
        '': 'http://www.w3.org/2005/Atom',
        'yt': 'http://www.youtube.com/xml/schemas/2015',
        'media': 'http://search.yahoo.com/mrss/'
    }

    entries = root.findall('entry', ns)[:limit]
    videos = []

    for entry in entries:
        video_id = entry.find('yt:videoId', ns).text
        title = entry.find('title', ns).text
        published = entry.find('published', ns).text
        link_el = entry.find('link', ns)
        link = link_el.get('href')

        videos.append({
            'video_id': video_id,
            'title': title,
            'url': link,
            'published': published
        })

    return videos


def main():
    print("=" * 50)
    print("批量获取频道最新视频")
    print("=" * 50)

    subscriptions, videos_data = load_data()
    existing_ids = {v['video_id'] for v in videos_data['videos']}

    new_count = 0

    for channel in subscriptions['channels']:
        print(f"\n📺 {channel['name']}")

        try:
            recent = fetch_recent_videos(channel['rss_url'], limit=5)
        except Exception as e:
            print(f"   ❌ 获取失败: {e}")
            continue

        fresh = [v for v in recent if v['video_id'] not in existing_ids]

        if not fresh:
            print(f"   ✓ 5 个视频均已收录")
            continue

        print(f"   最新 5 个视频中，{len(fresh)} 个是新收录的：")
        for v in fresh:
            print(f"     🆕 {v['title']}")

        for v in fresh:
            videos_data['videos'].append({
                "video_id": v['video_id'],
                "video_title": v['title'],
                "video_link": v['url'],
                "channel_name": channel['name'],
                "speaker_name": "",
                "primary_topic": "",
                "specific_topics": [],
                "related_channel": "",
                "related_topic": "",
                "topic_connection": [],
                "transcript": [],
                "ai_analysis": "",
                "created_at": datetime.utcnow().isoformat() + 'Z',
                "analyzed_at": None
            })
            new_count += 1

    if new_count:
        save_videos(videos_data)
        print(f"\n✅ 共新增 {new_count} 个视频到 videos.json")
    else:
        print(f"\n✓ 没有新视频需要添加")

    print("=" * 50)


if __name__ == '__main__':
    main()
