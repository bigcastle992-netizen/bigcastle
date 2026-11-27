#!/usr/bin/env python3
"""구글 타임라인 JSON에서 여행 기간만 잘라 작은 파일로 만듭니다. (Python 3, 추가 설치 없음)

사용 예 (도쿄 + 발리 한 번에):
  python trim_timeline.py 타임라인.json 여행_타임라인.json 2023-04-05:2023-04-10 2024-10-04:2024-10-11

- 입력 파일이 커도 됩니다(메모리 여유 필요, 보통 수백 MB까지 가능).
- 새 형식(semanticSegments)과 옛 형식(timelineObjects) 모두 처리합니다.
- 집/직장 정보(userLocationProfile), 원시 위치 신호(rawSignals)는 결과에서 뺍니다.
- 결과 파일에는 선택한 날짜 구간의 방문·이동 기록만 들어갑니다.
"""
import sys, json
from datetime import datetime, timedelta, timezone

def parse_ranges(args):
    out = []
    for a in args:
        s, e = a.split(":")
        out.append((datetime.fromisoformat(s).replace(tzinfo=timezone.utc) - timedelta(hours=14),
                    datetime.fromisoformat(e).replace(tzinfo=timezone.utc) + timedelta(days=1, hours=14)))
    return out

def ts(v):
    if v is None: return None
    try:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v / 1000 if v > 1e11 else v, timezone.utc)
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None

def inside(t, ranges):
    return t is not None and any(a <= t <= b for a, b in ranges)

def main():
    src, dst, *r = sys.argv[1:]
    ranges = parse_ranges(r)
    data = json.load(open(src, encoding="utf-8"))
    out = {}
    if isinstance(data, dict) and "semanticSegments" in data:      # 새 형식
        keep = []
        for seg in data["semanticSegments"]:
            if inside(ts(seg.get("startTime")), ranges) or inside(ts(seg.get("endTime")), ranges):
                keep.append(seg)
        out["semanticSegments"] = keep
    elif isinstance(data, dict) and "timelineObjects" in data:      # 옛 형식(월별 파일)
        keep = []
        for o in data["timelineObjects"]:
            v = o.get("placeVisit") or o.get("activitySegment") or {}
            d = v.get("duration", {})
            if inside(ts(d.get("startTimestamp") or d.get("startTimestampMs")), ranges):
                keep.append(o)
        out["timelineObjects"] = keep
    elif isinstance(data, list):                                    # 안드로이드 옛 내보내기(리스트)
        out["items"] = [x for x in data if inside(ts(x.get("startTime") or x.get("startTimestamp")), ranges)]
    else:
        raise SystemExit("알 수 없는 형식입니다. 최상위 키: " + ", ".join(list(data.keys())[:10]))
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False)
    n = sum(len(v) for v in out.values())
    print(f"완료: {n}개 기록을 {dst}에 저장했습니다.")

if __name__ == "__main__":
    main()
