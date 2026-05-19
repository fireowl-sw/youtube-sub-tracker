#!/usr/bin/env python3
"""
检查 YouTube 频道是否有新视频
只读取 RSS，不调用 yt-dlp（除非有新视频需要分析）
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


SUBSCRIPTIONS_FILE = Path(__file__).parent / "subscriptions.json"


def load_subscriptions():
    """加载订阅数据"""
    with open(SUBSCRIPTIONS_FILE, 'r') as f:
        return json.load(f)


def save_subscriptions(data):
    """保存订阅数据"""
    with open(SUBSCRIPTIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_latest_video(rss_url):
    """
    从 RSS 获取最新视频信息
    只解析第一个 <entry>，非常轻量
    """
    with urllib.request.urlopen(rss_url) as response:
        xml_text = response.read().decode('utf-8')

    root = ET.fromstring(xml_text)

    # YouTube RSS uses namespaces
    ns = {
        '': 'http://www.w3.org/2005/Atom',
        'yt': 'http://www.youtube.com/xml/schemas/2015',
        'media': 'http://search.yahoo.com/mrss/'
    }

    # 只获取第一个 entry（最新视频）
    entry = root.find('entry', ns)
    if entry is None:
        return None

    video_id = entry.find('yt:videoId', ns).text
    title = entry.find('title', ns).text
    published = entry.find('published', ns).text
    link = entry.find('link', ns).get('href')

    return {
        'video_id': video_id,
        'title': title,
        'published': published,
        'url': link
    }


def check_channel(channel_data):
    """检查单个频道是否有新视频"""
    print(f"\n📺 检查: {channel_data['name']}")
    print(f"   RSS: {channel_data['rss_url']}")

    try:
        latest = fetch_latest_video(channel_data['rss_url'])
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return None

    if latest is None:
        print("   ❌ 无法获取视频信息")
        return None

    print(f"   最新视频: {latest['title']}")
    print(f"   视频 ID: {latest['video_id']}")
    print(f"   发布时间: {latest['published']}")

    # 检查是否有新视频
    last_seen = channel_data.get('last_seen_video_id')

    if last_seen is None:
        print("   ✨ 首次检查，记录此视频")
        return latest

    if last_seen == latest['video_id']:
        print("   ✓ 没有新视频")
        return None

    print(f"   🆕 发现新视频！上次的: {last_seen}")
    return latest


def main():
    print("=" * 50)
    print("YouTube 订阅更新检查")
    print("=" * 50)

    data = load_subscriptions()
    new_videos = []

    for channel in data['channels']:
        latest = check_channel(channel)

        if latest:
            # 更新 last_seen
            channel['last_seen_video_id'] = latest['video_id']
            channel['last_check_time'] = datetime.utcnow().isoformat() + 'Z'

            # 检查是否已经分析过
            already_analyzed = any(
                v['video_id'] == latest['video_id']
                for v in data['analyzed_videos']
            )

            if not already_analyzed:
                new_videos.append({
                    'channel': channel['name'],
                    'channel_id': channel['channel_id'],
                    **latest
                })

    # 存回文件
    save_subscriptions(data)

    # 报告结果
    print("\n" + "=" * 50)
    if new_videos:
        print(f"🎉 发现 {len(new_videos)} 个新视频需要分析：")
        for v in new_videos:
            print(f"\n  - {v['channel']}: {v['title']}")
            print(f"    URL: {v['url']}")
        print("\n💡 下一步：用 yt-dlp 获取这些视频的字幕")
    else:
        print("✓ 所有频道没有新视频")
    print("=" * 50)

    return new_videos


if __name__ == '__main__':
    main()
