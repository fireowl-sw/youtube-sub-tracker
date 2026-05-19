# YouTube Sub Tracker

追踪 AI/LLM 相关 YouTube 频道的视频，自动下载字幕并展示。

## 追踪频道

- **Andrej Karpathy** — LLM、Transformer、GPT 实现
- **3Blue1Brown** — 数学原理、神经网络可视化
- **Two Minute Papers** — AI 前沿研究解读

## 功能

- ✅ RSS 订阅追踪新视频
- ✅ 自动下载英文字幕
- ✅ AI 主题分类和关联分析
- ✅ 可搜索/过滤的视频库
- ✅ 完整字幕表格展示

## 本地运行

```bash
# 1. 克隆项目
git clone <repo-url>
cd youtube-sub-tracker

# 2. 启动 HTTP 服务器
python3 -m http.server 8080

# 3. 浏览器访问
open http://localhost:8080
```

## 添加新视频

```bash
python3 add_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

需要安装 `yt-dlp` 并确保浏览器已登录 YouTube。

## 文件结构

```
├── index.html          # 主页面（自包含）
├── videos.json         # 视频数据库
├── subscriptions.json  # RSS 订阅配置
├── add_video.py        # 添加新视频
├── check_updates.py    # 检查更新
└── subtitles/          # 字幕文件（.gitignore）
```

## GitHub Pages

直接访问 `https://<username>.github.io/<repo>/` 即可查看。

---

_项目使用 Claude Code 构建_
