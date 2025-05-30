import socket
import os
from base64 import b64decode, b64encode
import sys
import hashlib

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

                    request = f"GET {filename} {start} {end}"
                    response = self.send_files(sock, request, addr, self.timeout)
                    if not response.startswith(f"FILE {filename}"):
                        raise ValueError(f"Unexpected response: {response}")
                    
                    if "OK" in response:
                        start = response.find('DATA') + 5
                        if start == -1:
                            raise ValueError("Invalid response format.")
                        
                        encoded = response[start:]
                        chunks = b64decode(encoded.encode())
                        f.write(chunks)

                        received_size += len(chunks)
                        print(f"Received {received_size} bytes of {filename}")
                    else:
                        raise ValueError(f"Unexpected response: {response}")

                close = f"GET {filename} {received_size} {size}"
                sock.sendto(close.encode(), addr)
                sock.settimeout(2)  # Short timeout for close confirmation
                try:
                    response, _ = sock.recvfrom(1024)
                    if response.decode() == "CLOSE":
                        print(f"Download of {filename} completed successfully.")
                    else:
                        print(f"Unexpected response after download: {response.decode()}")
                except socket.timeout:
                    print(f"Timeout waiting for close confirmation for {filename}.")
        finally:
            sock.close()

    def verify_files(self,filename):
        sfile = os.path.join("files", filename)
        if not os.path.exists(sfile):
            print(f"File {filename} does not exist.")
            return
        
        client_hash = hashlib.md5()
        with open(filename, 'rb') as f:
            while chunk := f.read(8192):
                client_hash.update(chunk)

        server_hash = hashlib.md5()
        with open(sfile, 'rb') as f:
            while chunk := f.read(8192):
                server_hash.update(chunk)

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











