### 데이터 수집 디테일
- NSL-KDD 패킷 데이터셋(공식 페이지에서는 데이터셋이 제공되지 않고 있음, kaggle 링크 첨부)
  - KDD Cup 99 데이터셋의 개선 버전
  - 41개의 특성과 하나의 레이블 필드로 이루어짐
  - https://www.kaggle.com/datasets/hassan06/nslkdd
```
duration: 연결 지속 시간 (초)
protocol_type: 프로토콜 타입 (예: tcp, udp, icmp)
service: 네트워크 서비스 유형 (예: http, ftp, telnet 등)
flag: 연결의 상태 (예: SF, S0 등)
src_bytes: 소스에서 목적지로 전송된 데이터의 바이트 수
dst_bytes: 목적지에서 소스로 전송된 데이터의 바이트 수
land: 소스와 목적지 IP가 같은지 여부 (1이면 같음, 0이면 다름)
wrong_fragment: 잘못된 프래그먼트의 수
urgent: 긴급 패킷의 수
hot: '핫' 인디케이터의 수
num_failed_logins: 로그인 실패 횟수
logged_in: 성공적으로 로그인했는지 여부 (1이면 로그인 성공, 0이면 실패)
num_compromised: '타협'된 조건의 수
root_shell: 루트 쉘을 얻었는지 여부 (1이면 예, 0이면 아니오)
su_attempted: su 명령 시도 횟수
num_root: 루트 계정에 접근한 수
num_file_creations: 생성된 파일의 수
num_shells: 쉘 프롬프트의 수
num_access_files: 접근된 파일의 수
num_outbound_cmds: 아웃바운드 명령의 수 (이 데이터셋에서는 항상 0)
is_host_login: 호스트 로그인이었는지 여부 (1이면 예, 0이면 아니오)
is_guest_login: 게스트 로그인이었는지 여부 (1이면 예, 0이면 아니오)
count: 연결 수 (연결된 호스트의 총 수)
srv_count: 서비스 연결 수 (동일 서비스에 대한 연결 수)
serror_rate: SYN 오류의 비율
srv_serror_rate: 서비스 SYN 오류의 비율
rerror_rate: REJ 오류의 비율
srv_rerror_rate: 서비스 REJ 오류의 비율
same_srv_rate: 동일 서비스 비율
diff_srv_rate: 다른 서비스 비율
srv_diff_host_rate: 서비스에서 다른 호스트 비율
dst_host_count: 대상 호스트 카운트
dst_host_srv_count: 대상 호스트 서비스 카운트
dst_host_same_srv_rate: 대상 호스트의 동일 서비스 비율
dst_host_diff_srv_rate: 대상 호스트의 다른 서비스 비율
dst_host_same_src_port_rate: 대상 호스트의 동일 소스 포트 비율
dst_host_srv_diff_host_rate: 대상 호스트 서비스에서 다른 호스트 비율
dst_host_serror_rate: 대상 호스트 SYN 오류 비율
dst_host_srv_serror_rate: 대상 호스트 서비스 SYN 오류 비율
dst_host_rerror_rate: 대상 호스트 REJ 오류 비율
dst_host_srv_rerror_rate: 대상 호스트 서비스 REJ 오류 비율
```
- 데이터셋 예시
```
0,udp,private,SF,105,146,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,254,254,1.00,0.00,1.00,0.00,0.00,0.00,0.01,0.00,0.00,0.00,0.00,0.00,anomaly
```
- 조사 과정에서 여러 데이터셋을 찾을 수 있었지만 nsl-kdd 데이터셋이 적합하다고 생각하여 선정

