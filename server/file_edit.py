import sys
sys.path.append("..")
import os
import socket
import ffmpeg
import time
import config
import utils
from datetime import datetime
from interface import tcp_encoder, tcp_decoder

# python-ffmpeg はffmpegの薄いラッパーっぽい
# gptの回答をチェック

def file_edit_main(connection: socket.socket, target_file_path: str, client_json: dict[str, any], media_type: str):
    target_file_name = target_file_path[target_file_path.rfind("/") + 1:]
    # extension = utils.get_file_extension(file_name)
    print(media_type)
    # data = connection.recv(config.sock_packet_size)

    # file_name = client_json["file_name"]
    args = client_json["args"]
    stream = ffmpeg.input(target_file_path)
    output_file_path = f"edited_video/{target_file_name}"
    stream = ffmpeg.output(stream, output_file_path, **args)
    output = ffmpeg.run(stream)
    print("output: ", output)
    print("動画編集終了")

    with open(output_file_path, "rb") as f:
        total_file_size = os.path.getsize(output_file_path)
        json_data = {"description": "", "file_name": target_file_name}

        read_bytes = utils.calc_readble_file_bytes(media_type, json_data)
        data = f.read(read_bytes)
        total_sent_bytes = 0
        while data:
            send_data = tcp_encoder.create_tcp_protocol(json_data, media_type, total_file_size, data)
            connection.send(send_data)
            total_sent_bytes += len(data)

            time.sleep(0.001)

            processing_message = f"{total_sent_bytes}/{total_file_size}バイト送信済み"
            # while抜けた後の最初のprint文が改行されるようにするために、制御コードが増えている
            sys.stdout.write(f"\033[2K\033[1A\033[2K\033[G{processing_message}\n" )
            sys.stdout.flush()

            data = f.read(read_bytes)
        print("編集したファイルの送信完了")

    # 編集前と編集後のファイルどちらも削除する
    os.remove(target_file_path)
    os.remove(output_file_path)
    print("ファイルの削除完了")









    
