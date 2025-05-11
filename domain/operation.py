from enum import Enum, unique


@unique
class Operation(Enum):
    COMPRESSION =  "動画ファイルを圧縮する"
    RESOLUTION_CHANGE = "動画の解像度を変更する"
    ASPECT_RATIO_CHANGE = "動画のアスペクト比を変更する"
    CONVERT_VIDEO_TO_AUDIO =  "動画をオーディオに変換する"
    CREATE_GIF_OR_WEBM = "指定した時間範囲で、GIFかWEBMを作成する"