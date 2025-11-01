import streamlit as st
from PIL import Image
from generator.ai import call_ai
from analyzer.image_utils import analyze_palm
from analyzer.role_map import role_name
from analyzer.camera_utils import init_camera, capture_photo
from analyzer.hand_detector import detect_hand_in_image

st.set_page_config(page_title="AI手相占卜", layout="centered")
st.title("📸 AI手相占卜")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

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
    
    # 初始化攝影機
    webrtc_ctx = init_camera()
    
    # 顯示攝影機狀態
    if not webrtc_ctx.state.playing:
        st.warning("🔴 攝影機未啟動 - 請點擊上方的 START 按鈕")
    
    # 拍照按鈕
    if st.button("📸 拍照", key="capture_btn", disabled=not webrtc_ctx.state.playing):
        with st.spinner("正在拍照..."):
            captured_image = capture_photo(webrtc_ctx)
            if captured_image is not None:
                # 檢查圖片是否包含手部
                hand_detected, num_landmarks, processed_image = detect_hand_in_image(captured_image)
                
                if hand_detected:
                    st.session_state.captured_image = captured_image
                    st.session_state.processed_image = processed_image  # 存儲處理後的圖片用於預覽
                    st.success(f"✅ 拍照成功！偵測到完整手部")
                else:
                    st.error("❌ 未偵測到完整手部，請重新拍照")
                    st.info("💡 請確保手掌完全在畫面中且光線充足")
            else:
                    st.error("❌ 拍照失敗，請重試")    
    
    # 顯示拍攝的照片
    if 'processed_image' in st.session_state:
        st.subheader("📷 拍攝結果")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # 將 numpy array 轉換為 PIL Image
            image = Image.fromarray(st.session_state.processed_image)
            st.image(image, caption="拍攝的手掌照片 (含關鍵點)", width=400)
        
        # 分析拍攝的照片
        try:
            # 檢查是否有成功拍攝的照片
            if 'captured_image' in st.session_state:
                image = Image.fromarray(st.session_state.captured_image)
                edges, features = analyze_palm(image)
                st.success("✅ 照片處理成功！")
                uploaded_file = True  # 標記有圖片可以分析
            else:
                uploaded_file = None
            
        except Exception as e:
            st.error(f"❌ 圖片處理錯誤：{str(e)}")
            uploaded_file = None


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
            
            # 檢查圖片是否包含手部
            hand_detected, num_landmarks, processed_image = detect_hand_in_image(image)
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(processed_image, caption="預覽照片", width=400)
            
            if hand_detected:
                edges, features = analyze_palm(image)
                st.success(f"✅ 圖片上傳成功！檔案大小：{file_size/1024/1024:.1f}MB")
                st.success(f"✋ 偵測到完整手部")
            else:
                st.error("❌ 未偵測到完整手部，無法進行分析")
                st.info("💡 請上傳包含清晰手掌的照片")
                st.stop()
                
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
        file_path = f"./assets/{role_name('tw', character)}.png"
        print(character)

        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            try:
                card = Image.open(file_path)
                st.image(card, caption="你的角色卡", width="content")
            except FileNotFoundError:
                st.error(f"找不到圖片: {file_path}")


