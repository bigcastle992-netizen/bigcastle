#!/usr/bin/env python3
"""브리핑(HTML 또는 텍스트)을 Blogger에 게시한다.

필요 환경변수 (코드/저장소에 넣지 말 것):
  BLOGGER_BLOG_ID, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN

사용:
  python3 post_to_blogger.py --title "제목" --file briefing.html [--draft] [--labels 미장,국장]
  (--file 생략 시 stdin에서 본문을 읽음)
"""
import argparse
import html
import json
import os
import sys
import urllib.parse
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
POSTS_URL = "https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"


def env(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"환경변수 {name} 가 설정되지 않았습니다.")
    return v


def access_token():
    data = urllib.parse.urlencode({
        "client_id": env("GOOGLE_CLIENT_ID"),
        "client_secret": env("GOOGLE_CLIENT_SECRET"),
        "refresh_token": env("GOOGLE_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data)) as r:
        return json.load(r)["access_token"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--file")
    ap.add_argument("--draft", action="store_true", help="공개하지 않고 초안으로 저장")
    ap.add_argument("--labels", default="")
    a = ap.parse_args()

    body = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    # HTML 태그가 없으면 일반 텍스트로 보고 이스케이프 + 줄바꿈 처리
    if "<" not in body:
        body = html.escape(body).replace("\n", "<br>\n")

    payload = {"kind": "blogger#post", "title": a.title, "content": body}
    if a.labels:
        payload["labels"] = [s.strip() for s in a.labels.split(",") if s.strip()]

    url = POSTS_URL.format(blog_id=env("BLOGGER_BLOG_ID"))
    if a.draft:
        url += "?isDraft=true"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {access_token()}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        print(json.load(r).get("url", "(게시됨)"))


if __name__ == "__main__":
    main()
