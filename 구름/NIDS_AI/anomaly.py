from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import requests
from scapy.all import sniff, IP, TCP
import time
from collections import defaultdict

# FastAPI 인스턴스 생성
app = FastAPI()

# 모델 로딩
model = joblib.load('Behavior_based_detection_NIDS_v1.pkl')

# 요청 데이터 모델 정의
class TrafficData(BaseModel):
    src_bytes: int
    dst_bytes: int
    same_srv_rate: float
    dst_host_srv_count: int

# 예측 엔드포인트 정의
@app.post("/predict/")
def predict(data: TrafficData):
    features = [[data.src_bytes, data.dst_bytes, data.same_srv_rate, data.dst_host_srv_count]]
    prediction = model.predict(features)
    return {"prediction": int(prediction[0])}

# 서비스 및 호스트 카운트를 저장할 딕셔너리
service_count = defaultdict(int)
total_count = defaultdict(int)
host_service_count = defaultdict(int)
host_connection_count = defaultdict(int)
start_time = time.time()

# 패킷 캡처 및 변수 추출 함수
def packet_callback(packet):
    global start_time

    if IP in packet and TCP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        dst_port = packet[TCP].dport
        src_bytes = len(packet[IP].payload)
        dst_bytes = len(packet[IP]) - len(packet[IP].payload)

        # 전체 연결 카운트 증가
        total_count[src_ip] += 1
        # 특정 서비스로의 연결 카운트 증가
        service_count[(src_ip, dst_port)] += 1
        # 목적지 호스트로의 서비스 카운트 증가
        host_service_count[dst_ip] += 1
        # 목적지 호스트로의 전체 연결 카운트 증가
        host_connection_count[dst_ip] += 1

        # 변수 계산
        same_srv_rate = service_count[(src_ip, dst_port)] / total_count[src_ip]
        dst_host_srv_count = host_service_count[dst_ip]

        # 데이터 패킷
        data = {
            "src_bytes": src_bytes,
            "dst_bytes": dst_bytes,
            "same_srv_rate": same_srv_rate,
            "dst_host_srv_count": dst_host_srv_count
        }

        # FastAPI 서버에 POST 요청 보내기
        response = requests.post("http://localhost:8000/predict/", json=data)
        print(response.json())

        elapsed_time = time.time() - start_time
        if elapsed_time > 60:  # 1분 간격으로 리셋
            # 통계 리셋
            service_count.clear()
            total_count.clear()
            host_service_count.clear()
            host_connection_count.clear()
            start_time = time.time()

# 인터페이스에서 패킷을 캡처
sniff(iface="eth0", prn=packet_callback)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
