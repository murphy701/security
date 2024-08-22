from scapy.all import sniff, IP, TCP, UDP, ICMP
import re

# 서버 IP 주소를 설정합니다.
SERVER_IP = "192.168.100.7"
EXTERNAL_NET = "any"  # 외부 네트워크를 의미하는 기본 값
HOME_NET = SERVER_IP

def parse_rule(rule):
    # 프로토콜 파싱
    protocol_match = re.search(r'^alert (tcp|udp|icmp|ip)', rule)
    protocol = protocol_match.group(1) if protocol_match else None

    # IP 주소 파싱
    source_ip_match = re.search(r'alert \w+ ([\$\w\.]+) ', rule)
    source_ip = source_ip_match.group(1) if source_ip_match else None

    dest_ip_match = re.search(r' -> ([\$\w\.]+)', rule)
    dest_ip = dest_ip_match.group(1) if dest_ip_match else None

    # 포트 파싱
    source_port_match = re.search(r'alert \w+ [\$\w\.]+ (\d+|any|\d+:\d+)', rule)
    source_port = source_port_match.group(1) if source_port_match else None

    dest_port_match = re.search(r' -> [\$\w\.]+ (\d+|any|\d+:\d+)', rule)
    dest_port = dest_port_match.group(1) if dest_port_match else None

    # flow 파싱
    flow_match = re.search(r'flow:\s*(to_server|to_client)', rule)
    flow = flow_match.group(1) if flow_match else None

    # 메시지 파싱
    msg_match = re.search(r'msg:"([^"]+)"', rule)
    msg = msg_match.group(1) if msg_match else "No msg found"

    sid_match = re.search(r'sid:(\d+);', rule)
    sid = sid_match.group(1) if sid_match else "No SID"

    # dsize 파싱
    dsize_match = re.search(r'dsize:(\d+|<\d+|>\d+);', rule)
    dsize = dsize_match.group(1) if dsize_match else None

    # id 파싱 (앞에 공백이 있는 경우만)
    id_match = re.search(r' id:(\d+);', rule)
    icmp_id = id_match.group(1) if id_match else None

    # TTL 파싱
    ttl_match = re.search(r'ttl:(\d+);', rule)
    ttl = ttl_match.group(1) if ttl_match else None

    # ICMP 관련 필드 파싱
    itype_match = re.search(r'itype:(\d+)', rule)
    itype = itype_match.group(1) if itype_match else None

    icode_match = re.search(r'icode:(\d+)', rule)
    icode = icode_match.group(1) if icode_match else None



    if icode and '>' in icode:
        icode = f'> {icode.split(">")[1]}'

    if protocol == "icmp":
        if source_ip == "$EXTERNAL_NET":
            source_ip = EXTERNAL_NET
        if dest_ip == "$HOME_NET":
            dest_ip = HOME_NET
    else:
        # flow 옵션이 있는 경우 다른 프로토콜에 대해 처리
        flow_match = re.search(r'flow:\s*(to_server|to_client)', rule)
        flow = flow_match.group(1) if flow_match else None

        if flow == "to_server":
            if source_ip == "$EXTERNAL_NET":
                source_ip = EXTERNAL_NET
            if dest_ip in ["$HOME_NET", "$SMTP_SERVERS", "$SQL_SERVERS"]:
                dest_ip = HOME_NET
        elif flow == "to_client":
            if source_ip in ["$HOME_NET", "$SMTP_SERVERS", "$SQL_SERVERS"]:
                source_ip = HOME_NET
            if dest_ip == "$EXTERNAL_NET":
                dest_ip = EXTERNAL_NET

    # content와 pcre 파싱 및 옵션 저장
    content_pcre_list = []
    combined_pattern = re.finditer(r'(content:"([^"]+)")|(pcre:"([^"]+)")', rule)
    for index, match in enumerate(combined_pattern):
        if match.group(2):  # content
            content = {
                "index": index,
                "type": "content",
                "value": match.group(2),
                "depth": None,
                "distance": None,
                "nocase": False,
                "fast_pattern": False
            }
            depth_match = re.search(r'depth:(\d+)', rule[match.end():])
            if depth_match:
                content["depth"] = depth_match.group(1)

            distance_match = re.search(r'distance:(\d+)', rule[match.end():])
            if distance_match:
                content["distance"] = distance_match.group(1)

            if 'nocase' in rule[match.end():]:
                content["nocase"] = True

            if 'fast_pattern' in rule[match.end():]:
                content["fast_pattern"] = True

            content_pcre_list.append(content)

        elif match.group(4):  # pcre
            pcre = {
                "index": index,
                "type": "pcre",
                "value": match.group(4),
                "depth": None,
                "distance": None,
                "nocase": False,
                "fast_pattern": False
            }
            depth_match = re.search(r'depth:(\d+)', rule[match.end():])
            if depth_match:
                pcre["depth"] = depth_match.group(1)

            distance_match = re.search(r'distance:(\d+)', rule[match.end():])
            if distance_match:
                pcre["distance"] = distance_match.group(1)

            if 'nocase' in rule[match.end():]:
                pcre["nocase"] = True

            if 'fast_pattern' in rule[match.end():]:
                pcre["fast_pattern"] = True

            content_pcre_list.append(pcre)

    # flags, fragbits, ip_proto 파싱
    flags = re.search(r'flags:([A-Z]+)', rule)
    fragbits = re.search(r'fragbits:([A-Z\+]+)', rule)
    ip_proto = re.search(r'ip_proto:(\d+)', rule)

    return {
        "protocol": protocol,
        "source_ip": source_ip,
        "dest_ip": dest_ip,
        "source_port": source_port,
        "dest_port": dest_port,
        "flow": flow,
        "msg": msg,
        "sid": sid,
        "dsize": dsize,
        "icmp_id": icmp_id,  # id 추가
        "ttl": ttl,
        "content_pcre_list": content_pcre_list,
        "flags": flags.group(1) if flags else None,
        "fragbits": fragbits.group(1) if fragbits else None,
        "ip_proto": ip_proto.group(1) if ip_proto else None,
        "itype": itype,
        "icode": icode
    }
