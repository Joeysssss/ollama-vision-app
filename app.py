import streamlit as st
import ollama
from ollama import Client
from groq import Groq
from PIL import Image, ImageOps
import base64
import io
import os

# --- 圖片處理函式 ---
def encode_image(image: Image.Image) -> str:
    """將圖片轉換為 Base64（修正 EXIF 方向並保證為 RGB，避免 JPEG 編碼失敗）"""
    # 修正 EXIF 方向（避免手機或相機拍照旋轉問題）
    image = ImageOps.exif_transpose(image)
    # 若非 RGB 模式（例如 RGBA 或灰階），轉換為 RGB
    if image.mode not in ("RGB",):
        image = image.convert("RGB")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# --- 金鑰安全讀取函式 ---
def get_api_key(key_name: str, direct_input: str = "") -> str:
    """
    依序自：
    1. 使用者介面直接輸入（優先）
    2. Streamlit Secrets (st.secrets)
    3. 系統環境變數 (os.environ)
    安全讀取 API 金鑰，若皆無則回傳空字串。
    """
    if direct_input and direct_input.strip():
        return direct_input.strip()
    
    # 嘗試由 Streamlit Secrets 讀取（防止未建立 secrets 檔案時崩潰）
    try:
        if key_name in st.secrets:
            val = st.secrets[key_name]
            if val and str(val).strip():
                return str(val).strip()
    except Exception:
        pass

    # 嘗試由系統環境變數讀取
    val = os.environ.get(key_name, "")
    return str(val).strip() if val else ""

# --- 模型分析函式 ---
def ollama_cloud_analyze_image(image: Image.Image, prompt: str, api_key: str, model_name: str = "gemma4:31b-cloud") -> tuple[bool, str]:
    """使用 Ollama Cloud API 分析圖片"""
    try:
        base64_image = encode_image(image)
        # 動態初始化 Client，避免啟動時未提供金鑰造成全域崩潰
        client = Client(
            host="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        response = client.chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [base64_image]
                }
            ],
        )
        # 提取回傳文字
        if isinstance(response, dict):
            content = response.get("message", {}).get("content", "")
        else:
            content = getattr(getattr(response, "message", None), "content", "")
        
        if not content:
            content = str(response)
        return True, content.strip()
    except Exception as e:
        return False, f"Ollama Cloud API 錯誤: {str(e)}"

def groq_analyze_image(image: Image.Image, prompt: str, api_key: str, model_name: str = "qwen/qwen3.8-27b") -> tuple[bool, str]:
    """使用 Groq API 分析圖片"""
    try:
        base64_image = encode_image(image)
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }

        # 動態初始化 Groq Client
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    image_content
                ]
            }],
            temperature=0.2,
            max_completion_tokens=1500,
            stream=False
        )
        content = completion.choices[0].message.content
        return True, content.strip()
    except Exception as e:
        return False, f"Groq API 錯誤: {str(e)}"

def ollama_local_analyze_image(image: Image.Image, prompt: str, model_name: str = "gemma3:4b") -> tuple[bool, str]:
    """使用本機端 Ollama API 分析圖片（僅限本機環境）"""
    try:
        base64_image = encode_image(image)
        response = ollama.chat(
            model=model_name,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [base64_image],
            }]
        )
        if isinstance(response, dict):
            content = response.get("message", {}).get("content", "")
        else:
            content = getattr(getattr(response, "message", None), "content", "")
        
        if not content:
            content = str(response)
        return True, content.strip()
    except Exception as e:
        return False, f"本機 Ollama 呼叫錯誤: {str(e)}\n請確認本機 Ollama 服務已啟動且已安裝模型 {model_name}。"

