import os
import queue
import threading
import time
import tkinter as tk


STYLE_PROMPTS = {
    "discord": (
        "根据用户选中文字的主要语言决定翻译方向："
        "如果主要是英文，就翻译成中文，但要保留 Discord / 网络聊天语气；"
        "如果主要是中文，就翻译成适合 Discord 聊天的英文。"
        "这个风格重点处理英文缩写、流行梗、网络黑话、吐槽、玩笑和阴阳怪气。"
        "中译英时，如果可以自然使用缩写或网络表达，就优先使用缩写，"
        "例如 good luck 可以写成 gl，thank you 可以写成 ty，"
        "I don't know 可以写成 idk，to be honest 可以写成 tbh。"
        "英译中时，不要逐字硬翻缩写和梗，要翻译出真实含义和语气。"
        "例如 absolute cinema 不能翻译成“绝对电影院”，要按语境翻译成类似“太神了”“电影级名场面”。"
        "不要把 Discord 风格写成正式英文或普通机器翻译。"
        "必须原样保留 emoji、链接、@用户名和代码片段。"
        "遇到网络缩写时按语境翻译，不要逐字翻译。"
        "遇到 lol/lmao/omg/fr/ngl/tbh/idk/rn 等词，要翻译出聊天语气。"
        "如果原文是吐槽、玩笑、阴阳怪气，要保留这种语气。"
        "中文要像真实年轻人聊天，不要像机器翻译。"
    ),
    "casual": (
        "根据用户选中文字的主要语言决定翻译方向："
        "如果主要是英文，就翻译成自然、清楚的中文；"
        "如果主要是中文，就翻译成自然、清楚的英文。"
        "风格适合日常交流，不要太正式，也不要过度使用网络缩写或流行梗。"
        "表达要像普通朋友、同学或同事之间的自然沟通。"
        "必须原样保留 emoji、链接、@用户名和代码片段。"
    ),
    "academic": (
        "根据用户选中文字的主要语言决定翻译方向："
        "如果主要是英文，就翻译成正式、严谨的中文；"
        "如果主要是中文，就翻译成正式、严谨的英文。"
        "风格要适合论文或学术写作，用词准确、客观，避免口语化表达。"
        "必须原样保留 emoji、链接、@用户名和代码片段。"
    ),
    "business": (
        "根据用户选中文字的主要语言决定翻译方向："
        "如果主要是英文，就翻译成礼貌、清晰、专业的中文；"
        "如果主要是中文，就翻译成礼貌、清晰、专业的英文。"
        "风格要适合商务邮件，语气尊重、简洁、得体。"
        "必须原样保留 emoji、链接、@用户名和代码片段。"
    ),
}


PROVIDERS = {
    "openai": {
        "name": "ChatGPT / OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4.1-mini",
        "base_url": None,
    },
    "deepseek": {
        "name": "DeepSeek",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL",
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
    },
}


HOTKEY = "<f8>"
HOTKEY_TEXT = "F8"

result_queue = queue.Queue()
is_translating = False


def check_dependencies():
    """检查第三方依赖是否已经安装。"""
    required_packages = {
        "openai": "openai",
        "pyperclip": "pyperclip",
        "pynput": "pynput",
    }

    missing_packages = []

    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print("缺少依赖：")
        print(", ".join(missing_packages))
        print()
        print("请先运行：")
        print("pip install -r requirements.txt")
        return False

    return True


def choose_provider():
    """让用户选择使用 OpenAI 还是 DeepSeek。"""
    print("请选择 API 服务商：")
    print("1. openai   - ChatGPT / OpenAI")
    print("2. deepseek - DeepSeek")

    provider_map = {
        "1": "openai",
        "2": "deepseek",
        "openai": "openai",
        "chatgpt": "openai",
        "deepseek": "deepseek",
    }

    while True:
        choice = input("请输入服务商编号或名称：").strip().lower()

        if choice in provider_map:
            return provider_map[choice]

        print("无效的服务商。请输入 1、2，或者输入服务商名称。")


def choose_style():
    """让用户选择一个内置翻译风格。"""
    print()
    print("请选择翻译风格：")
    print("1. discord  - Discord 缩写 / 梗 / 网络聊天")
    print("2. casual   - 日常交流")
    print("3. academic - 论文 / 学术写作")
    print("4. business - 商务邮件")

    style_map = {
        "1": "discord",
        "2": "casual",
        "3": "academic",
        "4": "business",
        "discord": "discord",
        "casual": "casual",
        "daily": "casual",
        "academic": "academic",
        "business": "business",
    }

    while True:
        choice = input("请输入风格编号或名称：").strip().lower()

        if choice in style_map:
            return style_map[choice]

        print("无效的风格。请输入 1、2、3、4，或者输入风格名称。")


