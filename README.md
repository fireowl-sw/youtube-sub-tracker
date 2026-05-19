# YouTube Sub Tracker

Track AI/LLM-related YouTube channels with automated subtitle downloading and analysis.

## 📊 Data View

- **GitHub Pages**: https://fireowl-sw.github.io/youtube-sub-tracker/
- **Feishu Spreadsheet**: [LLM YouTube landscape tracker](https://kbb6445k2b.feishu.cn/base/VeGEbUUANarJn1sxGfwcDgnNnEg)

## Tracked Channels

| Channel | Focus |
|---------|-------|
| **Andrej Karpathy** | LLM, Transformer, GPT Implementation |
| **3Blue1Brown** | Math Fundamentals, Neural Network Visualization |
| **Two Minute Papers** | AI Research Frontiers |

## Features

- ✅ RSS subscription tracking for new videos
- ✅ Automatic English subtitle download
- ✅ AI-powered topic categorization and relationship analysis
- ✅ Searchable/filterable video library
- ✅ Complete transcript table display
- 🤖 **OpenClaw Automation** — Scheduled update detection, auto-sync to Feishu

## Local Run

```bash
# 1. Clone project
git clone https://github.com/fireowl-sw/youtube-sub-tracker.git
cd youtube-sub-tracker

# 2. Start HTTP server
python3 -m http.server 8080

# 3. Open in browser
open http://localhost:8080
```

## Add New Video

```bash
python3 add_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Requires `yt-dlp` installation.

## 🤖 Automation (OpenClaw)

This project integrates **OpenClaw** for full automation:

- **Scheduled Detection**: Auto-check channel updates at 08:00, 14:00, 20:00 (Hong Kong Time)
- **Auto Processing**: Download subtitles and update data when new videos found
- **Auto Push**: Deploy to GitHub Pages after updates
- **Feishu Sync**: Auto-sync to [Feishu Spreadsheet](https://kbb6445k2b.feishu.cn/base/VeGEbUUANarJn1sxGfwcDgnNnEg)
- **Notification**: Feishu private message with update results

### 📥 Data Collection

```
YouTube RSS Feed → check_updates.py → New video detection
                                        ↓
                              yt-dlp subtitle download
                                        ↓
                              videos.json storage
                                        ↓
                    ┌──────────────────┴──────────────────┐
                    ↓                                     ↓
            GitHub Pages                          Feishu Spreadsheet
            (HTML Display)                      (Multi-dimensional Table)
```

**Data Flow:**

1. **RSS Subscription**: Check YouTube RSS feed hourly for latest videos
2. **Subtitle Download**: Use `yt-dlp` to download English subtitles (SRT format)
3. **Data Parsing**: Convert SRT to JSON transcript array
4. **AI Analysis**: Generate topic categorization and content summary from transcripts

### 📊 Summary Generation

Each video contains the following information:

| Field | Description | Source |
|------|-------------|--------|
| Video Title | Video title | YouTube RSS |
| Primary Topic | Main topic | AI transcript analysis |
| Specific Topics | Specific topics | AI transcript analysis |
| Content Summary | Content summary | AI transcript analysis |
| Related Content | Related videos | Cross-analysis |
| Transcript | Full subtitle | yt-dlp download |

### 🔄 Keeping Feishu Updated

Feishu spreadsheet auto-sync workflow:

```
Scheduled task → Detect new videos → Download subtitles → Update videos.json
                                                         ↓
                                              Get new video list
                                                         ↓
                                        lark-cli write to Feishu
                                                         ↓
                                        Feishu notify user
```

**Sync field order:**
Video Title → Video Link → Channel Name → Speaker Name → Primary Topic → Specific Topics → Content Summary → Related Channel → Related Topic → Topic Connection → Transcript URL

## File Structure

```
├── index.html          # Main page (self-contained)
├── videos.json         # Video database
├── subscriptions.json  # RSS subscription config
├── add_video.py        # Add new video
├── check_updates.py    # Check for updates
└── subtitles/          # Subtitle files (.gitignore)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

_Built with Claude Code_
