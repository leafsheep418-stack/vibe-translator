import os
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


STYLE_PROMPTS = {
    "discord": (
        "根据用户选中文字的语言决定翻译方向："
        "如果原文是中文，就翻译成适合 Discord 聊天的英文；"
        "如果原文不是中文，就翻译成中文，并保留 Discord / 网络聊天语气。"
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
        "根据用户选中文字的语言决定翻译方向："
        "如果原文是中文，就翻译成自然、清楚的英文；"
        "如果原文不是中文，就翻译成自然、清楚的中文。"
        "风格适合日常交流，不要太正式，也不要过度使用网络缩写或流行梗。"
        "表达要像普通朋友、同学或同事之间的自然沟通。"
        "必须原样保留 emoji、链接、@用户名和代码片段。"
    ),
    "academic": (
        "根据用户选中文字的语言决定翻译方向："
        "如果原文是中文，就翻译成正式、严谨的英文；"
        "如果原文不是中文，就翻译成正式、严谨的中文。"
        "风格要适合论文或学术写作，用词准确、客观，避免口语化表达。"
        "必须原样保留 emoji、链接、@用户名和代码片段。"
    ),
    "business": (
        "根据用户选中文字的语言决定翻译方向："
        "如果原文是中文，就翻译成礼貌、清晰、专业的英文；"
        "如果原文不是中文，就翻译成礼貌、清晰、专业的中文。"
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
        "default_model": "deepseek-v4-flash",
        "base_url": "https://api.deepseek.com",
    },
}


HOTKEYS = {
    "<f8>": "F8",
    "<ctrl>+<alt>+t": "Ctrl + Alt + T",
}
HOTKEY_TEXT = "F8 或 Ctrl + Alt + T"

result_queue = queue.Queue()
is_translating = False
hotkey_listener = None


STYLE_LABELS = {
    "discord": "discord - Discord 缩写 / 梗 / 网络聊天",
    "casual": "casual - 日常交流",
    "academic": "academic - 论文 / 学术写作",
    "business": "business - 商务邮件",
}


PROVIDER_LABELS = {
    "deepseek": "deepseek - DeepSeek",
    "openai": "openai - ChatGPT / OpenAI",
}


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
        messagebox.showerror(
            "缺少依赖",
            "缺少依赖："
            + ", ".join(missing_packages)
            + "\n\n请先运行：\npip install -r requirements.txt",
        )
        return False

    return True


def get_key_from_label(label):
    """从下拉框显示文字里取出真正的 key。"""
    for key, provider_label in PROVIDER_LABELS.items():
        if label == provider_label:
            return key

    for key, style_label in STYLE_LABELS.items():
        if label == style_label:
            return key

    return label.split()[0].strip().lower()


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

    # 快捷键触发时，用户可能还按着 F8。
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


def run_translate_worker(style, provider):
    """开一个后台线程执行翻译，避免 GUI 卡住。"""
    worker = threading.Thread(
        target=handle_hotkey,
        args=(style, provider),
        daemon=True,
    )
    worker.start()


def start_hotkey_listener(style, provider):
    """启动全局快捷键监听。"""
    from pynput import keyboard

    def on_translate_hotkey():
        run_translate_worker(style, provider)

    hotkeys = keyboard.GlobalHotKeys(
        {hotkey: on_translate_hotkey for hotkey in HOTKEYS}
    )

    hotkeys.start()
    return hotkeys


