#!/usr/bin/env python3
"""
AI Daily Report - Builder
生成静态网站
"""

import os
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "content" / "daily"
TEMPLATE_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "docs"  # GitHub Pages 需要 docs 作为发布目录

def load_config():
    config_file = PROJECT_ROOT / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_daily_reports():
    """获取所有日报"""
    reports = []
    
    if not CONTENT_DIR.exists():
        return reports
    
    for md_file in CONTENT_DIR.glob("*.md"):
        date = md_file.stem
        # 读取文件获取标题
        with open(md_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            title = date
            if 'title:' in first_line:
                # 提取标题
                title = first_line.replace('title:', '').strip().strip('"')
        
        reports.append({
            'date': date,
            'title': title,
            'url': f"./daily/{date}.html"
        })
    
    # 按日期倒序
    reports.sort(key=lambda x: x['date'], reverse=True)
    return reports

def get_latest_report():
    """获取最新日报"""
    reports = get_daily_reports()
    if reports:
        return reports[0]
    return None

def generate_index_html(reports, config):
    """生成首页"""
    site_config = config.get('site', {})
    latest = get_latest_report()
    
    reports_html = ""
    for report in reports[:30]:  # 最近30条
        reports_html += f"""
        <div class="report-item">
            <a href="{report['url']}">{report['title']}</a>
        </div>"""
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_config.get('title', 'AI Daily Report')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        header p {{ opacity: 0.9; }}
        .latest-report {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .latest-report h2 {{ color: #667eea; margin-bottom: 15px; }}
        .latest-report a {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 15px;
        }}
        .latest-report a:hover {{
            background: #764ba2;
        }}
        .archive {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .archive h2 {{ margin-bottom: 20px; color: #333; }}
        .report-item {{
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}
        .report-item:last-child {{ border-bottom: none; }}
        .report-item a {{
            color: #667eea;
            text-decoration: none;
            font-size: 1.1em;
        }}
        .report-item a:hover {{
            color: #764ba2;
        }}
        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{site_config.get('title', 'AI Daily Report')}</h1>
            <p>{site_config.get('description', '每日AI领域资讯早报')}</p>
        </header>
        
        {""
        if latest:
        f'''<div class="latest-report">
            <h2>📰 今日要闻</h2>
            <p>最新日报已更新，点击查看详细内容</p>
            <a href="{latest['url']}">查看今日日报 →</a>
        </div>'''
        else:
        '<div class="latest-report"><p>暂无日报</p></div>'
        ""}
        
        <div class="archive">
            <h2>📁 历史日报</h2>
            {reports_html if reports_html else '<p>暂无历史记录</p>'}
        </div>
        
        <footer>
            <p>{site_config.get('author', 'AI Daily Report')} · 自动生成</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html

def generate_report_html(date, config):
    """生成单篇日报"""
    md_file = CONTENT_DIR / f"{date}.md"
    
    if not md_file.exists():
        return None
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单转换 Markdown 到 HTML（实际可用 pandoc）
    html_content = content.replace('## ', '</h2><h2>').replace('### ', '</h3><h3>')
    html_content = html_content.replace('\n\n', '</p><p>')
    html_content = f'<p>{html_content}</p>'
    
    site_config = config.get('site', {})
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{date} - {site_config.get('title', 'AI Daily Report')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .report {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .report h1 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        .report h2 {{ color: #333; margin: 25px 0 15px; font-size: 1.4em; }}
        .report h3 {{ color: #555; margin: 20px 0 10px; font-size: 1.2em; }}
        .report p {{ margin-bottom: 15px; }}
        .back {{
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
        }}
        .back:hover {{ color: #764ba2; }}
        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back">← 返回首页</a>
        <div class="report">
            {html_content}
        </div>
        <footer>
            <p>AI Daily Report · {date}</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html

def build():
    """构建网站"""
    print(f"\n{'='*50}")
    print(f"开始构建网站")
    print(f"{'='*50}\n")
    
    config = load_config()
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "daily").mkdir(parents=True, exist_ok=True)
    
    # 生成首页
    reports = get_daily_reports()
    index_html = generate_index_html(reports, config)
    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"✓ 生成首页: index.html")
    
    # 生成每篇日报
    for report in reports:
        date = report['date']
        html = generate_report_html(date, config)
        if html:
            output_file = OUTPUT_DIR / "daily" / f"{date}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✓ 生成日报: daily/{date}.html")
    
    print(f"\n{'='*50}")
    print(f"构建完成! 共 {len(reports)} 篇日报")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    build()