### 모델 학습
1. 데이터 전처리
- 데이터 정제: 결측치 제거, 이상치 탐지 및 제거
- 특성 선택: 데이터의 특징을 기반으로 중요한 특성을 선택. 정보 이득, 상관 계수 분석 등의 기법을 사용할 수 있음
- 데이터 변환: 스케일링, 정규화, 범주형 데이터의 원-핫 인코딩 등을 수행
- 데이터 분할: 데이터를 훈련 세트와 테스트 세트로 분리. 일반적으로 80:20 또는 70:30 비율로 분할
2. 모델 선택
- 결정 트리: 이해하기 쉽고 해석 가능한 모델.
- 랜덤 포레스트: 여러 결정 트리의 결과를 평균내어 더 안정적인 예측을 제공.
- 서포트 벡터 머신 (SVM): 높은 차원의 데이터에 효과적.
- 신경망: 복잡한 패턴을 학습할 수 있으며, 깊은 학습이 가능.
3.모델 훈련
- 선택한 모델을 훈련 데이터를 사용하여 학습. 이 단계에서는 모델의 하이퍼파라미터를 설정하고 최적화할 수 있음.
4.모델 평가 및 최적화
- 모델의 성능을 개선하기 위해 하이퍼파라미터 튜닝을 수행. 그리드 서치, 랜덤 서치, 베이지안 최적화 등 다양한 방법을 사용할 수 있음. 앙상블 기법을 사용하여 여러 모델의 예측을 결합함으로써 성능을 향상
5.모델 선택 팁
- 데이터 셋 크기와 특성에 따라 적합한 모델 선택
- 크고 복잡하면 딥러닝이나 랜덤 포레스트, 작고 간단한 데이터 셋이면 svm, k-nn을 고려

- nsl-kdd 데이터 셋으로 탐지할 수 있는 공격 유형
  - normal traffic
  - DoS
    - smurf, pod(ping of death), land, neptune
  - Probe
    - nmap, portsweep
  - R2L(remote to local)
  - U2R(user to root)
    - rootkit, buffer_overflow, perl
  ### 예측에 필요한 변수
  - 총 변수 42개이므로 실제 발생하는 패킷을 캡처해서 42개의 변수를 만들어야 했음->시간이 너무 많이 들 것 같아 변수 선택법을 사용
  - 해당 학습 모델로 재패키징하여 변수 개수를 4개로 줄일 수 있었음
    - 대부분 ddos공격을 위한 변수 이며 주로 ddos 공격을 막기 위해 변수를 설정함
    - src bytes:출발지에서 전송된 바이트 수
    - dst_bytes
    - same_srv_rate
    - dst_host_srv_count
- 변수를 줄이는 코드
```
import pyshark

# 패킷 처리 함수
def process_packet(packet):
    data = {
        'src_bytes': len(packet.payload),
        'dst_bytes': len(packet.payload),
        'protocol_type': packet.transport_layer if hasattr(packet, 'transport_layer') else None,
        'service': packet.highest_layer,
        'flag': packet.tcp.flags if hasattr(packet, 'tcp') else None,
        'logged_in': None,  # 로그인 여부는 패킷 분석만으로는 추출 어려움
        # 아래 값들은 일정 시간 동안 패킷을 모니터링하고 집계해야 계산 가능
        'same_srv_rate': None,
        'dst_host_same_srv_rate': None,
        'dst_host_srv_count': None,
        'diff_srv_rate': None,
        'srv_serror_rate': None,
        'serror_rate': None,
        'dst_host_same_src_port_rate': None,
        'dst_host_diff_srv_rate': None,
        'count': None,
        'dst_host_srv_diff_host_rate': None,
        'srv_count': None
    }
    return data

# 패킷 캡처 및 데이터 저장
capture = pyshark.LiveCapture(interface='eth0')
capture.sniff(packet_count=10)
data_list = [process_packet(packet) for packet in capture]

# 데이터프레임으로 변환
import pandas as pd
df = pd.DataFrame(data_list)
print(df)
```
최종 코드
https://github.com/murphy701/security/blob/main/%EA%B5%AC%EB%A6%84/NIDS_AI/anomaly.py
- 패킷 캡처: scapy 라이브러리로 패킷을 캡처
- 패킷 처리: packet_callback 함수가 필요 정보를 추출하고 통계 업데이트
- 예측 요청: fastAPI 서버로 POST 요청하여 예측을 수행
- 통계 리셋: 1분 간격으로 통계 리셋하여 최신 정보를 유지
- 다음과 같은 결과를 확인할 수 있고 prediction 값이 0이면 정상 1이면 이상을 탐지한 것을 나타냄
![image](https://github.com/user-attachments/assets/93215953-83ad-4d0c-877c-6e568ac02c80)
