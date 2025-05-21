import sys
sys.path.append("..")
import os
import socket
import config
import time

import json
import utils
from interface import tcp_encoder, tcp_decoder
from domain.operation import Operation

def operation_select_flow():
    operation_list = [operaton for operaton in Operation]
    for i in range(len(operation_list)):
        print(f"{i + 1}.", operation_list[i].value)
    
    operation_number = int(input("実行したい処理を番号で選択して下さい : "))
    print()

    return operation_list[operation_number - 1].name

def args_select_flow(operation_name: str, request_json):
    input_args = {}
    filter_args = {}
    args = {}

    if operation_name == Operation.COMPRESSION.name:
        while True:
            print("圧縮後の品質を0~50の間から選んでください。")
            print("0が最も品質が高いですが。ファイルサイズは大きくなります。")
            crf_str = input(" > ")
            try:
                crf = int(crf_str)
            except Exception as e:
                print(e)
                continue
            if (crf < 0) or (crf > 50):
                print("0~50の間から選んでください")
                continue

            args["crf"] = crf
            break
    elif operation_name == Operation.RESOLUTION_CHANGE.name:
        while True:
            print("解像度を数字で指定してください。入力された数字はピクセルとして解釈されます")
            print("アスペクト比は維持されます")
            try:
                width = int(input("横(width) > "))
            except Exception as e:
                print(e)
                continue

            filter_args["scale"] = {}
            # -1ではなく、-2。奇数が算出されるとfmpegがエンコード時に弾いてしまう。
            # height not divisible by 2 (1280x763)
            # Error initializing output stream 0:0 -- Error while opening encoder for output stream #0:0 - maybe incorrect parameters such as bit_rate, rate, width or height
            filter_args["scale"]["pos_args"] = [width, -2]
            filter_args["scale"]["kw_args"] = {}
            break
    elif operation_name == Operation.ASPECT_RATIO_CHANGE.name:
        while True:
            print("アスペクト比を指定してください")
            try:
                width = int(input("横 > "))
            except Exception as e:
                print(e)
                continue
            
            try:
                height = int(input("縦 > "))
            except Exception as e:
                print(e)
                continue

            args["aspect"] = f"{width}:{height}"
            break
    elif operation_name == Operation.CONVERT_VIDEO_TO_AUDIO.name:
       args["vn"] = None
       args["acodec"] = "libmp3lame"
       args["q:a"] = 2
       request_json["output_extension"] = "mp3"

    elif operation_name == Operation.CREATE_GIF_OR_WEBM.name:
        while True:

            print("gifかwebmか番号で選択して下さい")
            extension_type_list = ["gif", "webm"]
            for i in range(len(extension_type_list)):
                print(f"{i + 1}.", extension_type_list[i])

            extension_number = int(input("> "))

            request_json["output_extension"] = extension_type_list[extension_number - 1]

            print("変換する時間範囲を設定します。")
            print("秒単位で入力して下さい。最大30秒です。")
            start_sec = int(input("開始地点 > "))
            input_args["ss"] = start_sec
            end_sec = int(input("終了地点 > "))
            input_args["t"] = end_sec

            break

    request_json["input_args"] = input_args
    request_json["filter_args"] = filter_args
    request_json["args"] = args

    return request_json


def upload_main(sock: socket.socket):
    dir_path = "video/"
    input_path = ""
    file_name = ""

    upload_video_list = list(filter(lambda s: not s[:1] == ".", os.listdir(dir_path)))
    for i in range(len(upload_video_list)): 
        full_path = os.path.join(dir_path, upload_video_list[i])
        if os.path.isfile(full_path):
            print(f"{i + 1}.", upload_video_list[i])

    while True:
        video_number_str = input("アップロードしたいファイルの番号を入力して下さい : ")
        video_number = int(video_number_str)
        if (video_number > len(upload_video_list) or (video_number < 1)):
            print("選択肢に存在する数字を指定してください")
            continue
        print()

        file_name = upload_video_list[video_number - 1]
        input_path = f"video/{file_name}"
        break

    operation = operation_select_flow()
    request_json = {"file_name": file_name, "operation": operation}
    request_json = args_select_flow(operation, request_json)

    with open(input_path, "rb") as f:
        # ファイルのサイズを取得(nバイト)
        f.seek(0, 2)
        total_file_byte_size = f.tell()
        f.seek(0)

        media_type = utils.get_file_extension(file_name)

        read_file_size = utils.calc_readble_file_bytes(media_type, request_json)
        first_data = f.read(read_file_size)

        
        request = tcp_encoder.create_tcp_protocol(request_json, media_type, total_file_byte_size, "".encode())
        sock.send(request)

        time.sleep(config.flow_switching_wait_sec)

        response_data = sock.recv(config.sock_packet_size)

        total_payload_size, json_data, media_type, payload  = tcp_decoder.decode_tcp_protocol(response_data)
        print(json_data["description"])    
        if(json_data["status"] == 400):
            sock.close()
            sys.exit(1)    

        data = first_data
        sent_data_result = first_data
        while data:
            request = tcp_encoder.create_tcp_protocol(request_json, media_type, total_file_byte_size, data)
            sock.send(request)

            # 暫定対応: 待つと以下エラーを回避できるので実行している。
            # ConnectionResetError: [Errno 104] Connection reset by peer
            time.sleep(config.send_wait_sec)

            processing_message = f"{len(sent_data_result)}/{total_file_byte_size}バイト送信済み"
            # while抜けた後の最初のprint文が改行されるようにするために、制御コードが増えている
            sys.stdout.write(f"\033[2K\033[1A\033[2K\033[G{processing_message}\n" )
            sys.stdout.flush()

            data = f.read(read_file_size)
            sent_data_result+= data
        
    respoonse = sock.recv(4096)
    total_payload_size, json_data, media_type, payload = tcp_decoder.decode_tcp_protocol(respoonse)
    print(json_data["description"])
    if json_data["status"] == 400:
        sys,exit()
