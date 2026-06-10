import random
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()


class SajuLottoSystem:

    def __init__(self):
        self.pool = list(range(1, 46))
        # 오행별 로또 번호 배속 (역학 기준 정렬)
        self.element_map = {
            "木": [3, 4, 8, 13, 14, 18, 23, 24, 28, 33, 34, 38, 43, 44],
            "火": [2, 7, 12, 17, 22, 27, 32, 37, 42],
            "土": [5, 10, 15, 20, 25, 30, 35, 40, 45],
            "金": [4, 9, 14, 19, 24, 29, 34, 39],
            "水": [1, 6, 11, 16, 21, 26, 31, 36, 41],
        }

    def _get_combined_saju_element(self, name: str, year: int):
        """연도 사주 오행과 이름의 자음 오행 기운을 결합하는 확장 알고리즘"""
        elements = ["金", "水", "木", "火", "土"]
        idx = (year - 4) % 10
        element_idx = idx // 2
        base_element = elements[element_idx]

        # 성명학적 기운 연출을 위한 단순 해시 연산 (이름에 따른 변수 생성)
        name_score = sum(ord(char) for char in name)

        if base_element == "木":
            return "火 (활동력 및 재물운 증가)", "火"
        elif base_element == "火":
            return "土 (현실적 결실 및 안정)", "土"
        elif base_element == "土":
            return "金 (횡재수 및 권력운 복원)", "金"
        elif base_element == "金":
            return "水 (지혜 및 유연한 소통)", "水"
        else:
            # 이름의 기운에 따라 木과 土 사이에서 유동적 조율 연출
            if name_score % 2 == 0:
                return "木 (성장 및 새로운 발전)", "木"
            else:
                return "土 (안정적인 재물 축적)", "土"

    def _verify_combination(self, numbers):
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

    def generate_saju_games(self, target_element, count=5):
        weights = [1.0] * 45
        lucky_numbers = self.element_map.get(target_element, [])
        for num in lucky_numbers:
            weights[num - 1] = 2.5

        results = []
        while len(results) < count:
            selected = random.choices(self.pool, weights=weights, k=10)
            selected = sorted(list(set(selected)))[:6]

            if len(selected) < 6:
                continue

            if self._verify_combination(selected) and selected not in results:
                results.append(selected)
        return results


saju_system = SajuLottoSystem()


# ----------------------------------------------------
# 1. 입력 화면 (메인 페이지) HTML - 이름 칸 추가
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>로또 필터 시스템</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h2>로또 사주 명식 필터</h2>
            <p>성명학적 흐름과 생년월일의 선천적 기운을 융합하여 조화로운 번호를 추출합니다.</p>
            <form action="/lotto" method="post">
                <div class="form-group">
                    <label>분석 대상자 성함</label>
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
                <button type="submit" class="btn">사주·성명 융합 추출</button>
            </form>
        </div>
    </body>
    </html>
    """


# ----------------------------------------------------
# 2. 결과 화면 HTML (이름 실시간 매핑 반영)
# ----------------------------------------------------
@app.post("/lotto", response_class=HTMLResponse)
def lotto_screen(
    user_name: str = Form(...),
    year: int = Form(...),
    birth_date: str = Form(...),
    time_slot: str = Form(...),
):
    desc, lucky_element = saju_system._get_combined_saju_element(user_name, year)
    games = saju_system.generate_saju_games(lucky_element, 5)

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

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>로또 필터 시스템</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f5f7fb; margin: 0; padding: 20px; display: flex; justify-content: center; }}
            .container {{ width: 100%; max-width: 450px; background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); box-sizing: border-box; }}
            h2 {{ text-align: center; color: #333; margin-top: 0; margin-bottom: 5px; font-size: 22px; }}
            .saju-box {{ background: #f0f4fc; border-radius: 12px; padding: 15px; margin-bottom: 20px; font-size: 14px; color: #3b82f6; border-left: 5px solid #3b82f6; text-align: left; line-height: 1.5; }}
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
            <h2>로또 필터 결과</h2>
            <div class="saju-box">
                🔮 <b>분석 정보:</b> {user_name}님 / {year}년 {birth_date[:2]}월 {birth_date[2:]}일 ({time_slot})<br>
                ✨ <b>보완 오행:</b> 이번 주 <b>{user_name}</b>님께 필요한 기운은 <b>{desc}</b>입니다. 성명학적 융합 분석에 따라 해당 기운을 가진 고유 번호대에 가중치(2.5x)를 반영하여 필터링을 수행했습니다.
            </div>
            <div class="results">{games_html}</div>
            <a href="/" class="btn">다시 조회하기</a>
        </div>
    </body>
    </html>
    """
