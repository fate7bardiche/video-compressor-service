import sys
sys.path.append("..")
import socket
import config
import time
import json
from interface import tcp_encoder, tcp_decoder
import file_upload
import edited_file_download
import share_video_processing_progress

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((config.server_address, config.server_port))
    except socket.error as err:
        print("コネクト時のエラーが起きました。")
        print(err)
    print("接続完了しました")

    time.sleep(config.flow_switching_wait_sec)

    while True:
        edited_data = sock.recv(config.sock_packet_size)
        print("first_edited_data", len(edited_data))
        total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(edited_data)
        if json_data["status"] == 200:
            print(json_data["description"])
            break
        else:
            print(json_data["description"])
            print(json_data["solution"])
            sys.exit(1)


    file_upload.upload_main(sock)
    share_video_processing_progress.main(sock)
    edited_file_download.edited_file_download(sock)