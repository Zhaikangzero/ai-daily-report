# AI Daily Report

每日 AI 领域资讯早报，自动抓取 + AI 整理 + GitHub Pages 发布。

## 关注领域

- AI（大模型、模型动态）
- 机器人
- AI 硬件
- AI 政策
- AI 应用创新

## 运行方式

### 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行抓取
python scripts/fetcher.py

# 生成报告
python scripts/summarizer.py

# 构建网站
python scripts/builder.py
```

### 自动运行

每天 7:00（北京）自动运行，发布到 GitHub Pages。

## 项目结构

```
├── .github/workflows/daily.yml  # 自动发布 workflow
├── scripts/
│   ├── fetcher.py              # 抓取资讯
│   ├── summarizer.py           # LLM 整理
│   └── builder.py              # 生成静态网站
├── templates/                   # 网站模板
├── content/daily/              # 每日报告
├── config.yaml                 # 配置文件
└── requirements.txt
```

## 配置

编辑 `config.yaml` 修改资讯源和配置。

## License

MIT
