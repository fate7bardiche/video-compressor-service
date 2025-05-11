import sys
sys.path.append("..")
import os
import socket
import ffmpeg
import time
import threading
from datetime import datetime

import config
import utils

from interface import tcp_encoder, tcp_decoder
from domain.operation import Operation

def file_edit_main(connection: socket.socket, target_file_path: str, client_json: dict[str, any], media_type: str):
    operation = client_json["operation"]

    output_file_stem = utils.get_file_stem(target_file_path)
    print(client_json)
    output_file_extension = media_type  if  client_json.get("output_extension") == None else client_json.get("output_extension")
    print(media_type)

    # file_name = client_json["file_name"]
    input_args = client_json["input_args"]
    filter_args = client_json["filter_args"]
    args = client_json["args"]
    print(input_args)
    stream = ffmpeg.input(target_file_path, **input_args)

    # mp3に変換時、動画に音声ストリームがなかったら、エラーを返す
    if  operation == Operation.CONVERT_VIDEO_TO_AUDIO: 
        probe = ffmpeg.probe(target_file_path, select_streams="a")
        if not probe.get('streams'):
            print("音声ストリームが存在する動画をアップロードして下さい")
            return
        
    if operation == Operation.CREATE_GIF_OR_WEBM:
        if output_file_extension == "gif":
            palette = ffmpeg.input(target_file_path).filter('fps', 15).filter('scale', 480. -2).output('palette.png', vframes=1, vf='paletegen')
            ffmpeg.run(palette, overwrite_output=True)

            filter_args["fps"]
            filter_args["fps"]["pos_args"] = 15
            filter_args["scale"]
            filter_args["scale"]["pos_args"] = [480, -2]
            filter_args["paletteuse"]
            filter_args["paletteuse"]["kw_args"] = {"dither": 'bayer'}

        if output_file_extension == "webm":
            args["vcodec"] = 'libvpx-vp9'
            args["acodec"] = 'libopus'
            args["video_bitrate"] = '1M'
            args["audio_bitrate"] = '128k'
            args["crf"] = 23
            args["deadline"] = 'good'

    # macにダウンロードしたmp4の時間トリミング(画面の切り出し)から
    for fa in list(filter_args.keys()):
        pos_args = filter_args[fa]["pos_args"]
        kw_args = filter_args[fa]["kw_args"]
        stream = stream.filter(fa, *pos_args, **kw_args)
    

    output_file_name = f"{output_file_stem}.{output_file_extension}"
    output_file_path = f"edited_video/{output_file_name}"
    print("output_file_path", output_file_path)
    # output_file_path = f"edited_video/{}"

    stream = ffmpeg.output(stream, output_file_path, **args)
    stream = ffmpeg.overwrite_output(stream)
    output = ffmpeg.run(stream)


    print("output: ", output)
    print("動画編集終了")

    with open(output_file_path, "rb") as f:
        total_file_size = os.path.getsize(output_file_path)
        json_data = {"description": "", "file_name": output_file_name}

        read_bytes = utils.calc_readble_file_bytes(media_type, json_data)
        data = f.read(read_bytes)
        total_sent_bytes = 0
        while data:
            send_data = tcp_encoder.create_tcp_protocol(json_data, media_type, total_file_size, data)
            connection.send(send_data)
            total_sent_bytes += len(data)

            time.sleep(0.0001)

            processing_message = f"{total_sent_bytes}/{total_file_size}バイト送信済み"
            # while抜けた後の最初のprint文が改行されるようにするために、制御コードが増えている
            sys.stdout.write(f"\033[2K\033[1A\033[2K\033[G{processing_message}\n" )
            sys.stdout.flush()

            data = f.read(read_bytes)
        print("編集したファイルの送信完了")

    # 編集前と編集後のファイルどちらも削除する
    os.remove(target_file_path)
    print("アップロードしたファイルの削除完了")
    os.remove(output_file_path)
    print("作成されたファイルの削除完了")









    
