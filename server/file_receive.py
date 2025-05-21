import sys
sys.path.append("..")
import os
import socket
import json
import config
import utils
from datetime import datetime
from interface import tcp_encoder, tcp_decoder


# 4TB: テラバイトをバイト表記で保持
upper_limit_dir_size = 4000000000000

# 引数のpathに渡したディレクトリ以下のサイズをバイト単位で返す
# ディレクトリがネストしている場合は再帰的に末端まで計算して合計する
def get_dir_size(path: str):
    total = 0
    if not os.path.isdir(path): 
        return 0
    for p in os.listdir(path):
        full_path = os.path.join(path, p)
        print(full_path)
        if os.path.isfile(full_path):
            total += os.path.getsize(full_path)
        elif os.path.isdir(full_path):
            total += get_dir_size(full_path)
    return total

def file_receive_main(connection: socket.socket, on_error: callable):
    # 初回の受信時だけパケットがファイルのバイト数を持っているので、whileとは別で処理する
    first_data = connection.recv(config.sock_packet_size)
    total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(first_data)

    print(total_payload_size)
    print(json_data)
    print(media_type)
    
    current_upload_strage_capacity = get_dir_size("video/")
    current_editrd_file_strage_capacity = get_dir_size("ffmpeg_files/")
    print("current_upload_strage_capaciy", current_upload_strage_capacity)
    print("current_editrd_file_strage_capaciy", current_editrd_file_strage_capacity)
    total_strage_capacity = current_upload_strage_capacity + current_editrd_file_strage_capacity
    if(total_payload_size  + total_strage_capacity > upper_limit_dir_size):
        description = "容量が上限に達したので、ファイルをアップロードできません。\n保管できるファイルサイズの合計は4TBまでです。"
        response_json = utils.create_default_json(400, description)
        response = tcp_encoder.create_tcp_protocol(response_json, media_type, total_payload_size, "hoge". encode())
        connection.send(response)
        print(response_json["description"])
        connection.close()
        on_error()
        sys.exit(1)
    else:
        description = f"上限の4TBまで余裕があるので、ファイルをアップロード可能です。残り{upper_limit_dir_size - total_strage_capacity}バイトです。"
        response_json = utils.create_default_json(200, description)
        response = tcp_encoder.create_tcp_protocol(response_json, media_type, total_payload_size, "hoge". encode())
        print("response len", len(response))
        connection.send(response)
        print(response_json["description"])

    file = "".encode()
    while True:
        data = connection.recv(config.sock_packet_size)

        total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(data)
        read_file_size = utils.calc_readble_file_bytes(media_type, json_data)

        file += payload
        if(len(payload) < read_file_size):
            file_size = len(file)
            # 指定されたファイルサイズと送られたデータのサイズが一致していたら
            if file_size == total_payload_size:
                print("指定されたファイルサイズと送られたデータのサイズが一致しました")
                break
            else:
                error_response_message = "指定されたファイルサイズと送られたデータのサイズが一致しませんでした"
                solution = "ヘッダーで指定するバイト数と、ファイルのバイト数が一致するようにしてください。"
                error_json = utils.create_default_json(400, error_response_message, solution)
                send_data = tcp_encoder.create_tcp_protocol(error_json, "", 0, "".encode())
                print(error_response_message)
                connection.send(send_data)
                on_error()
                sys.exit(1)

    file_stem = utils.get_file_stem(json_data["file_name"])
    output_file_path = f"video/{file_stem}_{datetime.now()}.{media_type}"
    with open(output_file_path, "wb") as f:
        print("write")
        f.write(file)
    
    current_upload_strage_capacity = get_dir_size("video/")
    current_editrd_file_strage_capacity = get_dir_size("ffmpeg_files/")
    total_strage_capacity = current_upload_strage_capacity + current_editrd_file_strage_capacity
    complete_message = f"ファイルのアップロードが完了しました, 残り{upper_limit_dir_size - total_strage_capacity}バイトアップロード可能です"
    print(complete_message)
    respoinse_json = utils.create_default_json(200, complete_message)
    response = tcp_encoder.create_tcp_protocol(respoinse_json, "null", 0, "".encode())
    connection.send(response)

    return output_file_path, json_data, media_type,