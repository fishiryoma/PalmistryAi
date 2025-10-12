import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

def call_ai(features):
    prompt = f"""
    你是一位手相占卜師，請根據以下掌紋特徵生成一段占卜解讀，字數約 200 個字：

    - 掌紋密度：{features['line_density']}
    - 平均方向：{features['avg_direction']}
    - 方向分散度：{features['direction_std']}
    - 交叉點數量：{features['cross_points']}

    開頭請用'你是一個'，生成一段完整的占卜文，內文不要提到原始數據，要將這些數據轉化為
    淺在的個性、人格特質、遇到困境時的處理方式及心態。
    最後一句話要換行'與你相近的西洋棋角色為：'，從西洋棋的比喻中選一個適合的角色出來。
    選項包含:士兵、騎士、主教、城堡、皇后、國王。
    冒號一律用全形。
    """
    print(prompt)
    response = model.generate_content(prompt)
    print(response.text)
    return response.text