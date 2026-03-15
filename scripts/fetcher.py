#!/usr/bin/env python3
"""
AI Daily Report - Fetcher
从各资讯源抓取最新内容
"""

import feedparser
import requests
import json
import yaml
import os
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
OUTPUT_DIR = Path(__file__).parent.parent / "content" / "daily"

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_rss(url, source_name):
    """抓取 RSS 订阅源"""
    print(f"📥 抓取 {source_name}: {url}")
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:10]:  # 取最新10条
            articles.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', '')[:500],
                'published': entry.get('published', ''),
                'source': source_name
            })
        print(f"   ✓ 获取 {len(articles)} 条")
        return articles
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return []

def fetch_web(url, source_name):
    """抓取网页"""
    print(f"🌐 抓取 {source_name}: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'lxml')
        
        articles = []
        # 简单提取标题和链接
        for a in soup.find_all('a', href=True)[:10]:
            title = a.get_text(strip=True)
            if title and len(title) > 10:
                articles.append({
                    'title': title,
                    'link': a['href'],
                    'summary': '',
                    'published': datetime.now().isoformat(),
                    'source': source_name
                })
        
        print(f"   ✓ 获取 {len(articles)} 条")
        return articles
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return []

def fetch_all():
    """抓取所有配置的源"""
    config = load_config()
    all_articles = []
    
    print(f"\n{'='*50}")
    print(f"开始抓取资讯 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    for source in config.get('sources', []):
        url = source['url']
        name = source['name']
        
        if 'rss' in url.lower() or 'feed' in url.lower():
            articles = fetch_rss(url, name)
        else:
            articles = fetch_web(url, name)
        
        all_articles.extend(articles)
    
    # 按发布时间排序
    all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    # 保存到文件
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = OUTPUT_DIR / f"{today}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'articles': all_articles,
            'fetched_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"抓取完成: 共 {len(all_articles)} 条")
    print(f"保存至: {output_file}")
    print(f"{'='*50}\n")
    
    return all_articles

if __name__ == "__main__":
    fetch_all()
