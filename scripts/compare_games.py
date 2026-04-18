#!/usr/bin/env python3
"""Solar Embedding API로 게임 간 특성 유사도를 수치화하고 차별점을 분석합니다."""
import sys, os, json, argparse, re
import requests

try:
    from openai import OpenAI
except ImportError:
    print("Error: pip install openai", file=sys.stderr)
    sys.exit(1)

UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY", "")
STEAM_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

client = OpenAI(api_key=UPSTAGE_API_KEY, base_url="https://api.upstage.ai/v1")

COMPARE_SYSTEM = """IMPORTANT: 반드시 한국어로만 답변하세요.

당신은 게임 디자인 비교 분석 전문가입니다.
타겟 게임과 경쟁작들의 정보를 비교하여 다음 구조로 분석하세요.

## 포지셔닝 맵
각 게임을 2개의 핵심 축(예: 난이도 vs 접근성, 서사 깊이 vs 액션 강도)으로 배치하여 설명하세요.

## 관점별 차별점

### 메커닉 차별점
타겟 게임이 경쟁작 대비 독보적인 메커닉 요소 3가지

### 서사/세계관 차별점
타겟 게임의 스토리/설정이 경쟁작과 다른 점

### 감정 경험 차별점
타겟 게임이 유발하는 감정이 경쟁작과 어떻게 다른가

### 타겟 플레이어층 차별점
타겟 게임이 주로 어필하는 플레이어 유형과 경쟁작의 차이

## 포지셔닝 전략
- 타겟 게임의 블루오션 영역 (경쟁작이 채우지 못한 니즈)
- 레드오션 영역 (경쟁이 치열한 요소)
- 기획 관점에서의 시사점 2가지"""


def get_embedding(text: str) -> list[float]:
    """Solar Embedding API로 텍스트 임베딩을 생성한다. 4096차원."""
    resp = client.embeddings.create(
        model="solar-embedding-1-large-passage",
        input=text[:8000],  # 토큰 제한 고려
    )
    return resp.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """코사인 유사도를 계산한다."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def resolve_appid(query: str) -> str:
    """URL, 숫자, 게임 이름에서 app ID를 반환한다."""
    m = re.search(r'/app/(\d+)', query)
    if m:
        return m.group(1)
    if query.strip().isdigit():
        return query.strip()
    r = requests.get(
        "https://store.steampowered.com/api/storesearch",
        params={"term": query, "cc": "US", "l": "english"},
        headers=STEAM_HEADERS,
        timeout=15,
    )
    items = r.json().get("items", [])
    if not items:
        raise ValueError(f"Steam에서 '{query}'를 찾을 수 없습니다.")
    appid = str(items[0]["id"])
    print(f"  검색 결과: {items[0]['name']} (ID: {appid})", file=sys.stderr)
    return appid


def fetch_game_info(query: str) -> dict:
    """Steam API로 게임 기본 정보를 가져온다."""
    appid = resolve_appid(query)
    r = requests.get(
        "https://store.steampowered.com/api/appdetails",
        params={"appids": appid, "cc": "US"},
        headers=STEAM_HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    d = r.json()
    if not d.get(appid, {}).get("success"):
        raise RuntimeError(f"App {appid} 정보 수집 실패")

    data = d[appid]["data"]
    description = re.sub(r'<[^>]+>', ' ', data.get("detailed_description", "") or data.get("short_description", ""))
    description = re.sub(r'\s+', ' ', description).strip()[:3000]

    return {
        "appid": appid,
        "title": data.get("name", ""),
        "developer": ", ".join(data.get("developers", [])),
        "genres": ", ".join(g["description"] for g in data.get("genres", [])),
        "categories": ", ".join(c["description"] for c in data.get("categories", [])[:5]),
        "release_date": data.get("release_date", {}).get("date", ""),
        "metacritic": data.get("metacritic", {}).get("score", "N/A"),
        "recommendations": data.get("recommendations", {}).get("total", 0),
        "description": description,
        "tags": [],  # Steam 태그는 별도 API 필요
    }


def embed_game(game_info: dict) -> list[float]:
    """게임 정보를 임베딩 텍스트로 변환 후 임베딩한다."""
    text = f"""게임: {game_info['title']}
