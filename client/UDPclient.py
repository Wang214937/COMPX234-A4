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
        self.retries = 5  # Number of retries for sending files
        self.timeout = 2  # Default timeout for operations

    def _load_file_list(self, file_list):
        with open(file_list, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def send_files(self,socket,message,addr,timeout):
        ctimeout = timeout
        for attempt in range(self.retries):
            try:
                socket.sendto(message.encode(), addr)
                response, _ = socket.recvfrom(1024)
                return response.decode()
            except socket.timeout:
                ctimeout *= 2  # Increase timeout for each retry
                self.sock.settimeout(ctimeout)
                print(f"Retry {attempt + 1} / {self.retries}")
        raise Exception("Max retries reached.")



    def download_files(self,filename,size,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        addr = (self.addr[0], port)

        try:
            print(f"[{filename}] Downloading {size} bytes" , end="", flush=True)
            received_size = 0
            with open(filename, 'wb') as f:
                while received_size < size:
                    start = received_size
                    end = min (start + 1000 -1, size - 1)

                    request = f"FILE{filename} GETSTART {start} END {end}"
                    response = self.send_files(sock, request, addr, self.timeout)

                    if not response.startswith(f"FILE {filename}"):
                        raise Exception(f"Unexpected response: {response}")
                    
                    if "OK" in response:
                        start = response.find('DATA') + 5
                        if start == -1:
                            raise Exception("DATA not found in response")
                        
                        encoded = response[start:]
                        try:
                            chunks = b64decode(encoded.encode('utf-8'))
                        except :
                            raise Exception("Base64 decode error")
                        
                        f.write(chunks)
                        received_size += len(chunks)
                        print("*", end="", flush=True)
                    else:
                        raise  Exception(f"Server error: {response}")

                close = f"FILE {filename} CLOSE"
                sock.sendto(close.encode(), addr)
                sock.settimeout(2)  # Short timeout for close confirmation
                try:
                    response, _ = sock.recvfrom(1024)
                    if  "CLOSE_OK" in response.decode():
                        print("\n Transfer complete.")
                except socket.timeout:
                    print("\n Warning: Close confirmation missing.")

            self.verify_files(filename)
        finally:
            sock.close()

    def verify_files(self,filename):
        sfile = os.path.join("files", filename)
        if not os.path.exists(sfile):
            print("Server file missing, skip verification.")
            return
        
        client_hash = hashlib.md5()
        with open(filename, 'rb') as f:
            while chunk := f.read(8192):
                client_hash.update(chunk)

        server_hash = hashlib.md5()
        with open(sfile, 'rb') as f:
            while chunk := f.read(8192):
                server_hash.update(chunk)

        if client_hash.hexdigest() == server_hash.hexdigest():
            print(f"MD5 hash verification OK:{client_hash.hexdigest()}")
        else:
            print(f"MD5 hash verification FAILED: Client {client_hash.hexdigest()} , Server:{server_hash.hexdigest()}")

    def start(self):
        for filename in self.file_list:
            print(f"Requesting download for {filename}")
            try:
                request = f"DOWNLOAD {filename}"
                response = self.send_files(self.sock, request, self.addr, self.timeout)

                if response.startswith("OK"):
                    try:
                        parts = response.split() 
                        size_index = parts.index("size") + 1
                        port_index = parts.index("port") + 1
                        size = int(parts[size_index])
                        port = int(parts[port_index])
                    except (ValueError, IndexError):
                        raise Exception(f"Invalid response format")

                    self.download_files(filename, size, port)    
                elif response.startswith("ERR"):
                    print(f"Server error: {response}")
                else:
                    print(f"Unexpected response format: {response}")
            except Exception as e:
                print(f"An error occurred: {e}")



        
        
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <host> <port> <file_list>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    file_list = sys.argv[3]

    client = UDPclient(host, port, file_list)
    client.start()











