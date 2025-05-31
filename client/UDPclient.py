import socket
import os
from base64 import b64decode, b64encode
import sys
import hashlib

class UDPclient:
    def __init__(self, host, port,file_list):
        self.server_addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_list = self.load_file_list(file_list)
        self.sock.settimeout(2)  # Set a default timeout for socket operations
        self.retries = 5  # Number of retries for sending files
        self.timeout = 2  # Default timeout for operations

    def load_file_list(self, filename):
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def send_files(self, socket, message, addr, timeout):
        ctimeout = timeout
        for attempt in range(self.retries):
            try:
                socket.sendto(message.encode(), addr)
                response, _ = socket.recvfrom(1024)
                return response.decode()
            except socket.timeout:
                ctimeout *= 2
                socket.settimeout(ctimeout)
                print(f"  Retry {attempt+1}/{self.retries}")
        raise Exception("Max retries exceeded")



    def download_files(self,filename,size,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        addr = (self.server_addr[0], port)
        
        try:
            print(f"[{filename}] Downloading {size} bytes", end='', flush=True)
            received_size = 0
            with open(filename, 'wb') as f:
                while received_size < size:
                    start = received_size
                    end = min(start + 1000 - 1, size - 1)

                    request = f"FILE {filename} GETSTART {start} END {end}"
                    response = self.send_files(sock, request, addr, self.timeout)

                    if not response.startswith(f"FILE {filename}"):
                        raise Exception(f"Invalid response: {response}")
                    
                    if "OK" in response:
                        start = response.find("DATA") + 5
                        if start < 5:
                            raise Exception("DATA field missing in response")
                        
                        encoded = response[start:]
                        try:
                            chunks = b64decode(encoded.encode())
                        except:
                            raise Exception("Base64 decode error")

                        f.write(chunks)
                        received_size += len(chunks) 
                        print("*", end='', flush=True)
                    else:
                        raise Exception(f"Server error: {response}")
                        
                close = f"FILE {filename} CLOSE"
                sock.sendto(close.encode(), addr)
                sock.settimeout(2)
                try:
                    response, _ = sock.recvfrom(1024)
                    if "CLOSE_OK" in response.decode():
                        print("\n  Transfer completed")
                except socket.timeout:
                    print("\n  Warning: Close confirmation missing")

            self.verify_files(filename)
            
        finally:
            sock.close()

    def verify_files(self,filename):
        sfile = os.path.join("files", filename)
        if not os.path.exists(sfile):
            print(" Server file missing, skip verification")
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
            print(f"  MD5 verification OK: {client_hash.hexdigest()}")
        else:
            print(f"  MD5 verification FAILED! Client: {client_hash.hexdigest()}, Server: {server_hash.hexdigest()}")

    def start(self):
        for filename in self.file_list:
            print(f"\nRequesting {filename}...")
            try:
                request = f"DOWNLOAD {filename}"
                response = self.send_files(self.sock, request, self.server_addr, self.timeout)
                
                if response.startswith("OK"):
                    try:
                        parts = response.split()
                        size_index = parts.index("SIZE") + 1
                        port_index = parts.index("PORT") + 1
                        size = int(parts[size_index])
                        data_port = int(parts[port_index])
                    except (ValueError, IndexError):
                        raise Exception("Invalid response format")

                    self.download_files(filename, size, data_port)
                elif response.startswith("ERR"):
                    print(f"  Server error: {response[4:]}")
                else:
                    print(f"  Unknown response: {response}")
                    
            except Exception as e:
                print(f"Failed to download {filename}: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 udp_client.py <HOST> <PORT> <FILE_LIST>")
        exit(1)

    client = UDPclient(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    client.start()










