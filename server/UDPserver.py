import socket 
import threading
import os
from base64 import b64encode
import sys
import random

class FileThread(threading.Thread):
    def __init__(self, filename, client_addr, data_port):
        super().__init__()
        self.filename = filename
        self.client_addr = client_addr
        self.data_port = data_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        self.sock.bind(('', data_port))
        self.chunk_size = 1000  # Size of each chunk to send
        self.file_path = os.path.join("files", filename)
        

    def run(self):
        try:
            if not os.path.exists(self.file_path):
                err = f"FILE {self.filename} ERR FILE_NOT_FOUND"
                self.sock.sendto(err.encode(), self.client_addr)
                return
            
            file_size = os.path.getsize(self.file_path)
            with open(self.file_path, 'rb') as f:
                while True:
                    try:
                        data,addr = self.sock.recvfrom(1024)
                        decoded = data.decode('utf-8').strip()

                        if not decoded.startswith("FILE"):
                            continue

                        if "CLOSE" in decoded:
                            self.sock.sendto(f"FILE {self.filename} CLOSE_OK".encode('utf-8'), addr)
                            break
                        
                        parts = decoded.split()
                        if len(parts) < 2 or parts[1] != self.filename:
                            continue

                        try:
                            start_index = parts.index("GETSTART") + 1
                            end_index = parts.index("END") + 1
                            start = int(parts[start_index])
                            end = int(parts[end_index])
                        except (ValueError, IndexError):
                            err = f"FILE{self.filename} ERR INVALID_RANGE"
                            self.sock.sendto(err.encode('utf-8'), addr)
                            continue    

                        if start < 0 or end >= file_size or start > end:
                            err = f"FILE{self.filename} ERR INVALID_RANGE"
                            self.sock.sendto(err.encode('utf-8'), addr)
                            continue

                        f.seek(start)
                        chunk = f.read(end - start + 1)
                        if not chunk:
                            err = f"FILE{self.filename} ERR READ_ERROR"
                            self.sock.sendto(err.encode('utf-8'), addr)
                            continue

                        encoded = b64encode(chunk).decode('utf-8')
                        response = (f"FILE {self.filename} OK START {start} END {end} DATA {encoded}")
                        self.sock.sendto(response.encode('utf-8'), addr)

                    except socket.timeout:
                        continue
                    except Exception as e:
                        print(f"Transfer error : {e}")
                        break

        except Exception as e:
            print(f"Transfer thread error: {e}")
        finally:
            self.sock.close()
            print(f"Closed transfer port {self.data_port}")



class UDPServer:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', port))
        print(f"UDP Server started on port {port}")

    def start(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                decoded_data = data.decode('utf-8').strip()

                if decoded_data.startswith("DOWNLOAD"):
                    try:
                        filename = decoded_data.split(maxsplit=1)[1].strip()
                    except IndexError:
                        continue
                        
                    file_path = os.path.join("files", filename)

                    if os.path.exists(file_path):
                        port = random.randint(50000, 51000)
                        size = os.path.getsize(file_path)
                        response = f"OK {filename} SIZE {size} PORT {port}"
                        self.sock.sendto(response.encode('utf-8'), addr)
                        file_thread = FileThread(filename, addr, port)
                        file_thread.start()
                        print(f"Started transfer for {filename} on port {port}")
                    else:
                        response = f"ERR {filename} NOT_FOUND"
                        self.sock.sendto(response.encode('utf-8'), addr)

            except Exception as e:
                print(f"Main server error : {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 UDPserver.py <port>")
        exit(1)

    if not os.path.exists("files"):
        os.makedirs("files")

    server = UDPServer(int(sys.argv[1]))
    server.start()