import sys
sys.path.append("..")
import os
import socket
import ffmpeg
import time
import threading
import asyncio
import math
from datetime import datetime


import config
import utils

from interface import tcp_encoder
from domain.operation import Operation

def file_edit_main(connection: socket.socket, target_file_path: str, client_json: dict[str, any], media_type: str, on_error: callable, on_finish: callable):
    operation = client_json["operation"]

    output_file_stem = utils.get_file_stem(target_file_path)
    output_file_extension = media_type  if  client_json.get("output_extension") == None else client_json.get("output_extension")

    input_args = client_json["input_args"]
    filter_args = client_json["filter_args"]
    args = client_json["args"]
    print("input_args: ", input_args)
    stream = ffmpeg.input(target_file_path, **input_args)
    probe = ffmpeg.probe(target_file_path, select_streams="a")
    print("probe: ", probe)

    # mp3に変換時、動画に音声ストリームがなかったら、エラーを返す
    if  operation == Operation.CONVERT_VIDEO_TO_AUDIO.name: 
        if len(probe.get('streams')) == 0:
            description = "音声ストリームが存在しなかったので、音声に変換できません"
            solution = "音声ストリームが存在する動画をアップロードして下さい"
            print(description)
            print(solution)
            send_data = tcp_encoder.create_tcp_protocol(utils.create_default_json(400, description, solution), "0", 0, "".encode())
            connection.send(send_data)
            on_error()
            sys.exit(1)
            return
        
    palette_name = f"ffmpeg_files/palette_{output_file_stem}.png"
    if operation == Operation.CREATE_GIF_OR_WEBM.name:
        if output_file_extension == "gif":
            palette = ffmpeg.input(target_file_path).filter('fps', 15).filter('scale', 480, -2).filter("palettegen").output(palette_name, vframes=1)
            ffmpeg.run(palette, overwrite_output=True)

            palette_in = ffmpeg.input(palette_name)
            stream = ffmpeg.filter([stream, palette_in], 'paletteuse', dither='bayer')

            filter_args["fps"] = {}
            filter_args["fps"]["pos_args"] = [15]
            filter_args["scale"] = {}
            filter_args["scale"]["pos_args"] = [480, -2]

        if output_file_extension == "webm":
            args["vcodec"] = 'libvpx-vp9'
            args["acodec"] = 'libopus'
            args["video_bitrate"] = '1M'
            args["audio_bitrate"] = '128k'
            args["crf"] = 23
            args["deadline"] = 'good'

    for fa in list(filter_args.keys()):
        pos_args = filter_args[fa]["pos_args"] if not filter_args[fa].get("pos_args") == None else []
        kw_args = filter_args[fa]["kw_args"] if not filter_args[fa].get("kw_args") == None else {}
        stream = stream.filter(fa, *pos_args, **kw_args)
    

    output_file_name = f"{output_file_stem}.{output_file_extension}"
    output_file_path = f"ffmpeg_files/edited_video/{output_file_name}"
    print("output_file_path", output_file_path)

    # '-progress', 'pipe:1': 標準出力(fd1)にログを吐き出す
    # '-stats_period', '60',: 60秒間隔で、ログを出す
    # '-nostats': 人間向けのログの代わりに機械向けのログを吐き出す
    stream = ffmpeg.output(stream, output_file_path, **args).global_args('-progress', 'pipe:1', '-stats_period', '60','-nostats')
    stream = ffmpeg.overwrite_output(stream)
    output = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True, quiet=True)
    
    duration =float(probe['format']['duration'])
    print("duration", duration)
    
    # 動画処理の進捗を確認し、clientに共有する
    while True:
        stdout_bits = output.stdout.readline()
        stdout_line = stdout_bits.decode().strip()

        key, value_str = stdout_line.split("=")

        # 正しく変換が終わったら
        if key == "progress" and value_str == "end":
            print()
            break
        
        # 進捗率を計算
        if key == "out_time_ms":
            ms_to_sec_division_num = 1000000

            # 少数第三位まで表示
            current_time_sec = math.floor((float(value_str) / ms_to_sec_division_num) * 1000) / 1000
            # 少数第三位まで表示
            current_parsent = math.floor((current_time_sec / duration * 100) * 1000) / 1000
            editing_progress_message = f"\033[2K\033[1A\033[2K\033[G{current_time_sec} / {duration}秒\n{current_parsent} / 100%" 
            sys.stdout.write(editing_progress_message)
            sys.stdout.flush()

            respoinse_json = utils.create_default_json(200, "問題なし")
            send_data = tcp_encoder.create_tcp_protocol(respoinse_json, "text", 0, editing_progress_message.encode())
            connection.send(send_data)

    out, err = output.communicate()
    if output.returncode == 0:
        print("進捗確認終了")
        send_data = tcp_encoder.create_tcp_protocol(utils.create_default_json(200, "編集完了"), "null", 0, "hoge".encode())
        connection.send(send_data)
    else:
        print("編集時にエラーが発生", err.decode())
        send_data = tcp_encoder.create_tcp_protocol(utils.create_default_json(400, "引数が不正です", "引数を確認してください"), "0", 0, "fuga".encode())
        connection.send(send_data)
        on_error()
        sys.exit(1)

    print("動画編集終了")


    time.sleep(config.send_wait_sec)


    with open(output_file_path, "rb") as f:
        total_file_size = os.path.getsize(output_file_path)
        json_data = utils.create_default_json(200)
        json_data["file_name"] = output_file_name

        read_bytes = utils.calc_readble_file_bytes(media_type, json_data)
        data = f.read(read_bytes)
        total_sent_bytes = 0
        while data:       
            send_data = tcp_encoder.create_tcp_protocol(json_data, media_type, total_file_size, data)
            connection.send(send_data)

            total_sent_bytes += len(data)

            time.sleep(config.send_wait_sec)

            processing_message = f"{total_sent_bytes}/{total_file_size}バイト送信済み"
            # while抜けた後の最初のprint文が改行されるようにするために、制御コードが増えている
            sys.stdout.write(f"\033[2K\033[1A\033[2K\033[G{processing_message}\n" )
            sys.stdout.flush()

            data = f.read(read_bytes)
        print("編集したファイルの送信完了")
        # 送信が終わったことをmedia_typeをnullで送信することでフラグとして使用する
        send_data = tcp_encoder.create_tcp_protocol(json_data, "null", total_file_size, "".encode())
        connection.send(send_data)


    # 編集前と編集後のファイルどちらも削除する
    utils.file_remove(target_file_path)
    print("アップロードしたファイルの削除完了")
    utils.file_remove(output_file_path)
    print("作成されたファイルの削除完了")
    utils.file_remove(palette_name)
    # IP制限を解除する
    on_finish()









    
