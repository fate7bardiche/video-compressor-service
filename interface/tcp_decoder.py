import json

def decode_tcp_protocol(data: bytes):
    header = data[:8]
    body = data[8:]
    json_size, media_type_size, total_payload_size = decode_tcp_header(header)
    json_data, media_type, payload = decode_tcp_body(body, json_size, media_type_size)
    return total_payload_size, json_data, media_type, payload

def decode_tcp_header(header: bytes):
    json_size = int.from_bytes(header[:2], "big")
    media_type_size = int.from_bytes(header[2:3], "big")
    total_payload_size = int.from_bytes(header[3:8], "big")
    return json_size, media_type_size, total_payload_size

def decode_tcp_body(body: bytes, json_size: int, media_type_size: int):
    # print("json_size", json_size)
    # print("body[:json_size]", body[:json_size])
    parsed_json = {}
    try:
        parsed_json: dict[str, any] = json.loads(body[:json_size].decode())
    except Exception as e:
        print("error_json_size", json_size)
        print("error_body[:json_size]", body[:json_size])
        print(e)
   

    media_type_head_index = json_size
    payload_size_head_index = media_type_head_index + media_type_size
    
    media_type = body[media_type_head_index: payload_size_head_index].decode()
    payload = body[payload_size_head_index :]

    return parsed_json, media_type, payload