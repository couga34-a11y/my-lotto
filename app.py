import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


class PureLottoSystem:

    def __init__(self):
        self.pool = list(range(1, 46))
        self.weights = [1.0] * 45

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

    def generate_games(self, count=5):
        results = []
        while len(results) < count:
            selected = random.choices(self.pool, weights=self.weights, k=10)
            selected = sorted(list(set(selected)))[:6]

            if len(selected) < 6:
                continue

            if self._verify_combination(selected) and selected not in results:
                results.append(selected)
        return results


lotto_system = PureLottoSystem()


@app.get("/", response_class=HTMLResponse)
def index():
    games = lotto_system.generate_games(5)

    # 로또 공 색상 클래스 지정 함수
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

    # HTML 내부 결과 렌더링
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

    # 모바일 최적화 UI (HTML/CSS)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>석연님 전용 로또 필터 시스템</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f5f7fb; margin: 0; padding: 20px; display: flex; justify-content: center; }}
            .container {{ width: 100%; max-width: 450px; background: white; padding: 25px 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); box-sizing: border-box; }}
            h2 {{ text-align: center; color: #333; margin-top: 0; margin-bottom: 5px; font-size: 22px; }}
            .subtitle {{ text-align: center; color: #888; font-size: 13px; margin-bottom: 25px; }}
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
            .btn:active {{ background: #1b64da; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>로또 최적 확률 추천 시스템</h2>
            <div class="subtitle">정규분포 및 연속 번호 제한 필터 완료</div>
            
            <div class="results">
                {games_html}
            </div>
            
            <a href="/" class="btn">새로운 번호 추출하기</a>
        </div>
    </body>
    </html>
    """
    return html_content