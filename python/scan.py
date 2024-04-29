import socket
import threading
import random

# Global list to store open ports
open_ports = []

def syn_scan(host, port):
    try:
        # Generate a random IP address
        random_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        # Connect to the target host using the random IP address
        result = sock.connect_ex((random_ip, port))
        if result == 0:
            open_ports.append(port)
            print(f"Port {port}/tcp\topen")
        sock.close()
    except Exception as e:
        pass

def syn_scan_ports(host, start_port, end_port, num_scans):
    print(f"Scanning ports on {host}...")
    for scan_count in range(num_scans):
        print(f"Scan {scan_count + 1}/{num_scans}")
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
        # Clear the list of open ports for the next scan
        open_ports.clear()

if __name__ == "__main__":
    target_host = input("Enter target host: ")
    start_port = int(input("Enter start port: "))
    end_port = int(input("Enter end port: "))
    num_scans = int(input("Enter number of scans: "))
    syn_scan_ports(target_host, start_port, end_port, num_scans)
