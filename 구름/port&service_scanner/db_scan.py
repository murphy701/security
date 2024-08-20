import socket
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

        db_services = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(db_service_scan, target, port) for port in open_ports]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(open_ports), desc="DB Service Scanning", unit="port"):
                result = future.result()
                db_services.append(result)

        if not db_services:
            print("No database services found.")
        else:
            print("Database services found:")
            for service, port in db_services:
                print(f"Service: {service}, Port: {port}")

if __name__ == "__main__":
    main()
