import socket

class UDPclient:
    def __init__(self, host, port,file_list):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_list = self._load_file_list(file_list)
        self.sock.settimeout(3)  # Set a default timeout for socket operations
        self.retries = 2  # Number of retries for sending files
        self.timeout = 5  # Default timeout for operations

    def _load_file_list(self, file_list):
        with open(file_list, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def send_files(self,socket,message,addr,timeout):
        ctimeout = timeout
        self.sock.settimeout(timeout) 
        for attempt in range(self.retries):
            try:
                socket.sendto(message.encode(), addr)
                response, _ = socket.recvfrom(1024)
                return response.decode()
            except socket.timeout:
                ctimeout *= 2  # Increase timeout for each retry
                self.sock.settimeout(ctimeout)
                print(f"the {attempt + 1} attempt failed, retrying...")
        


    def download_files(self,filename,size,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        addr = (self.addr[0], port)
        try:
            print(f"Starting download of {filename} from {addr[0]}:{addr[1]}")
            received_size = 0
            with open(filename, 'wb') as f:
                while received_size < size:
                    start = received_size
                    end = start + 1000
                   
                        
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











