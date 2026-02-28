# 格式转换工具

基于 Streamlit 的在线格式转换工具，支持 PDF 转文本、图片 OCR、图片格式转换、视频提取音频、Excel 转 CSV、二维码生成/解析、Base64 编解码、文件压缩。

## 功能

| 功能 | 说明 |
|------|------|
| PDF 转文本 | 上传 PDF，提取纯文本并下载 .txt |
| 图片 OCR | 上传图片，识别中英文文字 |
| 图片格式转换 | JPG / PNG / WebP 互转 |
| 视频提取音频 | MP4 等视频提取为 MP3 |
| Excel 转 CSV | 上传 xlsx/xls，导出 CSV |
| 二维码 | 生成二维码图片、解析二维码内容 |
| Base64 | 文本编码与解码 |
| 文件压缩 | 多文件打包为 ZIP 下载 |

## 本地运行

```bash
cd streamlit-converter
pip install -r requirements.txt
# OCR 需安装 Tesseract：https://github.com/tesseract-ocr/tesseract
# 二维码解析需系统 libzbar（如 macOS: brew install zbar）
streamlit run app.py
```

## 无法本地测试时

- **先部署再验证**：把仓库推到 GitHub，在 [Streamlit Cloud](https://share.streamlit.io/) 新建应用，主文件填 `app.py`。云端会用 `requirements.txt` 和 `Aptfile` 装好依赖，环境一致，部署完成后直接在网页里试用各功能即可。
- **依赖自检**：能跑 Python 但暂时不想起浏览器时，可在项目目录执行：
  ```bash
  pip install -r requirements.txt
  python verify.py
  ```
  通过则说明依赖和部分逻辑正常，之后需要时再执行 `streamlit run app.py` 做完整测试。

## 部署到 Streamlit Cloud

1. 将本仓库推送到 GitHub。
2. 在 [Streamlit Cloud](https://share.streamlit.io/) 选择该仓库。
3. 主文件路径填写：`app.py`。
4. 依赖：自动根据 `requirements.txt` 安装；系统依赖（Tesseract、libzbar）通过根目录 `Aptfile` 自动安装。
5. 部署后即可使用，无需数据库与登录。

## 技术栈

- **streamlit**：Web 界面
- **PyPDF2 / pdfplumber**：PDF 文本提取
- **Pillow / pytesseract**：图片处理与 OCR
- **moviepy**：视频转音频
- **pandas / openpyxl**：Excel 转 CSV
- **qrcode / pyzbar**：二维码生成与解析
- **base64 / zipfile**：Base64 与压缩（标准库）

## 说明

- 所有处理在浏览器与 Streamlit 服务器本地完成，不上传至第三方，不依赖数据库。
- 大文件或长时间转换可能受 Streamlit Cloud 资源与超时限制，建议控制文件大小与时长。
