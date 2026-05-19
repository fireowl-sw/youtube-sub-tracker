#!/usr/bin/env python3
"""
获取每个频道历史视频，直到达到目标数量
"""
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

SUBSCRIPTIONS_FILE = Path(__file__).parent / "subscriptions.json"
VIDEOS_FILE = Path(__file__).parent / "videos.json"
TARGET_PER_CHANNEL = 10  # 每个频道目标视频数


def load_data():
    with open(SUBSCRIPTIONS_FILE) as f:
        subscriptions = json.load(f)
    with open(VIDEOS_FILE) as f:
        videos_data = json.load(f)
    return subscriptions, videos_data


def save_videos(data):
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_rss_videos(rss_url, limit=15):
    """从 RSS 获取视频列表"""
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


def get_channel_speaker(channel_name):
    """获取频道演讲者名称"""
    speakers = {
        'Andrej Karpathy': 'Andrej Karpathy',
        '3Blue1Brown': 'Grant Sanderson',
        'Two Minute Papers': 'Károly Zsolnai-Fehér'
    }
    return speakers.get(channel_name, '')


def main():
    print("=" * 50)
    print("批量获取频道历史视频")
    print("=" * 50)

    subscriptions, videos_data = load_data()
    existing_ids = {v['video_id'] for v in videos_data['videos']}

    # 统计每个频道现有视频数
    channel_counts = {}
    for v in videos_data['videos']:
        ch = v.get('channel_name', '')
        if ch:
            channel_counts[ch] = channel_counts.get(ch, 0) + 1

    new_count = 0

    for channel in subscriptions['channels']:
        channel_name = channel['name']
        current_count = channel_counts.get(channel_name, 0)
        need = TARGET_PER_CHANNEL - current_count

        print(f"\n📺 {channel_name}")
        print(f"   当前: {current_count}, 目标: {TARGET_PER_CHANNEL}, 需要: {need}")

        if need <= 0:
            print(f"   ✓ 已达到目标")
            continue

        try:
            all_videos = fetch_rss_videos(channel['rss_url'], limit=15)
        except Exception as e:
            print(f"   ❌ 获取失败: {e}")
            continue

        # 过滤掉已存在的
        fresh = [v for v in all_videos if v['video_id'] not in existing_ids]

        if not fresh:
            print(f"   ✓ RSS 中的视频均已收录")
            continue

        # 只添加需要的数量
        to_add = fresh[:need]

        print(f"   新增 {len(to_add)} 个视频:")
        for v in to_add:
            print(f"     🆕 {v['title']}")

        speaker_name = get_channel_speaker(channel_name)

        for v in to_add:
            videos_data['videos'].append({
                "video_id": v['video_id'],
                "video_title": v['title'],
                "video_link": v['url'],
                "channel_name": channel_name,
                "speaker_name": speaker_name,
                "primary_topic": "",
                "specific_topics": [],
                "transcript": [],
                "ai_analysis": "",
                "created_at": datetime.utcnow().isoformat() + 'Z',
                "analyzed_at": None,
                "related": []
            })
            existing_ids.add(v['video_id'])
            new_count += 1
            channel_counts[channel_name] = channel_counts.get(channel_name, 0) + 1

    if new_count:
        save_videos(videos_data)
        print(f"\n✅ 共新增 {new_count} 个视频")
        print(f"   总视频数: {len(videos_data['videos'])}")
    else:
        print(f"\n✓ 没有新视频需要添加")

    print("=" * 50)


if __name__ == '__main__':
    main()
