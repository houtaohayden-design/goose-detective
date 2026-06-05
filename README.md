# 🪶 鹅探长 (Goose Detective)

在网易 MuMu 模拟器中玩鹅鸭杀时，实时记录玩家发言、转录成文字，并用 AI 分析逻辑漏洞，帮你抓出鸭子（狼人）。

## 功能

- **半透明侧边浮窗**：始终置顶悬浮在游戏上方，鹅鸭杀游戏风格（深湖蓝 + 鹅黄）
- **双路音频捕获**：同时录制系统音频（其他玩家）和麦克风（自己）
- **两种录制模式**：
  - 全程录制 — 记录整局游戏所有对话
  - 会议模式 — 拉铃后开始，仅记录讨论发言
- **说话人区分**：自动分离不同声纹并分配玩家编号（最多 16 人），支持右键手动重新归属
- **实时转录**：本地 Whisper（离线）或云端 STT（讯飞）可切换
- **AI 逻辑分析**：每段发言下方内联标记矛盾点，会议结束输出各玩家嫌疑度排名
- **多模型支持**：DeepSeek / OpenAI / Claude / Gemini / 通义千问 / Kimi / 文心一言，或任意 OpenAI 兼容 API，自己填 Key
- **全自定义快捷键**

## 安装

```bash
pip install -r requirements.txt
```

Windows 系统音频捕获需安装 [VB-Cable 虚拟声卡](https://vb-audio.com/Cable/)，并将游戏声音输出到该虚拟设备。

说话人分离（pyannote）需要免费的 [Hugging Face token](https://huggingface.co/settings/tokens)；首次运行会自动下载模型。

## 运行

```bash
python main.py
```

首次启动后点击 ⚙ 设置，填入：
- 音频：选择转录引擎、Whisper 模型大小
- AI 模型：选预设或自定义 Base URL + API Key + 模型名

## 打包为 exe（Windows）

```bash
pip install pyinstaller
pyinstaller goose_detective.spec
# 产物在 dist/鹅探长/
```

## 测试

```bash
QT_QPA_PLATFORM=offscreen python -m pytest -v
```

## 架构

```
main.py                  入口
config.py                配置（JSON 持久化）
audio/
  capture.py             双路音频捕获
  diarization.py         说话人分离 + 手动纠错
transcription/
  base.py                转录引擎抽象
  whisper_engine.py      本地 Whisper
  cloud_engine.py        云端 STT
analysis/
  router.py              多模型 AI 路由
  prompts.py             分析 Prompt
ui/
  overlay.py             主浮窗 + 后台录制线程
  transcript_panel.py    发言记录面板
  analysis_panel.py      嫌疑分析面板
  settings_dialog.py     设置对话框
  player_bubble.py       发言气泡组件
  theme.py / styles.qss  游戏风格主题
```

设计文档见 `../docs/superpowers/specs/`，实现计划见 `../docs/superpowers/plans/`。
