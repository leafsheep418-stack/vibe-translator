# 更新日志

这个文件用来记录项目每次比较重要的改动。

## Unreleased

- 新增 `config.json` 本地配置保存，可选择是否保存 API Key。
- 优化 GUI 布局，将“开始监听”改为更适合普通用户的“开启快捷翻译”。
- 新增 GUI 内置“使用方法”窗口，说明 API Key、基本用法和 OpenAI / DeepSeek API 链接。
- 翻译结果窗口新增“复制结果”按钮。
- 新增 `requirements-dev.txt` 和 `build_exe.bat`，为 PyInstaller 打包 exe 做准备。
- 将 DeepSeek 默认模型从 `deepseek-chat` 更新为 `deepseek-v4-flash`。
- 新增 GUI 设置窗口，可以在窗口里选择服务商、输入 API Key、选择模型和翻译风格。
- 新增“测试 API”按钮，方便确认 API Key 和网络是否可用。
- 新增备用快捷键 `Ctrl + Alt + T`，避免部分键盘的 `F8` 不易触发。
- 修复 GitHub 仓库中文本文件换行格式异常的问题。
- 改进 `discord` 风格 prompt，让它更适合网络聊天语气。
- 支持根据输入语言自动决定翻译方向：
  - 中文翻译成对应风格的英文
  - 英文和其他语言翻译成中文
- 将普通日常交流从 `discord` 风格中拆出，新增 `casual` 风格。
- 强化 `discord` 风格对缩写、流行梗和网络语气的处理，例如 `gl`、`lol`、`lmao`、`absolute cinema`。
