import socket
from tqdm import tqdm
import concurrent.futures

# Function to scan ports
def port_scan(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)  # Timeout 
    result = sock.connect_ex((target, port))
    sock.close()
    if result == 0:
        return port

# Function to check HTTP service
def check_http(target, port):
    print(f'{port}is coming')
    try:
        with socket.create_connection((target, port)) as sock:
            sock.settimeout(0.2)
            request = b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\nConnection: close\r\n\r\n"
            sock.send(request)
            response = sock.recv(4048000).decode()  # Decode the binary response
            if "HTTP/1.1 200 OK" in response or "HTTP/1.0 200 OK" in response:
                print(f'{port} is HTTP')
                return port
            else:
                print(f'{port} is not HTTP')
                return None
    except Exception as e:
        print(f"An error occurred while checking port {port}: {e}")
        return None

# Function to check HTTPS service
def check_https(target, port):
    try:
        with socket.create_connection((target, port)) as sock:
            sock.settimeout(0.2)
            sock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
            response = sock.recv(1024000).decode()
            if "HTTP/1.1 400" in response or "HTTP/1.0 400" in response:
                return port
            else:
                print(f'{port} is not HTTPS')
                return None
    except Exception as e:
        print(f"An error occurred while checking port {port}: {e}")
        return None

# Main function
def main():
    target = input("Enter target IP address: ")
    open_ports = []
    
    # Concurrent port scanning
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

    http_ports = []
    https_ports = []

    # Sequential HTTP service checking
    for port in open_ports:
        http_port = check_http(target, port)
        if http_port:
            http_ports.append(http_port)

    # Sequential HTTPS service checking
    for port in open_ports:
        https_port = check_https(target, port)
        if https_port:
            https_ports.append(https_port)

    print("HTTP Ports:", http_ports)
    print("HTTPS Ports:", https_ports)

    if not http_ports and not https_ports:
        print("No HTTP or HTTPS services found.")
    else:
        print("Services found:")
        for port in http_ports:
            print(f"Service: {port}, Type: HTTP")
        for port in https_ports:
            print(f"Service: {port}, Type: HTTPS")

if __name__ == "__main__":
    main()
