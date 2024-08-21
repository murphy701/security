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
  - mobsf 파일을 수정하여 frida 스크립트 삽입
  - environment.py 수정
```
def run_frida_script(self, frida_script_path):
    try:
        subprocess.Popen(['frida', '-U', '-f', 'com.ldjSxw.heBbQd', '-l', frida_script_path])
        logger.info('Frida script injected successfully')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error injecting Frida script: {e}')


def run_frida_server(self):
"""Start Frida Server."""
check = self.adb_command(['ps'], True)
    if b'fd_server' in check:
        logger.info('Frida Server is already running')
        return

    def start_frida():
        fnull = open(os.devnull, 'w')
        argz = [get_adb(),
                '-s',
                self.identifier,
                'shell',
                '/system/fd_server']
        subprocess.call(argz, stdout=fnull, stderr=subprocess.STDOUT)

    trd = threading.Thread(target=start_frida)
    trd.daemon = True
    trd.start()
    logger.info('Starting Frida Server')
    logger.info('Waiting for 2 seconds...')
    time.sleep(2)

    # 프리다 서버가 시작되면 run_frida_script 함수를 호출
    self.run_frida_script(r'C:\Users\owner\Desktop\프로젝트\모바일 샌드박스\anti-vm-bypass.js')
    logger.info('Inject Frida Script')
    logger.info('Waiting for 2 seconds...')
    time.sleep(2)
```
  - dynamic_analyzer.py수정
  - from mobsf.DynamicAnalyzer.views.android.environment import Environment 추가
```
def dynamic_analyzer(request, checksum, api=False):
"""Android Dynamic Analyzer Environment."""
try:
        identifier = None
        activities = None
        exported_activities = None
        if api:
            reinstall = request.POST.get('re_install', '1')
            install = request.POST.get('install', '1')
        else:
            reinstall = request.GET.get('re_install', '1')
            install = request.GET.get('install', '1')
        if not is_md5(checksum):
            # We need this check since checksum is not validated
            # in REST API
            return print_n_send_error_response(
                request,
                'Invalid Hash',
                api)
        package = get_package_name(checksum)
        if not package:
            return print_n_send_error_response(
                request,
                'Cannot get package name from checksum',
                api)
        logger.info('Creating Dynamic Analysis Environment for %s', package)
        try:
            identifier = get_device()
        except Exception:
            return print_n_send_error_response(
                request, get_android_dm_exception_msg(), api)

        # Get activities from the static analyzer results
        try:
            static_android_db = StaticAnalyzerAndroid.objects.get(
                MD5=checksum)
            exported_activities = python_list(
                static_android_db.EXPORTED_ACTIVITIES)
            activities = python_list(
                static_android_db.ACTIVITIES)
        except ObjectDoesNotExist:
            logger.warning(
                'Failed to get Activities. '
                'Static Analysis not completed for the app.')
        env = Environment(identifier)
        if not env.connect_n_mount():
            msg = 'Cannot Connect to ' + identifier
            return print_n_send_error_response(request, msg, api)
        version = env.get_android_version()
        logger.info('Android Version identified as %s', version)
        xposed_first_run = False
        if not env.is_mobsfyied(version):
            msg = ('This Android instance is not MobSFyed/Outdated.\n'
                   'MobSFying the android runtime environment')
            logger.warning(msg)
            if not env.mobsfy_init():
                return print_n_send_error_response(
                    request,
                    'Failed to MobSFy the instance',
                    api)
            if version < 5:
                # Start Clipboard monitor
                env.start_clipmon()
                xposed_first_run = True
        if xposed_first_run:
            msg = ('Have you MobSFyed the instance before'
                   ' attempting Dynamic Analysis?'
                   ' Install Framework for Xposed.'
                   ' Restart the device and enable'
                   ' all Xposed modules. And finally'
                   ' restart the device once again.')
            return print_n_send_error_response(request, msg, api)
        # Clean up previous analysis
        env.dz_cleanup(checksum)
        # Configure Web Proxy
        env.configure_proxy(package, request)
        # Supported in Android 5+
        env.enable_adb_reverse_tcp(version)
        # Apply Global Proxy to device
        env.set_global_proxy(version)
        if install == '1':
            # Install APK
            apk_path = Path(settings.UPLD_DIR) / checksum / f'{checksum}.apk'
            status, output = env.install_apk(
                apk_path.as_posix(),
                package,
                reinstall)
            if not status:
                # Unset Proxy
                env.unset_global_proxy()
                msg = (f'This APK cannot be installed. Is this APK '
                       f'compatible the Android VM/Emulator?\n{output}')
                return print_n_send_error_response(
                    request,
                    msg,
                    api)
        env_instance.run_frida_server() #안되면 삭제 바람
        logger.info('Testing Environment is Ready!')
        context = {'package': package,
                   'hash': checksum,
                   'android_version': version,
                   'version': settings.MOBSF_VER,
                   'activities': activities,
                   'exported_activities': exported_activities,
                   'title': 'Dynamic Analyzer'}
        template = 'dynamic_analysis/android/dynamic_analyzer.html'
```

### MobSF를 이용한 앱 정적/동적 분석 결과 확인
- 앱 업로드 -> 정적 분석 결과
- 에뮬레이터 실행 -> 동적 분석 결과

