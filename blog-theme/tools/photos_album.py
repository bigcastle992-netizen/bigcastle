#!/usr/bin/env python3
"""Google Photos 공유 앨범 -> 사진 목록(items.json), 썸네일, 번호 붙은 컨택트시트 생성.
사용: python3 photos_album.py <앨범링크> <작업폴더> [UTC오프셋시간(기본 9=도쿄/서울)]
"""
import sys, re, json, os, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def fetch(url, out):
    for _ in range(6):
        r = subprocess.run(["curl", "-s", "-m", "40", "-L", "-A", UA, "-o", out, "-w", "%{http_code} %{url_effective}", url], capture_output=True, text=True)
        if r.stdout.startswith("200"):
            return r.stdout
    raise SystemExit("앨범을 열지 못했습니다: " + r.stdout)

def parse(html):
    pat = re.compile(r'\["(AF1Qip[A-Za-z0-9_\-]+)",\["(https://lh3\.googleusercontent\.com/pw/[A-Za-z0-9_\-]+)",(\d+),(\d+)')
    items = {}
    for m in pat.finditer(html):
        pid, url, w, h = m.groups()
        tail = html[m.end():m.end() + 400]
        t = re.search(r',(\d{13}),', tail)
        items[pid] = dict(id=pid, url=url, w=int(w), h=int(h), ts=int(t.group(1)) if t else None)
    return sorted(items.values(), key=lambda x: x["ts"] or 0)

def main():
    link, work = sys.argv[1], sys.argv[2]
    off = int(sys.argv[3]) if len(sys.argv) > 3 else 9
    os.makedirs(work + "/thumbs", exist_ok=True)
    final = fetch(link, work + "/album.html")
    html = open(work + "/album.html", encoding="utf-8", errors="ignore").read()
    title = re.findall(r"<title>(.*?)</title>", html, re.S)
    items = parse(html)
    json.dump(items, open(work + "/items.json", "w"), ensure_ascii=False)
    print("title:", title[:1], "items:", len(items), "final:", final)

    def dl(i):
        subprocess.run(["curl", "-s", "-m", "40", "-A", UA, "-o", f"{work}/thumbs/{i:03d}.jpg", items[i]["url"] + "=w360"])
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(dl, range(len(items))))

    cols, rows, cell = 6, 5, 200
    per = cols * rows
    for s in range((len(items) + per - 1) // per):
        sheet = Image.new("RGB", (cols * cell, rows * (cell + 14)), (30, 30, 30))
        d = ImageDraw.Draw(sheet)
        for k in range(per):
            i = s * per + k
            if i >= len(items): break
            try:
                im = Image.open(f"{work}/thumbs/{i:03d}.jpg").convert("RGB")
            except Exception:
                continue
            im.thumbnail((cell, cell))
            x, y = (k % cols) * cell, (k // cols) * (cell + 14)
            sheet.paste(im, (x + (cell - im.width) // 2, y + 14 + (cell - im.height) // 2))
            ts = items[i]["ts"]
            t = (datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc) + datetime.timedelta(hours=off)) if ts else None
            d.text((x + 3, y + 1), f"#{i:03d} {t.strftime('%m/%d %H:%M') if t else ''}", fill=(255, 255, 0))
        sheet.save(f"{work}/sheet_{s:02d}.jpg", quality=80)
    print("sheets:", (len(items) + per - 1) // per)

if __name__ == "__main__":
    main()
