# This program was modified by [Michael R Newman] / [n01586930]

import socket
import argparse
import struct

def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    print(f"[*] Server will save each received file as 'received_<ip>_<port>.jpg' based on sender.")
    sock.bind(server_address)
    
    exp_num = 0
    buffer = {}
    eof_seq = None
    f = None
    
    try:
        while True:
            packet, addr = sock.recvfrom(4096)
            if not packet:
                continue
            
            seq_num = struct.unpack('!I', packet[:4])[0]
            data = packet[4:]
            ack = struct.pack('!I', seq_num)
            sock.sendto(ack, addr)

            if not data:
                eof_seq = seq_num
            else:
                if f is None:
                    print("==== Start of reception ====")
                    ip, sender_port = addr
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, 'wb')
                    print(f"[*] First packet received from {addr}. File opened for writing as '{sender_filename}'.")
                
                if seq_num == exp_num:
                    f.write(data)
                    exp_num += 1
                
                    while exp_num in buffer:
                        f.write(buffer.pop(exp_num))
                        exp_num += 1
                elif seq_num > exp_num:
                    buffer[seq_num] = data
            
            if eof_seq is not None and exp_num == eof_seq and not buffer:
                if f:
                    f.close()
                    f = None
                    print(f"[*] End of file signal received from {addr}. File closed.")
                exp_num = 0
                buffer.clear()
                eof_seq = None

    except KeyboardInterrupt:
        print("==== End of reception ====")
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        if f:
            f.close()
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data")
    args = parser.parse_args()

    try:
        run_server(args.port, args.output)
    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")