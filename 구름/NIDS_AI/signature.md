- 시그니처 기반 nids
  - 시그니처 데이터 베이스를 지속적으로 업데이트 해야 함
  - 신종 공격 탐지 어려움
  - 암호화 트래픽에서 탐지 어려움
- db에 유형 저장
```
[
    {
        "name": "TCP SYN Flood",
        "pattern": {
            "ip_src": "any",
            "ip_dst": "any",
            "tcp_sport": "any",
            "tcp_dport": "any",
            "flags": "S"
        }
    }
]
```
- 악성코드의 해시값을 저장하고 비교
```
import hashlib
import json
from scapy.all import sniff, IP, TCP, Raw

# 악성코드 해시 데이터베이스 로드
def load_malware_hashes(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return set(data['malware_hashes'])

# 페이로드의 해시 값 계산
def calculate_hash(payload):
    return hashlib.md5(payload).hexdigest()

# 패킷과 해시 매칭
def match_malware_hash(packet, malware_hashes):
    if packet.haslayer(Raw):
        payload = packet[Raw].load
        payload_hash = calculate_hash(payload)
        if payload_hash in malware_hashes:
            return True, payload_hash
    return False, None

# 패킷 콜백 함수
def packet_callback(packet):
    match, payload_hash = match_malware_hash(packet, malware_hashes)
    if match:
        print(f"Alert: Malware detected with hash {payload_hash} from {packet[IP].src}")

# 악성코드 해시 데이터베이스 로드
malware_hashes = load_malware_hashes('malware_hashes.json')

# 패킷 캡처 시작
sniff(prn=packet_callback, store=0)
```
- scapy 라이브러리를 이용한 패킷 캡처 분석
```
from scapy.all import sniff, IP, TCP

def packet_callback(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        tcp_sport = packet[TCP].sport
        tcp_dport = packet[TCP].dport
        print(f"Packet: {ip_src}:{tcp_sport} -> {ip_dst}:{tcp_dport}")

sniff(prn=packet_callback, store=0)
```
- 데이터베이스와 패킷 비교
```
import json

# 시그니처 로드
def load_signatures(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# 패킷과 시그니처 매칭
def match_signature(packet, signature):
    if packet.haslayer(IP) and packet.haslayer(TTCP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        tcp_sport = packet[TCP].sport
        tcp_dport = packet[TCP].dport
        flags = packet[TCP].flags

        pattern = signature['pattern']
        if (pattern['ip_src'] == "any" or pattern['ip_src'] == ip_src) and \
           (pattern['ip_dst'] == "any" or pattern['ip_dst'] == ip_dst) and \
           (pattern['tcp_sport'] == "any" or pattern['tcp_sport'] == tcp_sport) and \
           (pattern['tcp_dport'] == "any" or pattern['tcp_dport'] == tcp_dport) and \
           (pattern['flags'] == "any" or pattern['flags'] == flags):
            return True
    return False

# 패킷 콜백 함수
def packet_callback(packet):
    for signature in signatures:
        if match_signature(packet, signature):
            print(f"Alert: {signature['name']} detected from {packet[IP].src}")

# 시그니처 로드
signatures = load_signatures('signatures.json')

# 패킷 캡처 시작
sniff(prn=packet_callback, store=0)
```
- 룰의 파싱할 목록(양이 많아 부분적으로 생략됨-300개 이상)
- snort룰을 일부 이용하여 적용
- flow:to_client, established: 클라이언트로 가는 패킷 중 이미 tcp 연결이 설정된 상태에서만 룰을 적용
- classtype: snort룰에서 감지된 이벤트의 성격을 정의하는데 사용되는 필드
  - attempted-admin: 관리자 권한을 얻으려는 시도
  - trojan-activity: 트로이 목마 활동
  - successful-admin: 관리자 권한을 얻는 데 성공한 경우
  - suspicious-login: 의심스러운 로그인 시도

### 개발 과정
시그니처 기반 nids 룰 파싱 -> 실시간 패킷 캡처 -> 파싱한 룰과 비교 -> 시그니처와 일치한 패킷 발견 시 알림 발생

- 스노트 룰의 목록에 많은 룰들이 있고 룰을 단순화 하여 ->의 방향을 통일하고 포트 숫자 표시의 작업을 진행
- 테스트 환경 구성
  - HOME_NET(SERVER):metasploitable2
  - EXTERNAL_NET(CLIENT): host pc, kali linux
- echo+chargen bomb:두 서비스를 이용하여 공격, 무한히 트래픽을 전송하여 자원들 고갈시킴. 이 공격을 이용하여 테스트
- 해당 공격을 감지하는 룰들
```
alert udp $EXTERNAL_NET 19 -> $HOME_NET 7 ( msg:"SERVER-OTHER UDP echo+chargen bomb"; flow:to_server; metadata:policy max-detect-ips drop,ruleset community; reference:cve,1999-0103; reference:cve,1999-0635; classtype:attempted-dos; sid:271; rev:12; )
alert udp $EXTERNAL_NET 7 -> $HOME_NET 19 ( msg:"SERVER-OTHER UDP echo+chargen bomb"; flow:to_server; metadata:policy max-detect-ips drop,ruleset community; reference:cve,1999-0103; reference:cve,1999-0635; classtype:attempted-dos; sid:271; rev:12; )
alert udp $HOME_NET 7 -> $HOME_NET 19 ( msg:"SERVER-OTHER UDP echo+chargen bomb"; flow:to_server; metadata:policy max-detect-ips drop,ruleset community; reference:cve,1999-0103; reference:cve,1999-0635; classtype:attempted-dos; sid:271; rev:12; )
alert udp $HOME_NET 19 -> $HOME_NET 7 ( msg:"SERVER-OTHER UDP echo+chargen bomb"; flow:to_server; metadata:policy max-detect-ips drop,ruleset community; reference:cve,1999-0103; reference:cve,1999-0635; classtype:attempted-dos; sid:271; rev:12; )
```
- 8.14 최종본
- https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/NIDS_AI/signature.py
