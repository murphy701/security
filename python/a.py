import socket
import re

def service_scan(target, port):
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)  # Set timeout for connection attempt
        
        # Connect to the target port
        s.connect((target, port))
        
        # Receive banner response
        banner = s.recv(1024).decode().strip()
        
        # Extract service version from banner response using regex
        service_version = re.search(r'Server: (.+)', banner)
        if service_version:
            print(f"[+] Open port {port} : {service_version.group(1)}")
        else:
            print(f"[+] Open port {port} : Service version not found")
        
        # Close the socket connection
        s.close()
        
    except (socket.timeout, ConnectionRefusedError):
        print(f"[-] Port {port} is closed on {target}")
    except Exception as e:
        print(f"[-] Error scanning port {port}: {e}")

def os_scan(target):
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        s.settimeout(2)  # Set timeout for receiving ICMP packets
        
        # Send a dummy UDP packet to get ICMP Time Exceeded message with TTL info
        s.sendto(b'', (target, 80))  # Send to port 80 (HTTP)
        
        # Receive ICMP Time Exceeded message
        _, addr = s.recvfrom(1024)
        
        # Extract TTL value from the IP header
        ttl = addr[8]
        
        # Determine OS based on TTL value
        if ttl <= 64:
            print("[+] TTL indicates the target is running a Unix/Linux-based OS.")
        elif ttl <= 128:
            print("[+] TTL indicates the target is running a Windows-based OS.")
        else:
            print("[+] Unable to determine OS based on TTL.")
        
        # Close the socket connection
        s.close()
        
    except socket.timeout:
        print("[-] TTL scan timed out.")
    except Exception as e:
        print("[-] Error scanning TTL:", e)

def main():
    target = input("Enter target IP address: ")
    ports = [21, 22, 23, 25, 53, 80, 443, 3306]  # Example ports to scan
    
    print(f"Scanning {target}...")
    for port in ports:
        service_scan(target, port)
    
    print("\nPerforming OS scan based on TTL...")
    os_scan(target)

if __name__ == "__main__":
    main()
