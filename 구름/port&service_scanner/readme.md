### 기획
  - 기간 2024.05.02 ~ 2024.05.13
  - 프로젝트 계획 수립
    - 이론 정리, syn스캐너 구현, 포트 스캐너 구현, 서비스 스캐너 구현, 프로토콜 별 서비스 이해
  - 업무 분담
> |                    Name                    |  맡은 부분  |  구현한 프로그램 |
> | :----------------------------------------: | :---------: | :-------------:|
> | 안대현 | DB, 보고서 | db_scan.py|
> | 양성혁 | ssh, dns | scan.py |
> | 이지원 | ftp, smtp | ftp_smtp_scan.py |
> | 이효원 | http, https | http_scan.py |
  - 산출물 확정: 서비스 포트 스캐너
  - 아이디어: gui버전, ip 바꿔가며 스캔, 스캔 속도 조절, aws에서 사용 가능한 스캐너

  ### 실행
  - 단계 별 프로세스
    - 프로젝트 목표 설정 및 이론 정리
    - tcp/ip 프로토콜 이해, 멀티스레딩 이해
    - 스캐너 구현
    - 내용 취합 및 구현, 신규 기능 설계
    - 피드백 및 보고서 작성

### 최종 점검
- db_scan.py
  - 서비스 검증 로직에 문제가 있어 3306 mysql 포트가 unknwon으로 표시됨
<details>
<summary>final.py의 각 함수 내용</summary>
  1. port_scan(target, port): 주어진 대상 IP 주소와 포트에 대해 TCP 연결을 시도하여 포트가 열려 있는지 확인한다. 만약 포트가 열려 있다면 해당 포트를 반환한다.<br>
  2. service_scan(target, port): 주어진 대상 IP 주소와 포트에 대해 서비스를 스캔한다. 주어진 포트에 어떤 서비스가 열려 있는지 확인하고, 서비스를 식별하여 해당 서비스와 포트 번호를 반환한다.<br>
  3. check_ssh(target, port): SSH 서비스가 열려 있는지 확인한다. SSH 서비스는 소켓 연결을 통해 banner를 받고, 그 안에 'SSH' 문자열이 포함되어 있는지 확인한다.<br>
  4. check_dns(target, port): DNS 서비스가 열려 있는지 확인한다. DNS 쿼리를 보내 정상적인 응답을 받는지 확인한다.<br>
  5. check_ftp(target, port): FTP 서비스가 열려 있는지 확인한다. FTP 서버와 연결을 시도하고, 초기 응답 및 SYST 명령어에 대한 응답을 확인하여 FTP 서비스 여부를 판별한다.<br>
  6. check_smtp(target, port): SMTP 서비스가 열려 있는지 확인한다. SMTP 서버와 연결을 시도하고, 초기 응답 및 HELO 명령어에 대한 응답을 확인하여 SMTP 서비스 여부를 판별한다.<br>
  7. check_mysql(target, port): MySQL 서비스가 열려 있는지 확인한다. MySQL 커넥터를 사용하여 연결을 시도하고, 연결이 성공하는지 확인하여 MySQL 서비스 여부를 판별한다.<br>
  8. check_postgresql(target, port): PostgreSQL 서비스가 열려 있는지 확인한다. psycopg2를 사용하여 연결을 시도하고, 연결이 성공하는지 확인하여 PostgreSQL 서비스 여부를 판별한다.<br>
  9. check_mongodb(target, port): MongoDB 서비스가 열려 있는지 확인한다. MongoClient를 사용하여 연결을 시도하고, 연결이 성공하는지 확인하여 MongoDB 서비스 여부를 판별한다.<br>
  10 .check_http(target, port): HTTP 서비스가 열려 있는지 확인한다. 소켓을 생성하여 HTTP GET 요청을 보내고, 응답이 '200 OK'인지 확인하여 HTTP 서비스 여부를 판별한다.<br>
  11 .check_https(target, port): HTTPS 서비스가 열려 있는지 확인한다. 소켓을 생성하여 HTTPS GET 요청을 보내고, 응답이 '400 Bad Request'인지 확인하여 HTTPS 서비스 여부를 판별한다.<br>
  12 .main(): 사용자로부터 대상 IP 주소를 입력받고, 주어진 범위 내의 모든 포트에 대해 포트 스캔을 시작한다. 열린 포트를 찾으면 해당 포트를 출력하고, 그 후에 각 포트에 대해 서비스 스캔을 시작한다. 열린 서비스를 찾으면 서비스와 포트를 출력한다.
</details>

 - 구현 결과
   - 포트 스캔 후 열린 포트에 대한 배너그래빙 혹은 직접 연결을 시도해 서비스를 판별하는 로직으로 작성함, 효율적인 동작을 위해 멀티스레드를 활용한 병렬 작업을 진행
   - 이외에도 os detection, 네트워크 매핑(smtp) 등 구현과는 별개로 추가 아이디어를 제시 함 
### 추가 기능
- OS detection
  - 타겟의 os 등을 스캐닝을 통해 알아내는 기능, ttl, window_size를 통해 os를 유추한다.
<br>

```from scapy.all import IP, TCP, sr1

def detect_os(ip):
    # Define the target IP and port
    port = 80  # Common open port; adjust as necessary
    
    # Construct the SYN packet
    syn_packet = IP(dst=ip)/TCP(dport=port, flags="S")
    
    # Send the SYN packet and wait for one response
    response = sr1(syn_packet, timeout=1, verbose=0)
    
    if response is None:
        print("No response received.")
        return
    
    # Extract fields from the response
    ttl = response[IP].ttl
    window_size = response[TCP].window
    options = response[TCP].options
    
    # Determine OS based on TCP window size and TTL
    os_hint = "Unknown"
    if ttl > 64:
        os_hint = "Windows" if window_size == 8192 else "Unix/Linux"
    elif ttl <= 64:
        os_hint = "Linux/Unix"
    
    # Print results
    print(f"Detected OS Characteristics: TTL={ttl}, Window Size={window_size}, Options={options}")
    print(f"OS Hint: {os_hint}")
ip_address = "192.168.1.1"
detect_os(ip_address)
```
### 활용 및 개선 방안
서비스 스캐너를 구현하여 특징을 학습하고 지식을 쌓을 수 있었다. metasploitable v2를 이용하여 스캔을 하여 모의해킹 경험을 쌓을 수 있었다.<br><br>
하지만 db 서비스 검증 로직과 telnet 검증 로직이 잘 작동하지 않아 어려움을 겪었으며 새로운 아이디어를 토대로 개발해본 gui 버전은 불안정하여 응답 없음 오류가 발생하기도 했고 http, https 스캐너는 구현의 어려움으로 병렬 프로그래밍은 포기하고 구현을 하였으며 추후에도 개선이 필요하다.
