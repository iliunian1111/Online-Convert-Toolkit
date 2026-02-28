"""
依赖与核心逻辑自检脚本。不启动 Streamlit，不依赖浏览器。
在项目目录执行: python verify.py
"""
import sys

def main():
    errors = []
    # 1. 标准库
    try:
        import io
        import base64
        import zipfile
        from pathlib import Path
    except ImportError as e:
        errors.append(f"标准库: {e}")
        return errors

    # 2. 第三方依赖
    deps = [
        "streamlit",
        "PyPDF2",
        "pdfplumber",
        "PIL",
        "pytesseract",
        "pandas",
        "qrcode",
        "openpyxl",
    ]
    for name in deps:
        try:
            __import__(name)
        except ImportError as e:
            errors.append(f"{name}: {e}")

    # moviepy 较慢且可选，单独检查
    try:
        from moviepy.editor import VideoFileClip
    except ImportError as e:
        errors.append(f"moviepy: {e}")

    # pyzbar 需要系统 libzbar
    try:
        from pyzbar import pyzbar
    except ImportError as e:
        errors.append(f"pyzbar: {e}")

    if errors:
        print("以下依赖导入失败：")
        for e in errors:
            print("  -", e)
        return errors

    # 3. 简单逻辑自检
    assert base64.b64encode(b"hello").decode() == "aGVsbG8="
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("t.txt", b"test")
    buf.seek(0)
    with zipfile.ZipFile(buf, "r") as z:
        assert z.read("t.txt") == b"test"
    print("Base64 / Zip 逻辑自检通过。")

    print("\n全部自检通过。本地测试请运行: streamlit run app.py")
    return []


if __name__ == "__main__":
    errs = main()
    sys.exit(1 if errs else 0)
