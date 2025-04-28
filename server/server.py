import sys
sys.path.append("..")
import os
import socket
import config
from datetime import datetime

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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((config.server_address, config.server_port))
    sock.listen(5)

    connection, address  = sock.accept()

    # 初回の受信時だけパケットがファイルのバイト数を持っているので、whileとは別で処理する
    first_data = connection.recv(config.payload_byte_size)
    file_byte_size: int = int.from_bytes(first_data[:config.file_size_byte_length], "big")
    current_capaciy = get_dir_size()
    print("current_capaciy", current_capaciy)
    if(file_byte_size  + current_capaciy > upper_limit_dir_size):
        over_capacity_message = "error:容量が上限に達したので、ファイルをアップロードできません。\n保管できるファイルサイズの合計は4TBまでです。"
        connection.send(over_capacity_message.encode())
        print(over_capacity_message)
        connection.close()
        sys.exit(1)
    else:
        nnover_capacity_message = f"ok:上限の4TBまで余裕があるので、ファイルをアップロード可能です。残り{upper_limit_dir_size - current_capaciy}バイトです。"
        connection.send(nnover_capacity_message.encode())
        print(nnover_capacity_message)
    file = first_data[config.file_size_byte_length:]

    while True:
        data = connection.recv(config.payload_byte_size)
        
        file += data
        print(data)
        if(len(data) < config.payload_byte_size):
            file_size = len(file)
            print("受信したファイルのサイズ",  file_size)
            # 指定されたファイルサイズと送られたデータのサイズが一致していたら
            if file_size == file_byte_size:
                print("指定されたファイルサイズと送られたデータのサイズが一致しました")
                break
            else:
                error_response_message = "指定されたファイルサイズと送られたデータのサイズが一致しませんでした"
                connection.send(error_response_message.encode())
                print(error_response_message)
                sys.exit(1)
    
    with open(f"video/{datetime.now()}.mp4", "wb") as f:
        print("write")
        f.write(file)
    
    uploaded_capacity_size = get_dir_size()
    complete_message = f"ファイルのアップロードが完了しました, 残り{upper_limit_dir_size - uploaded_capacity_size}バイトアップロード可能です"
    print(complete_message)
    connection.send(complete_message.encode())

if __name__ == '__main__':
    main()
    