### API 커스터마이징을 통한 분석 자동화
- API: https://mobsf.live/api_docs
- API 사용 예시: https://gist.github.com/ajinabraham/0f5de3b0c7b7d3665e54740b9f536d81
![initial](https://github.com/user-attachments/assets/94125968-dc90-4922-ab93-e3c11a5c07d4)
- apk 업로드&정적&동적&pdf 분석 실행 코드(자동화된 코드 합치기 필요, frida 우회 등 기능 추가 필요함)
```
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import pdfkit
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

SERVER = "http://localhost:8000"
FILE = "APK 파일 경로"
APIKEY = 'API key'


def upload():
    """Upload File"""
    print("Uploading file")
    multipart_data = MultipartEncoder(fields={'file': (FILE, open(FILE, 'rb'), 'application/octet-stream')})
    headers = {'Content-Type': multipart_data.content_type, 'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/upload', data=multipart_data, headers=headers)
    return response.text


def scan(data):
    """Scan the file"""
    print("Scanning file")
    post_dict = json.loads(data)
    headers = {'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/scan', data=post_dict, headers=headers)

def dynamic_analysis(data):
    print("Starting Dynamic Analysis")
    post_dict = json.loads(data)
    headers = {'Authorization': APIKEY}
    response = requests.post(SERVER + '/api/v1/dynamic/start_analysis', data=post_dict, headers=headers)

def static_pdf(data):
    """Generate PDF Report"""
    print("Generate Static PDF report")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    url = "http://127.0.0.1:8000/static_analyzer/"+hash_value+"/"
    pdfkit.from_url(url, output_path = 'C:/Users/82107/Downloads/static.pdf', configuration=config)
    print("Report saved as static.pdf")

def dynamic_pdf(data):
    """Generate PDF Report"""
    print("Generate Dynamic PDF report")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    url = f"http://127.0.0.1:8000/dynamic_report/"+hash_value
    pdfkit.from_url(url, output_path = 'C:/Users/82107/Downloads/dynamic.pdf', configuration=config)
    print("Report saved as dynamic.pdf")


def json_resp(data):
    """Generate JSON Report"""
    print("Generate JSON report")
    headers = {'Authorization': APIKEY}
    data = {"hash": json.loads(data)["hash"]}
    response = requests.post(SERVER + '/api/v1/report_json', data=data, headers=headers)


def delete(data):
    """Delete Scan Result"""
    print("Deleting Scan")
    headers = {'Authorization': APIKEY}
    data = {"hash": json.loads(data)["hash"]}
    response = requests.post(SERVER + '/api/v1/delete_scan', data=data, headers=headers)
    print(response.text)


def mobsfy():
    """MobSFy the Environment"""
    print("MobSFy environment")
    headers = {'Authorization': APIKEY}
    identifier = "192.168.56.101:5555"
    response = requests.post(SERVER + '/api/v1/android/mobsfy', data={'identifier': identifier}, headers=headers)
    print(response.text)


def tls_tests(data):
    """Run TLS/SSL Security Tests"""
    print("Running TLS/SSL security tests")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    response = requests.post(SERVER + '/api/v1/android/tls_tests', data={'hash': hash_value}, headers=headers)
    with open("tls_tests.json", 'w') as tls_file:
        json.dump(response.json(), tls_file)
    print("TLS/SSL security tests saved as tls_tests.json")


def start_activity(data):
    """Start Activity or Exported Activity"""
    print("Starting activity")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    activity_name = "com.ldjSxw.heBbQd.MainActivity"  # Replace with the actual activity name
    response = requests.post(SERVER + '/api/v1/android/start_activity', data={'hash': hash_value, 'activity': activity_name}, headers=headers)
    print(response.text)


def frida_get_dependencies(data):
    """Frida Get Runtime Dependencies"""
    print("Getting Frida runtime dependencies")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    response = requests.post(SERVER + '/api/v1/frida/get_dependencies', data={'hash': hash_value}, headers=headers)
    with open("frida_dependencies.json", 'w') as frida_file:
        json.dump(response.json(), frida_file)
    print("Frida runtime dependencies saved as frida_dependencies.json")


def frida_view_logs(data):
    """View Frida Logs"""
    print("Viewing Frida logs")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    response = requests.post(SERVER + '/api/v1/frida/logs', data={'hash': hash_value}, headers=headers)
    with open("frida_logs.json", 'w') as frida_logs_file:
        json.dump(response.json(), frida_logs_file)
    print("Frida logs saved as frida_logs.json")


def stop_dynamic_analysis(data):
    """Stop Dynamic Analysis"""
    print("Stopping dynamic analysis")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    response = requests.post(SERVER + '/api/v1/dynamic/stop_analysis', data={'hash': hash_value}, headers=headers)
    print(response.text)


def dynamic_analysis_report_json(data):
    """Generate Dynamic Analysis JSON Report"""
    print("Generating Dynamic Analysis JSON report")
    headers = {'Authorization': APIKEY}
    hash_value = json.loads(data)["hash"]
    response = requests.post(SERVER + '/api/v1/dynamic/report_json', data={'hash': hash_value}, headers=headers)
    with open("dynamic_analysis_report.json", 'w') as report_file:
        json.dump(response.json(), report_file)
    print("Dynamic analysis JSON report saved as dynamic_analysis_report.json")


# Existing process
RESP = upload()
scan(RESP)
static_pdf(RESP)
dynamic_analysis(RESP)

mobsfy()
tls_tests(RESP)
start_activity(RESP)
frida_get_dependencies(RESP)
frida_view_logs(RESP)
stop_dynamic_analysis(RESP)
dynamic_analysis_report_json(RESP)
dynamic_pdf(RESP)
json_resp(RESP)

delete(RESP)
```
- API로 MobSF 컨트롤
  - APK <--> API <--> MobSF <--> Emulator
  - file 업로드 이후 user interaction이 없어야 함

### 결론
- 에뮬레이터에서 앱이 실행됨
- 위의 과정 없이는 앱이 vm에서 실행되지 않기 때문에 분석을 할 수 없었지만 해당 과정을 통해 해결할 수 있다.
