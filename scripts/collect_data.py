#!/usr/bin/env python3
"""수집된 게임 관련 raw 데이터를 구조화된 game_info.json으로 변환합니다."""
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

EXTRACT_SYSTEM = """IMPORTANT: You MUST respond in Korean only. ALL values in the JSON must be written in Korean. Output JSON only — no other text.
IMPORTANT: 반드시 한국어로만 답변하세요. JSON 내 모든 값은 반드시 한국어로 작성하세요. JSON만 출력하세요. 다른 텍스트는 일절 출력하지 마세요.

당신은 게임 정보 구조화 전문가입니다.
주어진 텍스트에서 게임 기획 분석에 필요한 정보를 추출하여 아래 JSON 형식으로 정확히 출력하세요.
정보가 없으면 빈 문자열 "" 또는 빈 배열 []로 채우세요.

{
  "title": "게임 제목",
  "developer": "개발사",
  "publisher": "퍼블리셔",
  "genre": "장르",
  "platform": "플랫폼 (PC, Switch, PS5 등)",
  "release": "출시일",
  "metacritic_score": "메타크리틱 점수",
  "total_reviews": "총 리뷰 수",
  "steam_url": "Steam 링크",
  "core_concept": "핵심 컨셉 한 문장",
  "core_mechanics": ["핵심 메커닉 1", "핵심 메커닉 2"],
  "story": "스토리 요약",
  "aesthetics": "미학적 특성 (아트 스타일, 사운드 등)",
  "progression": ["성장/진행 시스템 1", "성장/진행 시스템 2"],
  "target_audience": "타겟 유저층",
  "differentiators": ["차별화 포인트 1", "차별화 포인트 2"],
  "description": "전체 게임 설명"
}"""


def collect_from_steam(query: str) -> dict:
    """Steam API에서 게임 정보를 수집한다."""
    # app ID 해석
    m = re.search(r'/app/(\d+)', query)
    if m:
        appid = m.group(1)
    elif query.strip().isdigit():
        appid = query.strip()
    else:
        r = requests.get(
            "https://store.steampowered.com/api/storesearch",
            params={"term": query, "cc": "US", "l": "english"},
            headers=STEAM_HEADERS, timeout=15,
        )
        items = r.json().get("items", [])
        if not items:
            raise ValueError(f"Steam에서 '{query}'를 찾을 수 없습니다.")
        appid = str(items[0]["id"])
        print(f"  검색 결과: {items[0]['name']} (ID: {appid})", file=sys.stderr)

    r = requests.get(
        "https://store.steampowered.com/api/appdetails",
        params={"appids": appid, "cc": "US"},
        headers=STEAM_HEADERS, timeout=15,
    )
    r.raise_for_status()
    d = r.json()
    if not d.get(appid, {}).get("success"):
        raise RuntimeError(f"App {appid} 정보 수집 실패")

    data = d[appid]["data"]
    description = re.sub(r'<[^>]+>', ' ', data.get("detailed_description", "") or data.get("short_description", ""))
    description = re.sub(r'\s+', ' ', description).strip()

    raw = {
        "title": data.get("name", ""),
        "developer": ", ".join(data.get("developers", [])),
        "publisher": ", ".join(data.get("publishers", [])),
        "genre": ", ".join(g["description"] for g in data.get("genres", [])),
        "platform": ", ".join(k for k, v in data.get("platforms", {}).items() if v),
        "release": data.get("release_date", {}).get("date", ""),
        "metacritic_score": str(data.get("metacritic", {}).get("score", "")),
        "total_reviews": str(data.get("recommendations", {}).get("total", "")),
        "steam_url": f"https://store.steampowered.com/app/{appid}/",
        "description": description[:3000],
    }
    return raw


