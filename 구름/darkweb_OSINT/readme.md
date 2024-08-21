### 기획
- 기간 2024.06.01 ~ 2024.06.11
- 크롤링 사이트 선정: play뉴스, 빙안리안, 블랙 수트
- 최종 선정: play뉴스
- 업무분담
> |                    Name                    |  맡은 부분  |
> | :----------------------------------------: | :---------: |
> | 안대현 | 크롤링 로직 구현 |
> | 양성혁 | 파싱 로직 구현 |
> | 이지원 | alert 로직 구현 |
> | 이효원 | db 연동 |
### DAY 1
- OSINT 기반 다크웹 유출 정보 알림 시스템 개발을 위한 사전 리서치
- 비슷한 서비스를 제공하는 시스템 사전 조사(s2w lab, nshc, 쿤텍, 제로 다크웹)
(https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/darkweb_OSINT/darkweb_report.md)
- 다크 웹의 작동 방식
  - 다크웹에 접근
    - tor, I2P
  - 익명성과 프라이버시
    - onion 라우팅
    - garlic 라우팅
  - 콘텐츠 유형
    - 마켓플레이스: 약물, 무기, 위조 통화와 같은 불법 상품을 거래
    - 포럼과 커뮤니티: 합법적이거나 불법적인 다양한 주제를 논의하는 암호화된 포럼
    - Whistleblowing 플랫폼: SecureDrop과 같은 사이트는 고발자가 기자와 정보를 공유하는 데 안전하고 익명의 채널을 제공한다.
  - 결제 시스템
    - 암호화폐
  - 보안과 위험
    -  법 집행
    -  사기와 사기 행위
    -  악성 소프트웨어 및 익스플로잇
- 다크웹 에서 거래되는 정보의 종류
  - 개인 정보, 금융 정보, 의료 정보, 로그인 관련 데이터, 신용카드 정보, 계좌 번호와 비밀번호
### DAY2~3
![initial](https://github.com/user-attachments/assets/cfd2bbe9-08b3-4291-a6c8-34d7f8a18fbb)
### DAY4~7
- 다크 웹 사이트 구조 분석 후 알림 시스템 개발
### DAY 8~10
- 중간 점검 및 피드백, 수정 후 최종 점검
- (https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/darkweb_OSINT/darkweb.py)
  - 크롤러, 파서, db를 취합한 코드
- (https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/darkweb_OSINT/discord.py)
  - 알림을 디스코드로 보내는 봇을 만들었고 동작은 하나, 취합 코드의 버그로 기능 x
  - while True문의 동기 함수와 디스코드 봇의 비동기 함수가 양립할 수 없는 문제로 파악됨
