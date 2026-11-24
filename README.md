# AI 智慧影像辨識助手 (Ollama Vision App)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

這是一個基於 Streamlit 開發的現代化多模態 AI 影像分析 Web 應用程式。使用者可以上傳圖片，透過繁體中文 Prompt 提示詞，調用雲端視覺模型（Ollama Cloud 與 Groq）或本機模型進行影像描述、景點分析、文字辨識 (OCR) 以及專用支票資訊提取。

---

## 🌟 主要功能

1. **多模態影像分析**：支援 JPG、JPEG、PNG 格式圖片上傳，自動校正 EXIF 拍攝方向並轉為標準 RGB 編碼。
2. **多種實用 Prompt 範本**：
   - **觀光景點分析**：以旅客視角分析照片中的景致、人文特色與打卡亮點。
   - **一般圖片描述**：全面剖析圖像之構圖、主要主體、光影與色彩特徵。
   - **文件文字辨識 (OCR)**：結構化萃取圖片中文字內容。
   - **支票資訊辨識**：嚴格辨識銀行名稱、帳號、支票號碼、日期、中文大寫金額及阿拉伯數字金額；無效或模糊欄位明確標示為「無法辨識」，杜絕幻覺瞎猜。
   - **自訂提示詞**：完全自由編輯輸入任何分析要求。
3. **靈活雙雲端 API 支援**：
   - **Ollama Cloud**：透過官方雲端推論端點調用大規模視覺多模態模型。
   - **Groq API**：利用 LPU 超高速推論架構進行視覺解析。
   - **本機 Ollama 模式（選用）**：可於本地開發環境啟用，預設於雲端部署環境關閉，防止連線例外。
4. **一鍵複製分析成果**：內建程式碼/文字複製區塊，方便將辨識結果貼至其他軟體。
5. **高度安全性設計**：支援 Streamlit Secrets 與動態安全輸入介面，絕不上傳或硬編碼任何 API Key。

---

## 🧠 使用的 AI 模型說明

| 服務提供者 | 預設模型名稱 | 說明與特性 |
| :--- | :--- | :--- |
| **Ollama Cloud** | `gemma4:31b-cloud` | Ollama 雲端託管多模態模型，具備高階視覺與繁體中文理解力。 |
| **Groq** | `qwen/qwen3.8-27b` | Groq LPU 雲端推論模型，提供超低延遲的多模態影像與文字分析。 |
| **Ollama (本機)** | `gemma3:4b` | 本地自架 Ollama 輕量模型，適合於無網路或完全私有化環境中離線測試。 |

*註：若特定模型於平台進行版本更替，可於網頁側邊欄「🛠️ 模型名稱自訂」中隨時替換為可用的視覺模型。*

---

## 📁 專案架構

```text
ollama-vision-app/
├── app.py                     # Streamlit 應用程式主程式
├── requirements.txt           # Python 相依套件清單
├── README.md                  # 專案說明文件（本檔案）
├── .gitignore                 # Git 忽略檔案設定（排除 Secrets、快取與敏感圖檔）
├── DEPLOYMENT.md              # 部署紀錄與進度追蹤表
├── .streamlit/
│   ├── config.toml            # Streamlit 伺服器與主題樣式設定
│   └── secrets.toml.example   # Streamlit Secrets 設定範本
└── original/
    └── ch16-4-3.py            # 原始程式備份檔案
```

---

## 💻 本機安裝與執行方式

### 1. 複製專案庫
```bash
git clone https://github.com/Joeysssss/ollama-vision-app.git
cd ollama-vision-app
```

### 2. 安裝必要套件
建議使用 Python 3.10 或 3.11 環境：
```bash
python -m pip install -r requirements.txt
```

### 3. 設定 API Key（二擇一）

#### 方式 A：使用 Streamlit Secrets（推薦）
在 `.streamlit/` 資料夾下新增 `secrets.toml`（此檔案已被 `.gitignore` 排除，不會被 Git 追蹤）：
```toml
OLLAMA_API_KEY = "你的_OLLAMA_API_KEY"
GROQ_API_KEY = "你的_GROQ_API_KEY"
```

#### 方式 B：使用系統環境變數
- **Windows (PowerShell)**：
  ```powershell
  $env:OLLAMA_API_KEY="你的_OLLAMA_API_KEY"
  $env:GROQ_API_KEY="你的_GROQ_API_KEY"
  ```
- **macOS / Linux**：
  ```bash
  export OLLAMA_API_KEY="你的_OLLAMA_API_KEY"
  export GROQ_API_KEY="你的_GROQ_API_KEY"
  ```

#### 方式 C：網頁側邊欄動態輸入
直接啟動網頁，於左側側邊欄的「🔑 API Key 安全輸入」密碼欄位中輸入金鑰即可。

### 4. 啟動 Streamlit 應用程式
```bash
python -m streamlit run app.py
```
瀏覽器會自動開啟 `http://localhost:8501`。

---

## ☁️ Streamlit Community Cloud 部署方式

1. 將本專案推送至 GitHub Repository：`https://github.com/Joeysssss/ollama-vision-app`。
2. 前往 [Streamlit Community Cloud](https://share.streamlit.io/) 並登入 GitHub 帳號。
3. 點擊 **"Create app"**，並填寫設定：
   - **Repository**：`Joeysssss/ollama-vision-app`
   - **Branch**：`main`
   - **Main file path**：`app.py`
   - **App URL**：自訂為 `joey-ollama-vision`（若可用）
4. 點開 **"Advanced settings"** -> **"Secrets"**，貼上以下格式的金鑰：
   ```toml
   OLLAMA_API_KEY = "你的真實_OLLAMA_API_KEY"
   GROQ_API_KEY = "你的真實_GROQ_API_KEY"
   ```
5. 點擊 **"Deploy"**，等待建置與套件安裝完成即可公開連線使用。

---

## ❓ 常見錯誤及排除方法

| 錯誤訊息 / 現象 | 原因說明 | 解決方法 |
| :--- | :--- | :--- |
| `TypeError: can only concatenate str (not "NoneType") to str` | 原始程式在最外層串接未設定的環境變數。 | `app.py` 已改為動態安全讀取，若金鑰未設定會顯示繁體中文警告提示，不再崩潰。 |
| `尚未設定 OLLAMA_API_KEY` 或 `尚未設定 GROQ_API_KEY` | 尚未提供相應服務的認證金鑰。 | 請至 Streamlit Secrets、環境變數或網頁側邊欄密碼欄位中填寫有效 Key。 |
| `Ollama API 錯誤: 404 / connection refused` | 誤於雲端環境開啟本機 Ollama，或本機 Ollama 服務未開啟。 | 在雲端部署請選擇「Ollama Cloud」或「Groq」；本機測試請先確認本機 Ollama 服務已在背景執行。 |
| `Groq API 錯誤: rate limit / model not found` | 呼叫頻率過高或模型名稱異動。 | 請稍候再試，或於進階設定中指定 Groq 支援的其他視覺模型（如 `llama-3.2-11b-vision-preview`）。 |

---

## 🔗 雲端網站連結

- **Streamlit Community Cloud 網址**：`https://ollama-vision-app-14366033.streamlit.app/`
