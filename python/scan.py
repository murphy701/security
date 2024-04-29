import socket
import os
import struct
import threading

# Global list to store open ports
open_ports = []

def syn_scan(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.settimeout(1)
        packet = build_syn_packet(host, port)
        sock.sendto(packet, (host, port))
        response = sock.recvfrom(1024)
        if response:
            open_ports.append(port)
            print(f"Port {port}/tcp\topen")
        sock.close()
    except socket.error:
        pass
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        exit()
    except Exception as e:
        print(f"Error: {e}")

def build_syn_packet(host, port):
    dest_ip = socket.inet_aton(host)  # Destination IP address
    ip_header = struct.pack('!BBHHHBBH4s4s', 69, 0, 20, 54321, 0, 64, 6, 0, dest_ip, dest_ip)

    src_port = os.getpid() & 0xFFFF  # Source port (arbitrary)
    tcp_header = struct.pack('!HHLLBBHHH', src_port, port, 0, 0, 2, 2, 8192, 0, 0)

    pseudo_header = struct.pack('!4s4sBBH', dest_ip, dest_ip, 0, 6, len(tcp_header))
    checksum = calculate_checksum(pseudo_header + tcp_header)

    syn_packet = struct.pack('!HHLLBBHHH', src_port, port, 0, 0, 2, 2, 8192, checksum, 0)

    return ip_header + tcp_header

def calculate_checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i+1])
        s = s + w
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

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
