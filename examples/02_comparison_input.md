# 예시 2: 경쟁작 비교 요청

## 입력
```
Hollow Knight vs Hades Dead Cells 비교해줘
```

## 실행 순서
1. `compare_games.py --target "Hollow Knight" --competitors "Hades,Dead Cells"`

## 기대 출력 (similarity_matrix)
```json
{
  "target": "Hollow Knight",
  "competitors": ["Hades", "Dead Cells"],
  "similarity_matrix": [
    { "game": "Dead Cells", "similarity": 0.9124, "similarity_pct": "91.2%" },
    { "game": "Hades", "similarity": 0.8847, "similarity_pct": "88.5%" }
  ],
  "most_similar": "Dead Cells",
  "least_similar": "Hades"
}
```

## 포지셔닝 맵 (예시)
```
난이도(높음)
    │  Hollow Knight ●
    │         Dead Cells ●
    │  Hades ●
난이도(낮음)
    └─────────────────────
      서사 중심        액션 중심
```

## 블루오션 발견 (예시)
- Hollow Knight: 느린 탐험 + 환경 서사 조합 — 경쟁작 대비 차별화 영역
- 레드오션: 로그라이크 + 즉각 액션 — Hades/Dead Cells 모두 강점
