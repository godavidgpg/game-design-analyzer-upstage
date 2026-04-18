---
name: game-design-analyzer
description: Upstage Solar Pro 3 API와 게임 디자인 전문가 6인의 이론을 활용하여 게임 기획 요소를 구조적으로 분석하고 Word/PDF 리포트를 생성합니다. Steam URL, 게임 이름, JSON 파일을 입력받아 MDA 프레임워크, 재미 구조, 감정 공학, 경쟁작 비교를 포함한 전문 분석을 수행합니다. "게임 분석", "게임 리뷰 작성", "게임 기획 분석", "게임 디자인 평가", "장르 비교", "경쟁작 벤치마킹", "코어 루프 분석", "MDA 분석", "이 게임 기획 요소 분석해줘" 등의 요청에 사용합니다.
allowed-tools: Bash(python *), Read
---

# 게임 기획 분석기

## 스크립트 경로
모든 스크립트는 `C:/Users/vudrk/Desktop/AI Projects/` 기준:
- `scripts/analyze_game.py` — 전문가 6인 프레임워크 분석 (핵심)
- `scripts/fetch_reviews.py` — Steam 리뷰 수집 + Solar Pro 3 패턴 분석
- `scripts/compare_games.py` — Solar Embedding 기반 경쟁작 유사도 비교
- `scripts/collect_data.py` — raw 데이터 → 구조화 JSON 변환
- `references/expert_philosophies.md` — 전문가 철학 참고 문서

## 환경 설정
`UPSTAGE_API_KEY`는 Claude Code settings.json의 env에 설정됨. 별도 지정 불필요.

---

## 워크플로우

### Step 0: 입력값 판별

`$ARGUMENTS` 분석:

| 형태 | 판별 기준 | 처리 방법 |
|------|----------|----------|
| Steam URL | `store.steampowered.com` 포함 | `--steam "<URL>"` |
| 게임 이름 | 일반 텍스트 | `--steam "<이름>"` (자동 검색) |
| JSON 파일 | `.json`으로 끝남 | `--game-data "<경로>"` |
| 비교 요청 | "vs", "비교", "경쟁작" 포함 | Step 3으로 바로 이동 |

출력 파일명: 게임 이름 기반 자동 생성 (공백→`_`, 소문자)
예: `Hollow Knight` → `hollow_knight_report.docx`

---

### Step 1: 게임 데이터 수집

#### 1-A. Steam에서 자동 수집 (권장)
```bash
cd "C:/Users/vudrk/Desktop/AI Projects" && \
python scripts/collect_data.py --steam "<게임명 또는 URL>" --output output/<게임명>_info.json
```

#### 1-B. raw 텍스트 파일에서 수집
```bash
cd "C:/Users/vudrk/Desktop/AI Projects" && \
python scripts/collect_data.py --input <파일경로> --output output/<게임명>_info.json
```

collect_data.py가 하는 것:
- Steam API로 공식 소개글, 장르, 개발사, Metacritic 수집
- Solar Pro 3로 핵심 메커닉, 스토리, 차별점 구조화 추출
- game_info.json 형식으로 저장

---

### Step 2: Steam 리뷰 수집 (선택, gap 분석용)

Steam URL에서 appid 추출 가능한 경우 자동 실행:
```bash
cd "C:/Users/vudrk/Desktop/AI Projects" && \
python scripts/fetch_reviews.py --appid "<appid 또는 URL 또는 게임명>" \
  --language koreana --count 100 --output output/<게임명>_reviews.json
```

한국어 리뷰가 10건 미만이면 자동으로 영어 리뷰로 재시도.

fetch_reviews.py 출력:
- 긍정/부정 패턴 TOP 5
- 플레이타임별 평가 경향
- 기획 시사점 3가지

---

### Step 3: 전문가 프레임워크 분석 (핵심)

```bash
cd "C:/Users/vudrk/Desktop/AI Projects" && \
python scripts/analyze_game.py \
  --game-data output/<게임명>_info.json \
  [--review-data output/<게임명>_reviews.json] \
  --output output/<게임명>_analysis.json
```

리뷰 데이터가 있으면 `--review-data`를 추가하면 gap 분석이 자동 포함된다.

생성되는 6개 분석:
- Jesse Schell — Elemental Tetrad + 5 Lenses
- Raph Koster — 패턴, 학습 곡선, Chunking
- MDA 프레임워크 — Mechanics→Dynamics→Aesthetics 인과 체인
- Tynan Sylvester — 감정 트리거 10종, 가치 변화
- Shigeru Miyamoto — 온보딩, 반응성, A-ha! 모먼트
- Hidetaka Miyazaki — 환경 서사, 극복 미학
- 통합 교차 분석 (강점/약점 각 3개, 혁신 포인트)
- [리뷰 있을 시] 디자이너 의도 vs 플레이어 경험 간극 분석

---

