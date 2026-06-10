import os
import random
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# 구글 공식 최신 SDK 설정 (API v1 안정판 고정)
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
            
            # 레이턴시 극소화를 위한 초경량 고속 모델 gemini-3.1-flash-lite 적용
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
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
        for i in range(len(numbers
