import streamlit as st
from PIL import Image
from generator.ai import call_ai
from analyzer.image_utils import analyze_palm
from analyzer.role_map import role_name

st.set_page_config(page_title="手相占卜 AI", layout="centered")
st.title("📸 手相占卜 AI 測試版")

# 圖片上傳區塊
uploaded_file = st.file_uploader(
    "請上傳你的手掌照片 (最大 10MB)", 
    type=["jpg", "png", "jpeg"],
    help="支援格式：JPG, PNG, JPEG | 檔案大小限制：10MB"
)

st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

if uploaded_file:
    # 檢查檔案大小 (10MB = 10 * 1024 * 1024 bytes)
    file_size = uploaded_file.size
    max_size = 10 * 1024 * 1024  # 10MB
    
    if file_size > max_size:
        st.error(f"❌ 檔案太大！目前檔案大小：{file_size/1024/1024:.1f}MB，請上傳小於 10MB 的圖片。")
        st.info("💡 提示：如果檔案一直無法上傳，可能是 Streamlit Cloud 的限制，請嘗試壓縮圖片。")
        st.stop()
    
    try:
        image = Image.open(uploaded_file)
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(image, caption="預覽照片", width=400)
        edges, features = analyze_palm(image)
        st.success(f"✅ 圖片上傳成功！檔案大小：{file_size/1024/1024:.1f}MB")
    except Exception as e:
        st.error(f"❌ 圖片格式錯誤或檔案損壞：{str(e)}")
        st.stop()
    if st.button("開始分析手相"):
        # 立即顯示分析狀態
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        
        status_placeholder.info("🔮 正在分析手相，請稍候...")
        
        with st.spinner("分析手相中..."):
            result = call_ai(features)
            
        # 清除狀態訊息，顯示結果
        status_placeholder.empty()
        result_placeholder.write(result)
        
        character = result.split("與你相近的西洋棋角色為：")[-1].strip()[:2]
        file_path = f"./assets/{role_name("tw", character)}.png"
        print(character)

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            try:
                card = Image.open(file_path)
                st.image(card, caption="你的角色卡", width="content")
            except FileNotFoundError:
                st.error(f"找不到圖片: {file_path}")


else:
    st.info("請先上傳手掌照片才能進行分析。")


