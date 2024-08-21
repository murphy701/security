### 기획
- 기간 2024.05.13 ~ 2024.05.27

### MOBSF 구조의 이해
- 설정 파일(config.py)
- 소스코드 / 메타데이터 저장소 분리
- 정적 / 동적 분석 모듈 구조 / 호출 관계 파악
- api 구조 및 사용법 이해
- 에뮬레이터 연동

### 암호화된 DEX 파일이 포함된 APK 분석 시 대시보드에 해당 DEX에 대한 정보 제공 방법
- DEX 파일
  - Dex에는 Android 런타임에서 궁극적으로 실행되는 코드가 기계어 상태로 포함 되어 있고 이것을 디컴파일 하면 smail 코드가 됨
- 앱 리패키징 -> apktool(opensource)
- pycryptodome 파이브러리 사용
- 파일 복호화 방법
  - 알고리즘: aes-128/ecb
  - key:dbcdcfghijklmaop

<details>
  <summary>dex파일 복호화 & 리패키징 후 MobSF 자동 분석 요청 로직</summary><br>
(https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/mobSF/DEX.py)<br>
decrypt_file(input file, output_file):<br>
  -주어진 input_file의 데이터를 aes-128/ecb 방식으로 암호화된 키를 이용하여 복호화<br>
  -결과를 output_file에 저장:<br>
unzip_apk(apk_path, extract_to):<br>
  -주어진 apk파일을 압축 해제하여 지정된 디렉토리에 추출<br>
zip_apk(apk_path, encrypted_dex_filename):<br>
  -주어진 디렉터리를 재귀적으로 탐색하여 파일을 압축하여 새로운 zip파일(output_path)을 생성<br>
process_apk(apk_path, encrypted_dex_filename):<br>
  -주어진 apk파일을 처리, 먼저 apk파일을 압축 해제하고 암호화된 dex파일을 찾음<br>
  -해당 dex파일을 복호화하고 수정된 apk파일을 다시 패키징하여 최종적으로 재패키징 된 apk파일을 생성<br>
</details>

### 에뮬레이터 연동 및 탐지 우회
- 설정 파일 내 에뮬레이터 정보 기입
  - genymotion 사용, x86 안드로이드 9.0v(arm translation tool 설치)
    - 동적 분석 환경설정 시연:![2024-05-22 17-07-19 (1)](https://github.com/user-attachments/assets/f6a58b0c-01e3-4e6e-ba35-e30dad90b09d)
- MobSF로 에뮬레이터/앱 컨트롤
- 에뮬레이터 탐지 우회(frida/non-frida)
  - (https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/mobSF/frida.md)
 
### 결론
- 에뮬레이터에서 앱이 실행됨
- 위의 과정 없이는 앱이 vm에서 실행되지 않기 때문에 분석을 할 수 없었지만 해당 과정을 통해 해결할 수 있다.