def build_settings_window(root):
    """创建设置窗口，让用户选择服务商、填写 API Key 和选择风格。"""
    global hotkey_listener

    root.title("Vibe Translator V0.2")
    root.geometry("520x500")
    root.minsize(460, 460)
    root.resizable(True, True)

    main_frame = ttk.Frame(root, padding=18)
    main_frame.pack(fill="both", expand=True)

    title_label = ttk.Label(
        main_frame,
        text="Vibe Translator",
        font=("Microsoft YaHei UI", 16, "bold"),
    )
    title_label.pack(anchor="w")

    subtitle_label = ttk.Label(
        main_frame,
        text=f"选择配置后，按 {HOTKEY_TEXT} 翻译当前选中文字。",
    )
    subtitle_label.pack(anchor="w", pady=(4, 16))

    provider_label = ttk.Label(main_frame, text="API 服务商")
    provider_label.pack(anchor="w")

    provider_var = tk.StringVar(value=PROVIDER_LABELS["deepseek"])
    provider_box = ttk.Combobox(
        main_frame,
        textvariable=provider_var,
        values=list(PROVIDER_LABELS.values()),
        state="readonly",
    )
    provider_box.pack(fill="x", pady=(4, 10))

    api_key_label = ttk.Label(main_frame, text="API Key")
    api_key_label.pack(anchor="w")

    api_key_var = tk.StringVar(value=os.getenv("DEEPSEEK_API_KEY", ""))
    api_key_entry = ttk.Entry(main_frame, textvariable=api_key_var, show="*")
    api_key_entry.pack(fill="x", pady=(4, 10))

    model_label = ttk.Label(main_frame, text="模型（可不改）")
    model_label.pack(anchor="w")

    model_var = tk.StringVar(value=PROVIDERS["deepseek"]["default_model"])
    model_entry = ttk.Entry(main_frame, textvariable=model_var)
    model_entry.pack(fill="x", pady=(4, 10))

    style_label = ttk.Label(main_frame, text="翻译风格")
    style_label.pack(anchor="w")

    style_var = tk.StringVar(value=STYLE_LABELS["discord"])
    style_box = ttk.Combobox(
        main_frame,
        textvariable=style_var,
        values=list(STYLE_LABELS.values()),
        state="readonly",
    )
    style_box.pack(fill="x", pady=(4, 12))

    status_var = tk.StringVar(value="还没有开始监听。")
    status_label = ttk.Label(main_frame, textvariable=status_var)
    status_label.pack(anchor="w", pady=(0, 12))

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x")

    start_button = ttk.Button(button_frame, text="开始监听")
    start_button.pack(side="left")

    test_button = ttk.Button(button_frame, text="测试 API")
    test_button.pack(side="left", padx=(8, 0))

    hide_button = ttk.Button(button_frame, text="最小化", command=root.iconify)
    hide_button.pack(side="left", padx=(8, 0))

    def refresh_provider_fields(event=None):
        provider = get_key_from_label(provider_var.get())
        provider_info = PROVIDERS[provider]
        api_key_var.set(os.getenv(provider_info["api_key_env"], ""))
        model_var.set(os.getenv(provider_info["model_env"], provider_info["default_model"]))

    def close_app():
        global hotkey_listener

        if hotkey_listener is not None:
            hotkey_listener.stop()
            hotkey_listener = None

        root.destroy()

    quit_button = ttk.Button(button_frame, text="退出", command=close_app)
    quit_button.pack(side="right")

    def start_listening():
        global hotkey_listener

        if hotkey_listener is not None:
            messagebox.showinfo("提示", "已经在监听快捷键了。")
            return

        provider = get_key_from_label(provider_var.get())
        style = get_key_from_label(style_var.get())
        provider_info = PROVIDERS[provider]
        api_key = api_key_var.get().strip()
        model = model_var.get().strip()

        if not api_key:
            messagebox.showwarning("缺少 API Key", "请先输入当前服务商的 API Key。")
            return

        if not model:
            model = provider_info["default_model"]
            model_var.set(model)

        os.environ[provider_info["api_key_env"]] = api_key
        os.environ[provider_info["model_env"]] = model

        hotkey_listener = start_hotkey_listener(style, provider)

        provider_box.config(state="disabled")
        api_key_entry.config(state="disabled")
        model_entry.config(state="disabled")
        style_box.config(state="disabled")
        start_button.config(state="disabled")

        status_var.set(f"正在后台监听 {HOTKEY_TEXT}。当前风格：{style}")
        messagebox.showinfo(
            "已启动",
            f"后台翻译已启动。\n\n选中英文或中文后，按 {HOTKEY_TEXT} 显示翻译结果。",
        )

    def test_api():
        provider = get_key_from_label(provider_var.get())
        style = get_key_from_label(style_var.get())
        provider_info = PROVIDERS[provider]
        api_key = api_key_var.get().strip()
        model = model_var.get().strip()

        if not api_key:
            messagebox.showwarning("缺少 API Key", "请先输入当前服务商的 API Key。")
            return

        if not model:
            model = provider_info["default_model"]
            model_var.set(model)

        os.environ[provider_info["api_key_env"]] = api_key
        os.environ[provider_info["model_env"]] = model

        test_button.config(state="disabled")
        status_var.set("正在测试 API，请稍等。")

        def worker():
            try:
                result = translate_text("祝大家好运", style, provider)
                result_queue.put(("测试结果", result))
                root.after(0, status_var.set, "API 测试完成。可以点击“开始监听”。")
            except Exception as error:
                result_queue.put(("测试失败", f"请检查 API Key、网络连接和账号状态。\n\n错误信息：{error}"))
                root.after(0, status_var.set, "API 测试失败。")
            finally:
                root.after(0, test_button.config, {"state": "normal"})

        threading.Thread(target=worker, daemon=True).start()

    provider_box.bind("<<ComboboxSelected>>", refresh_provider_fields)
    start_button.config(command=start_listening)
    test_button.config(command=test_api)
    root.protocol("WM_DELETE_WINDOW", close_app)
    api_key_entry.focus()


def main():
    if not check_dependencies():
        return

    root = tk.Tk()
    build_settings_window(root)

    root.after(100, check_result_queue, root)
    root.mainloop()


if __name__ == "__main__":
    main()
