import tkinter as tk
from tkinter import messagebox
import socket
import mysql.connector
import psycopg2
from pymongo import MongoClient
from tqdm import tqdm
import concurrent.futures
import time
from scapy.all import *

def start_scan():
    target = entry.get()
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(port_scan, target, port) for port in range(1, 65536)]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(range(1, 65536)), desc="Port Scanning", unit="port"):
            result = future.result()
            if result:
                open_ports.append(result)

    if not open_ports:
        messagebox.showinfo("Port Scanning", "No open ports found.")
    else:
        port_services = []
        time.sleep(0.1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(service_scan, target, port) for port in open_ports]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(open_ports), desc="Service Scanning", unit="port"):
                result = future.result()
                port_services.append(result)

        if not port_services:
            messagebox.showinfo("Service Scanning", "No services found.")
        else:
            services_found = ""
            for service, port in port_services:
                services_found += f"Service: {service}, Port: {port}\n"
            messagebox.showinfo("Service Scanning", services_found)

def port_scan(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)  
    result = sock.connect_ex((target, port))
    sock.close()
    if result == 0:
        return port

def service_scan(target, port):
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
    elif check_smtp(target,port):
        return ("SMTP", port)
    elif check_http(target,port):
        return ("HTTP", port)
    elif check_https(target,port):
        return ("HTTPS", port)
    else:
        return ("Unknown", port)

def check_ssh(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            result = sock.connect_ex((target, port))
            if result == 0:
                banner = sock.recv(1024)
                decoded_banner = banner.decode('utf-8', errors='ignore')
                return 'SSH' in decoded_banner
    except (socket.timeout, ConnectionRefusedError):
        return False
    return False

def check_dns(target, port):
    query = b"\x59\xf6\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x77\x77\x77\x06\x67\x6f\x6f\x67\x6c\x65\x03\x63\x6f\x6d\x00\x00\x01\x00\x01"
    expected_header = b'Y\xf6\x81\x80\x00\x01\x00\x01\x00\x04\x00\x00'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(2)
        sock.sendto(query, (target, port))
        response, _ = sock.recvfrom(1024)
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
            if response.startswith(b"220"):
                sock.sendall(b"SYST\r\n")
                response = sock.recv(1024)
                if response.startswith(b"215") or response.startswith(b"530"):
                    return True
            return False
    except (socket.timeout, ConnectionRefusedError, UnicodeDecodeError):
        return False

# SMTP 서비스 확인 함수
def check_smtp(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((target, port))
            response = sock.recv(1024)
            if response.startswith(b"220"):
                sock.sendall(b"HELO example.com\r\n")
                response = sock.recv(1024)
                if response.startswith(b"250"):
                    return True
            return False
    except (socket.timeout, ConnectionRefusedError, UnicodeDecodeError):
        return False

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

def check_mongodb(target, port):
    try:
        client = MongoClient(target, port, serverSelectionTimeoutMS=1000)
        client.server_info()
        client.close()
        return True
    except:
        return False

def check_http(target, port):
    try:
        with socket.create_connection((target, port)) as sock:
            sock.settimeout(0.2)
            request = b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\nConnection: close\r\n\r\n"
            sock.send(request)
            response = sock.recv(4048000).decode()
            if "HTTP/1.1 200 OK" in response or "HTTP/1.0 200 OK" in response:
                return True
            else:
                return False
    except Exception as e:
        return False

def check_https(target, port):
    try:
        with socket.create_connection((target, port)) as sock:
            sock.settimeout(0.2)
            sock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
            response = sock.recv(1024000).decode()
            if "HTTP/1.1 400" in response or "HTTP/1.0 400" in response:
                return True
            else:
                return False
    except Exception as e:
        return False

root = tk.Tk()
root.title("Port Scanner")

label = tk.Label(root, text="Enter target IP address:")
label.pack()

entry = tk.Entry(root)
entry.pack()

scan_button = tk.Button(root, text="Start Scan", command=start_scan)
scan_button.pack()

root.mainloop()
