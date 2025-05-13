import sys
sys.path.append("..")
import os
import socket
import ffmpeg
import time
import threading
import asyncio
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
    probe = ffmpeg.probe(target_file_path, select_streams="a")

    # mp3に変換時、動画に音声ストリームがなかったら、エラーを返す
    if  operation == Operation.CONVERT_VIDEO_TO_AUDIO: 
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

    # '-progress', 'pipe:1': 標準出力(fd1)にログを吐き出す
    # '-stats_period', '60',: 60秒間隔で、ログを出す
    # '-nostats': 人間向けのログの代わりに機械向けのログを吐き出す
    stream = ffmpeg.output(stream, output_file_path, **args).global_args('-progress', 'pipe:1', '-stats_period', '60','-nostats')
    stream = ffmpeg.overwrite_output(stream)
    # output = ffmpeg.run_async(stream, pipe_stdout=True, quiet=True)
    output = ffmpeg.run_async(stream, pipe_stdout=True, quiet=True)

    print(probe)
    duration =float(probe['format']['duration'])
    print("duration", duration)
    while True:
        # line = asyncio.get_event_loop().run_in_executor(None, output)
        line_bits = output.stdout.readline()
        line = line_bits.decode().strip()
        if len(line) == 0:
            send_data = tcp_encoder.create_tcp_protocol({}, "null", 0, "".encode())
            connection.send(send_data)
            print()
            break

        key, value_str = line.split("=")
        if key == "out_time_ms":
            current_time_sec = (float(value_str) / 1000000)
            total_time_sec = duration / 1000000
            # print((time_sec / duration) * 100)
            editing_progress_message = f"\033[2K\033[1A\033[2K\033[G{current_time_sec} / {duration}秒\n{current_time_sec / duration * 100} / 100%" 
            sys.stdout.write(editing_progress_message)
            sys.stdout.flush()
            # print(f"{(} / 100")
            send_data = tcp_encoder.create_tcp_protocol({}, "text", 0, editing_progress_message.encode())
            connection.send(send_data)

    # print("output: ", output)
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









    
