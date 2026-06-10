import os
import random
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from google import genai

app = FastAPI()

# Render 환경변수 또는 로컬 설정에서 Gemini API 키 로드
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AISajuLottoSystem:
    def __init__(self):
        self.pool = list(range(1, 46))
        # 오행별 기본 매핑 데이터 (필터 가중치 반영용 기본 축)
        self.element_map = {
            "木": [3, 4, 8, 13, 14, 18, 23, 24, 28, 33, 34, 38, 43, 44],
            "火": [2, 7, 12, 17, 22, 27, 32, 37, 42],
            "土": [5, 10, 15, 20, 25, 30, 35, 40, 45],
            "金": [4, 9, 14, 19, 24, 29, 34, 39],
            "水": [1, 6, 11, 16, 21, 26, 31, 36, 41]
        }

    def _get_ai_fortune(self, name: str, year: int, birth_date: str, time_slot: str):
        """Gemini AI를 호출하여 고유한 사주 분석 및 로또 행운 요소를 획득하는 함수"""
        if not GEMINI_API_KEY:
            return {
                "reading": "현재 AI 엔진의 핵심 Key 설정이 누락되었습니다. Render 대시보드에서 환경변수를 설정해 주십시오.",
                "lucky_element": "金"
            }
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            너는 정통 사주명리학과 성명학에 정통한 대한민국 최고의 AI 역술가이다.
            아래 사용자의 명식 정보를 기반으로 정밀 사주를 분석하고 이번 주 주간 운세를 작성하라.
            
            [사용자 명식 정보]
            - 성함: {name}
            - 출생연도: {year}년
            - 출생월일: {birth_date[:2]}월 {birth_date[2:]}일
            - 태어난 시간: {time_slot}
            
            [작성 지침 - 절대 준수]
            1. 존댓말로 작성하고 전문적이고 신뢰감 있는 무당 혹은 역술가의 뉘앙스를 풍겨라.
            2. 이번 주의 '종합 주간 총평', '재물운', '직장/커리어운', '행운의 요일(평일 중 2개)', '행운의 구매 방위'를 융합하여 서술형 문장들로 아주 정밀하게 풀어내라.
            3. 답변의 맨 마지막 줄에는 반드시 딱 이 형태 그대로만 추가하라: "최종 보완 오행: [오행]"
               ([오행] 자리에 木, 火, 土, 金, 水 중 사용자의 이름과 사주 밸런스를 고려해 이번 주 로또 횡재수를 도울 가장 필요한 오행 딱 하나만 선택하여 넣어라. 예: 최종 보완 오행: 水)
            """
            response = model.generate_content(prompt)
            full_text = response.text
            
            # 마지막 줄에서 보완 오행 추출하는 파싱 로직
            lucky_element = "金"
            for el in ["木", "火", "土", "金", "水"]:
                if f"최종 보완 오행: {el}" in full_text or el in full_text[-20:]:
                    lucky_element = el
                    break
            
            # 화면 표시를 위해 특수 지시어 라인 제거
            display_text = full_text.replace(f"최종 보완 오행: {lucky_element}", "").strip()
            return {"reading": display_text, "lucky_element": lucky_element}
            
        except Exception as e:
            return {
                "reading": f"우주의 기운을 읽어오는 중 미세한 노이즈가 발생했습니다. (에러: {str(e)})",
                "lucky_element": "土"
            }

    def _verify_combination(self, numbers):
        total_sum = sum(numbers)
        if not (100 <= total_sum <= 170): return False
        odds = len([n for n in numbers if n % 2 != 0])
        if odds == 0 or odds == 6: return False

        consecutive_count = 0
        max_consecutive = 1
        current_consecutive = 1
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:
                current_consecutive += 1
                consecutive_count += 1
            else:
                if current_consecutive > max_consecutive: max_consecutive = current_consecutive
                current_consecutive = 1
        if current_consecutive > max_consecutive: max_consecutive = current_consecutive
        if max_consecutive >= 3 or consecutive_count >= 3: return False
        return True

    def generate_saju_games(self, target_element, count=5):
        weights = [1.0] * 45
        lucky_numbers = self.element_map.get(target_element, [4, 9, 14, 19, 24, 29, 34, 39])
        for num in lucky_numbers:
            weights[num - 1] = 3.5  # AI가 지정한 행운 오행의 가중치를 3.5배로 더 강화

        results = []
        while len(results) < count:
            selected = random.choices(self.pool, weights=weights, k=10)
            selected = sorted(list(set(selected)))[:6]
            if len(selected) < 6: continue
            if self._verify_combination(selected) and selected not in results:
                results.append(selected)
        return results

saju_system = AISajuLottoSystem()

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AI로또 필터 시스템</title>
        <link rel="apple-touch-icon" sizes="180x180" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <link rel="icon" type="image/png" sizes="32x32" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: radial-gradient(circle at center, #1a2a4c 0%, #0d1a33 100%); margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #fff; box-sizing: border-box; }
            .container { width: 100%; max-width: 400px; background: rgba(255, 255, 255, 0.08); padding: 30px 20px; border-radius: 24px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); box-sizing: border-box; text-align: center; }
            h2 { margin-top: 0; font-size: 22px; color: #ffd700; }
            p { color: #a1b0cc; font-size: 14px; margin-bottom: 25px; }
            .form-group { margin-bottom: 20px; text-align: left; }
            label { display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 8px; font-weight: 500; }
            input, select { width: 100%; padding: 14px; background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 12px; color: #fff; font-size: 16px; box-sizing: border-box; outline: none; }
            input:focus, select:focus { border-color: #ffd700; }
            .btn { display: block; width: 100%; padding: 16px; background: linear-gradient(135deg, #ffd700 0%, #b8860b 100%); color: #0d1a33; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 25px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2); }
            #loading { display: none; margin-top: 15px; font-size: 14px; color: #ffd700; font-weight: bold; }
        </style>
        <script>
            def showLoading():
                document.getElementById('btn-submit').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
        </script>
    </head>
    <body>
        <div class="container">
            <h2>AI 로또 사주 명식 필터</h2>
            <p>구글 Gemini AI가 선천적 명식과 성명학을 실시간 분석하여 최적의 횡재수 보완 필터링을 수행합니다.</p>
            <form action="/lotto" method="post" onsubmit="document.getElementById('btn-submit').style.display='none'; document.getElementById('loading').style.display='block';">
                <div class="form-group">
                    <label>성함</label>
                    <input type="text" name="user_name" placeholder="예: 홍길동" required>
                </div>
                <div class="form-group">
                    <label>출생 연도 (4자리)</label>
                    <input type="number" name="year" placeholder="예: 1985" required min="1930" max="2026">
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
                <div id="loading">🔮 AI가 우주의 기운과 명식을 정밀 분석 중입니다... (약 2~3초 소요)</div>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/lotto", response_class=HTMLResponse)
def lotto_screen(user_name: str = Form(...), year: int = Form(...), birth_date: str = Form(...), time_slot: str = Form(...)):
    # AI 기반 실시간 풀이 데이터 획득
    ai_data = saju_system._get_ai_fortune(user_name, year, birth_date, time_slot)
    games = saju_system.generate_saju_games(ai_data["lucky_element"], 5)

    def get_color_class(num):
        if num <= 10: return "ball-yellow"
        elif num <= 20: return "ball-blue"
        elif num <= 30: return "ball-red"
        elif num <= 40: return "ball-gray"
        else: return "ball-green"

    games_html = ""
    for idx, game in enumerate(games, 1):
        balls_html = "".join(f'<div class="ball {get_color_class(n)}">{n:02d}</div>' for n in game)
        games_html += f"""
        <div class="game-row">
            <span class="game-label">{idx}게임</span>
            <div class="balls-container">{balls_html}</div>
        </div>
        """

    # AI가 줄바꿈(\n) 처리한 문장들을 HTML 줄바꿈(<br>)으로 변경
    formatted_reading = ai_data["reading"].replace("\n", "<br>")

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>로또 필터 시스템</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f5f7fb; margin: 0; padding: 20px; display: flex; justify-content: center; }}
            .container {{ width: 100%; max-width: 480px; background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); box-sizing: border-box; }}
            h2 {{ text-align: center; color: #333; margin-top: 0; margin-bottom: 15px; font-size: 22px; }}
            .saju-box {{ background: #f0f4fc; border-radius: 12px; padding: 15px; margin-bottom: 15px; font-size: 14px; color: #3b82f6; border-left: 5px solid #3b82f6; text-align: left; line-height: 1.5; }}
            .ai-box {{ background: #fdfaf2; border-radius: 12px; padding: 18px; margin-bottom: 20px; font-size: 14px; color: #333; border-left: 5px solid #d4af37; text-align: left; line-height: 1.7; box-shadow: inset 0 0 10px rgba(0,0,0,0.01); }}
            .ai-title {{ font-weight: bold; font-size: 15px; margin-bottom: 10px; color: #b8860b; border-bottom: 1px solid #f1e3c4; padding-bottom: 5px; }}
            .game-row {{ display: flex; align-items: center; margin-bottom: 15px; padding: 12px; background: #fafbfc; border-radius: 12px; border: 1px solid #edf1f7; }}
            .game-label {{ font-weight: bold; color: #555; font-size: 14px; width: 50px; flex-shrink: 0; }}
            .balls-container {{ display: flex; gap: 8px; justify-content: flex-start; width: 100%; }}
            .ball {{ width: 36px; height: 36px; border-radius: 50%; color: white; font-weight: bold; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .ball-yellow {{ background: #fbc02d; }}
            .ball-blue {{ background: #1e88e5; }}
            .ball-red {{ background: #e53935; }}
            .ball-gray {{ background: #8e8e93; }}
            .ball-green {{ background: #43a047; }}
            .btn {{ display: block; width: 100%; padding: 15px; background: #3182f6; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer; text-align: center; box-shadow: 0 4px 10px rgba(49,130,246,0.3); transition: background 0.2s; margin-top: 25px; text-decoration: none; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>AI 로또 명식 필터 결과</h2>
            <div class="saju-box">
                🔮 <b>입력 명식:</b> {user_name}님 / {year}년 {birth_date[:2]}월 {birth_date[2:]}일 ({time_slot} 출생)
            </div>
            
            <div class="ai-box">
                <div class="ai-title">Gemini AI의 맞춤 운세 해설</div>
                {formatted_reading}
                <br><br>
                💡 <i>AI가 지정한 보완 오행 번호대에 <b>재물 가중치(3.5x)</b>를 부여하여 번호를 조합했습니다.</i>
            </div>

            <div class="results">{games_html}</div>
            <a href="/" class="btn">다시 명식 입력하기</a>
        </div>
    </body>
    </html>
    """
