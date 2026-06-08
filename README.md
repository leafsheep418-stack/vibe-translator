# vibe-translator

vibe-translator 是一个 AI 风格翻译器。

V0.1 是一个 Windows 桌面后台小工具：用户先运行程序，然后在 Discord、浏览器、Word 或其他软件里选中英文文字，按 `F8`，程序会临时模拟 `Ctrl + C` 读取选中文字，调用 AI 翻译，并弹出一个小窗口显示中文翻译结果。

这个项目会尽量保持简单清楚，适合新手学习和逐步扩展。

## V0.1 功能

- 后台等待快捷键
- 读取用户当前选中的英文文字
- 按当前风格翻译成中文
- 弹出小窗口显示翻译结果
- 支持 OpenAI / ChatGPT API
- 支持 DeepSeek API
- 内置三个风格：
  - `discord`：适合 Discord 聊天，日常、自然、轻松
  - `academic`：适合论文和学术写作，正式、严谨
  - `business`：适合商务邮件，礼貌、清晰、专业
- 保留 emoji、链接、@用户名和代码片段

## 项目结构

```text
vibe-translator/
  main.py
  requirements.txt
  README.md
  .env.example
  .gitignore
```

## 安装

创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境。

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 设置 API Key

本项目通过环境变量读取 API Key，不要把真实 Key 写进代码。

如果使用 OpenAI / ChatGPT：

```powershell
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

可选：指定 OpenAI 模型：

```powershell
$env:OPENAI_MODEL="gpt-4.1-mini"
```

如果使用 DeepSeek：

```powershell
$env:DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

可选：指定 DeepSeek 模型：

```powershell
$env:DEEPSEEK_MODEL="deepseek-chat"
```

`.env.example` 只放示例，不要写真实 API Key。如果之后你创建本地 `.env` 文件，也不要上传到 GitHub。

## 运行

```bash
python main.py
```

程序启动后会让你选择：

1. API 服务商：OpenAI / ChatGPT 或 DeepSeek
2. 翻译风格：`discord`、`academic` 或 `business`

然后程序会在后台等待快捷键。

## 使用方式

1. 在 Discord、浏览器、Word 或其他软件里，用鼠标选中一段英文。
2. 保持文字处于蓝底选中状态。
3. 按 `F8`。
4. 程序会临时模拟 `Ctrl + C`，读取选中文字。
5. 程序调用 AI 翻译。
6. 弹出一个小窗口显示中文翻译结果。
7. 关闭小窗口后，可以继续使用其他软件。

关闭命令行窗口即可退出程序。

## Roadmap

- [x] Basic command-line translator
- [x] Selected text translation with global hotkey
- [ ] Style presets refinement
- [ ] Web UI
- [ ] Custom presets
- [ ] Clipboard translation
- [ ] Global hotkey settings
- [ ] Screenshot OCR translation
- [ ] Overlay translated image on selected screen area
- [ ] Translation history

## 给新手的说明

`main.py` 里最重要的几个函数：

- `choose_provider()`：选择 OpenAI / ChatGPT 或 DeepSeek。
- `choose_style()`：选择翻译风格。
- `copy_selected_text()`：模拟 `Ctrl + C`，读取选中的文字。
- `translate_text(text, style, provider)`：调用 API 翻译文本。
- `show_popup(root, title, text)`：弹出窗口显示翻译结果。

目前代码故意保持简单。后续可以一步一步加入托盘图标、配置文件、快捷键设置、截图 OCR 和覆盖图层翻译。
