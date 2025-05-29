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

    def send_files(self,socket,addr,timeout=5):
        self.sock.settimeout(timeout) 
        for file_name in self.file_list:
            try:
                with open(file_name, 'rb') as f:
                    data = f.read()
                    socket.sendto(data, addr)
                    print(f"Sent {file_name} to {addr}")
            except FileNotFoundError:
                print(f"File {file_name} not found.")
            except Exception as e:
                print(f"Error sending {file_name}: {e}")



