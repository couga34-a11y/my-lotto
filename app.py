import os
import random
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# 구글 공식 최신 SDK 클라이언트 안전 초기화 (API v1 안정판 고정)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = None
if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={'api_version': 'v1'}
    )


class PremiumAISajuSystem:

    def __init__(self):
        self.pool = list(range(1, 46))
        self.element_map = {
            "木": [3, 4, 8, 13, 14, 18, 23, 24, 28, 33, 34, 38, 43, 44],
            "火": [2, 7, 12, 17, 22, 27, 32, 37, 42],
            "土": [5, 10, 15, 20, 25, 30, 35, 40, 45],
            "金": [4, 9, 14, 19, 24, 29, 34, 39],
            "水": [1, 6, 11, 16, 21, 26, 31, 36, 41],
        }

    def get_fortune_and_element(
        self, name: str, year: int, birth_date: str, time_slot: str
    ):
        if not client:
            return {
                "reading": "Render 대시보드 Environment 탭에서 GEMINI_API_KEY를 다시 확인해 주세요.",
                "lucky_element": "金",
            }

        try:
            prompt = f"""
            너는 정통 사주명리학과 성명학에 정통한 대한민국 최고의 AI 역술가이다.
            아래 사용자의 명식 정보를 기반으로 정밀 사주를 분석하고 이번 주 주간 운세를 작성하라.
            
            [사용자 명식 정보]
            - 성함: {name}
            - 출생연도: {year}년
            - 출생월일: {birth_date[:2]}월 {birth_date[2:]}일
            - 태어난 시간: {time_slot}
            
            [작성 지침]
            1. 존댓말로 작성하고 신뢰감 있는 역술가의 뉘앙스로 서술하라.
            2. 이번 주의 '주간 총평', '재물운', '직장/커리어운', '행운의 요일(평일 중 2개)', '행운의 구매 방위'를 녹여내어 정밀하게 풀어내라.
            3. 답변의 맨 마지막 줄에는 반드시 딱 이 형태 그대로만 추가하라: "최종 보완 오행: [오행]"
               ([오행] 자리에 木, 火, 土, 金, 水 중 이번 주 로또 횡재수를 도울 가장 필요한 오행 딱 하나만 선택하여 넣어라. 예: 최종 보완 오행: 水)
            """
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            full_text = response.text

            lucky_element = "金"
            for el in ["木", "火", "土", "金", "水"]:
                if f"최종 보완 오행: {el}" in full_text or el in full_text[-20:]:
                    lucky_element = el
                    break

            display_text = full_text.replace(
                f"최종 보완 오행: {lucky_element}", ""
            ).strip()
            return {"reading": display_text, "lucky_element": lucky_element}

        except Exception as e:
            return {
                "reading": f"명식을 분석하는 과정에서 노이즈가 발생했습니다. (원인: {str(e)})",
                "lucky_element": "土",
            }

    def verify_numbers(self, numbers):
        total_sum = sum(numbers)
        if not (100 <= total_sum <= 170):
            return False
        odds = len([n for n in numbers if n % 2 != 0])
        if odds == 0 or odds == 6:
            return False

        consecutive_count = 0
        max_consecutive = 1
        current_consecutive = 1
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:
                current_consecutive += 1
                consecutive_count += 1
            else:
                if current_consecutive > max_consecutive:
                    max_consecutive = current_consecutive
                current_consecutive = 1
        if current_consecutive > max_consecutive:
            max_consecutive = current_consecutive
        if max_consecutive >= 3 or consecutive_count >= 3:
            return False
        return True

    def generate_games(self, target_element, count=5):
        weights = [1.0] * 45
        lucky_numbers = self.element_map.get(target_element, [])
        for num in lucky_numbers:
            weights[num - 1] = 3.5

        results = []
        while len(results) < count:
            selected = random.choices(self.pool, weights=weights, k=10)
            selected = sorted(list(set(selected)))[:6]
            if len(selected) < 6:
                continue
            if self.verify_numbers(selected) and selected not in results:
                results.append(selected)
        return results


saju_system = PremiumAISajuSystem()


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AI LOTTO FILTER SYSTEM</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background-color: #0f1a30; 
                margin: 0; 
                padding: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh; 
                color: #fff; 
                box-sizing: border-box; 
                overflow: hidden;
            }
            
            /* ✨ 1. 앱 초기 표지 (Splash Screen) 스타일 */
            #splash-screen {
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100vw; 
                height: 100vh;
                background-color: #0f1a30; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center;
                z-index: 9999; 
                transition: opacity 0.5s ease-out, visibility 0.5s;
            }
            
            /* 촤라락 모션을 위한 텍스트 컨테이너 */
            .splash-container {
                text-align: center;
                animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
            }
            
            /* 시인성을 극대화한 황금빛 타이틀 */
            .splash-title { 
                font-size: 28px; 
                font-weight: 900; 
                color: #facc15; 
                letter-spacing: -0.5px; 
                margin-bottom: 12px;
                text-shadow: 0 2px 10px rgba(250, 204, 21, 0.2);
            }
            
            /* 하부 서브 텍스트 라인 */
            .splash-subtitle { 
                font-size: 13px; 
                color: #64748b; 
                letter-spacing: 5px; 
                text-transform: uppercase; 
                padding-left: 5px;
            }
            
            /* 🖥️ 2. 메인 입력창 컨테이너 (초기 은닉) */
            .container { 
                display: none; 
                width: 100%; 
                max-width: 420px; 
                background: #1e293b; 
                padding: 40px 24px; 
                border-radius: 24px; 
                border: 1px solid rgba(255, 255, 255, 0.05); 
                box-sizing: border-box; 
                text-align: center; 
                margin: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                animation: fadeIn 0.5s ease-out;
            }
            
            h2 { margin-top: 0; font-size: 24px; color: #facc15; font-weight: 900; }
            p { color: #94a3b8; font-size: 14px; margin-bottom: 30px; line-height: 1.5; }
            .form-group { margin-bottom: 24px; text-align: left; }
            label { display: block; font-size: 14px; color: #cbd5e1; margin-bottom: 10px; font-weight: 600; }
            input, select { width: 100%; padding: 16px; background: #0f1a30; border: 1px solid #334155; border-radius: 14px; color: #fff; font-size: 16px; box-sizing: border-box; outline: none; }
            input:focus, select:focus { border-color: #facc15; }
            .btn { display: block; width: 100%; padding: 18px; background: #d97706; color: #000; border: none; border-radius: 14px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 30px; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3); }
            #loading { display: none; margin-top: 15px; font-size: 14px; color: #facc15; font-weight: bold; line-height: 1.6; }

            /* ⚡ 촤라락 올라오는 모션 및 페이드인 애니메이션 정의 */
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(30px); filter: blur(4px); }
                to { opacity: 1; transform: translateY(0); filter: blur(0); }
            }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        </style>
    </head>
    <body>

        <div id="splash-screen">
