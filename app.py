import streamlit as st
from PIL import Image
from generator.ai import call_ai
from analyzer.image_utils import analyze_palm
from analyzer.role_map import role_name
from analyzer.camera_utils import init_camera, capture_photo
import numpy as np

st.set_page_config(page_title="手相占卜 AI", layout="centered")
st.title("📸 手相占卜 AI 測試版")

# 選擇輸入方式
input_method = st.radio(
    "選擇照片來源：",
    ["使用攝影機", "上傳照片"],
    horizontal=True
)

if input_method == "上傳照片":
    # 圖片上傳區塊
    uploaded_file = st.file_uploader(
        "請上傳你的手掌照片 (最大 10MB)", 
        type=["jpg", "png", "jpeg"],
        help="支援格式：JPG, PNG, JPEG | 檔案大小限制：10MB"
    )
    if not uploaded_file:
        st.info("💡 請先上傳手掌照片才能進行分析。")
else:
    uploaded_file = None
    # 攝影機區塊
    st.subheader("攝影機模式")
    st.info("💡 攝影機會自動偵測手部並顯示關鍵點，請拍攝手掌照片。")
    
    # 初始化攝影機
    webrtc_ctx = init_camera()
    
    # 顯示攝影機狀態
    if webrtc_ctx.state.playing:
        st.success("🟢 攝影機已啟動")
    else:
        st.warning("🔴 攝影機未啟動 - 請點擊上方的 START 按鈕")
    
    # 拍照按鈕
    if st.button("拍照", key="capture_btn", disabled=not webrtc_ctx.state.playing):
        with st.spinner("正在拍照..."):
            captured_image = capture_photo(webrtc_ctx)
            if captured_image is not None:
                st.session_state.captured_image = captured_image
            else:
                st.error("❌ 拍照失敗，可能原因：")
                st.write("- 攝影機畫面未完全載入")
                st.write("- 請稍等幾秒後重試")
    
    # 顯示拍攝的照片
    if 'captured_image' in st.session_state:
        st.subheader("📷 拍攝結果")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # 將 numpy array 轉換為 PIL Image
            image = Image.fromarray(st.session_state.captured_image)
            st.image(image, caption="拍攝的手掌照片", width=400)
        
        # 分析拍攝的照片
        try:
            edges, features = analyze_palm(image)
            st.success("✅ 照片處理成功！")
            
            # 設定 uploaded_file 為拍攝的圖片以便後續處理
            uploaded_file = True  # 標記有圖片可以分析
            
        except Exception as e:
            st.error(f"❌ 圖片處理錯誤：{str(e)}")
            uploaded_file = None

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
    # 處理上傳的檔案
    if input_method == "上傳照片":
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
    
    else:  # 攝影機模式
        # 使用已經處理過的拍攝照片
        if 'captured_image' in st.session_state:
            image = Image.fromarray(st.session_state.captured_image)
            edges, features = analyze_palm(image)
        else:
            st.error("❌ 請先拍照。")
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


