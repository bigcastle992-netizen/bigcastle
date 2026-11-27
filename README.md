# 예약 작업 모음

## 미장 마감 요약 + 국장 관심 종목
- 폴더: `stock-briefing/`
- 프롬프트: `stock-briefing/prompt.md`
- 스케줄: 평일(월~금) 08:40 KST (`CRON_TZ=Asia/Seoul 40 8 * * 1-5`)
- 모델: claude-sonnet-5-5
- 알림: 푸시 켜짐, 이메일 꺼짐

다른 PC에서는 이 프롬프트를 복사해 같은 스케줄로 예약 작업을 만들면 됩니다.

## Blogger 자동 게시 (선택)
- 스크립트: `stock-briefing/post_to_blogger.py`
- 1회 설정(본인): Google Cloud에서 Blogger API v3 사용 설정 → OAuth 클라이언트(데스크톱) 생성 →
  스코프 `https://www.googleapis.com/auth/blogger` 로 refresh token 발급 → 블로그 ID(`blogID=` 값) 확인
- 환경변수: `BLOGGER_BLOG_ID`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`
  (환경 설정에만 등록, 코드/저장소에 넣지 말 것)
- 테스트: `python3 stock-briefing/post_to_blogger.py --title "테스트" --file x.html --draft`
