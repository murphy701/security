import socket
import threading
import ipaddress

# Global list to store open ports
open_ports = []

def syn_scan(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append((host, port))
            print(f"Port {port}/tcp\topen")
        sock.close()
    except Exception as e:
        pass

def syn_scan_decoy(decoy_ip, target_host, port_range):
    start_port, end_port = port_range
    for port in range(start_port, end_port + 1):
        syn_scan(decoy_ip, port)
        syn_scan(target_host, port)

def divide_port_range(start_port, end_port, num_divisions):
    port_ranges = []
    ports_per_division = (end_port - start_port + 1) // num_divisions
    remaining_ports = (end_port - start_port + 1) % num_divisions
    current_port = start_port
    for _ in range(num_divisions):
        if remaining_ports > 0:
            ports_for_division = ports_per_division + 1
            remaining_ports -= 1
        else:
            ports_for_division = ports_per_division
        port_ranges.append((current_port, current_port + ports_for_division - 1))
        current_port += ports_for_division
    return port_ranges

def syn_scan_ports_decoy(decoy_ips, target_host, port_range):
    print(f"Scanning ports on {target_host} with decoy IPs...")
    threads = []
    port_ranges = divide_port_range(*port_range, len(decoy_ips))
    for decoy_ip, port_range in zip(decoy_ips, port_ranges):
        thread = threading.Thread(target=syn_scan_decoy, args=(decoy_ip, target_host, port_range))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    if open_ports:
        print("Open ports:")
        for host, port in sorted(open_ports):
            print(f"Decoy IP: {host}, Port: {port}")
    else:
        print("No open ports found.")

if __name__ == "__main__":
    target_host = input("Enter target host: ")
    start_port = int(input("Enter start port: "))
    end_port = int(input("Enter end port: "))
    
    num_decoys = int(input("Enter the number of decoy IPs: "))
    decoy_ips = [str(ip) for ip in ipaddress.IPv4Network('10.0.0.0/24').hosts()][:num_decoys]  # Example: Generate decoy IPs from a specific range
    
    syn_scan_ports_decoy(decoy_ips, target_host, (start_port, end_port))
