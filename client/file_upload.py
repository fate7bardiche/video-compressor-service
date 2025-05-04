import sys
sys.path.append("..")
import os
import socket
import config
import time
import json
import utils
from interface import tcp_encoder, tcp_decoder


def upload_main(sock: socket.socket):
    # input_path = 'video/example.mp4'
    
    dir_path = "video/"
    upload_video_options = os.listdir(dir_path)
    input_path = ""
    file_name = ""

    for i in range(len(upload_video_options)):
        # 隠しファイルを除外
        if upload_video_options[i][:1] == ".":
            continue 
        
        full_path = os.path.join(dir_path, upload_video_options[i])
        if os.path.isfile(full_path):
            print(f"{i + 1}.", upload_video_options[i])

    while True:
        video_number_str = input("アップロードしたいファイルの番号を入力して下さい : ")
        video_number = int(video_number_str)
        if (video_number > len(upload_video_options) or (video_number < 1)):
            print("選択肢に存在する数字を指定してください")
            continue

        file_name = upload_video_options[video_number - 1]
        input_path = f"video/{file_name}"
        break

    with open(input_path, "rb") as f:
        # ファイルのサイズを取得(nバイト)
        f.seek(0, 2)
        total_file_byte_size = f.tell()
        f.seek(0)

        print("file_byte_size", total_file_byte_size)

        media_type = utils.get_file_extension(file_name)
        reruest_json = {"file_name": file_name, "operation": "COMPRESSION", "args": {"crf": 23}}


        read_file_size = utils.calc_readble_file_bytes(media_type, reruest_json)
        first_data = f.read(read_file_size)

        
        request = tcp_encoder.create_tcp_protocol(reruest_json, media_type, total_file_byte_size, "".encode())
        print("request_byte_len", len(request))
        sock.send(request)

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