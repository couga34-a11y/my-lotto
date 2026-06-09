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


# ----------------------------------------------------
# 1. 초기 화면 (스플래시 스크린) HTML/CSS 생성 함수
# ----------------------------------------------------
def get_splash_screen():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>로또 필터 시스템</title>
        
        <link rel="apple-touch-icon" sizes="180x180" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <link rel="icon" type="image/png" sizes="32x32" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <link rel="icon" type="image/png" sizes="16x16" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-title" content="로또 필터">
        
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: radial-gradient(circle at center, #1a2a4c 0%, #0d1a33 100%); margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; overflow: hidden; color: #fff; }
            .content-box { text-align: center; }
            .logo-area { position: relative; width: 180px; height: 180px; margin: 0 auto 30px; }
            .golden-ball { width: 100px; height: 100px; background: radial-gradient(circle at 30% 30%, #ffd700 0%, #b8860b 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 36px; font-weight: bold; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 40px rgba(255, 215, 0, 0.7); }
            .swirl-particles { position: absolute; width: 180px; height: 180px; top: 0; left: 0; background: url('https://i.ibb.co/3s8sK8b/swirl-particles.png') no-repeat center/contain; animation: spin-swirl 5s linear infinite; }
            @keyframes spin-swirl { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            h1 { font-size: 24px; font-weight: bold; margin: 0 0 10px; color: #fff; }
            .subtitle { font-size: 14px; color: #a1b0cc; margin: 0 0 40px; }
            .loading-text { font-size: 14px; color: #888; margin: 0; }
        </style>
    </head>
    <body>
        <div class="content-box">
            <div class="logo-area">
                <div class="swirl-particles"></div>
                <div class="golden-ball">1</div>
            </div>
            <h1>로또 필터 시스템</h1>
            <p class="subtitle">정규분포 & 연속 조합 최적화 완료</p>
            <p class="loading-text">최적의 조합을 불러오는 중...</p>
        </div>
        <script>
            // 2초 뒤에 메인 결과 화면으로 자동 이동
            setTimeout(function() {
                window.location.href = '/lotto';
            }, 2000);
        </script>
    </body>
    </html>
    """


# ----------------------------------------------------
# 2. 메인 결과 화면 HTML/CSS 생성 함수
# ----------------------------------------------------
def get_main_screen():
    games = lotto_system.generate_games(5)

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
        
        <link rel="apple-touch-icon" sizes="180x180" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <link rel="icon" type="image/png" sizes="32x32" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        <link rel="icon" type="image/png" sizes="16x16" href="https://i.ibb.co/3s8sK8b/swirl-particles.png">
        
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
            <h2>로또 필터 시스템</h2>
            <div class="subtitle">정규분포 & 연속 조합 최적화 완료</div>
            <div class="results">{games_html}</div>
            <a href="/lotto" class="btn">새로운 번호 추출하기</a>
        </div>
    </body>
    </html>
    """


# ----------------------------------------------------
# 3. FastAPI 엔드포인트 설정
# ----------------------------------------------------
@app.get("/api/lotto")
def get_lotto_api(count: int = 5):
    """지정한 개수(기본 5개)만큼 필터링된 로또 게임 데이터를 반환하는 API"""
    games = lotto_system.generate_games(count)
    return {"status": "success", "filter_mode": "pure_balance", "games": games}


@app.get("/", response_class=HTMLResponse)
def index():
    return get_splash_screen()


@app.get("/lotto", response_class=HTMLResponse)
def lotto_screen():
    return get_main_screen()