def _try_parse_json(raw: str) -> dict | None:
    """다양한 방법으로 JSON 파싱을 시도한다. 실패 시 None 반환."""
    # 마크다운 코드블록 제거
    raw = re.sub(r'```json\s*', '', raw)
    raw = re.sub(r'```\s*', '', raw)

    # 첫 { 에서 마지막 } 사이만 추출
    start = raw.find('{')
    end = raw.rfind('}')
    if start == -1 or end == -1:
        return None
    candidate = raw[start:end+1]

    # 1차 시도: 그대로
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 2차 시도: 후행 콤마 제거 (JSON5 스타일 오류)
    fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # 3차 시도: 마지막 완전한 키-값 쌍까지만 자르기
    # (모델이 max_tokens에서 잘린 경우)
    for brace_end in range(len(candidate) - 1, -1, -1):
        if candidate[brace_end] == '}':
            try:
                return json.loads(candidate[:brace_end+1])
            except json.JSONDecodeError:
                continue
    return None


def extract_with_solar(raw_text: str) -> dict:
    """Solar Pro 3로 raw 텍스트에서 구조화된 게임 정보를 추출한다."""
    for attempt in range(2):
        temp = 0.1 if attempt == 1 else 0.2
        resp = client.chat.completions.create(
            model="solar-pro3",
            messages=[
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": f"다음 텍스트에서 게임 정보를 추출하세요:\n\n{raw_text[:8000]}"},
                {"role": "assistant", "content": "{"},
            ],
            temperature=temp,
            max_tokens=2048,
        )
        content = resp.choices[0].message.content
        # Solar Pro 3가 이미 { 를 포함하면 그대로, 아니면 prepend
        raw = content if content.lstrip().startswith("{") else "{" + content
        result = _try_parse_json(raw)
        if result:
            return result
        if attempt == 0:
            print("[경고] JSON 파싱 1차 실패, 재시도...", file=sys.stderr)

    # 최종 실패 시 Steam description만 보존
    print("[경고] JSON 파싱 최종 실패, Steam 기본 데이터만 사용합니다.", file=sys.stderr)
    return {"description": raw_text, "title": "Unknown"}


def merge_steam_with_solar(steam_data: dict, solar_data: dict) -> dict:
    """Steam API 데이터와 Solar 추출 데이터를 병합한다. Steam 수치 데이터 우선."""
    merged = {**solar_data}  # Solar 데이터 기반
    # Steam의 수치/정확한 데이터로 덮어쓰기
    for key in ["title", "developer", "publisher", "genre", "platform",
                "release", "metacritic_score", "total_reviews", "steam_url"]:
        if steam_data.get(key):
            merged[key] = steam_data[key]
    # description은 Steam 것이 더 완전함
    if steam_data.get("description"):
        merged["description"] = steam_data["description"]
    return merged


def main():
    parser = argparse.ArgumentParser(description="게임 데이터 수집 및 구조화")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--steam", help="Steam URL, App ID, 또는 게임 이름")
    source.add_argument("--input", help="raw 텍스트 파일 경로 (기획서, 웹 수집 텍스트 등)")
    parser.add_argument("--output", default=None, help="결과 저장 경로 (.json)")
    parser.add_argument("--no-solar", action="store_true",
                        help="Solar 추출 건너뜀 (Steam 데이터만 사용)")
    args = parser.parse_args()

    if args.steam:
        print(f"[Steam] '{args.steam}' 정보 수집 중...", file=sys.stderr)
        steam_data = collect_from_steam(args.steam)
        print(f"  → {steam_data['title']} 수집 완료", file=sys.stderr)

        if args.no_solar:
            result = steam_data
        else:
            print("[Solar Pro 3] 구조화 분석 중...", file=sys.stderr)
            solar_data = extract_with_solar(steam_data["description"])
            result = merge_steam_with_solar(steam_data, solar_data)
            print("[완료]", file=sys.stderr)

    else:
        with open(args.input, "r", encoding="utf-8") as f:
            raw_text = f.read()
        print(f"[파일] {args.input} 로드 완료 ({len(raw_text)}자)", file=sys.stderr)
        print("[Solar Pro 3] 구조화 추출 중...", file=sys.stderr)
        result = extract_with_solar(raw_text)
        print("[완료]", file=sys.stderr)

    output_str = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"[저장] {args.output}", file=sys.stderr)
    else:
        print(output_str)


if __name__ == "__main__":
    main()