# --- 主畫面介面 ---
def main():
    st.set_page_config(
        page_title="AI 智慧影像辨識助手",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- 側邊欄設定 ---
    with st.sidebar:
        st.header("⚙️ 系統設定")
        
        # 檢查是否啟用本機模式（預設關閉，確保 Streamlit Cloud 僅呈現雲端選項）
        is_local_env = os.environ.get("ENABLE_LOCAL_OLLAMA", "").lower() in ("1", "true", "yes")
        enable_local = st.checkbox(
            "啟用本機 Ollama 模式",
            value=is_local_env,
            help="僅限在本機具備 Ollama 服務的環境下勾選。Streamlit Cloud 等雲端環境請保持關閉。"
        )

        # 依環境動態決定可用的 API
        if enable_local:
            api_options = ["Ollama Cloud", "Groq", "Ollama (本機)"]
        else:
            api_options = ["Ollama Cloud", "Groq"]

        st.subheader("選擇推論引擎")
        api_choice = st.radio("API 服務:", api_options, index=0)

        st.divider()

        # 安全金鑰輸入區（供未設定 Streamlit Secrets 時直接輸入）
        st.subheader("🔑 API Key 安全輸入")
        st.caption("優先使用 Streamlit Secrets；若未設定可於下方輸入（不會儲存至伺服器或 GitHub）：")
        user_ollama_key = st.text_input("OLLAMA_API_KEY", type="password", help="用於 Ollama Cloud 的 Bearer Token")
        user_groq_key = st.text_input("GROQ_API_KEY", type="password", help="用於 Groq API 的金鑰")

        st.divider()

        # 進階模型名稱調整
        with st.expander("🛠️ 模型名稱自訂（進階）", expanded=False):
            if api_choice == "Ollama Cloud":
                custom_model = st.text_input("Ollama Cloud 模型名稱", value="gemma4:31b-cloud")
            elif api_choice == "Groq":
                custom_model = st.text_input("Groq 視覺模型名稱", value="qwen/qwen3.8-27b")
            else:
                custom_model = st.text_input("本機 Ollama 模型名稱", value="gemma3:4b")

        st.divider()
        st.info("💡 隱私提示：圖片將傳送至您選擇的雲端服務（Ollama Cloud / Groq）進行辨識分析，請勿上傳機密文件或未授權隱私照片。")

    st.title("🖼️ AI 智慧影像辨識助手")
    st.markdown("支援多模態視覺 AI 分析，包含一般場景描述、觀光景點解析、文字辨識 (OCR) 及支票資訊提取。")

    # 預設提示詞設定
    prompt_presets = {
        "一般圖片描述": "請針對此圖片，使用繁體中文詳細說明你看到了什麼，包含主要物體、場景、色彩與細節特徵。",
        "觀光景點分析": "請針對此圖片，使用繁體中文說明你看到了什麼？如果你是一位觀光客，請說明你看到的景點特點、文化氛圍與值得參觀的亮點。",
        "文件文字辨識": "請仔細辨識並提取圖片中的所有文字內容（OCR），維持原有排版與結構，並以繁體中文清楚列出。",
        "支票資訊辨識": (
            "請仔細檢查此支票圖片，精確辨識並提取以下關鍵資訊：\n"
            "1. 銀行名稱（付款行庫/分行）\n"
            "2. 發票人帳號 / 支票帳號\n"
            "3. 支票號碼（票號）\n"
            "4. 發票日期（開票日期）\n"
            "5. 中文大寫金額（如：新台幣 零 壹 貳 參 肆 伍 陸 柒 捌 玖 拾 佰 仟 萬）\n"
            "6. 阿拉伯數字金額\n"
            "7. 受款人姓名/抬頭（若有）\n\n"
            "【嚴格要求】：\n"
            "- 請依上述編號逐項條列輸出。\n"
            "- 若特定欄位空白、模糊或無法清楚辨識，請明確標示為「無法辨識」或「無」，嚴禁自行猜測或推斷任何數字與字元。"
        ),
        "自訂提示詞": ""
    }

    col_preset, _ = st.columns([2, 1])
    with col_preset:
        selected_preset = st.selectbox("選擇提示詞範本：", list(prompt_presets.keys()), index=1)

    # 若切換範本，動態填充文字方塊
    default_text = prompt_presets[selected_preset]
    prompt_input = st.text_area(
        "提示詞 (Prompt)：",
        value=default_text,
        height=120,
        help="您可以直接編輯或微調提示詞內容。"
    )

    uploaded_file = st.file_uploader(
        "上傳欲分析的圖片：",
        type=["jpg", "jpeg", "png"],
        help="支援 JPG、JPEG 與 PNG 格式。"
    )

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        analyze_clicked = st.button("🚀 開始分析", type="primary", use_container_width=True)

    # 顯示版面：左側預覽、右側結果
    col_preview, col_result = st.columns(2)

    if analyze_clicked:
        if uploaded_file is None:
            st.warning("⚠️ 請先上傳圖檔後再進行分析。")
        elif not prompt_input.strip():
            st.warning("⚠️ 請輸入提示詞。")
        else:
            # 開啟圖片並顯示預覽
            image = Image.open(uploaded_file)
            with col_preview:
                st.subheader("📸 已上傳的圖片")
                st.image(image, caption=uploaded_file.name, use_container_width=True)

            # 檢查並取得對應的 API Key
            api_ready = True
            active_key = ""
            
            if api_choice == "Ollama Cloud":
                active_key = get_api_key("OLLAMA_API_KEY", user_ollama_key)
                if not active_key:
                    api_ready = False
                    st.error("❌ 尚未設定 OLLAMA_API_KEY。請在左側側邊欄輸入，或於 Streamlit Secrets / 系統環境變數中設定。")
            elif api_choice == "Groq":
                active_key = get_api_key("GROQ_API_KEY", user_groq_key)
                if not active_key:
                    api_ready = False
                    st.error("❌ 尚未設定 GROQ_API_KEY。請在左側側邊欄輸入，或於 Streamlit Secrets / 系統環境變數中設定。")

            if api_ready:
                with col_result:
                    st.subheader("🤖 AI 分析結果")
                    with st.spinner(f"使用 {api_choice} 分析中，請稍候..."):
                        if api_choice == "Ollama Cloud":
                            success, result_text = ollama_cloud_analyze_image(
                                image, prompt_input, active_key, custom_model
                            )
                        elif api_choice == "Groq":
                            success, result_text = groq_analyze_image(
                                image, prompt_input, active_key, custom_model
                            )
                        else:
                            success, result_text = ollama_local_analyze_image(
                                image, prompt_input, custom_model
                            )

                    if success:
                        st.success("✅ 影像分析完成！")
                        st.markdown(result_text)
                        st.divider()
                        st.caption("📋 複製原始分析文字：")
                        st.code(result_text, language=None)
                    else:
                        st.error("❌ 分析失敗，請檢查以下錯誤訊息：")
                        st.code(result_text, language=None)
    elif uploaded_file is not None:
        # 尚未按下分析但已上傳圖片時，先提供預覽
        image = Image.open(uploaded_file)
        with col_preview:
            st.subheader("📸 已上傳的圖片")
            st.image(image, caption=uploaded_file.name, use_container_width=True)

if __name__ == "__main__":
    main()
