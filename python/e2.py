import socket
import ssl
import mysql.connector
import psycopg2
from pymongo import MongoClient
from tqdm import tqdm
import concurrent.futures

# Function to scan ports
def port_scan(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)  # Timeout 설정
    result = sock.connect_ex((target, port))
    sock.close()
    if result == 0:
        return port

# Function to check HTTP service
def check_http(target, port):
    try:
        with socket.create_connection((target, port)) as sock:
            request=b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\nConnection: close\r\n\r\n"
            sock.send(request)
            response = sock.recv(4048000).decode()  # Decode the binary response
            print(f"{port}HTTP Response:", response)
            if "HTTP/1.1 200 OK"in response or "HTTP/1.0 200 OK" in response:
                print(f'{port} is HTTP')
                return "HTTP"
            else:
                print(f'{port} is not HTTP')
                return None
    except Exception as e:
        pass
    return None

# Function to check HTTPS service
def check_https(target, port):
    with socket.create_connection((target, port)) as sock:
        sock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
        response = sock.recv(1024000).decode()
                #print("HTTPS Response:", response)
        if "HTTP/1.1 400" in response or "HTTP/1.0 400" in response:
            return "HTTPS"
        else:
            print(f'{port} is not HTTPS')
            return None

# Function to scan for database services
def db_service_scan(target, port):
    if check_mysql(target, port):
        return ("MySQL", port)
    elif check_postgresql(target, port):
        return ("PostgreSQL", port)
    elif check_mongodb(target, port):
        return ("MongoDB", port)
    else:
        return ("Unknown", port)

# Function to check MySQL service
def check_mysql(target, port):
    try:
        connection = mysql.connector.connect(
            host=target,
            port=port,
            user="root",
            password="",
            connect_timeout=1
        )
        connection.close()
        return True
    except mysql.connector.Error:
        return False

# Function to check PostgreSQL service
def check_postgresql(target, port):
    try:
        connection = psycopg2.connect(
            host=target,
            port=port,
            user="postgres",
            password="",
            connect_timeout=1
        )
        connection.close()
        return True
    except psycopg2.OperationalError:
        return False

# Function to check MongoDB service
def check_mongodb(target, port):
    try:
        client = MongoClient(target, port, serverSelectionTimeoutMS=1000)
        client.server_info()
        client.close()
        return True
    except:
        return False

# Main function
def main():
    target = input("Enter target IP address: ")
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(port_scan, target, port) for port in range(1, 500)]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(range(1, 500)), desc="Port Scanning", unit="port"):
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
                print(f"Port {port} result: {result}")
                if result:
                    service_types[result] = "HTTP"
                else:
                    print(f"skip port {port}")
                    continue
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_https, target, port) for port in open_ports]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(open_ports), desc="HTTPS Service Scanning", unit="port"):
                port=future.port
                result = future.result()
                if result:
                    service_types[result] = "HTTPS"
                else:
                    print(f"skip {port}")
                    continue

        if not service_types:
            print("No HTTP or HTTPS services found.")
        else:
            print("Services found:")
            for service, service_type in service_types.items():
                print(f"Service: {service}, Type: {service_type}")

if __name__ == "__main__":
    main()
