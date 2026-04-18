# 예시 3: Steam URL 직접 입력

## 입력
```
https://store.steampowered.com/app/1145360/ 분석해줘
```

## 실행 순서
1. URL에서 appid `1145360` 자동 추출
2. `analyze_game.py --steam "https://store.steampowered.com/app/1145360/" --output output/hades_report.docx`
   (collect_data + fetch_reviews 단계를 analyze_game.py 내부에서 처리)

## appid 추출 로직
```python
# analyze_game.py의 resolve_steam_appid()
m = re.search(r'/app/(\d+)', query)  # → "1145360"
```

## Steam API 파라미터 (중요)
```
store.steampowered.com/api/appdetails?appids=1145360&cc=US
```
`cc=US` 필수 — `cc=KR`은 일부 게임에서 success: false 반환

## 기대 출력
```
[Steam] App ID: 1145360 상세 정보 수집 중...
[Steam] 'Hades' 정보 수집 완료
[Steam] 한국어 리뷰 수집 중...
[Steam] 리뷰 수집 완료 (긍정 38, 부정 2)
[분석 중] Jesse Schell...
...
결과 저장: output/hades_report.docx
```
