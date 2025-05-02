import sys
sys.path.append("..")
import socket
import config
import time
import json
from interface import tcp_encoder, tcp_decoder


def main(sock: socket.socket):
    input_path = 'video/example.mp4'

    with open(input_path, "rb") as f:
        f.seek(0, 2)
        total_file_byte_size = f.tell()
        f.seek(0)

        print("file_byte_size", total_file_byte_size)

        media_type = "mp4"
        reruest_json = {"arg1": "example"}
        reruest_json_str_bits = json.dumps(reruest_json).encode()

        # パケットのサイズを1400バイトに揃えるために、(1400 - ヘッダー - jsonのバイトサイズ - メディアタイプのバイトサイズ) した値をファイルから読み込む
        # すべて足すと1400になる
        read_file_size = config.payload_byte_size - len(media_type.encode()) - len(reruest_json_str_bits)
        first_data = f.read(read_file_size)
        # payloadにjsonとfile_typeが入ってしまっている
        # fileサイズは、それらを引いた値する必要がある
        # =====

        
        request = tcp_encoder.create_tcp_protocol(reruest_json, media_type, total_file_byte_size, "".encode())
        print("request_byte_len", len(request))
        sock.send(request)

        sock.settimeout(2)
        time.sleep(0.5)

        response_data = sock.recv(config.sock_packet_size)

        print(len(response_data))

        total_payload_size, json_data, media_type, payload  = tcp_decoder.decode_tcp_protocol(response_data)
        capacity_check_message = json_data["description"]
        if("error:" in capacity_check_message):
            print(capacity_check_message.replace("error:", ""))   
            sock.close()
            sys.exit(1)    
        print(capacity_check_message.replace("ok:", ""))   

        data = first_data
        sent_data_result = first_data
        while data:
            request = tcp_encoder.create_tcp_protocol(reruest_json, media_type, total_file_byte_size, data)
            sock.send(request)

            # 暫定対応: 待つと以下エラーを回避できるので実行している。
            # ConnectionResetError: [Errno 104] Connection reset by peer
            time.sleep(0.001)

            processing_message = f"{len(sent_data_result)}/{total_file_byte_size}バイト送信済み"
            # while抜けた後の最初のprint文が改行されるようにするために、制御コードが増えている
            sys.stdout.write(f"\033[2K\033[1A\033[2K\033[G{processing_message}\n" )
            sys.stdout.flush()

            data = f.read(read_file_size)
            sent_data_result+= data
        
    respoonse = sock.recv(4096)
    total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(respoonse)
    print(json_data["description"])

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((config.server_address, config.server_port))
    except socket.error as err:
        print("コネクト時のエラー")
        print(err)

    print("接続完了しました")

    main(sock)