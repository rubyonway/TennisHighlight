# 🎾 TennisHighlight · 网球高光视频剪辑 Skill

**把球场上的好球，变成值得反复回看的高光。**

那记终于打穿的正手，那段舍不得结束的多拍，还有跑到场边也救回来的球。打的时候很过瘾，回家却很难从一长段录像里重新找到。

TennisHighlight 为爱打球、也想打得更好的你而设计。把网球原片交给它，用一句话开启剪辑与复盘：挑出精彩回合，剪成 **5 分钟以内的高光集锦**，再把击球统计、球路落点和训练建议，放进一份可以边看边复盘的 HTML 报告。

**留下值得分享的一球，也找到下一次进步的方向。**

[English](README.EN.md) · [高光视频 Demo](https://github.com/rubyonway/TennisHighlight/releases/download/demo-v1/tennis-highlight-v5.mp4) · [HTML 复盘 Demo](https://github.com/rubyonway/TennisHighlight/releases/download/demo-v1/tennis-review-html-demo.zip)

## 先看效果

点击下方播放按钮，即可观看完整 4 分 25 秒集锦。在线播放版为 720p，1080p 原画质下载见下表。

https://github.com/user-attachments/assets/208f0f5d-fc70-4ef9-92a4-05a1dcb99d4f

| Demo | 你会看到什么 | 下载 |
| --- | --- | --- |
| 高光剪辑视频 | 4 分 25 秒、7 个完整回合、1080p、现场声音，带球路与落点示意 | [MP4，约 404 MB](https://github.com/rubyonway/TennisHighlight/releases/download/demo-v1/tennis-highlight-v5.mp4) |
| HTML 复盘报告 | 高光视频、567 条回球记录、落点分布、动作截图与练习建议 | [完整演示包，约 405 MB](https://github.com/rubyonway/TennisHighlight/releases/download/demo-v1/tennis-review-html-demo.zip) |

HTML 演示包解压后，打开 `网球训练复盘.html` 即可使用。请保留同目录的“媒体”文件夹。包内已包含高光视频，**不包含三段原片**；全片统计及原片时间索引保留，原片播放入口已移除。看完整 demo 只需下载 HTML 演示包。

## 能做什么

### 1. 好球，值得完整看一遍

- **挑出精彩回合**：结合目标球员的击球质量、连续回球拍数和有画面依据的精彩终结球，挑选长回合、多拍对拉与高光瞬间。
- **保留一分的起承转合**：从回合开始剪到死球，留下攻防转换和最后一拍；通过精选完整回合控制集锦时长。
- **让视线跟得上球**：按球路设置构图关键帧，适当跟随与缩放，让击球者和关键球路更清楚。
- **把球路画出来**：在可辨认的片段添加轨迹、回球计数和类似鹰眼视角的落点示意，直观看方向与深浅。

### 2. 看见优势，也找到下一次该练什么

- **正反手表现**：统计全片正手、反手与无法分类的回球，展示回球结果、回合延续有效率和未知样本，让数字有据可查。
- **球速与移动参考**：在机位、标定和连续跟踪条件支持时，提供正反手平均球速、移动距离等视频估计，并注明覆盖范围；证据不足时留空。
- **动作拆解**：截取关键击球画面，结合原片时间，观察准备、脚步、触球和随挥中的可见问题。
- **可执行的练习建议**：把“脚步再好一点”变成下一次上场就能练的动作提示、练习组数与目标。

### 3. 一份报告，把这一场串起来

集锦播放、技术统计、落点图、逐球明细和训练建议集中在同一页。点击高光落点回看对应片段，筛选正反手与回球结果，也可以下载数据继续分析。包含原片的完整交付还支持按原片时间回看。

## 安装与使用

将整个技能文件夹命名为 `tennis-video-review`，放入 Codex 的 skills 目录。默认位置为 `~/.codex/skills/tennis-video-review`。

也可以用 Git 安装到尚不存在的目标目录：

```bash
git clone https://github.com/rubyonway/TennisHighlight.git ~/.codex/skills/tennis-video-review
```

开启新会话，提供视频路径，然后说：

```text
用 $tennis-video-review 剪辑网球视频，以更靠近拍摄机位的球员为主，保留完整回合，剪成 5 分钟以内的高光集锦，并统计全片正反手表现、分析击球动作，生成可播放视频的 HTML 复盘报告。
```

**输入网球原片，带走高光集锦和一份属于自己的训练复盘。**

完整执行说明见 [SKILL.md](SKILL.md)。这是供 Codex 使用的工作流 Skill，包含分析与剪辑指引、统计和预览辅助脚本；识别效果取决于视频清晰度、机位、遮挡与复核情况，未内置专用网球识别模型。

## 关于数据，认真一点

- 高光里的表现不能代替全场统计；回合延续有效率也不等于逐球界内率。
- “鹰眼式”指落点示意的呈现方式。单机位视频估计不具备专业鹰眼判罚或雷达测速精度。
- 看不清的球保留未知。使用用户观察校准的落点会明确标注，不能用校准结果反过来证明同一观察。

## 辅助脚本与说明

需要 Python 3.9 或以上，辅助脚本只使用标准库。视频处理按任务需要使用本地 FFmpeg／FFprobe，无需公司内网或指定云服务。

```bash
# 汇总逐球标注，保留未知结果
python3 scripts/summarize_events.py /path/to/events.json --output /path/to/summary.json

# 本地预览 HTML，支持拖动视频进度
python3 scripts/serve_report.py /path/to/report-folder --port 8921

# 校验辅助脚本
python3 scripts/check_helpers.py
```

更多细节：[数据与报告约定](references/data-and-report.md) · [视频分析与剪辑](references/video-analysis.md)。

本仓库的演示视频与报告通过 [Releases](https://github.com/rubyonway/TennisHighlight/releases/tag/demo-v1) 单独提供，安装 Skill 无需下载演示素材。使用 Skill 生成的个人视频与报告默认保存在本地。
