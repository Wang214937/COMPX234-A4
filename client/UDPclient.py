import socket

class UDPclient:
    def __init__(self, ip, port,file_list):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_list = self._load_file_list(file_list)

    def _load_file_list(self, file_list):
        with open(file_list, 'r') as f:
            return [line.strip() for line in f if line.strip()]
