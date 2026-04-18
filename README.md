# 🎮 Game Design Analyzer

**Upstage Solar Pro 3 API**와 게임 디자인 전문가 6인의 이론을 활용하여, Steam 게임을 자동으로 분석하고 전문 기획 리포트(.docx / .pdf / .md)를 생성하는 **Claude Code 스킬**입니다.

> "게임 분석 리포트 만들어줘" 한 마디로 — Steam 데이터 수집 → 전문가 프레임워크 분석 → 리뷰 gap 분석 → 경쟁작 비교까지 자동화

---

## 📋 목차

- [데모](#-데모)
- [핵심 기능](#-핵심-기능)
- [아키텍처](#-아키텍처)
- [전문가 프레임워크](#-전문가-프레임워크-6인)
- [설치 방법](#-설치-방법)
- [사용법](#-사용법)
- [프로젝트 구조](#-프로젝트-구조)
- [기술 상세](#-기술-상세)

---

## 🎬 데모

```
사용자: Hollow Knight 게임 분석해줘
```

→ 자동으로:
1. Steam API에서 게임 데이터 수집
2. 한국어 리뷰 50건 수집 + Solar Pro 3 패턴 분석
3. 전문가 6인 관점 분석 실행 (약 3~5분)
4. `output/hollow_knight_report.docx` 생성

---

## ✨ 핵심 기능

| 기능 | 설명 |
|------|------|
| **Steam 자동 수집** | URL, 게임명, App ID → 자동으로 게임 정보 + 리뷰 수집 |
| **전문가 6인 분석** | Schell, Koster, MDA, Sylvester, Miyamoto, Miyazaki 프레임워크 |
| **리뷰 gap 분석** | 디자이너 의도 vs 실제 플레이어 경험 간극 추출 |
| **경쟁작 임베딩 비교** | Solar Embedding 4096차원으로 코사인 유사도 측정 |
| **다양한 출력 포맷** | `.docx` / `.pdf` / `.md` / `.json` |
| **Claude Code 스킬** | 자연어로 호출 가능한 Claude Code skill |

---

## 🏗 아키텍처

```
사용자 입력 (게임명 / Steam URL / JSON)
         │
         ▼
┌─────────────────┐    Steam API
│ collect_data.py │ ◄──────────── 게임 기본정보, 장르, Metacritic
│                 │    Solar Pro 3
│                 │ ──────────────► 핵심 메커닉, 스토리, 차별점 구조화
└────────┬────────┘
         │
         ▼
┌─────────────────┐    Steam Reviews API
│ fetch_reviews.py│ ◄──────────── 최근 리뷰 50~100건
│                 │    Solar Pro 3
│                 │ ──────────────► 긍정/부정 패턴, 플레이타임별 경향, 기획 시사점
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│              analyze_game.py                │
│                                             │
│  Jesse Schell   → Elemental Tetrad + 5 Lenses│
│  Raph Koster    → 패턴 학습, Chunking         │
│  MDA Framework  → M→D→A 인과 체인            │
│  Tynan Sylvester→ 감정 트리거 10종            │
│  Shigeru Miyamoto→ 온보딩, 반응성             │
│  Hidetaka Miyazaki→ 환경 서사, 극복 미학      │
│                                             │
│  + 통합 교차 분석 (강점/약점/혁신 포인트)       │
│  + 리뷰 gap 분석 (의도 vs 경험 간극)           │
└────────┬────────────────────────────────────┘
         │
         ├──────────────────────────┐
         ▼                          ▼
 output/report.docx        compare_games.py (선택)
                           Solar Embedding 유사도 비교
                           블루오션/레드오션 포지셔닝
```

---

## 👥 전문가 프레임워크 6인

### 1. Jesse Schell — 구조 분석
**핵심 이론**: Elemental Tetrad + 5 Lenses  
게임을 `Mechanics / Story / Aesthetics / Technology` 4축으로 분해하고, 각 축이 서로를 어떻게 지지하는지 평가합니다. Essential Experience, Flow, Interest Curve 등 5개 렌즈를 적용합니다.

### 2. Raph Koster — 재미 구조
**핵심 이론**: A Theory of Fun  
`"재미란 패턴을 학습하는 과정에서 오는 쾌감"`  
플레이어가 실제로 학습하는 핵심 패턴, 패턴 깊이, Grokking Point, Chunking 구조를 분석합니다.

### 3. MDA 프레임워크 — 시스템 인과
**핵심 이론**: Mechanics → Dynamics → Aesthetics  
8가지 Aesthetic 유형(Sensation, Fantasy, Narrative, Challenge, Fellowship, Discovery, Expression, Submission) 중 주력 Aesthetic을 식별하고, 이를 구현하는 Dynamics → Mechanics 역방향 체인을 추적합니다.

### 4. Tynan Sylvester — 감정 공학
**핵심 이론**: Designing Games  
`"게임은 경험을 생성하는 기계이며, 경험은 감정의 흐름이다"`  
감정 트리거 10종(Learning, Challenge, Acquisition, Spectacle 등), 미귀인 효과, 메커닉 대비 경험 비율(엘레강스)을 분석합니다.

### 5. Shigeru Miyamoto — 접근성 설계
**핵심 이론**: 환경 교육 + 보편적 접근성  
`"환경이 가르쳐야 한다. 매뉴얼 없이도 플레이할 수 있어야 한다"`  
첫 5분 온보딩, A-ha! 모먼트 설계, 반응성, 이탈 지점 분석을 수행합니다.

### 6. Hidetaka Miyazaki — 극복의 미학
**핵심 이론**: 환경 스토리텔링 + 난이도 설계  
`"세계 자체가 이야기를 말해야 한다" + "높은 난이도는 보상의 전제 조건"`  
환경 서사 비율, 좌절→극복 감정 아크, 모호함의 가치, 발견 설계를 분석합니다.

---

## ⚙️ 설치 방법

### 1. 레포 클론

```bash
git clone https://github.com/<your-username>/game-design-analyzer.git
cd game-design-analyzer
```

### 2. Python 패키지 설치

```bash
pip install openai requests python-docx fpdf2
```

### 3. API 키 설정

[Upstage Console](https://console.upstage.ai)에서 API 키를 발급받은 후:

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일에 키 입력
UPSTAGE_API_KEY=up_xxxxxxxxxxxxx
```

또는 환경변수로 직접 설정:
```bash
export UPSTAGE_API_KEY=up_xxxxxxxxxxxxx   # Mac/Linux
set UPSTAGE_API_KEY=up_xxxxxxxxxxxxx      # Windows CMD
$env:UPSTAGE_API_KEY="up_xxxxxxxxxxxxx"   # Windows PowerShell
```

### 4. Claude Code 스킬 설치 (선택)

Claude Code CLI에서 자연어로 호출하려면 `skill.md`를 스킬 디렉토리에 복사합니다:

```bash
# Mac/Linux
cp skill.md ~/.claude/skills/game-design-analyzer.md

# Windows
copy skill.md %USERPROFILE%\.claude\skills\game-design-analyzer.md
```

그 다음 `skill.md` 내의 `<BASE_DIR>`를 이 레포를 클론한 절대 경로로 수정하세요.

---

## 🚀 사용법

### A. Claude Code 스킬로 사용 (추천)

스킬 설치 후 Claude Code CLI에서:

```
/game-design-analyzer Hollow Knight
/game-design-analyzer https://store.steampowered.com/app/1145360/
/game-design-analyzer Hollow Knight 경쟁작 비교 포함해서
/game-design-analyzer Baldur's Gate 3 vs Divinity Original Sin 2 비교
```

### B. 스크립트 직접 실행

#### 빠른 분석 (Steam에서 바로)
```bash
UPSTAGE_API_KEY=your_key python scripts/analyze_game.py \
  --steam "Hollow Knight" \
  --output output/hollow_knight_report.docx
```

#### 전체 파이프라인 (가장 상세한 결과)
```bash
# 1. 게임 데이터 수집
UPSTAGE_API_KEY=your_key python scripts/collect_data.py \
  --steam "Hollow Knight" \
  --output output/hollow_knight_info.json

# 2. 리뷰 수집
UPSTAGE_API_KEY=your_key python scripts/fetch_reviews.py \
  --appid "Hollow Knight" \
  --count 100 \
  --output output/hollow_knight_reviews.json

# 3. 전문가 분석 + gap 분석
UPSTAGE_API_KEY=your_key python scripts/analyze_game.py \
  --game-data output/hollow_knight_info.json \
  --review-data output/hollow_knight_reviews.json \
  --output output/hollow_knight_report.docx
```

#### 경쟁작 비교
```bash
UPSTAGE_API_KEY=your_key python scripts/compare_games.py \
  --target "Hollow Knight" \
  --competitors "Hades,Dead Cells,Ori and the Blind Forest" \
  --output output/hollow_knight_compare.json
```

#### 특정 전문가만 분석
```bash
UPSTAGE_API_KEY=your_key python scripts/analyze_game.py \
  --steam "Hollow Knight" \
  --analysis schell \       # schell | koster | mda | sylvester | miyamoto | miyazaki
  --output output/test.docx
```

---

## 📁 프로젝트 구조

```
game-design-analyzer/
│
├── skill.md                      # Claude Code 스킬 정의 파일
│                                 # → ~/.claude/skills/에 복사하면 /game-design-analyzer 로 호출 가능
│
├── scripts/
│   ├── analyze_game.py           # 핵심: 전문가 6인 프레임워크 분석 + 리포트 생성
│   ├── collect_data.py           # Steam API + Solar Pro 3로 게임 데이터 구조화
│   ├── fetch_reviews.py          # Steam 리뷰 수집 + Solar Pro 3 패턴 분석
│   └── compare_games.py          # Solar Embedding 기반 경쟁작 유사도 비교
│
├── references/
│   └── expert_philosophies.md    # 전문가 6인 철학 & 분석 프레임워크 참고 문서
│
├── output/                       # 분석 결과물 저장 (gitignore)
│   └── .gitkeep
│
├── .env.example                  # 환경변수 템플릿
├── .gitignore
└── README.md
```

---

## 🔬 기술 상세

### Solar Pro 3 한국어 출력 처리
Solar Pro 3는 내부적으로 영어 Chain-of-Thought를 먼저 생성한 후 한국어 답변을 출력하는 경향이 있습니다. 이를 처리하기 위해 3중 레이어를 적용합니다:

```python
# 1. 시스템 프롬프트에 강제 지시
"IMPORTANT: 반드시 한국어로만 답변하세요."

# 2. Assistant prefix로 출력 시작점 강제
{"role": "assistant", "content": "## 분석 결과\n\n"}

# 3. 후처리로 영어 CoT 제거
def strip_english_cot(text):
    for i, line in enumerate(text.split("\n")):
        if re.search(r'[\uAC00-\uD7A3]', line):  # 첫 한글 줄부터 반환
            return "\n".join(lines[i:])
```

### Solar Embedding 유사도 비교
`solar-embedding-1-large-passage` 모델로 4096차원 벡터를 생성하고 코사인 유사도를 계산합니다:

```python
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (sum(x**2 for x in a)**0.5 * sum(x**2 for x in b)**0.5)
```

### Steam API 활용
```
게임 정보: store.steampowered.com/api/appdetails?appids=<id>&cc=US
게임 검색: store.steampowered.com/api/storesearch?term=<name>
리뷰 수집: store.steampowered.com/appreviews/<id>?json=1&language=koreana
```
> `cc=US` 파라미터가 필수입니다. 한국 리전(`cc=KR`)은 일부 게임에서 응답 실패가 발생합니다.

### 출력 포맷 라우팅
```python
def save_output(results, output_path, game_title):
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".pdf":    → fpdf2 + 맑은고딕 폰트
    elif ext == ".docx": → python-docx
    elif ext == ".md":   → 마크다운 텍스트
    else:                → JSON
```

---

## 📊 리포트 구조

| 섹션 | 내용 | 조건 |
|------|------|------|
| 1. 개요 | 게임 기본 정보 + 핵심 발견 3줄 | 항상 |
| 2. 구조 분석 | Mechanics/Story/Aesthetics/Technology 4축 | 항상 |
| 3. 재미의 구조 | 핵심 패턴, 학습 곡선 | 항상 |
| 4. 시스템 인과 | M→D→A 체인, 주력 Aesthetic | 항상 |
| 5. 감정 공학 | 감정 트리거, 인간 가치 변화 | 항상 |
| 6. 접근성 | 온보딩, 반응성, A-ha! 모먼트 | 항상 |
| 7. 도전과 극복 | 난이도 곡선, 환경 스토리텔링 | 항상 |
| 8. 통합 분석 | 공통 강점/약점 3개, 혁신 포인트 | 항상 |
| 9. 플레이어 리뷰 | 긍정/부정 패턴, 플레이타임별 경향 | 리뷰 데이터 있을 시 |
| 10. 의도-경험 간극 | 미학/패턴/접근성/감정 gap | 리뷰 데이터 있을 시 |
| 11. 경쟁작 비교 | 유사도 매트릭스, 포지셔닝 맵 | 비교 요청 시 |
| 12. 종합 | 강점/약점 3개, 기획 혁신 포인트 | 항상 |

---

## 🔑 API 키 발급

1. [Upstage Console](https://console.upstage.ai) 접속
2. 회원가입 / 로그인
3. API Keys → Create New Key
4. `.env` 파일에 `UPSTAGE_API_KEY=발급받은키` 입력

> Solar Pro 3 + Solar Embedding API 사용 비용이 발생합니다. 전체 분석 1회 기준 약 7~10회 API 호출.

---

## ⚠️ 주의사항

- **Steam 검색 정확도**: 게임명보다 Steam URL 사용을 권장합니다 (`"Hades"` → `"Hades II"` 로 잡힐 수 있음)
- **분석 시간**: API 호출 7회 이상 → 전체 분석 약 3~5분 소요
- **PDF 한글**: Windows `C:/Windows/Fonts/malgun.ttf` (맑은고딕)이 필요합니다
- **리뷰 저작권**: 리뷰 원문은 직접 리포트에 수록하지 않고 요약/인용 형태로만 사용합니다

---

## 📄 라이선스

MIT License