def print_rule_by_sid(parsed_rules, target_sid):
    for rule in parsed_rules:
        if rule["sid"] == target_sid:
            print(f"Rule with SID {target_sid}:")
            print(rule)
            break
    else:
        print(f"No rule found with SID {target_sid}")

def match_rule_to_packet(packet, parsed_rules):
    packet_proto = None
    if packet.haslayer(TCP):
        packet_proto = 'tcp'
        proto_layer = packet[TCP]
    elif packet.haslayer(UDP):
        packet_proto = 'udp'
        proto_layer = packet[UDP]
    elif packet.haslayer(ICMP):
        packet_proto = 'icmp'
        proto_layer = packet[ICMP]

    if not packet_proto:
        return  # TCP/UDP/ICMP가 아닌 패킷은 처리하지 않음

    packet_ip = packet[IP]

    for rule in parsed_rules:
        if rule["protocol"] != packet_proto:
            continue  # 프로토콜이 일치하지 않으면 다음 룰로

        # IP 주소와 포트 번호 비교
        if rule["source_ip"] != "any" and rule["source_ip"] != packet_ip.src:
            continue
        if rule["dest_ip"] != "any" and rule["dest_ip"] != packet_ip.dst:
            continue

        if rule["source_port"] and rule["source_port"] != "any":
            if '-' in rule["source_port"]:
                start_port, end_port = map(int, rule["source_port"].split(':'))
                if not (start_port <= proto_layer.sport <= end_port):
                    continue
            elif str(proto_layer.sport) != rule["source_port"]:
                continue

        if rule["dest_port"] and rule["dest_port"] != "any":
            if '-' in rule["dest_port"]:
                start_port, end_port = map(int, rule["dest_port"].split(':'))
                if not (start_port <= proto_layer.dport <= end_port):
                    continue
            elif str(proto_layer.dport) != rule["dest_port"]:
                continue

        # TTL 검사
        if rule["ttl"] and str(packet_ip.ttl) != rule["ttl"]:
            continue

        # dsize 검사
        if rule["dsize"]:
            payload_size = len(bytes(proto_layer.payload))
            if rule["dsize"].startswith(">"):
                if not (payload_size > int(rule["dsize"][1:])):
                    continue
            elif rule["dsize"].startswith("<"):
                if not (payload_size < int(rule["dsize"][1:])):
                    continue
            else:
                if payload_size != int(rule["dsize"]):
                    continue

        # ICMP 룰 처리
        if rule["protocol"] == "icmp":
            icmp_layer = packet[ICMP]

            # Check ICMP type
            if rule.get("itype") and rule["itype"] != str(icmp_layer.type):
                continue

            # Check ICMP code
            if rule.get("icode"):
                icmp_code = icmp_layer.code
                rule_icode = rule["icode"]

                if ">" in rule_icode:
                    threshold = int(rule_icode.strip(">"))
                    if not (icmp_code > threshold):
                        continue
                elif "<" in rule_icode:
                    threshold = int(rule_icode.strip("<"))
                    if not (icmp_code < threshold):
                        continue
                elif "=" in rule_icode:
                    threshold = int(rule_icode.strip("="))
                    if icmp_code != threshold:
                        continue
                else:
                    if icmp_code != int(rule_icode):
                        continue

            # Check ICMP ID
            if rule.get("icmp_id") and str(icmp_layer.id) != rule["icmp_id"]:
                continue

        # `content`나 `pcre`가 없는 경우 처리
        if not rule["content_pcre_list"]:
            source_ip_port = f"{packet_ip.src}:{proto_layer.sport}" if packet_proto != 'icmp' else packet_ip.src
            dest_ip_port = f"{packet_ip.dst}:{proto_layer.dport}" if packet_proto != 'icmp' else packet_ip.dst
            if packet_ip.dst == SERVER_IP:
                dest_ip_port = f"SERVER_NET:{proto_layer.dport}" if packet_proto != 'icmp' else packet_ip.dst
            print(f"[ALERT] Matched Rule: {rule['mclearsg']} (SID: {rule['sid']})")
            print(f"Source: {source_ip_port} -> Destination: {dest_ip_port}")
            print(f"Metadata: Protocol={rule['protocol']}, Flags={rule['flags']}, Fragbits={rule['fragbits']}, IP Proto={rule['ip_proto']}")
            print("-----------------------------------------------------------------------------------------------------------------------")
            continue

        # 페이로드 매칭 (content나 pcre이 있는 경우에만)
        payload = bytes(proto_layer.payload).decode(errors='ignore')

        match_found = False
        offset = 0
        for content_pcre in rule["content_pcre_list"]:
            value = content_pcre["value"]
            search_area = payload[offset:]

            # nocase 적용
            if content_pcre["nocase"]:
                value = value.lower()
                search_area = search_area.lower()

            if content_pcre["type"] == "content":
                match_index = search_area.find(value)
                if match_index == -1:
                    match_found = False
                    break
                if content_pcre["depth"] is not None:
                    if match_index + len(value) > int(content_pcre["depth"]):
                        match_found = False
                        break
                if content_pcre["distance"] is not None:
                    if match_index < int(content_pcre["distance"]):
                        match_found = False
                        break

                offset = match_index + len(value)
                match_found = True

            elif content_pcre["type"] == "pcre":
                regex_flags = re.IGNORECASE if content_pcre["nocase"] else 0
                if re.search(value, search_area, regex_flags):
                    match_found = True
                    break
                else:
                    match_found = False
                    break

            if content_pcre["fast_pattern"]:
                match_found = True
                break

        if match_found:
            source_ip_port = f"{packet_ip.src}:{proto_layer.sport}" if packet_proto != 'icmp' else packet_ip.src
            dest_ip_port = f"{packet_ip.dst}:{proto_layer.dport}" if packet_proto != 'icmp' else packet_ip.dst
            if packet_ip.dst == SERVER_IP:
                dest_ip_port = f"SERVER_NET:{proto_layer.dport}" if packet_proto != 'icmp' else packet_ip.dst
            print(f"[ALERT] Matched Rule: {rule['msg']} (SID: {rule['sid']})")
            print(f"Source: {source_ip_port} -> Destination: {dest_ip_port}")
            print(f"Metadata: Protocol={rule['protocol']}, Flags={rule['flags']}, Fragbits={rule['fragbits']}, IP Proto={rule['ip_proto']}")
            print("-----------------------------------------------------------------------------------------------------------------------")
            break  # 매칭된 룰이 있으면 종료



