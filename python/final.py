import socket
import threading

def stealth_scan(host, port, results):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        # Send SYN packet
        result = sock.connect_ex((host, port))
        # If connection succeeds, the port is open
        if result == 0:
            try:
                service = socket.getservbyport(port, 'tcp')
            except OSError:
                service = "unknown"
            results.append((port, "open", service))
        # Close the connection without completing the handshake
        sock.close()
    except Exception as e:
        pass

def stealth_scan_ports(host, start_port, end_port):
    print(f"Scanning ports on {host}...")
    results = []
    threads = []
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=stealth_scan, args=(host, port, results))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    
    # Print results for open ports only
    for port, state, service in results:
        print(f"{port}/tcp\t{state}\t{service}")

if __name__ == "__main__":
    target_host = input("Enter target host: ")
    start_port = int(input("Enter start port: "))
    end_port = int(input("Enter end port: "))

    stealth_scan_ports(target_host, start_port, end_port)
