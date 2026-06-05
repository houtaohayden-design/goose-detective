<p align="center">
  <img src="assets/icons/goose.png" alt="鹅探长" width="120" />
</p>

<h1 align="center">🪶 鹅探长 (Goose Detective)</h1>

<p align="center">
  <strong>鹅鸭杀 AI 场外军师 —— 实时转录发言，AI 抓狼，让你赢在逻辑上</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey" alt="Platform" />
  <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build" />
</p>

---

## 🎯 这是什么

在鹅鸭杀中，信息就是一切。**鹅探长**是一个桌面浮窗工具，在你游玩时实时录制所有玩家的语音发言，转录成文字，并调用大模型分析每个人的逻辑漏洞，帮你精准锁定鸭子（狼人）。

> 窗口始终半透明悬浮在游戏上方，不遮挡、不干扰，像真正的侦探助手一样安静工作。

## ✨ 功能

### 音频捕获
- **双路录制**：同时捕获系统音频（其他玩家发言）和麦克风（你自己），两路独立存储
- **两种模式**：
  - 全程录制 — 整局游戏所有对话不遗漏
  - 会议模式 — 拉铃触发的讨论阶段自动开始录制
- **说话人分离**：自动识别不同声纹，给每个玩家分配编号（最多 16 人）
- **手动纠错**：右键点击发言气泡可重新归属说话人

### 语音转录
| 引擎 | 说明 |
|------|------|
| 本地 Whisper | 完全离线，支持 tiny/base/small/medium/large-v3 多档模型 |
| 云端 STT | 讯飞 IAT 实时语音转写 |

### AI 逻辑分析
- **实时矛盾检测**：每段发言下方即时标记逻辑漏洞
- **嫌疑度排名**：会议结束输出每个玩家的 0-100 评分 + 证据链
- **多模型自由切换**：

| 预设模型 | 说明 |
|----------|------|
| DeepSeek | 默认，性价比高 |
| OpenAI (GPT-4o) | 逻辑强悍 |
| Claude | Anthropic API 兼容模式 |
| Gemini | Google 多模态能力 |
| 通义千问 | 阿里云 DashScope |
| Kimi | Moonshot |
| 文心一言 | 百度千帆 v2 |

也支持任意自定义 OpenAI 兼容 API——填 Base URL + Key 即可。

### 交互体验
- 半透明浮窗，始终置顶于游戏上方
- 鹅鸭杀游戏风格主题（深湖蓝 + 鹅黄）
- 全自定义快捷键（录制/会议/显示隐藏）

## 📸 截图

> TODO: 添加截图展示

## 🚀 快速开始

### 环境要求

- Python 3.11+
- **Windows**：需安装 [VB-Cable 虚拟声卡](https://vb-audio.com/Cable/) 并将游戏音频输出到该设备
- **macOS**：需安装 [BlackHole](https://github.com/ExistentialAudio/BlackHole) 虚拟声卡

### 安装

```bash
# 克隆仓库
git clone https://github.com/houtaohayden-design/goose-detective.git
cd goose-detective

# 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

首次启动后：
1. 点击 ⚙️ **设置**
2. 选择转录引擎（Whisper / 云端 STT）
3. 选择 AI 模型并填入 API Key
4. 若有 HF Token 可填入，说话人分离更精准

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+R` | 开始/停止全程录制 |
| `Ctrl+Shift+M` | 开始/停止会议录制 |
| `Ctrl+Shift+H` | 显示/隐藏浮窗 |

## ⌨️ 技术架构

```
main.py                  # 应用入口，初始化 Qt 窗口 + 配置
config.py                # JSON 持久化配置管理
audio/
  capture.py             # sounddevice 双路音频捕获
  diarization.py         # pyannote.audio 声纹分离 + 手动纠错
transcription/
  base.py                # 转录引擎抽象接口
  whisper_engine.py      # faster-whisper 本地离线转录
  cloud_engine.py        # 讯飞 IAT WebSocket 云端实时转写
analysis/
  router.py              # 多模型 AI 路由（OpenAI 兼容协议）
  prompts.py             # 分析 Prompt 模板
ui/
  overlay.py             # 主浮窗 + 后台录制线程调度
  transcript_panel.py    # 实时发言记录面板
  analysis_panel.py      # 嫌疑分析排名面板
  player_bubble.py       # 发言气泡组件（支持右键纠错）
  settings_dialog.py     # 设置对话框
  theme.py / styles.qss  # 鹅鸭杀游戏风格主题
```

## 📦 打包为 exe

在 Windows 上构建安装包，详见 [PACKAGING.md](PACKAGING.md)。

### GitHub Actions（推荐）
推送代码后，在 Actions 标签页手动触发 "Build Windows Installer"，构建完成后下载 Artifact。

### 本地构建
```bash
pip install pyinstaller
pyinstaller goose_detective.spec
# 产物在 dist/鹅探长/
```

## 🧪 测试

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -v
```

## ❓ 常见问题

<details>
<summary><b>macOS 上录制不到系统音频？</b></summary>

需安装 BlackHole 虚拟声卡并设为默认输出/多输出设备。然后在设置中选择 BlackHole 作为音频源。
</details>

<details>
<summary><b>说话人分离不准怎么办？</b></summary>

1. 确保你的 Hugging Face Token 已正确填入
2. 右键点击错误归属的发言气泡，手动重新分配说话人
3. 说话人分离需要 pyannote 模型（首次运行自动下载，约 300MB）
</details>

<details>
<summary><b>AI 分析没有反应？</b></summary>

检查 API Key 和 Base URL 是否填写正确。可以用 DeepSeek（价格极低）先试跑，只需注册 [platform.deepseek.com](https://platform.deepseek.com) 获取 Key。
</details>

<details>
<summary><b>Whisper 模型选哪个？</b></summary>

- `tiny` : 最快，适合低配机器
- `medium` : 平衡，推荐
- `large-v3` : 最准，需要 ~3GB 显存
</details>

## 🤝 贡献

欢迎提 Issue 和 PR！大方向欢迎，细节自取。

## 📄 许可

MIT License

---

<p align="center">
  <i>用逻辑抓狼，别靠直觉。</i> 🕵️‍♂️
</p>
