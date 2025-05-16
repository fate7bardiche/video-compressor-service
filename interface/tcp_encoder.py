import sys
sys.path.append("..")
import config
import json

def create_tcp_protocol(json_data, media_type: str, file_byte_size: int, payload: bytes):
    json_str = json.dumps(json_data)
    json_str_bits = json_str.encode() 
    print("json_str_bits:", len(json_str_bits))
    media_type_bits = media_type.encode()
    header = create_tcp_header(json_str_bits, media_type_bits, file_byte_size)
    body = json_str_bits + media_type_bits + payload
    return header + body

def create_tcp_header(json_str_bits: str, media_type_bits: str, payload_size: int):
    j = int.to_bytes(len(json_str_bits), 2, "big") 
    m = int.to_bytes(len(media_type_bits), 1, "big")
    p = int.to_bytes(payload_size, config.file_size_byte_length, "big")
    return j + m + p