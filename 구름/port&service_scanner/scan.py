import argparse
import socket
import mysql.connector
import psycopg2
from pymongo import MongoClient
from tqdm import tqdm
import concurrent.futures
import time

# 포트 스캔 함수
def port_scan(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)  # Timeout 설정
    result = sock.connect_ex((target, port))
    sock.close()
    if result == 0:
        return port

# 데이터베이스 서비스 스캔 함수
def db_service_scan(target, port):
    if check_mysql(target, port):
        return ("MySQL", port)
    elif check_postgresql(target, port):
        return ("PostgreSQL", port)
    elif check_mongodb(target, port):
        return ("MongoDB", port)
    elif check_ssh(target, port):
        return ("SSH", port)
    elif check_dns(target,port):
        return ("DNS",port)
    elif check_ftp(target,port):
        return("FTP",port)
    elif check_ftp(target,port):
        return("FTP",port)
    elif check_smtp(target,port):
        return ("SMTP", port)
    else:
        return ("Unknown", port)

#SSH 서비스 확인 함수
def check_ssh(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)  # 타임아웃 설정
            result = sock.connect_ex((target, port))  # 연결 시도
            if result == 0:  # 연결 성공
                banner = sock.recv(1024)
                decoded_banner = banner.decode('utf-8', errors='ignore')
                return 'SSH' in decoded_banner
    except (socket.timeout, ConnectionRefusedError):
        return False
    return False

#DNS 서비스 확인 함수
def check_dns(target, port):
    # DNS A레코드 google.com
    query = b"\x59\xf6\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77\x06\x67\x6f\x6f\x67\x6c\x65\x03\x63\x6f\x6d\x00\x00\x01\x00\x01"
    expected_header = b'Y\xf6\x81\x80\x00\x01\x00\x01\x00\x04\x00\x00'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(2)
        # 해당 포트에 구글 A 레코드 보내기.
        sock.sendto(query, (target, port))
        # DNS 응답 받아서 예상과 비교.
        response, _ = sock.recvfrom(1024)  # Adjust buffer size as needed
        if len(response) >= len(expected_header) and response[:len(expected_header)] == expected_header:
            return True
        else:
            return False
    except socket.timeout:
        return False
    finally:
        sock.close()

# FTP 서비스 확인 함수
def check_ftp(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((target, port))
            response = sock.recv(1024)
            if response.startswith(b"220"):  # 서버 초기 응답 확인

                sock.sendall(b"SYST\r\n")   # SYST (OS 정보 확인)명령어 보내기
                response = sock.recv(1024)
                if response.startswith(b"215") or response.startswith(b"530"):  # 서버의 응답이 215(시스템 정보) 또는 530(login필요)인지 확인
                    return True
            return False
    except (socket.timeout, ConnectionRefusedError, UnicodeDecodeError):
        return False


def check_smtp(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((target, port))
            response = sock.recv(1024)
            if response.startswith(b"220"):  # 서버 초기 응답 확인
                sock.sendall(b"HELO example.com\r\n")
                response = sock.recv(1024)
                if response.startswith(b"250"):  # 서버의 응답이 250(요청한 메일이 정상적으로 완료)
                    return True
            return False
    except (socket.timeout, ConnectionRefusedError, UnicodeDecodeError):
        return False


# MySQL 서비스 확인 함수
def check_mysql(target, port):
    try:
        connection = mysql.connector.connect(
            host=target,
            port=port,
            user="root",  # 사용자 이름은 연결에 필요하지 않으므로 임의의 값을 사용.
            password="",  # 비밀번호도 마찬가지.
            connect_timeout=1
        )
        connection.close()
        return True
    except mysql.connector.Error:
        return False

# PostgreSQL 서비스 확인 함수
def check_postgresql(target, port):
    try:
        connection = psycopg2.connect(
            host=target,
            port=port,
            user="postgres",  # 사용자 이름은 연결에 필요하지 않으므로 임의의 값을 사용.
            password="",  # 비밀번호도 마찬가지.
            connect_timeout=1
        )
        connection.close()
        return True
    except psycopg2.OperationalError:
        return False

# MongoDB 서비스 확인 함수
def check_mongodb(target, port):
    try:
        client = MongoClient(target, port, serverSelectionTimeoutMS=1000)
        client.server_info()
        client.close()
        return True
    except:
        return False

# 메인 함수
def main():
    parser = argparse.ArgumentParser(description='Scan open ports and detect database services.')
    parser.add_argument('target', help='Target IP address')
    parser.add_argument('-p', '--port', help='Port range (e.g., "1-100" or "80")', default='1-1023')
    args = parser.parse_args()

    target = args.target
    port_range = args.port.split('-')
    start_port = int(port_range[0])
    end_port = int(port_range[-1]) + 1

    open_ports = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(port_scan, target, port) for port in range(start_port, end_port)]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(range(start_port, end_port)), desc="Port Scanning", unit="port"):
            result = future.result()
            if result:
                open_ports.append(result)

    if not open_ports:
        print("No open ports found.")
    else:
        print("Open ports:")
        for port in open_ports:
            print(f"Port {port}")

        db_services = []
        time.sleep(0.1)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(db_service_scan, target, port) for port in open_ports]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(open_ports), desc="Service Scanning", unit="port"):
                result = future.result()
                db_services.append(result)

        if not db_services:
            print("No database services found.")
        else:
            print("services found:")
            for service, port in db_services:
                print(f"Service: {service}, Port: {port}")

if __name__ == "__main__":
    main()
