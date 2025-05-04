import sys
sys.path.append("..")
import socket
import config
import time
import json
from interface import tcp_encoder, tcp_decoder
import file_upload
import edited_file_download

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((config.server_address, config.server_port))
    except socket.error as err:
        print("コネクト時のエラー")
        print(err)

    print("接続完了しました")

    file_upload.upload_main(sock)
    edited_file_download.edited_file_download(sock)