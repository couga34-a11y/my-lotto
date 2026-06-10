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
            2. 이번 주의 '주간 총평', '재물운', '직장/커리어운', '행운의 요일(평일 중 2개)', '행운의 구매 방위'를 녹여내어 간략하게 풀어내라.
            3. 답변의 맨 마지막 줄에는 반드시 딱 이 형태 그대로만 추가하라: "최종 보완 오행: [오행]"
               ([오행] 자리에 木, 火, 土, 金, 水 중 이번 주 로또 횡재수를 도울 가장 필요한 오행 딱 하나만 선택하여 넣어라. 예: 최종 보완 오행: 水)
            """
            
            # 구글 공식 규격에 맞는 올바른 플래시 모델명으로 최종 정비
            response = client.models.generate_content(
                model="gemini-2.5-flash",
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
                background-color: #0f1a30 !important; 
                margin: 0; 
                padding: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh; 
                color: #fff; 
                box-sizing: border-box; 
                overflow-x: hidden;
            }
            
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
                transition: opacity 0.4s ease-out, visibility 0.4s;
            }
            
            .splash-container {
                text-align: center;
                animation: slideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
            }
            
            .splash-title { 
                font-size: 26px; 
                font-weight: 900; 
                color: #facc15; 
                letter-spacing: -0.5px; 
                margin-bottom: 10px;
                text-shadow: 0 2px 10px rgba(250, 204, 21, 0.2);
            }
            
            .splash-subtitle { 
                font-size: 12px; 
                color: #64748b; 
                letter-spacing: 4px; 
                text-transform: uppercase; 
                padding-left: 4px;
            }
            
            .container { 
                display: none; 
                width: calc(100% - 40px); 
                max-width: 400px; 
                background-color: #1e293b !important; 
                background: #1e293b !important;
                padding: 35px 20px; 
                border-radius: 24px; 
                border: 1px solid rgba(255, 255, 255, 0.08); 
                box-sizing: border-box; 
                text-align: center; 
                margin: 20px auto; 
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
                animation: fadeIn 0.4s ease-out;
            }
            
            h2 { margin-top: 0; font-size: 22px; color: #facc15; font-weight: 900; }
            p { color: #94a3b8; font-size: 13.5px; margin-bottom: 25px; line-height: 1.5; text-align: center; }
            .form-group { margin-bottom: 20px; text-align: left; }
            label { display: block; font-size: 13.5px; color: #cbd5e1; margin-bottom: 8px; font-weight: 600; }
            
            input, select { 
                width: 100%; 
                padding: 14px; 
                background-color: #0f1a30 !important; 
                border: 1px solid #334155; 
                border-radius: 12px; 
                color: #fff; 
                font-size: 16px; 
                box-sizing: border-box; 
                outline: none; 
            }
            input:focus, select:focus { border-color: #facc15; }
            
            .btn { 
                display: block; 
                width: 100%; 
                padding: 16px; 
                background: #d97706 !important; 
                color: #000 !important; 
                border: none; 
                border-radius: 12px; 
                font-size: 16px; 
                font-weight: bold; 
                cursor: pointer; 
                margin-top: 25px; 
                box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3); 
            }
            
            #loading { display: none; margin-top: 15px; font-size: 14px; color: #facc15; font-weight: bold; line-height: 1.6; }

            @keyframes slideUp {
                from { opacity: 0; transform: translateY(25px); filter: blur(2px); }
                to { opacity: 1; transform: translateY(0); filter: blur(0); }
            }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        </style>
    </head>
    <body>
        <div id="splash-screen">
            <div class="splash-container">
                <div class="splash-title">AI LOTTO FILTER SYSTEM</div>
                <div class="splash-subtitle">Quantum Saju System</div>
            </div>
        </div>

        <div class="container" id="main-container">
            <h2>AI LOTTO FILTER SYSTEM</h2>
            <p>구글 Gemini AI가 선천적 명식과 성명학을 실시간 분석하여 최적의 횡재수 보완 필터링을 수행합니다.</p>
            <form action="/lotto" method="post" onsubmit="document.getElementById('btn-submit').style.display='none'; document.getElementById('loading').style.display='block';">
                <div class="form-group">
                    <label>성함</label>
                    <input type="text" name="user_name" placeholder="예: 홍길동" required>
                </div>
                <div class="form-group">
                    <label>출생 연도 (4자리)</label>
                    <input type="number" name="year" placeholder="예: 1999" required min="1930" max="2026">
                </div>
                <div class="form-group">
                    <label>출생 월 및 일</label>
                    <input type="text" name="birth_date" placeholder="예: 0317" required pattern="[0-9]{4}">
                </div>
                <div class="form-group">
                    <label>태어난 시간</label>
                    <select name="time_slot">
                        <option value="unknown">모름 / 상관없음</option>
                        <option value="자시">자시 (23시~01시)</option>
                        <option value="축시">축시 (01시~03시)</option>
                        <option value="인시">인시 (03시~05시)</option>
                        <option value="묘시">묘시 (05시~07시)</option>
                        <option value="진시">진시 (07시~09시)</option>
                        <option value="사시">사시 (09시~11시)</option>
                        <option value="오시">오시 (11시~13시)</option>
                        <option value="미시">미시 (13시~15시)</option>
                        <option value="신시">신시 (15시~17시)</option>
                        <option value="유시">유시 (17시~19시)</option>
                        <option value="술시">술시 (19시~21시)</option>
                        <option value="해시">해시 (21시~23시)</option>
                    </select>
                </div>
                <button type="submit" id="btn-submit" class="btn">AI 융합 사주 분석 및 번호 추출</button>
                <div id="loading">AI 사주 연산 및 로또 조합 필터링 중...<br>(정밀 추론 연산으로 인해 약 10~15초 소요)</div>
            </form>
        </div>

        <script>
            window.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    const splash = document.getElementById('splash-screen');
                    const main = document.getElementById('main-container');
                    if(splash && main) {
                        splash.style.opacity = '0';
                        splash.style.visibility = 'hidden';
                        main.style.display = 'block';
                    }
                }, 2200); 
            });
        </script>
    </body>
    </html>
    """


