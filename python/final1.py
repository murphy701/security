import socket
import ssl

# 포트 스캔 함수
def port_scan(target):
    open_ports = []
    for port in range(1, 65536):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)  # Timeout 설정
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

# HTTP 서비스 확인 함수
def check_http(target, port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, port)) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                ssock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                response = ssock.recv(1024)
                if response.startswith(b"HTTP"):
                    return True
    except:
        pass
    return False

# HTTPS 서비스 확인 함수
def check_https(target, port):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, port)) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                ssock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                response = ssock.recv(1024)
                if response.startswith(b"HTTP"):
                    return True
    except:
        pass
    return False

# 메인 함수
def main():
    target = input("Enter target IP address: ")
    open_ports = port_scan(target)
    if not open_ports:
        print("No open ports found.")
    else:
        print("Open ports:")
        for port in open_ports:
            print(f"Port {port}")

        print("\nScanning for HTTP and HTTPS services...")
        http_ports = []
        https_ports = []
        for port in open_ports:
            if check_http(target, port):
                http_ports.append(port)
            elif check_https(target, port):
                https_ports.append(port)

        if http_ports:
            print("HTTP services found on ports:", http_ports)
        else:
            print("No HTTP services found.")

        if https_ports:
            print("HTTPS services found on ports:", https_ports)
        else:
            print("No HTTPS services found.")

if __name__ == "__main__":
    main()
