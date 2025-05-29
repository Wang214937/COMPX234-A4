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