import cv2
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.latest_frame = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.drawing_spec_landmark = self.mp_drawing.DrawingSpec(
            color=(0, 255, 0),  # 關鍵點
            thickness=4,            # 點的粗細
            circle_radius=4         # 點的半徑
        )
        self.drawing_spec_connection = self.mp_drawing.DrawingSpec(
            color=(255, 255, 255),  # 連線
            thickness=4       # 連線粗細
        )
        
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # 轉換為 RGB 進行 MediaPipe 處理
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.latest_frame = rgb_img.copy()
        
        # MediaPipe 手部偵測
        results = self.hands.process(rgb_img)
        # 在 BGR 圖像上繪製關鍵點（用於顯示）
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    img, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.drawing_spec_landmark,
                    connection_drawing_spec=self.drawing_spec_connection
                )
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    
    def get_latest_frame(self):
        return self.latest_frame

def init_camera():
    """初始化攝影機"""
    RTC_CONFIGURATION = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    })
    
    ctx = webrtc_streamer(
        key="camera",
        video_transformer_factory=VideoTransformer,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=False,
    )
    
    return ctx

def capture_photo(ctx):
    """拍照功能"""
    print("開始拍照...")
    if ctx.video_transformer:
        captured = ctx.video_transformer.get_latest_frame()
        if captured is not None:
            print(f"拍照成功，圖片尺寸: {captured.shape}")
            return captured
        else:
            print("拍照失敗：沒有可用畫面")
            return None
    else:
        print("拍照失敗：video_transformer 為空")
        return None