def packet_callback(packet):
    ''''# 패킷의 dsize (페이로드 크기) 계산
    if packet.haslayer(TCP):
        payload_size = len(bytes(packet[TCP].payload))
    elif packet.haslayer(UDP):
        payload_size = len(bytes(packet[UDP].payload))
    elif packet.haslayer(ICMP):
        payload_size = len(bytes(packet[ICMP].payload))
        icmp_type = packet[ICMP].type
        icmp_code = packet[ICMP].code
        icmp_id = packet[ICMP].id
    else:
        payload_size = 0  # 지원되지 않는 프로토콜의 경우
        icmp_type = None
        icmp_code = None
        icmp_id = None

    # iptype (IP 프로토콜) 확인
    if packet.haslayer(IP):
        ip_type = packet[IP].proto
        ttl_value = packet[IP].ttl
    else:
        ip_type = "Unknown"
        ttl_value = "Unknown"

    # 세부 정보 출력
    print(f"Captured Packet dsize (payload size): {payload_size} bytes")
    print(f"Captured Packet iptype: {ip_type}")
    print(f"Captured Packet TTL: {ttl_value}")
    if packet.haslayer(ICMP):
        print(f"Captured Packet ICMP type: {icmp_type}")
        print(f"Captured Packet ICMP code: {icmp_code}")
        print(f"Captured Packet ICMP id: {icmp_id}")
    '''
    '''payload_data = None

    if packet.haslayer(TCP):
        payload_data = bytes(packet[TCP].payload)
    elif packet.haslayer(UDP):
        payload_data = bytes(packet[UDP].payload)
    elif packet.haslayer(ICMP):
        payload_data = bytes(packet[ICMP].payload)

    if payload_data:
        print("Captured Packet Payload:")
        print(payload_data.decode(errors='ignore'))  # 페이로드를 출력합니다.'''

    # 실시간으로 패킷을 캡처하고 룰과 비교
    match_rule_to_packet(packet, parsed_rules)

# rule.txt 파일에서 룰 파싱
with open('rule.txt', 'r') as file:
    rules = file.readlines()

parsed_rules = []
for rule in rules:
    parsed_rule = parse_rule(rule.strip())
    parsed_rules.append(parsed_rule)
'''
target_sid = "144"  # 여기에 원하는 SID를 입력하세요
print_rule_by_sid(parsed_rules, target_sid)
'''

# 패킷 캡처 시작
interface = "VMware Network Adapter VMnet8"
sniff(iface=interface, prn=packet_callback, store=0)
