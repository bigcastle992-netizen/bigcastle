# 나는 SOLO 맛집 → Blogger 자동 업로드

흐름: 예약 작업(`prompt.md`)이 최신 회차 식당을 조사해 `posts/*.md` 작성·커밋 → `upload_blogger.py`가 Blogger에 **초안**으로 업로드 → 직접 검토 후 발행.

## 1회 설정 (본인이 해야 함)
1. Google Cloud Console에서 프로젝트 생성 → **Blogger API v3** 사용 설정
2. OAuth 클라이언트(데스크톱) 생성, 스코프 `https://www.googleapis.com/auth/blogger`로 refresh token 발급
3. 블로그 ID: Blogger 관리 화면 URL의 `blogID=` 값
4. 환경변수 등록: `BLOGGER_BLOG_ID`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (코드/저장소에 넣지 말 것)

## 실행
```bash
pip install -r requirements.txt
python upload_blogger.py --dry-run   # 확인만
python upload_blogger.py             # 초안 업로드
python upload_blogger.py --publish   # 즉시 발행(비권장)
```
