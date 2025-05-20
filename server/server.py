import sys
sys.path.append("..")
import socket
import threading

import config
import file_receive
import file_edit
import utils
from interface import tcp_encoder

client_ip_address_list = []

def remove_ip_address(ip_address: str):
    client_ip_address_list.remove(ip_address)

def thread_worker(connection: socket.socket, ip_address):
    uploaded_file_path, json_data, media_type, = file_receive.file_receive_main(connection, lambda : remove_ip_address(ip_address))
    file_edit.file_edit_main(connection, uploaded_file_path, json_data, media_type, lambda : remove_ip_address(ip_address), lambda : remove_ip_address(ip_address))

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((config.server_address, config.server_port))
    sock.listen(5)

    # connection, address  = sock.accept()

    # uploaded_file_path, json_data, media_type, = file_receive.file_receive_main(connection)
    # file_edit.file_edit_main(connection, uploaded_file_path, json_data, media_type)

    while True:
        connection, address  = sock.accept()

        ip_address = address[0]
        if client_ip_address_list.count(ip_address) >= 1 :
            description = "あなたと同一のIPアドレスが現在アクセス中です。\n同一のIPアドレスからは同時に動画変換処理を行うことはできません。"
            solution = "時間を置いて再度実行してください。"
            response_json = utils.create_default_json(400, description, solution)
            response = tcp_encoder.create_tcp_protocol(response_json, "text", 0, "".encode())
            connection.send(response)
            continue
        else:
            response_json = utils.create_default_json(200, "利用可能です。", "")
            response = tcp_encoder.create_tcp_protocol(response_json, "text", 0, "".encode())
            connection.send(response)
        
        client_ip_address_list.append(ip_address)
        print(client_ip_address_list)
        thread = threading.Thread(target=thread_worker, args=(connection, ip_address), daemon=True)
        thread.start()
        


        

