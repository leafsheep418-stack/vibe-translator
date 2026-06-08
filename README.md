# vibe-translator

vibe-translator 是一个 AI 风格翻译器。

V0.2 是一个 Windows 桌面后台小工具：用户先运行程序，在 GUI 设置窗口里选择 API 服务商、输入 API Key、选择翻译风格，然后在 Discord、浏览器、Word 或其他软件里选中文字，按 `F8` 或 `Ctrl + Alt + T`，程序会临时模拟 `Ctrl + C` 读取选中文字，调用 AI 翻译，并弹出一个小窗口显示翻译结果。

当前翻译方向会根据输入语言自动决定：如果选中内容是中文，就翻译成对应风格的英文；如果选中内容不是中文，就翻译成中文。

这个项目会尽量保持简单清楚，适合新手学习和逐步扩展。

## V0.2 功能

- GUI 设置窗口
- 在窗口里选择 OpenAI / ChatGPT 或 DeepSeek
- 在窗口里输入 API Key
- 在窗口里选择翻译风格
- 可以在窗口里测试 API 是否可用
- 后台等待快捷键
- 读取用户当前选中的文字
- 中文内容翻译成对应风格的英文
- 英文和其他语言内容翻译成中文
- 弹出小窗口显示翻译结果
- 支持 OpenAI / ChatGPT API
- 支持 DeepSeek API
- 内置四个风格：
  - `discord`：适合 Discord 聊天，重点处理缩写、流行梗、网络黑话和吐槽语气
  - `casual`：适合日常交流，自然、清楚、不太正式
  - `academic`：适合论文和学术写作，正式、严谨
  - `business`：适合商务邮件，礼貌、清晰、专业
- 保留 emoji、链接、@用户名和代码片段

## 项目结构

```text
vibe-translator/
  main.py
  requirements.txt
  README.md
  CHANGELOG.md
  LICENSE
  .env.example
  .gitignore
  .gitattributes
```

## 翻译风格

`discord` 适合 Discord 这类网络聊天场景。它会尽量理解缩写、流行梗、网络黑话和吐槽语气。比如中文“祝大家好运”更适合翻成 `gl everyone`，而不是很正式的 `Good luck, everyone`。英文里的 `absolute cinema` 也不会被直译成“绝对电影院”，而会按语境翻译成更像网络表达的中文。

`casual` 适合普通日常交流。它比 `discord` 更克制，不会刻意塞很多缩写或梗。

`academic` 适合论文和学术写作。

`business` 适合商务邮件。

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

V0.2 可以直接在 GUI 设置窗口里输入 API Key，不需要提前在 PowerShell 里设置。

如果你仍然想用环境变量，也可以这样设置。程序打开后会自动读取对应环境变量。

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
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
```

`.env.example` 只放示例，不要写真实 API Key。如果之后你创建本地 `.env` 文件，也不要上传到 GitHub。

## 运行

```bash
python main.py
```

程序启动后会打开 GUI 设置窗口。你需要选择：

1. API 服务商：OpenAI / ChatGPT 或 DeepSeek
2. API Key
3. 模型
4. 翻译风格：`discord`、`casual`、`academic` 或 `business`

然后点击“开始监听”，程序会在后台等待快捷键。

## 使用方式

1. 运行 `python main.py`。
2. 在 GUI 设置窗口里选择服务商、输入 API Key、选择风格。
3. 可以先点击“测试 API”，确认 API Key 和网络可用。
4. 点击“开始监听”。
5. 在 Discord、浏览器、Word 或其他软件里，用鼠标选中一段英文或中文。
6. 保持文字处于蓝底选中状态。
7. 按 `F8` 或 `Ctrl + Alt + T`。
8. 程序会临时模拟 `Ctrl + C`，读取选中文字。
9. 程序调用 AI 翻译。
10. 弹出一个小窗口显示翻译结果。
11. 关闭小窗口后，可以继续使用其他软件。

关闭 GUI 设置窗口即可退出程序。

## Roadmap

- [x] Basic command-line translator
- [x] Selected text translation with global hotkey
- [x] Auto direction for Chinese and non-Chinese text
- [x] Separate Discord and casual styles
- [x] GUI settings window
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

- `build_settings_window(root)`：创建 GUI 设置窗口。
- `copy_selected_text()`：模拟 `Ctrl + C`，读取选中的文字。
- `translate_text(text, style, provider)`：调用 API 翻译文本。
- `show_popup(root, title, text)`：弹出窗口显示翻译结果。

目前代码故意保持简单。后续可以一步一步加入托盘图标、配置文件、快捷键设置、截图 OCR 和覆盖图层翻译。
