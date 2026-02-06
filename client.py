# This program was modified by [Michael R Newman] / [n01586930]

import socket
import argparse
import struct
import os

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (target_ip, target_port)
    sock.settimeout(0.5)
    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    seq_num = 0

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return
    
    print(f"[*] Starting file transmission of '{input_file}'...")

    try:
        with open(input_file, 'rb') as f:
            while True:
                chunk = f.read(4092)
                
                if not chunk:
                    break
                
                header = struct.pack('!I', seq_num)
                packet = header + chunk

                while True: 
                    sock.sendto(packet, server_address)
                    try:
                        ack_packet, _ = sock.recvfrom(4)
                        ack_num = struct.unpack('!I', ack_packet)[0]
                        if ack_num == seq_num:
                            seq_num += 1
                            break
                    except socket.timeout:
                        continue

        sock.sendto(b'', server_address)
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