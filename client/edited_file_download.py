import sys
sys.path.append("..")
import socket
import time
import json

import config
import utils
from interface import tcp_encoder, tcp_decoder



def edited_file_download(sock: socket.socket):
    edited_data = sock.recv(config.sock_packet_size)
    total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(edited_data)
    if(json_data["status"] == 400):
        print(json_data["description"])
        print(json_data["solution"])
        sock.close()
        sys.exit(1)    

    file_name = json_data["file_name"]
    payload_file_bytes = utils.calc_readble_file_bytes(media_type, json_data)

    file = payload
    while edited_data:
        edited_data = sock.recv(config.sock_packet_size)
        total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(edited_data)

        if media_type == "null" :
            file_size = len(file)
            if file_size == total_payload_size:
                print("指定されたファイルサイズと送られたデータのサイズが一致しました")
                break
            else:
                error_response_message = "指定されたファイルサイズと送られたデータのサイズが一致しませんでした"
                print(error_response_message)
                sys.exit(1)

        if(json_data["status"] == 400):
            print(json_data["description"])
            print(json_data["solution"])
            sock.close()
            sys.exit(1)    

        file += payload

    output_file_path = f"edited_video/{file_name}"
    with open(output_file_path, "wb") as f:
        f.write(file)

    
    print("ファイルの保存が完了しました。")

    
            