### Step 4: 경쟁작 비교 (선택)

"비교", "vs", "경쟁작", "포지셔닝" 등이 요청에 포함된 경우:
```bash
cd "C:/Users/vudrk/Desktop/AI Projects" && \
python scripts/compare_games.py \
  --target "<타겟 게임>" \
  --competitors "<경쟁작1>,<경쟁작2>,<경쟁작3>" \
  --output output/<게임명>_compare.json
```

compare_games.py가 하는 것:
- Solar Embedding (4096차원)으로 게임 간 코사인 유사도 측정
- 유사도 매트릭스 생성 (가장 유사한 경쟁작 / 가장 다른 경쟁작)
- Solar Pro 3로 메커닉/서사/감정/타겟층별 차별점 분석
- 블루오션/레드오션 영역 식별

---

### Step 5: 최종 리포트 생성

```bash
cd "C:/Users/vudrk/Desktop/AI Projects" && \
python scripts/analyze_game.py \
  --game-data output/<게임명>_info.json \
  [--review-data output/<게임명>_reviews.json] \
  --output output/<게임명>_report.docx
```

확장자별 자동 분기: `.docx` / `.pdf` / `.md` / `.json`

완료 후:
1. 저장 경로 안내
2. 핵심 인사이트 3줄 요약 제공

---

## 리포트 구조

```
1. 개요          게임 기본 정보 + 핵심 발견 3줄 요약
2. 구조 분석     Mechanics/Story/Aesthetics/Technology 4축
3. 재미의 구조   핵심 패턴, 학습 곡선, 흥미 유지 메커니즘
4. 시스템 인과   M→D→A 체인, 주력 미학 유형
5. 감정 공학     감정 트리거, 인간 가치 변화, 우아함
6. 접근성        온보딩, 환경 교육, 반응성
7. 도전과 극복   난이도 곡선, 환경 스토리텔링
8. 통합 분석     공통 강점/약점 3개, 혁신 포인트
9. 플레이어 리뷰 긍정/부정 패턴, 플레이타임별 경향   (리뷰 데이터 있을 시)
10. 의도-경험 간극 미학/패턴/접근성/감정 각 간극    (리뷰 데이터 있을 시)
11. 경쟁작 비교  유사도 매트릭스, 포지셔닝           (비교 요청 시)
12. 종합         강점/약점 3개, 기획 혁신 포인트
```

---

## 평가 시나리오

### Eval 1: 단일 게임 이름 분석
**입력**: `Hollow Knight`
**기대 결과**:
- `output/hollow_knight_info.json` 생성 (title, core_mechanics 포함)
- `output/hollow_knight_reviews.json` 생성 (analysis 필드 존재)
- `output/hollow_knight_report.docx` 생성 (6개 전문가 섹션 + 통합 분석 포함)
- 총 소요 시간 5분 이내
**실패 조건**: JSON 파싱 오류, 빈 분석 섹션, 한국어 미출력

### Eval 2: Steam URL 직접 입력
**입력**: `https://store.steampowered.com/app/1145360/` (Hades)
**기대 결과**:
- appid `1145360` 자동 추출
- Steam API에서 게임 정보 정상 수집 (`cc=US` 파라미터 사용)
- `output/hades_report.docx` 생성
**실패 조건**: `success: false` Steam API 오류, 게임명 추출 실패

### Eval 3: 경쟁작 비교 요청
**입력**: `Hollow Knight vs Hades Dead Cells 비교`
**기대 결과**:
- `compare_games.py` 실행 (`--target "Hollow Knight" --competitors "Hades,Dead Cells"`)
- `output/hollow_knight_compare.json`에 `similarity_matrix` 배열 존재
- `most_similar`, `least_similar` 필드 존재
- 포지셔닝 맵 + 블루오션/레드오션 분석 포함
**실패 조건**: 임베딩 API 오류, 유사도 수치 미출력

---

## Gotchas

- **Steam 검색 1순위**: 정확한 이름이나 URL 권장 (예: "Hades" → "Hades II" 잡힐 수 있음)
- **Solar Pro 3 JSON 이중 중괄호**: 응답이 이미 `{`로 시작하면 prepend 금지 — `collect_data.py`에서 처리됨
- **리뷰 언어**: 한국어 10건 미만이면 영어로 자동 재시도 후 Solar로 한국어 분석
- **임베딩 차원**: solar-embedding-1-large-passage는 4096차원, 벡터 비교는 정규화 후 코사인
- **전체 분석 시간**: API 호출 7+회 → 약 3~5분 소요
- **리뷰 저작권**: 리뷰 원문은 직접 리포트에 넣지 않고 반드시 요약/인용 형태로 사용
- **출시 5년 이상 차이**: 경쟁작 비교 시 Technology 축 비교는 무의미할 수 있음
- **output/ 폴더**: 중간 결과물은 모두 output/에 저장됨
