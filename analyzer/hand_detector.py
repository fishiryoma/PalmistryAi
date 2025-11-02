import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import streamlit as st

@st.cache_resource
def get_hands_model():
    """
    初始化並快取 MediaPipe Hands 模型。
    使用 @st.cache_resource 確保模型只被載入一次。
    """
    hands = mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    return hands

def detect_hand_in_image(image, hands_model):
    """
    檢測圖片中是否包含完整的手部 (21個關鍵點)。
    這個版本接收一個已經初始化的 hands_model 來避免重複載入。
    
    Args:
        image: PIL Image 或 numpy array
        hands_model: 已經初始化的 MediaPipe Hands 模型
        
    Returns:
        tuple: (hand_detected: bool, num_landmarks: int, processed_image: numpy array)
    """
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    # 轉換圖片格式
    if isinstance(image, Image.Image):
        # 如果影像是 RGBA，轉換為 RGB
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        rgb_img = np.array(image)
    else:
        rgb_img = image
    
    # 確保是 RGB 格式
    if len(rgb_img.shape) == 3 and rgb_img.shape[2] == 4:
        rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGBA2RGB)

    # MediaPipe 手部偵測
    results = hands_model.process(rgb_img)
    
    hand_detected = False
    num_landmarks = 0
    processed_image = rgb_img.copy()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            num_landmarks = len(hand_landmarks.landmark)
            # 檢查是否有完整的21個關鍵點
            if num_landmarks == 21:
                hand_detected = True
                
                # 在圖片上繪製關鍵點
                mp_drawing.draw_landmarks(
                    processed_image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=(0, 255, 0), thickness=4, circle_radius=4
                    ),
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=(255, 255, 255), thickness=4
                    )
                )
                break
    
    return hand_detected, num_landmarks, processed_image