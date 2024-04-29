import socket
import threading

# Global list to store open ports
open_ports = []

def syn_scan(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
            print(f"Port {port}/tcp\topen")
        sock.close()
    except Exception as e:
        pass

def syn_scan_ports(host, start_port, end_port):
    print(f"Scanning ports on {host}...")
    threads = []
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=syn_scan, args=(host, port))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    if open_ports:
        print("Open ports:", ', '.join(str(port) for port in sorted(open_ports)))
    else:
        print("No open ports found.")

if __name__ == "__main__":
    target_host = input("Enter target host: ")
    start_port = int(input("Enter start port: "))
    end_port = int(input("Enter end port: "))
    syn_scan_ports(target_host, start_port, end_port)
