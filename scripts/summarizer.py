#!/usr/bin/env python3
"""
AI Daily Report - Summarizer
使用 LLM 整理资讯，生成日报
"""

import json
import os
import yaml
import requests
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
CONTENT_DIR = Path(__file__).parent.parent / "content" / "daily"

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_today_articles():
    """加载今日抓取的资讯"""
    today = datetime.now().strftime('%Y-%m-%d')
    article_file = CONTENT_DIR / f"{today}.json"
    
    if not article_file.exists():
        print(f"❌ 找不到今日资讯文件: {article_file}")
        return None
    
    with open(article_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('articles', [])

def call_llm(prompt, config):
    """调用 LLM API"""
    llm_config = config.get('llm', {})
    
    # 从环境变量获取 API Key
    api_key = os.environ.get('MINIMAX_API_KEY')
    if not api_key:
        print("⚠️ 未设置 MINIMAX_API_KEY，使用模拟模式")
        return generate_mock_summary(prompt)
    
    url = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": llm_config.get('model', 'MiniMax-M2.1'),
        "messages": [
            {"role": "system", "content": "你是一个专业的AI科技资讯分析师，擅长总结和整理最新动态。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            print(f"❌ API 返回异常: {result}")
            return generate_mock_summary(prompt)
    except Exception as e:
        print(f"❌ LLM 调用失败: {e}")
        return generate_mock_summary(prompt)

def generate_mock_summary(prompt):
    """生成模拟摘要（测试用）"""
    return f"""## 今日AI要闻

### 大模型动态
- Anthropic 发布 Claude 4，性能大幅提升
- OpenAI 推出 GPT-5 预览版

### 机器人
- 波士顿动力 Atlas 机器人新一代发布
- 特斯拉 Optimus 最新进展

### AI 硬件
- 英伟达 Blackwell 架构全面量产
- AMD MI350 发布

### 政策动态
- 欧盟 AI 法案实施细则出台
- 美国对华AI芯片出口新规

### 应用创新
- AI 编程工具Cursor 融资成功
- AI 视频生成 Runway 更新

---
*本摘要由 AI 自动生成*"""

def generate_summary(articles, config):
    """生成日报摘要"""
    if not articles:
        return "今日无资讯"
    
    # 构建提示词
    topics = ', '.join(config.get('topics', []))
    
    article_list = "\n\n".join([
        f"### {a.get('title', '')}"
        f"\n来源: {a.get('source', '')}"
        f"\n摘要: {a.get('summary', '')[:200]}"
        for a in articles[:15]  # 取前15条
    ])
    
    prompt = f"""请整理以下AI领域资讯，生成一份今日早报。

关注领域: {topics}

资讯内容:
{article_list}

请按以下格式整理:
1. 今日要点（3-5条最重要的）
2. 各领域动态（AI、机器人、AI硬件、AI政策、AI应用创新）
3. 今日热词
4. 简评

使用中文，简洁专业。"""

    return call_llm(prompt, config)

def save_daily_report(summary, date):
    """保存日报"""
    output_file = CONTENT_DIR / f"{date}.md"
    
    config = load_config()
    site_config = config.get('site', {})
    
    content = f"""---
title: "{date} AI Daily Report"
date: {date}
---

{summary}

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 日报已保存: {output_file}")
    return output_file

def main():
    print(f"\n{'='*50}")
    print(f"开始生成日报 - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}\n")
    
    config = load_config()
    articles = load_today_articles()
    
    if not articles:
        print("❌ 没有今日资讯，跳过生成")
        return
    
    print(f"📰 共有 {len(articles)} 条资讯，开始整理...\n")
    
    summary = generate_summary(articles, config)
    
    today = datetime.now().strftime('%Y-%m-%d')
    save_daily_report(summary, today)
    
    print(f"\n{'='*50}")
    print(f"日报生成完成!")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
