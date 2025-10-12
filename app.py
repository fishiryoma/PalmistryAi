import streamlit as st
from PIL import Image
from generator.ai import call_ai
from analyzer.image_utils import analyze_palm
from analyzer.role_map import role_name

st.set_page_config(page_title="手相占卜 AI", layout="centered")
st.title("📸 手相占卜 AI 測試版")

# 圖片上傳區塊
uploaded_file = st.file_uploader("請上傳你的手掌照片", type=["jpg", "png"])

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
    image = Image.open(uploaded_file)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(image, caption="預覽照片", width=400)
    edges, features = analyze_palm(image)
    st.success("圖片上傳成功！")
    if st.button("開始分析手相"):
        with st.spinner("分析手相中..."):
            result = call_ai(features)
            st.write(result)
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


