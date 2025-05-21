import sys
sys.path.append("..")
import socket

import config
from interface import tcp_decoder


def main(sock: socket.socket):
    while True:
        edited_data = sock.recv(config.sock_packet_size)
        total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(edited_data)

        if(media_type == "null"):
            print(json_data["description"])
            break

        if(json_data["status"] == 400):
            print(json_data["description"])
            print(json_data["solution"])
            sock.close()
            sys.exit(1)

        sys.stdout.write(payload.decode())
        sys.stdout.flush()