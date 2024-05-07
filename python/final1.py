import socket
import ssl
import mysql.connector
import psycopg2
from pymongo import MongoClient
from tqdm import tqdm
import concurrent.futures

# 포트 스캔 함수
def port_scan(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)  # Timeout 설정
    result = sock.connect_ex((target, port))
    sock.close()
    if result == 0:
        return port

# HTTP 서비스 확인 함수
def check_http(target, port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, port)) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                ssock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                response = ssock.recv(1024)
                if response.startswith(b"HTTP"):
                    return "HTTP"
    except:
        pass
    return None

# HTTPS 서비스 확인 함수
def check_https(target, port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, port)) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                ssock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                response = ssock.recv(1024)
                if response.startswith(b"HTTP"):
                    return "HTTPS"
    except:
        pass
    return None

# 데이터베이스 서비스 스캔 함수
def db_service_scan(target, port):
    if check_mysql(target, port):
        return ("MySQL", port)
    elif check_postgresql(target, port):
        return ("PostgreSQL", port)
    elif check_mongodb(target, port):
        return ("MongoDB", port)
    else:
        return ("Unknown", port)

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
    target = input("Enter target IP address: ")
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(port_scan, target, port) for port in range(1, 65536)]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(range(1, 65536)), desc="Port Scanning", unit="port"):
            result = future.result()
            if result:
                open_ports.append(result)

    if not open_ports:
        print("No open ports found.")
    else:
        print("Open ports:")
        for port in open_ports:
            print(f"Port {port}")

        service_types = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_http, target, port) for port in open_ports]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(open_ports), desc="HTTP Service Scanning", unit="port"):
                result = future.result()
                if result:
                    service_types[result] = "HTTP"

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_https, target, port) for port in open_ports]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(open_ports), desc="HTTPS Service Scanning", unit="port"):
                result = future.result()
                if result:
                    service_types[result] = "HTTPS"

        if not service_types:
            print("No HTTP or HTTPS services found.")
        else:
            print("Services found:")
            for service, service_type in service_types.items():
                print(f"Service: {service}, Type: {service_type}")

if __name__ == "__main__":
    main()
