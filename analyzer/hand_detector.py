import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

def detect_hand_in_image(image):
    """
    檢測圖片中是否包含完整的手部 (21個關鍵點)
    
    Args:
        image: PIL Image 或 numpy array
        
    Returns:
        tuple: (hand_detected: bool, num_landmarks: int, processed_image: numpy array)
    """
    # 初始化 MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,  # 靜態圖片模式
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    
    # 轉換圖片格式
    if isinstance(image, Image.Image):
        rgb_img = np.array(image)
    else:
        rgb_img = image
    
    # 確保是 RGB 格式
    if len(rgb_img.shape) == 3 and rgb_img.shape[2] == 3:
        # 如果是 BGR 轉為 RGB
        if np.max(rgb_img) <= 1.0:
            rgb_img = (rgb_img * 255).astype(np.uint8)
    
    # MediaPipe 手部偵測
    results = hands.process(rgb_img)
    
    hand_detected = False
    num_landmarks = 0
    processed_image = rgb_img.copy()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            num_landmarks = len(hand_landmarks.landmark)
            # 檢查是否有完整的21個關鍵點
            if num_landmarks == 21:
                hand_detected = True
                
                # 在圖片上繪製關鍵點 (可選)
                # 轉換為 BGR 格式繪製
                bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                    bgr_img, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=(0, 255, 0), thickness=4, circle_radius=4
                    ),
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=(255, 255, 255), thickness=4
                    )
                )
                processed_image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
                break
    
    hands.close()
    return hand_detected, num_landmarks, processed_image