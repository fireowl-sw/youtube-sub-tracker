# YouTube Sub Tracker

追踪 AI/LLM 相关 YouTube 频道的视频，自动下载字幕并展示。

## 📊 Data View

- **GitHub Pages**: https://fireowl-sw.github.io/youtube-sub-tracker/
- **Feishu Spreadsheet**: [LLM YouTube landscape tracker](https://kbb6445k2b.feishu.cn/base/VeGEbUUANarJn1sxGfwcDgnNnEg)

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
- 🤖 **OpenClaw 自动化** — 定时检测更新、自动同步飞书

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

## 🤖 Automation (OpenClaw)

本项目集成了 **OpenClaw** 实现全自动化：

- **定时检测**: 每天 08:00、14:00、20:00（香港时区）自动检查频道更新
- **自动处理**: 发现新视频后自动下载字幕、更新数据
- **自动推送**: 更新后自动推送到 GitHub Pages
- **飞书同步**: 自动同步到 [Feishu Spreadsheet](https://kbb6445k2b.feishu.cn/base/VeGEbUUANarJn1sxGfwcDgnNnEg)
- **消息通知**: 飞书私聊通知更新结果

### 📥 Data Collection

```
YouTube RSS Feed → check_updates.py → 新视频检测
                                        ↓
                              yt-dlp 字幕下载
                                        ↓
                              videos.json 存储
                                        ↓
                    ┌──────────────────┴──────────────────┐
                    ↓                                     ↓
            GitHub Pages                          Feishu Spreadsheet
            (HTML 展示)                           (多维表格)
```

**数据流说明：**

1. **RSS 订阅**：每小时检查 YouTube RSS feed，获取最新视频信息
2. **字幕下载**：使用 `yt-dlp` 下载英文字幕（SRT 格式）
3. **数据解析**：SRT 转换为 JSON 格式的 transcript 数组
4. **AI 分析**：基于字幕内容生成主题分类和内容摘要

### 📊 Summary Generation

每个视频包含以下信息：

| 字段 | 说明 | 来源 |
|------|------|------|
| Video Title | 视频标题 | YouTube RSS |
| Primary Topic | 主主题 | AI 分析字幕 |
| Specific Topics | 具体话题 | AI 分析字幕 |
| Content Summary | 内容摘要 | AI 分析字幕 |
| Related Content | 关联视频 | 交叉分析 |
| Transcript | 完整字幕 | yt-dlp 下载 |

### 🔄 Keeping Feishu Updated

飞书表格自动同步流程：

```
定时任务触发 → 检测新视频 → 下载字幕 → 更新 videos.json
                                              ↓
                              获取新视频列表
                                              ↓
                              lark-cli 写入飞书表格
                                              ↓
                              飞书私聊通知用户
```

**同步字段顺序：**
Video Title → Video Link → Channel Name → Speaker Name → Primary Topic → Specific Topics → Content Summary → Related Channel → Related Topic → Topic Connection → Transcript URL

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
