import socket

class UDPclient:
    def __init__(self, host, port,file_list):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_list = self._load_file_list(file_list)
        self.sock.settimeout(3)  # Set a default timeout for socket operations
        self.retries = 2  # Number of retries for sending files

    def _load_file_list(self, file_list):
        with open(file_list, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def send_files(self,socket,message,addr,timeout):
        ctimeout = timeout
        self.sock.settimeout(timeout) 
        for attempt in range(self.retries):
            try:
                socket.sendto(message.encode(), addr)
                print(f"Sent message to {addr}: {message}")
                return
            except socket.timeout:
                print(f"Attempt {attempt + 1} timed out. Retrying...")
                self.sock.settimeout(ctimeout * (attempt + 2))


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

    def start(self):

        print(f"Starting UDP client at {addr}")
        
        
if __name__ == "__main__":
    client.start()











