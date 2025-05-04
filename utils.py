import json
import config


# パケットのサイズを1400バイトに揃えるために、(1400 - ヘッダー - jsonのバイトサイズ - メディアタイプのバイトサイズ) した値をファイルから読み込む
# すべて足すと1400になる
# payloadは1400バイトと決まっているので、ファイルのサイズはpayloadのバイト数からjsonのサイズととfile_typeのサイズだけ読み込む必要がある
def calc_readble_file_bytes(media_type: str, json_data: any):
    media_type_bits_len = len(media_type.encode())
    json_str_bits_len = len(json.dumps(json_data).encode())
    return config.payload_byte_size - media_type_bits_len - json_str_bits_len

def get_file_stem(file_name: str):
    return file_name[ file_name.rfind("/") + 1 : file_name.rfind(".")]

def get_file_extension(file_name: str):
    return file_name[file_name.rfind(".") + 1:]