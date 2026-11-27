#!/usr/bin/env python3
"""posts/*.md 를 Blogger에 '초안'으로 업로드한다. 업로드한 파일은 posts/.uploaded.json에 기록해 중복을 막는다.

환경변수: BLOGGER_BLOG_ID, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
사용: python upload_blogger.py [--dry-run] [--publish]
"""
import json, os, re, sys, urllib.parse, urllib.request
from pathlib import Path

import markdown  # pip install markdown

POSTS = Path(__file__).parent / "posts"
STATE = POSTS / ".uploaded.json"


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise ValueError(f"front matter 없음: {path.name}")
    meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
    title = meta["title"].strip()
    labels = [x.strip() for x in meta.get("labels", "").split(",") if x.strip()]
    html = markdown.markdown(m.group(2), extensions=["tables"])
    return title, labels, html


def post_json(url, data, headers):
    req = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def access_token():
    body = urllib.parse.urlencode({
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", body)) as r:
        return json.load(r)["access_token"]


def main():
    dry, publish = "--dry-run" in sys.argv, "--publish" in sys.argv
    done = json.loads(STATE.read_text()) if STATE.exists() else {}
    todo = [p for p in sorted(POSTS.glob("*.md")) if p.name not in done]
    if not todo:
        print("업로드할 새 글 없음"); return
    token = None if dry else access_token()
    for p in todo:
        title, labels, html = parse(p)
        if dry:
            print(f"[dry-run] {p.name}: {title} {labels} ({len(html)} bytes)"); continue
        url = f"https://www.googleapis.com/blogger/v3/blogs/{os.environ['BLOGGER_BLOG_ID']}/posts/"
        url += "" if publish else "?isDraft=true"
        res = post_json(url, {"title": title, "content": html, "labels": labels},
                        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        done[p.name] = res.get("url") or res["id"]
        STATE.write_text(json.dumps(done, ensure_ascii=False, indent=2))
        print(f"업로드 완료({'발행' if publish else '초안'}): {p.name} -> {res.get('url', res['id'])}")


if __name__ == "__main__":
    main()