def check_api_key(provider):
    """检查当前服务商需要的 API Key 是否存在。"""
    provider_info = PROVIDERS[provider]
    api_key_env = provider_info["api_key_env"]

    if os.getenv(api_key_env):
        return True

    print(f"没有检测到 {api_key_env}。")
    print("请先设置环境变量，再运行程序。")
    print()
    print("Windows PowerShell 示例：")
    print(f'$env:{api_key_env}="your_api_key_here"')
    return False


def translate_text(text, style, provider):
    """调用 OpenAI SDK，并且只返回翻译结果。"""
    from openai import OpenAI

    provider_info = PROVIDERS[provider]
    api_key = os.getenv(provider_info["api_key_env"])
    model = os.getenv(provider_info["model_env"], provider_info["default_model"])

    if provider_info["base_url"]:
        client = OpenAI(api_key=api_key, base_url=provider_info["base_url"])
    else:
        client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    STYLE_PROMPTS[style]
                    + "只输出翻译结果，不要解释翻译选择。"
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def copy_selected_text():
    """模拟 Ctrl + C，读取当前软件里被选中的文字。"""
    import pyperclip
    from pynput.keyboard import Controller, Key

    keyboard = Controller()
    old_clipboard = pyperclip.paste()
    clipboard_marker = "__VIBE_TRANSLATOR_EMPTY_SELECTION__"

    # 快捷键触发时，用户可能还按着 Ctrl / Shift / T。
    # 稍微等一下，可以让目标软件先恢复到正常状态，再执行复制。
    time.sleep(0.35)

    pyperclip.copy(clipboard_marker)

    keyboard.press(Key.ctrl)
    keyboard.press("c")
    keyboard.release("c")
    keyboard.release(Key.ctrl)

    time.sleep(0.35)

    selected_text = pyperclip.paste()

    # 尽量不改变用户原本的剪贴板内容。
    pyperclip.copy(old_clipboard)

    if selected_text == clipboard_marker:
        return ""

    return selected_text.strip()


def handle_hotkey(style, provider):
    """快捷键触发后的完整流程：复制、翻译、发送结果到窗口队列。"""
    global is_translating

    if is_translating:
        result_queue.put(("提示", "正在翻译上一段文字，请稍等。"))
        return

    is_translating = True

    try:
        selected_text = copy_selected_text()

        if not selected_text:
            result_queue.put(("提示", "没有读取到选中的文字。请先用鼠标选中文字，再按快捷键。"))
            return

        translated_text = translate_text(selected_text, style, provider)
        result_queue.put(("翻译结果", translated_text))
    except Exception as error:
        result_queue.put(("翻译失败", f"请检查 API Key、网络连接和账号状态。\n\n错误信息：{error}"))
    finally:
        is_translating = False


def show_popup(root, title, text):
    """弹出一个小窗口显示翻译结果。"""
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("520x260")
    window.attributes("-topmost", True)

    text_box = tk.Text(window, wrap="word", font=("Microsoft YaHei UI", 11))
    text_box.insert("1.0", text)
    text_box.config(state="disabled")
    text_box.pack(fill="both", expand=True, padx=12, pady=(12, 8))

    close_button = tk.Button(window, text="关闭", command=window.destroy)
    close_button.pack(pady=(0, 12))

    window.focus_force()


def check_result_queue(root):
    """定期检查是否有新的翻译结果需要显示。"""
    try:
        while True:
            title, text = result_queue.get_nowait()
            show_popup(root, title, text)
    except queue.Empty:
        pass

    root.after(100, check_result_queue, root)


def start_hotkey_listener(style, provider):
    """启动全局快捷键监听。"""
    from pynput import keyboard

    def on_translate_hotkey():
        worker = threading.Thread(
            target=handle_hotkey,
            args=(style, provider),
            daemon=True,
        )
        worker.start()

    hotkeys = keyboard.GlobalHotKeys({
        HOTKEY: on_translate_hotkey,
    })

    hotkeys.start()
    return hotkeys


def main():
    print("Vibe Translator V0.1")
    print("--------------------")

    if not check_dependencies():
        return

    provider = choose_provider()

    if not check_api_key(provider):
        return

    style = choose_style()

    print()
    print("后台翻译工具已启动。")
    print("使用方法：")
    print("1. 在 Discord、浏览器、Word 或其他软件里选中一段英文或中文。")
    print(f"2. 按 {HOTKEY_TEXT}。")
    print("3. 等待小窗口显示翻译结果。")
    print()
    print("关闭这个命令行窗口即可退出程序。")

    root = tk.Tk()
    root.withdraw()

    start_hotkey_listener(style, provider)
    root.after(100, check_result_queue, root)
    root.mainloop()


if __name__ == "__main__":
    main()
