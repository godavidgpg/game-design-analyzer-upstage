# 예시 1: 게임 이름으로 전체 분석

## 입력
```
Hollow Knight 분석해줘
```

## 실행 순서
1. `collect_data.py --steam "Hollow Knight"` → `output/hollow_knight_info.json`
2. `fetch_reviews.py --appid "Hollow Knight"` → `output/hollow_knight_reviews.json`
3. `analyze_game.py --game-data ... --review-data ... --output output/hollow_knight_report.docx`

## 기대 출력
```
[Steam] 'Hollow Knight' 검색 중...
[Steam] 'Hollow Knight' (ID: 367520) 발견
[Solar Pro 3] 구조화 분석 중...
[완료] output/hollow_knight_info.json

[리뷰 수집] App ID: 367520, 언어: koreana, 목표: 100건
[완료] 50건 수집
[Solar Pro 3] 리뷰 패턴 분석 중...
[완료] output/hollow_knight_reviews.json

[분석 중] Jesse Schell — 구조 분석...
[완료] Jesse Schell — 구조 분석
... (6개 전문가)
[통합 분석 중]...
[간극 분석 중]...
결과 저장: output/hollow_knight_report.docx
```

## 핵심 인사이트 (예시)
1. **핵심 강점**: Discovery + Challenge Aesthetic의 균형 — 탐험과 극복이 시너지를 냄
2. **핵심 약점**: Miyamoto 관점에서 온보딩 허들 — 첫 3분 내 이탈률이 높을 수 있음
3. **혁신 포인트**: 지도 구매 메커닉이 Discovery Aesthetic을 역설적으로 강화
