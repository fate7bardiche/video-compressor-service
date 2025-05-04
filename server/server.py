import sys
sys.path.append("..")
import socket
import config
import file_receive
import file_edit

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((config.server_address, config.server_port))
    sock.listen(5)

    connection, address  = sock.accept()

    uploaded_file_path, json_data, media_type, = file_receive.file_receive_main(connection)
    file_edit.file_edit_main(connection, uploaded_file_path, json_data, media_type)

