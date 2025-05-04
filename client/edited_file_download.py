import sys
sys.path.append("..")
import socket
import time
import json

import config
import utils
from interface import tcp_encoder, tcp_decoder



def edited_file_download(sock: socket.socket):

        
    # ファイルの処理状況をの確認
    # デフォルトは1分間隔
    
    edited_data = sock.recv(config.sock_packet_size)
    total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(edited_data)

    file_name = json_data["file_name"]
    payload_file_bytes = utils.calc_readble_file_bytes(media_type, json_data)

    file = payload
    while edited_data:
        edited_data = sock.recv(config.sock_packet_size)
        total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(edited_data)
        file += payload

        # 編集後のファイルをダウンロードする
        # while True:

        if(len(payload) < payload_file_bytes):
            print("payload len", len(payload))
            print("read_file_size", payload_file_bytes)
            file_size = len(file)
            print("受信したファイルのサイズ",  file_size)
            # 指定されたファイルサイズと送られたデータのサイズが一致していたら
            if file_size == total_payload_size:
                print("指定されたファイルサイズと送られたデータのサイズが一致しました")
                break
            else:
                error_response_message = "指定されたファイルサイズと送られたデータのサイズが一致しませんでした"
                print(error_response_message)
                # .send(error_response_message.encode())
                sys.exit(1)

        
    output_file_path = f"edited_video/{file_name}"
    with open(output_file_path, "wb") as f:
        f.write(file)

    
    print("ファイルの保存が完了しました。")

    
            