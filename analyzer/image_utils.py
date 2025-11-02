import cv2
import numpy as np
from PIL import Image
import streamlit as st

def analyze_palm(image: Image.Image):
    """
    分析掌紋圖片，回傳邊緣圖與特徵資料
    """
    # 轉換格式：去除背景留下膚色
    masked = skin_mask(image)
    gray_masked = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)

    # 邊緣偵測
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray_masked)

    # 使用 np.median 自動計算 Canny 閾值
    v = np.median(enhanced[enhanced > 0]) if np.any(enhanced > 0) else 0
    sigma = 0.33
    lower_thresh = int(max(0, (1.0 - sigma) * v))
    upper_thresh = int(min(255, (1.0 + sigma) * v))
    edges = cv2.Canny(enhanced, lower_thresh, upper_thresh)

    # 計算線條密度（正規化）
    hand_area = cv2.countNonZero(gray_masked)
    if hand_area > 0:
        density = np.sum(edges > 0) / hand_area
        if density < 0.05:
            line_density_str = "低"
        elif density < 0.1:
            line_density_str = "中"
        else:
            line_density_str = "高"
    else:
        line_density_str = "無法判斷"
        density = 0

    # 計算平均方向與分散度
    avg_direction, direction_std = analyze_line_directions(edges)

    # 定位手掌
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = masked.copy()
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)

    # 交叉點偵測（Corner Detection）
    corners = cv2.goodFeaturesToTrack(np.float32(gray_masked), maxCorners=500, qualityLevel=0.02, minDistance=15)
    cross_points = len(corners) if corners is not None else 0

    # 回傳特徵資料
    features = {
        "line_density": f"{line_density_str} ({density:.3f})",
        "avg_direction": f"{avg_direction:.2f} rad" if avg_direction is not None else "無法判斷",
        "direction_std": f"{direction_std:.2f}" if direction_std is not None else "無法判斷",
        "cross_points": cross_points
    }

    return edges, features

def skin_mask(image: Image.Image):
    # 轉換格式：PIL → NumPy → OpenCV
    img = np.array(image.convert("RGB"))
    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # 定義膚色範圍（可微調）
    lower = np.array([0, 30, 60])
    upper = np.array([20, 150, 255])
    mask = cv2.inRange(img_hsv, lower, upper)

    # 只保留膚色區域
    result = cv2.bitwise_and(img, img, mask=mask)
    return result

def analyze_line_directions(edges):
    """
    使用 Hough Transform 偵測線條，計算平均方向與分散度
    """
    
    h, w = edges.shape
    hough_threshold = int(w / 3.5) if w > 0 else 100

    lines = cv2.HoughLines(edges, 1, np.pi / 180, hough_threshold)
    directions = []

    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            # 篩選掉接近水平的線條 (±5.7度)，減少邊界干擾
            if (theta > 0.1) and (theta < np.pi - 0.1):
                directions.append(theta)

    if directions:
        avg_direction = float(np.mean(directions))          # 平均方向（弧度）
        direction_std = float(np.std(directions))           # 分散度（標準差）
    else:
        avg_direction, direction_std = None, None

    return avg_direction, direction_std
