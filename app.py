<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>AI LOTTO FILTER SYSTEM</title>
        <style>
            /* 🎨 메인 입력창 화면(image_e398fe.png)과 동일한 다크 네이비 톤 셋업 */
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
            
            /* ✨ 1. 입력창 디자인과 일치시킨 앱 초기 표지 (Splash Screen) */
            #splash-screen {
                position: fixed; 
                top: 0; 
                left: 0; 
                width: 100vw; 
                height: 100vh;
                background-color: #0f1a30; /* 입력창 배경과 동일 화합 */
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
            
            /* 입력창 메인 타이틀과 100% 동일한 서체 및 옐로우 컬러 */
            .splash-title { 
                font-size: 28px; 
                font-weight: 900; 
                color: #facc15; /* 고시인성 옐로우 */
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
                background: #1e293b; /* image_e398fe.png 박스 톤 */
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

        <!-- 🔮 1. 깔끔한 테크니컬 표지 영역 -->
        <div id="splash-screen">
            <div class="splash-container">
                <div class="splash-title">AI LOTTO FILTER SYSTEM</div>
                <div class="splash-subtitle">Quantum Saju System</div>
            </div>
        </div>

        <!-- 🖥️ 2. 메인 사주 입력창 영역 -->
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

        <!-- ⚡ 3. 2.5초 후 자동 화면 전환 스크립트 -->
        <script>
            window.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    const splash = document.getElementById('splash-screen');
                    const main = document.getElementById('main-container');
                    
                    splash.style.opacity = '0';
                    splash.style.visibility = 'hidden';
                    main.style.display = 'block';
                }, 2500); // 2.5초 제어
            });
        </script>
    </body>
    </html>
