import sys
sys.path.append("..")
import os
import socket
import config
from datetime import datetime
from interface import tcp_encoder, tcp_decoder
import json

# 4TB: テラバイトをバイト表記で保持
upper_limit_dir_size = 4000000000000

def get_dir_size(path: str="video/"):
    total = 0
    for p in os.listdir(path):
        full_path = os.path.join(path, p)
        if os.path.isfile(full_path):
            total += os.path.getsize(full_path)
        elif os.path.isdir(full_path):
            total += get_dir_size(full_path)
    return total

def main(connection: socket.socket):
    # 初回の受信時だけパケットがファイルのバイト数を持っているので、whileとは別で処理する
    first_data = connection.recv(config.sock_packet_size)
    print("request len", len(first_data))
    total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(first_data)

    print(json_data)
    print(media_type)
    print(total_payload_size)
    
    current_capaciy = get_dir_size()
    print("current_capaciy", current_capaciy)
    if(total_payload_size  + current_capaciy > upper_limit_dir_size):
        response_json = {"description": "error:容量が上限に達したので、ファイルをアップロードできません。\n保管できるファイルサイズの合計は4TBまでです。"}
        response = tcp_encoder.create_tcp_protocol(response_json, media_type, total_payload_size, "hoge". encode())
        connection.send(response)
        print(response_json["description"])
        connection.close()
        sys.exit(1)
    else:
        response_json = {"description": f"ok:上限の4TBまで余裕があるので、ファイルをアップロード可能です。残り{upper_limit_dir_size - current_capaciy}バイトです。"}
        response = tcp_encoder.create_tcp_protocol(response_json, media_type, total_payload_size, "hoge". encode())
        print("response len", len(response))
        connection.send(response)
        print(response_json["description"])



    file = "".encode()
    print("file len", len(file))
    while True:
        data = connection.recv(config.sock_packet_size)

        total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(data)
        read_file_size = config.payload_byte_size - len(media_type.encode()) - len(json.dumps(json_data).encode())

        file += payload
        # print(payload)
        # print(len(payload))
        if(len(payload) < read_file_size):
            print("payload len", len(payload))
            print("read_file_size", read_file_size)
            file_size = len(file)
            print("受信したファイルのサイズ",  file_size)
            # 指定されたファイルサイズと送られたデータのサイズが一致していたら
            if file_size == total_payload_size:
                print("指定されたファイルサイズと送られたデータのサイズが一致しました")
                break
            else:
                error_response_message = "指定されたファイルサイズと送られたデータのサイズが一致しませんでした"
                print(error_response_message)
                connection.send(error_response_message.encode())
                sys.exit(1)

    output_file_path = f"video/{datetime.now()}.mp4"
    with open(output_file_path, "wb") as f:
        print("write")
        f.write(file)
    
    uploaded_capacity_size = get_dir_size()
    complete_message = f"ファイルのアップロードが完了しました, 残り{upper_limit_dir_size - uploaded_capacity_size}バイトアップロード可能です"
    print(complete_message)
    respoinse_json = {"description": complete_message}
    response = tcp_encoder.create_tcp_protocol(respoinse_json, "none", 0, "".encode())
    connection.send(response)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((config.server_address, config.server_port))
    sock.listen(5)

    connection, address  = sock.accept()

    main(connection)
