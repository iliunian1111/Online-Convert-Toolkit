"""
在线格式转换工具 - Streamlit
支持：PDF转文本、图片OCR、图片格式转换、视频提取音频、
     Excel转CSV、二维码生成/解析、Base64编解码、文件压缩
"""
# Streamlit Cloud (Linux) 下 apt 安装的 libzbar 在 /usr/lib/x86_64-linux-gnu，需在导入 pyzbar 前设置
import os
_zbar_path = "/usr/lib/x86_64-linux-gnu"
if os.name == "posix" and os.path.isdir(_zbar_path):
    os.environ["LD_LIBRARY_PATH"] = _zbar_path + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")

import io
import base64
import zipfile
from pathlib import Path

import streamlit as st

# 页面配置（必须最先执行）
st.set_page_config(
    page_title="格式转换工具",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="auto",
)

# 自定义样式：科技感 + 移动端适配
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    h1, h2, h3 {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00d4ff !important;
        font-weight: 600 !important;
    }
    
    .tool-card {
        background: rgba(0, 212, 255, 0.08);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .tool-card:hover {
        border-color: rgba(0, 212, 255, 0.6);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
    }
    
    .stButton > button {
        font-family: 'JetBrains Mono', monospace !important;
        background: linear-gradient(90deg, #00d4ff, #0099cc) !important;
        color: #0f0f23 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.5) !important;
        transform: translateY(-1px);
    }
    
    .stDownloadButton > button {
        font-family: 'JetBrains Mono', monospace !important;
        background: linear-gradient(90deg, #00ff88, #00cc6a) !important;
        color: #0f0f23 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    .stRadio > div {
        flex-direction: column !important;
    }
    
    @media (max-width: 768px) {
        .tool-card { padding: 1rem; }
        h1 { font-size: 1.5rem !important; }
    }
</style>
""", unsafe_allow_html=True)


def pdf_to_text():
    """PDF 转文本"""
    st.subheader("📄 PDF 转文本")
    uploaded = st.file_uploader("上传 PDF 文件", type=["pdf"], key="pdf_upload")
    if uploaded:
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(uploaded) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            full_text = "\n\n".join(text_parts) if text_parts else "未能提取到文本。"
            st.text_area("提取的文本", full_text, height=300)
            st.download_button(
                "下载 .txt 文件",
                data=full_text.encode("utf-8"),
                file_name=Path(uploaded.name).stem + ".txt",
                mime="text/plain",
                key="pdf_dl",
            )
        except Exception as e:
            st.error(f"处理失败：{e}")


def image_ocr():
    """图片 OCR 文字提取"""
    st.subheader("🔍 图片 OCR 文字提取")
    uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "webp", "bmp"], key="ocr_upload")
    if uploaded:
        try:
            import pytesseract
            from PIL import Image
            import sys
            # Streamlit Cloud (Linux) 下 apt 安装的 tesseract 在 /usr/bin，显式指定避免 PATH 问题
            if sys.platform == "linux":
                pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
            img = Image.open(uploaded)
            if img.mode != "RGB":
                img = img.convert("RGB")
            text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            st.text_area("识别结果", text or "未识别到文字。", height=300)
            if text.strip():
                st.download_button(
                    "下载 .txt 文件",
                    data=text.encode("utf-8"),
                    file_name=Path(uploaded.name).stem + "_ocr.txt",
                    mime="text/plain",
                    key="ocr_dl",
                )
        except Exception as e:
            err_msg = str(e).lower()
            if "tesseract" in err_msg or "not found" in err_msg:
                st.error(
                    "未检测到 Tesseract OCR。本地运行请安装 Tesseract。"
                    "部署到 Streamlit Cloud 时：① 确保仓库根目录有 packages.txt（不是 Aptfile）且含 tesseract-ocr 和 tesseract-ocr-chi-sim；"
                    "② 在应用设置里点「Clear cache and redeploy」重新部署。"
                )
            else:
                st.error(f"OCR 失败：{e}")


def image_convert():
    """图片格式转换"""
    st.subheader("🖼️ 图片格式转换")
    uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "webp", "bmp"], key="img_upload")
    if uploaded:
        from PIL import Image
        fmt = st.selectbox("转换为格式", ["jpg", "png", "webp"], key="img_fmt")
        img = Image.open(uploaded)
        if img.mode in ("RGBA", "P") and fmt.lower() == "jpg":
            img = img.convert("RGB")
        buf = io.BytesIO()
        save_kw = {}
        if fmt.lower() == "webp":
            save_kw["quality"] = 90
        save_fmt = "JPEG" if fmt.lower() == "jpg" else fmt.upper()
        img.save(buf, format=save_fmt, **save_kw)
        buf.seek(0)
        out_name = Path(uploaded.name).stem + f".{fmt}"
        st.download_button("下载转换后的图片", data=buf.getvalue(), file_name=out_name, mime=f"image/{fmt}", key="img_dl")


def video_to_audio():
    """视频提取音频"""
    st.subheader("🎵 视频提取音频 (MP4 → MP3)")
    uploaded = st.file_uploader("上传视频", type=["mp4", "avi", "mov", "mkv"], key="video_upload")
    if uploaded:
        with st.spinner("正在提取音频..."):
            try:
                import tempfile
                from moviepy.editor import VideoFileClip
                with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=False) as tmp_in:
                    tmp_in.write(uploaded.getvalue())
                    tmp_path = tmp_in.name
                try:
                    clip = VideoFileClip(tmp_path)
                    audio = clip.audio
                    if audio is None:
                        st.error("该视频没有音轨。")
                    else:
                        out_path = tempfile.mktemp(suffix=".mp3")
                        try:
                            audio.write_audiofile(out_path, codec="mp3", logger=None)
                            with open(out_path, "rb") as f:
                                mp3_data = f.read()
                            st.download_button(
                                "下载 MP3",
                                data=mp3_data,
                                file_name=Path(uploaded.name).stem + ".mp3",
                                mime="audio/mpeg",
                                key="audio_dl",
                            )
                        finally:
                            Path(out_path).unlink(missing_ok=True)
                    clip.close()
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            except Exception as e:
                err = str(e).lower()
                if "ffmpeg" in err or "ffprobe" in err or "could not find" in err or "no such file" in err:
                    st.error(
                        "提取失败：未找到 ffmpeg。部署到 Streamlit Cloud 时请确保根目录有 packages.txt 且含 ffmpeg，"
                        "并在应用设置中执行一次「Clear cache and redeploy」。"
                    )
                else:
                    st.error(f"提取失败：{e}")


def excel_to_csv():
    """Excel 转 CSV"""
    st.subheader("📊 Excel 转 CSV")
    uploaded = st.file_uploader("上传 Excel", type=["xlsx", "xls"], key="excel_upload")
    if uploaded:
        try:
            import pandas as pd
            df = pd.read_excel(uploaded, sheet_name=0)
            st.dataframe(df.head(20), use_container_width=True)
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
            csv_buf.seek(0)
            st.download_button(
                "下载 CSV",
                data=csv_buf.getvalue(),
                file_name=Path(uploaded.name).stem + ".csv",
                mime="text/csv",
                key="csv_dl",
            )
        except Exception as e:
            st.error(f"转换失败：{e}")


def qr_tools():
    """二维码生成与解析"""
    st.subheader("📱 二维码生成与解析")
    tab_gen, tab_parse = st.tabs(["生成二维码", "解析二维码"])
    with tab_gen:
        content = st.text_input("输入内容（文本或链接）", key="qr_content")
        if content:
            try:
                import qrcode
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(content)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                st.image(buf, caption="二维码预览")
                st.download_button("下载二维码图片", data=buf.getvalue(), file_name="qrcode.png", mime="image/png", key="qr_gen_dl")
            except Exception as e:
                st.error(f"生成失败：{e}")
    with tab_parse:
        qr_file = st.file_uploader("上传二维码图片", type=["png", "jpg", "jpeg"], key="qr_parse_upload")
        if qr_file:
            try:
                from pyzbar import pyzbar
                from PIL import Image
                img = Image.open(qr_file)
                decoded = pyzbar.decode(img)
                if decoded:
                    for d in decoded:
                        st.success(f"解析结果：{d.data.decode('utf-8', errors='replace')}")
                else:
                    st.warning("未识别到二维码。")
            except Exception as e:
                err = str(e)
                if "zbar" in err.lower() or "shared library" in err.lower():
                    st.error(
                        "解析失败：未找到 zbar 库。部署到 Streamlit Cloud 时请确保根目录有 packages.txt 且含 libzbar0，"
                        "并在应用设置中执行一次「Clear cache and redeploy」。"
                    )
                else:
                    st.error(f"解析失败：{e}")


def base64_tools():
    """Base64 编码解码"""
    st.subheader("🔐 Base64 编码 / 解码")
    tab_enc, tab_dec = st.tabs(["编码", "解码"])
    with tab_enc:
        enc_input = st.text_area("输入要编码的文本", key="b64_enc_in")
        if st.button("编码", key="b64_enc_btn"):
            if enc_input:
                encoded = base64.b64encode(enc_input.encode("utf-8")).decode("ascii")
                st.code(encoded)
                st.download_button("下载编码结果", data=encoded, file_name="encoded.txt", mime="text/plain", key="b64_enc_dl")
            else:
                st.warning("请输入文本。")
    with tab_dec:
        dec_input = st.text_area("输入要解码的 Base64 字符串", key="b64_dec_in")
        if st.button("解码", key="b64_dec_btn"):
            if dec_input:
                try:
                    decoded = base64.b64decode(dec_input).decode("utf-8")
                    st.code(decoded)
                    st.download_button("下载解码结果", data=decoded, file_name="decoded.txt", mime="text/plain", key="b64_dec_dl")
                except Exception as e:
                    st.error(f"解码失败：{e}")
            else:
                st.warning("请输入 Base64 字符串。")


def file_compress():
    """文件压缩"""
    st.subheader("📦 文件压缩")
    uploaded = st.file_uploader("选择要压缩的文件（可多选）", type=None, accept_multiple_files=True, key="zip_upload")
    if uploaded:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in uploaded:
                zf.writestr(f.name, f.getvalue())
        zip_buf.seek(0)
        name = "archive.zip"
        if len(uploaded) == 1:
            name = Path(uploaded[0].name).stem + ".zip"
        st.download_button("下载 ZIP", data=zip_buf.getvalue(), file_name=name, mime="application/zip", key="zip_dl")


# 工具列表与对应函数
TOOLS = [
    ("PDF 转文本", pdf_to_text),
    ("图片 OCR", image_ocr),
    ("图片格式转换", image_convert),
    ("视频提取音频", video_to_audio),
    ("Excel 转 CSV", excel_to_csv),
    ("二维码", qr_tools),
    ("Base64", base64_tools),
    ("文件压缩", file_compress),
]

# 侧边栏选择工具
st.sidebar.markdown("## 🔄 格式转换工具")
st.sidebar.markdown("---")
choice = st.sidebar.radio("选择功能", [t[0] for t in TOOLS], label_visibility="collapsed")

# 主标题
st.markdown("# 格式转换工具")
st.markdown("上传文件或输入内容，一键转换并下载。")
st.markdown("---")

# 执行选中工具
for name, func in TOOLS:
    if choice == name:
        func()
        break

st.sidebar.markdown("---")
st.sidebar.caption("无需登录 · 本地处理 · 数据不留存")
