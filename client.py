# This program was modified by [Michael R Newman] / [n01586930]

import socket
import argparse
import struct
import time
import os

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (target_ip, target_port)
    sock.settimeout(0.1)
    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    seq_num = 0
    buffer = {}
    retrans_time = 0.5
    eof_received = False

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return
    
    print(f"[*] Starting file transmission of '{input_file}'...")

    try:
        with open(input_file, 'rb') as f:
            while True:
                
                if not eof_received and (seq_num - sum(1 for i in buffer.values() if i['acked']) < 50):                    
                    chunk = f.read(4092)
                    
                    if chunk:
                        header = struct.pack('!I', seq_num)
                        packet = header + chunk
                        buffer[seq_num] = {
                            'data': packet,
                            'time': time.time(),
                            'acked': False
                        }
                        sock.sendto(packet, server_address)
                        seq_num += 1
                    else:
                        eof_received = True
                    
                while True: 
                    
                    try:
                        ack_packet, _ = sock.recvfrom(4)
                        ack_num = struct.unpack('!I', ack_packet)[0]
                        if ack_num in buffer:
                            buffer[ack_num]['acked'] = True
                    except socket.timeout:
                        break
                    
                now = time.time()
                
                for seq_id, into in buffer.items():
                    
                    if not into['acked'] and now - into['time'] > retrans_time:
                        sock.sendto(into['data'], server_address)
                        buffer[seq_id]['time'] = now
                        
                if eof_received and all(info['acked'] for info in buffer.values()):
                    break
                    
                time.sleep(0.001)
                            
        eof_header = struct.pack('!I', seq_num)
        sock.sendto(eof_header + b'', server_address)
        print("[*] File transmission complete.")
                    
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)