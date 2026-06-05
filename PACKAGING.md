# 打包说明

鹅探长是 Windows 桌面工具，安装包必须在 **Windows** 上构建（PyInstaller 不支持跨平台编译，无法在 macOS/Linux 上产出 Windows exe）。下面是三种方式，任选其一。

## 方式一：GitHub Actions 自动构建（推荐，无需 Windows 机器）

仓库已包含 `.github/workflows/build-windows.yml`。把代码推到 GitHub 后：

- **手动触发**：进入仓库 Actions 标签页 → "Build Windows Installer" → Run workflow。完成后在该次运行的 Artifacts 里下载 `GooseDetective-Windows-Installer`。
- **打 tag 自动发布**：
  ```bash
  git tag v1.0.0 && git push origin v1.0.0
  ```
  工作流会自动构建并把安装包附加到对应的 GitHub Release。

工作流在 Windows runner 上完成：安装依赖 → 跑测试 → PyInstaller 打包 → Inno Setup 编译安装包。

## 方式二：本地 Windows 一键构建

在 Windows 机器上：

1. 安装 [Python 3.11](https://www.python.org/downloads/) 和 [Inno Setup 6](https://jrsoftware.org/isdl.php)
2. 双击运行 `build_windows.bat`

产物：
- 免安装版：`dist\GooseDetective\`（绿色版，整个文件夹拷走即可运行）
- 安装包：`dist\installer\鹅探长-Setup-1.0.0.exe`

> 若未装 Inno Setup，脚本仍会产出免安装版，只是跳过安装包步骤。

## 方式三：手动命令

```bat
pip install -r requirements.txt pyinstaller
pyinstaller goose_detective.spec
REM 然后用 Inno Setup 编译：
"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer\installer.iss
```

## 自定义图标

把一个 `.ico` 文件放到 `assets/icons/goose.ico`，PyInstaller 会自动用作程序图标（缺省时构建仍能成功，只是用默认图标）。

## 用户运行的前置条件

安装包只打包应用本身，以下为运行时依赖，需用户自行准备：

- **VB-Cable 虚拟声卡**（捕获系统音频）：<https://vb-audio.com/Cable/>
- **Hugging Face token**（说话人分离 pyannote 模型，免费）：首次使用在设置中填入
- **AI 模型 API Key**：DeepSeek / OpenAI 等，在设置中填入
- 首次运行会自动下载 Whisper 与 pyannote 模型（约 1.5GB + 300MB）

> 提示：模型体积大，若希望安装包内置模型实现真正离线开箱即用，可在 PyInstaller 的 `datas` 中加入预下载的模型目录——会显著增大安装包（数 GB），按需取舍。
