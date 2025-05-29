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

    def download_files(self,filename,size,port):
        addr = (self.ip, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        try:
            sock.sendto(f"DOWNLOAD {filename} {size}".encode(), addr)
            print(f"Requesting download of {filename} from {addr}")
            with open(filename, 'wb') as f:
                while True:
                    data, _ = sock.recvfrom(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"Downloaded {filename} successfully.")
        except socket.timeout:
            print(f"Timeout while downloading {filename}.")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
        finally:
            sock.close()

    def verify_files(self,filename):
        try:
            with open(filename, 'rb') as f:
                data = f.read()
                if data:
                    print(f"File {filename} exists and is not empty.")
                else:
                    print(f"File {filename} is empty.")
        except FileNotFoundError:
            print(f"File {filename} does not exist.")
            