개발사: {game_info['developer']}
장르: {game_info['genres']}
카테고리: {game_info['categories']}
설명: {game_info['description']}"""
    return get_embedding(text)


def qualitative_analysis(target: dict, competitors: list[dict]) -> str:
    """Solar Pro 3로 정성적 차별점을 분석한다."""
    def game_summary(g):
        return f"""### {g['title']}
- 개발사: {g['developer']}
- 장르: {g['genres']}
- Metacritic: {g['metacritic']}
- 추천 수: {g['recommendations']:,}
- 설명: {g['description'][:500]}"""

    content = f"## 타겟 게임\n{game_summary(target)}\n\n## 경쟁작\n"
    content += "\n\n".join(game_summary(c) for c in competitors)

    resp = client.chat.completions.create(
        model="solar-pro3",
        messages=[
            {"role": "system", "content": COMPARE_SYSTEM},
            {"role": "user", "content": content},
            {"role": "assistant", "content": "## 포지셔닝 맵\n\n"},
        ],
        temperature=0.5,
        max_tokens=4096,
    )
    raw = resp.choices[0].message.content
    lines = raw.split("\n")
    for i, line in enumerate(lines):
        if re.search(r'[\uAC00-\uD7A3]', line.strip()):
            return "## 포지셔닝 맵\n\n" + "\n".join(lines[i:])
    return "## 포지셔닝 맵\n\n" + raw


def main():
    parser = argparse.ArgumentParser(description="게임 간 유사도 및 차별점 비교 분석")
    parser.add_argument("--target", required=True, help="분석 대상 게임 (이름/URL/ID)")
    parser.add_argument("--competitors", required=True,
                        help="경쟁작 목록, 쉼표 구분 (예: 'Hades,Dead Cells,Hollow Knight')")
    parser.add_argument("--output", default=None, help="결과 저장 경로 (.json)")
    args = parser.parse_args()

    competitor_list = [c.strip() for c in args.competitors.split(",") if c.strip()]

    # 게임 정보 수집
    print(f"[수집] 타겟: {args.target}", file=sys.stderr)
    target_info = fetch_game_info(args.target)
    print(f"  → {target_info['title']}", file=sys.stderr)

    competitor_infos = []
    for comp in competitor_list:
        print(f"[수집] 경쟁작: {comp}", file=sys.stderr)
        try:
            info = fetch_game_info(comp)
            competitor_infos.append(info)
            print(f"  → {info['title']}", file=sys.stderr)
        except Exception as e:
            print(f"  → 실패: {e}", file=sys.stderr)

    if not competitor_infos:
        print("Error: 경쟁작 정보를 하나도 가져오지 못했습니다.", file=sys.stderr)
        sys.exit(1)

    # 임베딩 생성
    print("[임베딩] Solar Embedding 생성 중...", file=sys.stderr)
    target_emb = embed_game(target_info)
    print(f"  {target_info['title']} 완료", file=sys.stderr)

    similarity_matrix = []
    comp_embeddings = []
    for info in competitor_infos:
        emb = embed_game(info)
        comp_embeddings.append(emb)
        sim = cosine_similarity(target_emb, emb)
        similarity_matrix.append({
            "game": info["title"],
            "similarity": round(sim, 4),
            "similarity_pct": f"{sim*100:.1f}%",
        })
        print(f"  {info['title']} ↔ {target_info['title']}: {sim*100:.1f}%", file=sys.stderr)

    # 유사도 순 정렬
    similarity_matrix.sort(key=lambda x: x["similarity"], reverse=True)

    # 정성 분석
    print("[Solar Pro 3] 차별점 분석 중...", file=sys.stderr)
    analysis = qualitative_analysis(target_info, competitor_infos)
    print("[완료]", file=sys.stderr)

    result = {
        "target": target_info["title"],
        "competitors": [c["title"] for c in competitor_infos],
        "similarity_matrix": similarity_matrix,
        "most_similar": similarity_matrix[0]["game"] if similarity_matrix else None,
        "least_similar": similarity_matrix[-1]["game"] if similarity_matrix else None,
        "qualitative_analysis": analysis,
        "game_details": {
            "target": target_info,
            "competitors": competitor_infos,
        },
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
