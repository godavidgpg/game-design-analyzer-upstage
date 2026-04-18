#!/usr/bin/env python3
"""Steam 리뷰를 수집하고 Solar Pro 3로 패턴을 분석합니다."""
import sys, os, json, argparse, time, re
import requests

try:
    from openai import OpenAI
except ImportError:
    print("Error: pip install openai", file=sys.stderr)
    sys.exit(1)

UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY", "")
STEAM_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

client = OpenAI(api_key=UPSTAGE_API_KEY, base_url="https://api.upstage.ai/v1")

REVIEW_ANALYSIS_PROMPT = """IMPORTANT: 반드시 한국어로만 답변하세요.

당신은 게임 플레이어 리뷰 데이터 분석 전문가입니다.
아래 Steam 리뷰 데이터를 분석하여 다음 구조로 정확히 출력하세요.

## 수치 요약
- 총 리뷰 수: (제공된 샘플 수)
- 긍정 리뷰 비율: (%)
- 부정 리뷰 비율: (%)

## 긍정 패턴 TOP 5
반복적으로 칭찬받는 요소를 구체적으로 나열하세요. 각 항목마다 언급 빈도와 대표 인용구 포함.

## 부정 패턴 TOP 5
반복적으로 불만이 제기되는 요소를 구체적으로 나열하세요. 각 항목마다 심각도(치명적/불편/사소)와 대표 인용구 포함.

## 플레이타임별 평가 경향
- 단기 플레이어 (10시간 미만): 주요 반응
- 중기 플레이어 (10~50시간): 주요 반응
- 장기 플레이어 (50시간 이상): 주요 반응

## 기획 시사점 3가지
리뷰 데이터에서 도출되는 게임 기획 관점의 인사이트를 구체적으로 서술하세요."""


def fetch_reviews(appid: str, language: str = "koreana", count: int = 100) -> list[dict]:
    """Steam appreviews API로 리뷰를 수집한다. cursor 기반 페이지네이션 지원."""
    all_reviews = []
    cursor = "*"
    per_page = min(100, count)

    while len(all_reviews) < count:
        params = {
            "json": 1,
            "language": language,
            "num_per_page": per_page,
            "review_type": "all",
            "purchase_type": "steam",
            "filter": "recent",
            "cursor": cursor,
        }
        r = requests.get(
            f"https://store.steampowered.com/appreviews/{appid}",
            params=params,
            headers=STEAM_HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()

        batch = data.get("reviews", [])
        if not batch:
            break

        all_reviews.extend(batch)
        cursor = data.get("cursor", "")
        if not cursor or len(batch) < per_page:
            break

        time.sleep(1)  # rate limit

    return all_reviews[:count]


def analyze_reviews_with_solar(reviews: list[dict]) -> str:
    """Solar Pro 3로 리뷰 패턴을 분석한다."""
    positives = [r for r in reviews if r.get("voted_up")]
    negatives = [r for r in reviews if not r.get("voted_up")]

    def format_reviews(lst, limit=25):
        result = []
        for r in lst[:limit]:
            text = re.sub(r'\s+', ' ', r.get("review", "")).strip()[:400]
            playtime_h = r.get("author", {}).get("playtime_forever", 0) // 60
            if text:
                result.append(f"[{playtime_h}h] {text}")
        return result

    pos_texts = format_reviews(positives)
    neg_texts = format_reviews(negatives)

    content = f"""총 {len(reviews)}개 리뷰 (긍정: {len(positives)}, 부정: {len(negatives)})

【긍정 리뷰 샘플 ({len(pos_texts)}건)】
{chr(10).join(f'- {t}' for t in pos_texts)}

【부정 리뷰 샘플 ({len(neg_texts)}건)】
{chr(10).join(f'- {t}' for t in neg_texts)}"""

    # 12,000자 제한
    if len(content) > 12000:
        content = content[:12000] + "\n...(이하 생략)"

    resp = client.chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": REVIEW_ANALYSIS_PROMPT},
            {"role": "user", "content": content},
            {"role": "assistant", "content": "## 수치 요약\n\n"},
        ],
        temperature=0.4,
        max_tokens=4096,
    )
    raw = resp.choices[0].message.content

    # 영어 CoT 제거
    lines = raw.split("\n")
    for i, line in enumerate(lines):
        if re.search(r'[\uAC00-\uD7A3]', line.strip()):
            raw = "\n".join(lines[i:])
            break

    return "## 수치 요약\n\n" + raw


def resolve_appid(query: str) -> str:
    """URL, 숫자, 게임 이름에서 app ID를 반환한다."""
    m = re.search(r'/app/(\d+)', query)
    if m:
        return m.group(1)
    if query.strip().isdigit():
        return query.strip()
    # 이름으로 검색
    r = requests.get(
        "https://store.steampowered.com/api/storesearch",
        params={"term": query, "cc": "US", "l": "english"},
        headers=STEAM_HEADERS,
        timeout=15,
    )
    items = r.json().get("items", [])
    if not items:
        raise ValueError(f"Steam에서 '{query}'를 찾을 수 없습니다.")
    return str(items[0]["id"])


def main():
    parser = argparse.ArgumentParser(description="Steam 리뷰 수집 및 분석")
    parser.add_argument("--appid", required=True, help="Steam App ID, URL, 또는 게임 이름")
    parser.add_argument("--language", default="koreana", help="리뷰 언어 (koreana/english)")
    parser.add_argument("--count", type=int, default=100, help="수집할 리뷰 수 (기본 100)")
    parser.add_argument("--raw-only", action="store_true", help="수집만 하고 Solar 분석 건너뜀")
    parser.add_argument("--output", default=None, help="결과 저장 경로 (.json)")
    args = parser.parse_args()

    appid = resolve_appid(args.appid)
    print(f"[리뷰 수집] App ID: {appid}, 언어: {args.language}, 목표: {args.count}건", file=sys.stderr)

    reviews = fetch_reviews(appid, args.language, args.count)
    print(f"[완료] {len(reviews)}건 수집", file=sys.stderr)

    if args.raw_only:
        result = {"appid": appid, "count": len(reviews), "reviews": reviews}
    else:
        if args.language == "koreana" and len(reviews) < 10:
            print("[경고] 한국어 리뷰가 적습니다. --language english 로 재시도합니다.", file=sys.stderr)
            reviews = fetch_reviews(appid, "english", args.count)
            print(f"[영어 재수집] {len(reviews)}건", file=sys.stderr)

        print("[Solar Pro 3] 리뷰 패턴 분석 중...", file=sys.stderr)
        analysis = analyze_reviews_with_solar(reviews)
        print("[완료] 리뷰 분석 완료", file=sys.stderr)

        result = {
            "appid": appid,
            "count": len(reviews),
            "analysis": analysis,
            "raw_sample": reviews[:10],  # 원본 샘플 10건 보존
        }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[저장] {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
