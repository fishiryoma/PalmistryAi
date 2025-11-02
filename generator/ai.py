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

        特徵數據參考範圍:
        - 掌紋密度: 分為「高、中、低」三級。數值越高代表越密集。
        - 平均方向 (rad): 範圍約 0.1 到 3.0。代表掌紋的整體走向。
        - 方向分散度: 範圍約 0.0 (所有線條平行) 到 0.9 (線條方向非常分散)。
        - 交叉點數量: 範圍約 0 到 500+。代表手掌中主要線條的交錯數量。

        請嚴格按照以下要求，用「{output_language}」回答，並輸出一個 JSON 物件:
        1.  不要在回覆中提及原始數據。
        2.  JSON 物件需包含以下四個 keys: "personality", "difficulty", "love", "chess_piece"。
        3.  "personality" 的內容以「你是一個...」開頭，描述人格特質。
        4.  "difficulty" 的內容以「遇到困難時，你會...」開頭，描述面對困難的態度。
        5.  "love" 的內容以「在愛情上，你是...」開頭，描述愛情觀。
        6.  "chess_piece" 的內容僅為一個西洋棋角色名稱。請根據以下指引，從「士兵、騎士、主教、城堡、皇后、國王」中選擇最適合的一個：
            - **國王 (King):** 適合特徵：高掌紋密度、極多的交叉點。象徵核心、領導力與複雜性。
            - **皇后 (Queen):** 適合特徵：高方向分散度、高掌紋密度、多交叉點。象徵全能、適應力強與多元。
            - **城堡 (Rook):** 適合特徵：低方向分散度（線條平行）、低交叉點。象徵直接、穩固與專注。
            - **主教 (Bishop):** 適合特徵：低方向分散度、中等交叉點。象徵目標明確、有策略性。
            - **騎士 (Knight):** 適合特徵：高方向分散度、中等交叉點。象徵不拘一格、靈活與跳躍性思維。
            - **士兵 (Pawn):** 適合特徵：低掌紋密度、低交叉點。象徵潛力、專一與按部就班。
        7.  請綜合所有特徵，選出最符合整體感覺的角色。

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

        Reference ranges for feature data:
        - Line Density: Categorized as "High", "Medium", "Low". Higher values mean denser lines.
        - Average Direction (rad): Ranges from approx. 0.1 to 3.0. Represents the overall orientation of palm lines.
        - Direction Standard Deviation: Ranges from approx. 0.0 (all lines parallel) to 0.9 (lines are very spread out).
        - Number of Cross Points: Ranges from approx. 0 to 500+. Represents the number of intersections of major lines in the palm.

        Please strictly follow the requirements below, respond in "{output_language}", and output a JSON object:
        1. Do not mention the raw data in your response.
        2. The JSON object must contain these four keys: "personality", "difficulty", "love", "chess_piece".
        3. The value for "personality" should start with "You are a person who...", describing personality traits.
        4. The value for "difficulty" should start with "When facing difficulties, you...", describing attitude towards challenges.
        5. The value for "love" should start with "In love, you are...", describing attitude towards love.
        6. The value for "chess_piece" should be only one of the following chess piece names. Choose the one that fits best based on the following guidelines:
            - **King:** Suitable for: High line density, very high number of cross points. Symbolizes the core, leadership, and complexity.
            - **Queen:** Suitable for: High direction standard deviation, high line density, high number of cross points. Symbolizes versatility, adaptability, and diversity.
            - **Rook:** Suitable for: Low direction standard deviation (parallel lines), low number of cross points. Symbolizes directness, stability, and focus.
            - **Bishop:** Suitable for: Low direction standard deviation, medium number of cross points. Symbolizes clear goals and strategic thinking.
            - **Knight:** Suitable for: High direction standard deviation, medium number of cross points. Symbolizes unconventional thinking, flexibility, and agility.
            - **Pawn:** Suitable for: Low line density, low number of cross points. Symbolizes potential, dedication, and step-by-step progress.
        7. Synthesize all features to select the character that best fits the overall impression.

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

        特徴データの参考範囲:
        - 手相の密度: 「高」、「中」、「低」の3段階に分類されます。値が高いほど密度が高いことを意味します。
        - 平均方向 (rad): 範囲は約0.1から3.0です。手相全体の方向性を示します。
        - 方向の標準偏差: 範囲は約0.0（すべての線が平行）から0.9（線の方向が非常に分散）です。
        - 交差点の数: 範囲は約0から500以上です。手のひらの主要な線の交差する数を表します。

        以下の要件に厳密に従い、「{output_language}」で回答し、JSONオブジェクトを出力してください:
        1. 回答に元のデータを含めないでください。
        2. JSONオブジェクトには、"personality"、"difficulty"、"love"、"chess_piece" の4つのキーを含める必要があります。
        3. "personality" の値は「あなたは...」で始まり、人格的特徴を説明してください。
        4. "difficulty" の値は「困難に直面したとき、あなたは...」で始まり、困難に対する態度を説明してください。
        5. "love" の値は「恋愛において、あなたは...」で始まり、恋愛観を説明してください。
        6. "chess_piece" の値は、以下のガイドラインに基づいて、最も適したチェスの駒の名前一つだけにしてください。選択肢: 「ポーン」、「ナイト」、「ビショップ」、「ルーク」、「クイーン」、「キング」。
            - **キング (King):** 適した特徴：高い手相の密度、非常に多い交差点の数。核心、リーダーシップ、複雑さを象徴します。
            - **クイーン (Queen):** 適した特徴：高い方向の標準偏差、高い手相の密度、多い交差点の数。万能性、適応力、多様性を象徴します。
            - **ルーク (Rook):** 適した特徴：低い方向の標準偏差（平行な線）、少ない交差点の数。直接的、安定、集中を象徴します。
            - **ビショップ (Bishop):** 適した特徴：低い方向の標準偏差、中程度の交差点の数。明確な目標と戦略性を象徴します。
            - **ナイト (Knight):** 適した特徴：高い方向の標準偏差、中程度の交差点の数。型にはまらない思考、柔軟性、機敏さを象徴します。
            - **ポーン (Pawn):** 適した特徴：低い手相の密度、少ない交差点の数。可能性、献身、一歩一歩進むことを象徴します。
        7. すべての特徴を総合的に判断し、全体の印象に最も合うキャラクターを選んでください。

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