import socket 
import threading
import os

class UDPServer:
    def __init__(self, port, file_list):
        self.port = port
        self.file_list = self._load_file_list(file_list)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        print(f"UDP Server started on port {self.port}")

    def start(self):
        threading.Thread(target=self._listen_for_requests, daemon=True).start()
        print(f"UDP Server is listening on port {self.port}")
        while True:
            data, addr = self.sock.recvfrom(1024)
            decoded_data = data.decode('utf-8')
            print(f"Received request from {addr}: {decoded_data}")

            