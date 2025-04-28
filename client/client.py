import sys
sys.path.append("..")
import socket
import config
import ffmpeg
import os
import time


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((config.server_address, config.server_port))
    except socket.error as err:
        print("コネクト時のエラー")
        print(err)

    print("接続完了しました")

    input_path = 'video/example.mp4'

    with open(input_path, "rb") as f:
        f.seek(0, 2)
        file_byte_size = f.tell()
        f.seek(0)

        print("file_byte_size", file_byte_size)
        print("file_byte_size", os.path.getsize(input_path))

        first_data = f.read(config.payload_byte_size - config.file_size_byte_length)
        
        file_byte_size_bits = int.to_bytes(file_byte_size, config.file_size_byte_length, "big")
        sock.send(file_byte_size_bits + first_data)

        data = f.read(config.payload_byte_size)
        result = first_data
        while data:
            processing_message = f"{len(result)}/{file_byte_size}バイト送信済み"
            sys.stdout.write("\033[2K\033[G%s" % processing_message)
            sys.stdout.flush()

            # 暫定対応: 待つと以下エラーを回避できるので実行している。
            # ConnectionResetError: [Errno 104] Connection reset by peer
            time.sleep(0.001)
            
            sock.send(data)
            data = f.read(config.payload_byte_size)
            result+= data
            
        print("file_byte_size", file_byte_size)
        print(os.path.getsize(input_path))
            
    respoonse = sock.recv(4096)
    print(respoonse.decode())

if __name__ == "__main__":
    main()