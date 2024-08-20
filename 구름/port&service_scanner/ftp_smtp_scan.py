import socket
import threading
import ftplib
import smtplib

def scan(target_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        print("Port open: " + str(port))
        s.close()
    except:
        print("Port closed: " + str(port))
    return None

def m_port_scan(target_ip, start_port, end_port):
    print(f"scanning {target_ip}...")

    # 각 포트를 스캔하기 위한 스레드 생성
    threads = []
    open_ports = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(target_ip, port))
        threads.append(t)
        t.start()

    # 모든 스레드가 완료될 때까지 대기
    for t in threads:
        t.join()

    print("스캔 완료")

    # 열린 포트 출력
    print("open ports:")
    for port in open_ports:
        print(f"port {port}is open")

def check_smtp(target, port):
    try:
        # SMTP 서비스에 연결
        smtp = smtplib.SMTP(host=target, port=port, timeout=1)
        smtp.quit()  # 연결 종료
        return True
    except smtplib.SMTPException:
        return False

# Updated FTP check function with corrected ftplib usage and logical flow
def check_ftp(target, port):
    try:
        # FTP 서비스에 연결
        ftp = ftplib.FTP()
        ftp.connect(host=target, port=port, timeout=1)
        ftp.login()  # 익명 로그인을 시도
        ftp.quit()   # 연결을 종료
        return True
    except ftplib.all_errors as e:
        return False

def check_postgresql(target, port):
    try:
        connection = psycopg2.connect(
            host=target,
            port=port,
            user="postgres",  # 사용자 이름은 연결에 필요하지 않으므로 임의의 값을 사용.
            password="",  # 비밀번호도 마찬가지.
            connect_timeout=1
        )
        connection.close()
        return True
    except psycopg2.OperationalError:
        return False

# 사용 예시
target_ip = "127.0.0.1"
start_port = 1
end_port = 1024

m_port_scan(target_ip, start_port, end_port)
scan_ftp_service(target_ip)
scan_smtp_service(target_ip)
