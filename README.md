# 예약 작업 모음

## 미장 마감 요약 + 국장 관심 종목
- 폴더: `stock-briefing/`
- 프롬프트: `stock-briefing/prompt.md`
- 스케줄: 평일(월~금) 08:40 KST (`CRON_TZ=Asia/Seoul 40 8 * * 1-5`)
- 모델: claude-sonnet-5-5
- 알림: 푸시 켜짐, 이메일 꺼짐

다른 PC에서는 이 프롬프트를 복사해 같은 스케줄로 예약 작업을 만들면 됩니다.

## 나는 SOLO 맛집 블로그 자동 업로드
- 폴더: `solo-blog/` (설정 방법은 `solo-blog/README.md`)
- 매주 방송 회차 식당 조사 → 마크다운 → Blogger 초안 업로드
