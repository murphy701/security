- nids 작동 방식
- 패킷 기반
- 장점
  - 실시간 데이터 분석 가능
  - 세부 정보를 포함하기 때문에 미묘한 패턴을 감지 가능
- 단점
  - 데이터 양이 많음
  - 데이터 전처리가 복잡함
- 로그 기반
- 장점
  - 구조화된 데이터로 되어 있어 전처리에 용이
  - 저렴한 저장, 처리
- 단점
  - 실시간 데이터 분석 할 시 탐지 지연될 수도 있음
  - 제한된 정보: 네트워크 트래픽의 일부 정보만 있어 모든 공격 탐지가 어려울 수도 있음
- 웹 서버
- nids를 테스트 하려면 여러 기능이 있어야 함
  - 로그인 기능
  - db 연동
  - 게시판
  - 외부에서 접속할 수 있는 기능
  - https
### 도커 인프라 구축
- 도커 설치
  - docker desktop
- docker compose
  - 여러 컨테이너를 관리해 주는 프로그램
  - docker desktop 설치 시 자동으로 설치 됨
- 실행이 되지 않을 경우 다음과 같은 해결책 사용
```
powershell 관리자 권한으로 실행
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    virtual machine platform 설치 명령
 dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
 windows subsystem for linux 기능 활성화
 wsl --install
 wsl --set-default-version 2
 그 외에 오류는 검색으로 해결하기
```
- docker compose 사용 방법
  - docker-compose.yml 파일을 생성하여 컨테이너에 빌드할 설정을 기술
  - 이후 docker-compose up -d나 docker-compose up -d --build로 실행

https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/NIDS_AI/nids.zip
- 해당 파일로 nids가 실행되는 컨테이너, 웹서버와 관련된 3개의 컨테이너를 생성
- docker-compose로 실행 시 docker-compose.yml파일과 dockerfile의 내용에 따라 capture.sh가 자동으로 실행되어 패킷을 캡처

### 알게 된 점
- 모듈 설치가 안 될 경우 내부에 직접 접속해서 설치해 보는 것이 빠르다
  - docker-php-ext-install mysqli(컨테이너 내부 접속)
- 버전 빌드
  - .yml 파일 사용 시 dockerfile보다 우선시 되므로 특정 버전을 설치하고 싶을 경우 yml 파일의 빌드 부분을 다음과 같이 처리
```
build: .
```
