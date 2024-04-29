import socket
import threading
import random

# Global list to store open ports
open_ports = []

def syn_scan(host, port):
    try:
        # Create a raw socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.settimeout(1)

        # Build the IP header
        ip_header = b'\x45\x00\x00\x28'  # IP version, header length, type of service, total length
        ip_header += b'\xab\xcd\x00\x00'  # Identification, flags, fragment offset
        ip_header += b'\x40\x06\x00\x00'  # TTL, protocol (TCP), checksum
        ip_header += socket.inet_aton("192.168.1.2")  # Source IP address
        ip_header += socket.inet_aton(host)  # Destination IP address

        # Build the TCP header
        tcp_source_port = random.randint(1025, 65535)  # Random source port
        tcp_header = struct.pack('!HHLLBBHHH', tcp_source_port, port, 0, 0, 2, 0, 8192, 0, 0)

        # Calculate the TCP pseudo header checksum
        pseudo_header = socket.inet_aton("192.168.1.2") + socket.inet_aton(host) + b'\x00\x06' + struct.pack('!H', len(tcp_header))
        tcp_checksum = calculate_checksum(pseudo_header + tcp_header)

        # Build the final SYN packet
        syn_packet = ip_header + tcp_header + struct.pack('!H', tcp_checksum) + b'\x00\x00\x00\x00\x02\x04\x05\xb4\x04\x02'

        # Send the SYN packet
        sock.sendto(syn_packet, (host, port))

        # Receive response
        response, _ = sock.recvfrom(1024)
        if response:
            open_ports.append(port)
            print(f"Port {port}/tcp\topen")
    except socket.error:
        pass
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        exit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

def calculate_checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i + 1])
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
    syn_scan_ports(target_host, max(1, start_port), end_port)
