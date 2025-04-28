import sys
sys.path.append("..")
import socket
import config
from datetime import datetime


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((config.server_address, config.server_port))
    sock.listen(5)

    connection, address  = sock.accept()

    # 初回の受信時だけパケットがファイルのバイト数を持っているので、whileとは別で処理する
    first_data = connection.recv(config.payload_byte_size)
    file_byte_size: int = int.from_bytes(first_data[:config.file_size_byte_length], "big")
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

    complete_message = "ファイルのアップロードが完了しました"
    print(complete_message)
    connection.send(complete_message.encode())


        

if __name__ == '__main__':
    main()