@app.post("/lotto", response_class=HTMLResponse)
def lotto_screen(
    user_name: str = Form(...),
    year: int = Form(...),
    birth_date: str = Form(...),
    time_slot: str = Form(...),
):
    ai_data = saju_system.get_fortune_and_element(
        user_name, year, birth_date, time_slot
    )
    games = saju_system.generate_games(ai_data["lucky_element"], 5)

    def get_color_class(num):
        if num <= 10:
            return "ball-yellow"
        elif num <= 20:
            return "ball-blue"
        elif num <= 30:
            return "ball-red"
        elif num <= 40:
            return "ball-gray"
        else:
            return "ball-green"

    games_html = ""
    for idx, game in enumerate(games, 1):
        balls_html = "".join(
            f'<div class="ball {get_color_class(n)}">{n:02d}</div>' for n in game
        )
        games_html += f"""
        <div class="game-row">
            <span class="game-label">{idx}게임</span>
            <div class="balls-container">{balls_html}</div>
        </div>
        """

    formatted_reading = ai_data["reading"].replace("\n", "<br>")

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AI LOTTO FILTER SYSTEM</title>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background-color: #0f1a30 !important; 
                background: #0f1a30 !important;
                margin: 0; 
                padding: 20px; 
                display: flex; 
                justify-content: center; 
                align-items: flex-start;
                min-height: 100vh;
                box-sizing: border-box;
            }}
            
            .container {{ 
                width: 100%; 
                max-width: 460px; 
                background-color: #ffffff !important; 
                background: #ffffff !important;
                padding: 25px 20px; 
                border-radius: 24px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
                box-sizing: border-box; 
            }}
            
            h2 {{ text-align: center; color: #1e293b; margin-top: 0; margin-bottom: 20px; font-size: 22px; font-weight: 800; }}
            
            .saju-box {{ 
                background-color: #f0f4fc !important; 
                background: #f0f4fc !important; 
                border-radius: 14px; 
                padding: 15px; 
                margin-bottom: 16px; 
                font-size: 14px; 
                color: #2563eb; 
                border-left: 5px solid #2563eb; 
                text-align: left; 
                line-height: 1.5; 
                box-sizing: border-box;
            }}
            
            .ai-box {{ 
                background-color: #fdfaf2 !important; 
                background: #fdfaf2 !important; 
                border-radius: 14px; 
                padding: 18px; 
                margin-bottom: 24px; 
                font-size: 14px; 
                color: #1e293b; 
                border-left: 5px solid #d97706; 
                text-align: left; 
                line-height: 1.7; 
                box-sizing: border-box;
            }}
            
            .ai-title {{ font-weight: bold; font-size: 15px; margin-bottom: 12px; color: #b45309; border-bottom: 1px solid #f1e3c4; padding-bottom: 6px; }}
            
            .game-row {{ 
                display: flex; 
                align-items: center; 
                margin-bottom: 12px; 
                padding: 14px 12px; 
                background-color: #f8fafc !important; 
                background: #f8fafc !important; 
                border-radius: 14px; 
                border: 1px solid #e2e8f0; 
                box-sizing: border-box;
            }}
            
            .game-label {{ font-weight: 800; color: #64748b; font-size: 13.5px; width: 55px; flex-shrink: 0; text-align: left; }}
            .balls-container {{ display: flex; gap: 7px; justify-content: flex-start; width: 100%; }}
            .ball {{ width: 34px; height: 34px; border-radius: 50%; color: white; font-weight: bold; display: flex; align-items: center; justify-content: center; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            
            .ball-yellow {{ background: #f59e0b; }}
            .ball-blue {{ background: #3b82f6; }}
            .ball-red {{ background: #ef4444; }}
            .ball-gray {{ background: #71717a; }}
            .ball-green {{ background: #10b981; }}
            
            .btn {{ 
                display: block; 
                width: 100%; 
                padding: 16px; 
                background-color: #2563eb !important; 
                background: #2563eb !important;
                color: white !important; 
                border: none; 
                border-radius: 14px; 
                font-size: 16px; 
                font-weight: bold; 
                cursor: pointer; 
                text-align: center; 
                box-shadow: 0 4px 12px rgba(37,99,235,0.3); 
                margin-top: 25px; 
                text-decoration: none; 
                box-sizing: border-box; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>AI 로또 필터링 결과</h2>
            
            <div class="saju-box">
                🔮 <b>입력 명식:</b> {user_name}님 / {year}년 {birth_date[:2]}월 {birth_date[2:]}일 ({time_slot} 출생)
            </div>
            
            <div class="ai-box">
                <div class="ai-title">Gemini AI의 운세 해설</div>
                {formatted_reading}
                <br><br>
                💡 <i>AI가 지정한 보완 오행 번호대에 <b>재물 가중치(3.5x)</b>를 부여하여 번호를 조합했습니다.</i>
            </div>

            <div class="results">{games_html}</div>

            <a href="/" class="btn">다시 입력하기</a>
        </div>
    </body>
    </html>
    """
