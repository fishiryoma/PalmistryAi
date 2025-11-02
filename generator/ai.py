import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from config import LANGUAGES

load_dotenv()
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

def get_prompt(features, lang):
    """Generates a language-specific prompt that asks for a JSON output."""

    output_language = LANGUAGES.get(lang, {}).get("name", "繁體中文")

    json_structure_prompt = '''
{
  "personality": "...",
  "difficulty": "...",
  "love": "...",
  "chess_piece": "..."
}
'''

    prompts = {
        "zh-TW": f"""
        你是一位手相占卜師。請根據以下掌紋特徵，生成一段占卜解讀。
        特徵數據:
        - 掌紋密度: {features['line_density']}
        - 平均方向: {features['avg_direction']}
        - 方向分散度: {features['direction_std']}
        - 交叉點數量: {features['cross_points']}

        請嚴格按照以下要求，用「{output_language}」回答，並輸出一個 JSON 物件:
        1.  不要在回覆中提及原始數據。
        2.  JSON 物件需包含以下四個 keys: "personality", "difficulty", "love", "chess_piece"。
        3.  "personality" 的內容以「你是一個...」開頭，描述人格特質。
        4.  "difficulty" 的內容以「遇到困難時，你會...」開頭，描述面對困難的態度。
        5.  "love" 的內容以「在愛情上，你是...」開頭，描述愛情觀。
        6.  "chess_piece" 的內容僅為一個西洋棋角色名稱，從「士兵、騎士、主教、城堡、皇后、國王」中選擇最適合的一個。

        請直接輸出符合以下結構的 JSON 物件，不要包含任何額外說明或 markdown 格式。
        範例輸出格式:
        ```json{json_structure_prompt}```
        """,
        "en": f"""
        You are a palm reader. Based on the following palm features, generate a reading.
        Features data:
        - Line Density: {features['line_density']}
        - Average Direction: {features['avg_direction']}
        - Direction Standard Deviation: {features['direction_std']}
        - Number of Cross Points: {features['cross_points']}

        Please strictly follow the requirements below, respond in "{output_language}", and output a JSON object:
        1. Do not mention the raw data in your response.
        2. The JSON object must contain these four keys: "personality", "difficulty", "love", "chess_piece".
        3. The value for "personality" should start with "You are a person who...", describing personality traits.
        4. The value for "difficulty" should start with "When facing difficulties, you...", describing attitude towards challenges.
        5. The value for "love" should start with "In love, you are...", describing attitude towards love.
        6. The value for "chess_piece" should be only one of the following chess piece names that fits best: "Pawn", "Knight", "Bishop", "Rook", "Queen", "King".

        Please output only the JSON object that follows the structure below, without any extra explanations or markdown formatting.
        Example output format:
        ```json{json_structure_prompt}```
        """,
        "ja": f"""
        あなたは手相占いの専門家です。以下の手相の特徴に基づいて、占いの結果を生成してください。
        特徴データ:
        - 手相の密度: {features['line_density']}
        - 平均方向: {features['avg_direction']}
        - 方向の標準偏差: {features['direction_std']}
        - 交差点の数: {features['cross_points']}

        以下の要件に厳密に従い、「{output_language}」で回答し、JSONオブジェクトを出力してください:
        1. 回答に元のデータを含めないでください。
        2. JSONオブジェクトには、"personality"、"difficulty"、"love"、"chess_piece" の4つのキーを含める必要があります。
        3. "personality" の値は「あなたは...」で始まり、人格的特徴を説明してください。
        4. "difficulty" の値は「困難に直面したとき、あなたは...」で始まり、困難に対する態度を説明してください。
        5. "love" の値は「恋愛において、あなたは...」で始まり、恋愛観を説明してください。
        6. "chess_piece" の値は、最も適したチェスの駒の名前一つだけにしてください。選択肢: 「ポーン」、「ナイト」、「ビショップ」、「ルーク」、「クイーン」、「キング」。

        追加の説明やマークダウン形式を含めず、以下の構造に従ったJSONオブジェクトを直接出力してください。
        出力フォーマット例:
        ```json{json_structure_prompt}```
        """
    }
    return prompts.get(lang, prompts["zh-TW"])

def call_ai(features, lang='zh-TW'):
    prompt = get_prompt(features, lang)
    
    try:
        response = model.generate_content(prompt)
        
        raw_text = response.text
        
        json_match = raw_text.strip()
        if json_match.startswith("```json"):
            json_match = json_match[7:]
        if json_match.endswith("```"):
            json_match = json_match[:-3]
        
        parsed_json = json.loads(json_match.strip())
        
        analysis_text = f"{parsed_json['personality']}\n\n{parsed_json['difficulty']}\n\n{parsed_json['love']}"
        
        return {
            "analysis": analysis_text,
            "character": parsed_json["chess_piece"]
        }

    except Exception as e:
        print(f"Error calling AI or parsing JSON: {e}")
        return {
            "analysis": t["error_ai"],
            "character": "Error"
        }