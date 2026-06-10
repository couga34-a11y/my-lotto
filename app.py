import random
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()


class PremiumSajuLottoSystem:

    def __init__(self):
        self.pool = list(range(1, 46))
        # 오행별 고유 번호대 매핑
        self.element_map = {
            "木 (성장과 시작)": [3, 4, 8, 13, 14, 18, 23, 24, 28, 33, 34, 38, 43, 44],
            "火 (열정과 확산)": [2, 7, 12, 17, 22, 27, 32, 37, 42],
            "土 (안정과 조화)": [5, 10, 15, 20, 25, 30, 35, 40, 45],
            "金 (결단과 횡재)": [4, 9, 14, 19, 24, 29, 34, 39],
            "水 (지혜와 흐름)": [1, 6, 11, 16, 21, 26, 31, 36, 41],
        }

    def _calculate_advanced_saju(
        self, name: str, year: int, birth_date: str, time_slot: str
    ):
        """이름, 년, 월, 일, 시를 융합하여 결정론적 사주 데이터셋을 도출하는 핵심 알고리즘"""
        name_hash = sum(ord(char) for char in name)

        try:
            month = int(birth_date[:2])
            day = int(birth_date[2:])
        except:
            month, day = 1, 1

        time_weights = {
            "unknown": 5, "자시": 1, "축시": 2, "인시": 3, "묘시": 4, 
            "진시": 5, "사시": 6, "오시": 7, "미시": 8, "신시": 9, 
            "유시": 10, "술시": 11, "해시": 12
        }
        time_val = time_weights.get(time_slot, 5)

        # 융합 매직 넘버 생성
        magic_number = name_hash + year + month + day + time_val

        elements_list = [
            "木 (성장과 시작)",
            "火 (열정과 확산)",
            "土 (안정과 조화)",
            "金 (결단과 횡재)",
            "水 (지혜와 흐름)",
        ]
        selected_element = elements_list[magic_number % 5]

        # 매직 넘버 기반 가변 운세 데이터 생성
        days_pool = [("월요일", "수요일"), ("화요일", "목요일"), ("수요일", "금요일"), ("목요일", "토요일"), ("월요일", "금요일")]
        directions_pool = ["동쪽", "서쪽", "남쪽", "북쪽", "동남쪽"]
        
        money_fortunes = [
            "횡재수보다는 리스크 방어가 우선입니다. 보수적 스탠스를 유지하십시오.",
            "예상치 못한 소소한 이익이 따릅니다. 자산 관리에 집중하십시오.",
            "투자운이 평탄합니다. 무리한 지출을 피하면 결실이 맺힙니다.",
            "강한 재물 기운이 흐릅니다. 결단력을 발휘하기 좋은 시기입니다.",
            "안정적인 재물 축적이 가능한 흐름입니다. 내실을 다지십시오."
        ]
        
        job_fortunes = [
            "본인의 전문 영역에서 완벽성을 기할 수 있는 안정적인 타이밍입니다.",
            "주변과의 불필요한 마찰을 피하면 무난하고 평온하게 흐릅니다.",
            "맡은 바 임무나 정비, 관리 등에서 역량이 빛을 발하는 주간입니다.",
            "새로운 변화보다는 기존 기반을 점검하고 유지할 때 이롭습니다.",
            "동료들과의 협업이나 소통을 통해 복잡한 문제가 매끄럽게 해결됩니다."
        ]

        fortune_data = {
            "element": selected_element,
            "days": days_pool[magic_number % 5],
            "direction": directions_pool[magic_number % 5],
            "money": money_fortunes[magic_number % 5],
            "job": job_fortunes[magic_number % 5]
        }

        return fortune_data

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
        lucky_numbers = self.element_map.get(target_element, [])
        for num in lucky_numbers:
            weights[num - 1] = 3.0

        results = []
        while len(results) < count:
            selected = random.choices(self.pool, weights=weights, k=10)
            selected = sorted(list(set(selected)))[:6]
            if len(selected) < 6: continue
            if self._verify_combination(selected) and selected not in results:
                results.append(selected)
        return results


saju_system = PremiumSajuLottoSystem()


# ----------------------------------------------------
# 1. 입력 화면 HTML
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
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: radial-gradient(circle at center, #1a2a4c 0%, #0d1a33 100%); margin: 0
