import streamlit as st
from PIL import Image
from generator.ai import call_ai
from analyzer.image_utils import analyze_palm
from analyzer.role_map import role_name
from analyzer.camera_utils import init_camera, capture_photo
from analyzer.hand_detector import detect_hand_in_image, get_hands_model
import json
import os
from config import LANGUAGES

def load_translations():
    path = os.path.join(os.path.dirname(__file__), 'locales.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

translations = load_translations()

col1, col2 = st.columns([3, 1])
with col2:
    selected_lang_key = st.selectbox(
        label="Language",
        options=LANGUAGES.keys(),
        format_func=lambda key: LANGUAGES[key]["name"],
        key="language_selector"
    )

t = translations[selected_lang_key]

st.set_page_config(page_title=t["page_title"], layout="centered")
st.title(t["title"])

st.markdown('''
    <style>
    div.stButton > button:first-child {
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    </style>
''', unsafe_allow_html=True)

input_method = st.radio(
    t["radio_label"],
    [t["radio_option_camera"], t["radio_option_upload"]],
    horizontal=True
)

if input_method == t["radio_option_upload"]:
    uploaded_file = st.file_uploader(
        t["uploader_label"],
        type=["jpg", "png", "jpeg", "webp"],
        help=t["uploader_help"]
    )
    if not uploaded_file:
        st.info(t["info_upload_first"])
else:
    uploaded_file = None
    st.subheader(t["subheader_camera_mode"])
    webrtc_ctx = init_camera()
    if not webrtc_ctx.state.playing:
        st.warning(t["warning_camera_not_started"])
    
    hands_model = get_hands_model()

    if st.button(t["button_capture"], key="capture_btn", disabled=not webrtc_ctx.state.playing):
        with st.spinner(t["spinner_capturing"]):
            captured_image = capture_photo(webrtc_ctx)
            if captured_image is not None:
                hand_detected, num_landmarks, processed_image = detect_hand_in_image(captured_image, hands_model)

                if hand_detected:
                    st.session_state.captured_image = captured_image
                    st.session_state.processed_image = processed_image  # Store processed image for preview
                    st.success(t["success_capture"])
                else:
                    st.error(t["error_no_hand_detected"])
                    st.info(t["info_ensure_hand_in_frame"])
            else:
                st.error(t["error_capture_failed"])

    if 'processed_image' in st.session_state:
        st.subheader(t["subheader_capture_result"])
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            image = Image.fromarray(st.session_state.processed_image)
            st.image(image, caption=t["caption_captured_image"], width=360)

        try:
            if 'captured_image' in st.session_state:
                image = Image.fromarray(st.session_state.captured_image)
                edges, features = analyze_palm(image)
                st.session_state.palm_features = { "edges": edges, "features": features}
                st.success(t["success_image_processing"])
                uploaded_file = True 
            else:
                uploaded_file = None

        except Exception as e:
            st.error(t["error_image_processing"].format(e=str(e)))
            uploaded_file = None


if uploaded_file:
    if input_method == t["radio_option_upload"]:
        # Check file size (10MB = 10 * 1024 * 1024 bytes)
        file_size = uploaded_file.size
        max_size = 10 * 1024 * 1024  # 10MB

        if file_size > max_size:
            st.error(t["error_file_too_large"].format(size=file_size/1024/1024))
            st.info(t["info_compress_image"])
            st.stop()

        try:
            image = Image.open(uploaded_file)
            
            # Get the cached hands model
            hands_model = get_hands_model()
            hand_detected, num_landmarks, processed_image = detect_hand_in_image(image, hands_model)

            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(processed_image, caption=t["caption_preview_image"], width=360)

            if hand_detected:
                edges, features = analyze_palm(image)
                st.success(t["success_upload"].format(size=file_size/1024/1024))
                st.success(t["success_hand_detected"])
            else:
                st.error(t["error_no_hand_for_analysis"])
                st.info(t["info_upload_clear_palm"])
                st.stop()

        except Exception as e:
            st.error(t["error_image_format"].format(e=str(e)))
            st.stop()

    else:  
        if 'captured_image' in st.session_state:
            image = Image.fromarray(st.session_state.captured_image)
            edges = st.session_state.palm_features["edges"]
            features = st.session_state.palm_features["features"]
        else:
            st.error(t["error_capture_first"])
            st.stop()

    if st.button(t["button_analyze"]):
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        status_placeholder.info(t["info_analyzing"])

        ai_result = None
        with st.spinner(t["spinner_analyzing"]):
            ai_result = call_ai(features, lang=selected_lang_key)

        status_placeholder.empty()
        
        if ai_result and ai_result["character"] != "Error":
            result_placeholder.write(f"{ai_result['analysis']}\n\n{t['caption_character_card']}：{ai_result['character']}")
            character = ai_result["character"]
            lang_key_for_role = LANGUAGES[selected_lang_key]["key_for_role_map"]
            file_path = f"./assets/{role_name(lang_key_for_role, character)}.png"
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                card = Image.open(file_path)
                st.image(card, caption=t["caption_character_card"])
        else:
            result_placeholder.error(ai_result["analysis"])
