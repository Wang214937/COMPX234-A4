import socket 
import threading
import os
from base64 import b64encode
import sys
import random

class FileThread(threading.Thread):
    def __init__(self, filename, addr, port):
        super().__init__()
        self.filename = filename
        self.addr = addr
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        self.sock.bind(('', self.port))
        self.chunk_size = 1000  # Size of each chunk to send
        self.file_path = os.path.join("files", filename)
        

    def run(self):
        try:
            if not os.path.exists(self.file_path):
                err = f"ERROR File not found: {self.filename}"
                self.sock.sendto(err.encode('utf-8'), self.addr)
                return

            file_size = os.path.getsize(self.file_path)
            with open(self.file_path, 'rb') as f:
                while True:
                    try:
                        data,addr = self.sock.recvfrom(1024)
                        decodeed = data.decode('utf-8').strip()

                        if not decodeed.startswith("FILE"):
                            print(f"Invalid request: {decodeed}")
                            continue

                        if "CLOSE" in decodeed:
                            print(f"Closing connection for {self.filename}")
                            self.sock.sendto("CLOSE".encode('utf-8'), self.addr)
                            break
                        
                        parts = decodeed.split()
                        if len(parts) < 2 or parts[1] != "FILE" or parts[1] != self.filename:
                            continue

                        try:
                            start_index = parts.index("START") + 1
                            end_index = parts.index("END") + 1
                            start = int(parts[start_index])
                            end = int(parts[end_index])
                        except ValueError:
                            err = f"ERROR Invalid request format for file {self.filename}"
                            self.sock.sendto(err.encode('utf-8'), self.addr)
                            continue    

                        if start < 0 or end >= file_size or start > end:
                            err = f"ERROR Invalid range: {start}-{end} for file {self.filename}"
                            self.sock.sendto(err.encode('utf-8'), self.addr)
                            continue

                        f.seek(start)
                        chunk = f.read(end - start + 1)
                        if not chunk:
                            err = f"ERROR No data to send for {self.filename} in range {start}-{end}"
                            self.sock.sendto(err.encode('utf-8'), self.addr)
                            continue

                        encoded = b64encode(chunk).decode('utf-8')
                        response = f"FILE {self.filename} DATA {encoded}"
                        self.sock.sendto(response.encode('utf-8'), self.addr)

                    except socket.timeout:
                        print(f"Timeout waiting for request for {self.filename}")
                        continue
        
        except Exception as e:
            print(f"Error in FileThread for {self.filename}: {e}")
        finally:
            self.sock.close()
            print(f"FileThread for {self.filename} finished.")



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
                    filename = decoded_data.split()[1]
                    file_path = os.path.join(os.path(), filename)

                    if os.path.exists(file_path):
                        port = random.randint(50000, 51000)
                        size = os.path.getsize(file_path)
                        response = f"DOWNLOAD {filename} {port} {size}"
                        self.sock.sendto(response.encode('utf-8'), addr)
                        file_thread = FileThread(filename, addr, port, self.sock)
                        file_thread.start()

                    else:
                        response = f"ERROR File not found: {filename}"
                        self.sock.sendto(response.encode('utf-8'), addr)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python UDPserver.py <port>")
        sys.exit(1)

    if not os.path.exists("files"):
        os.makedirs("files")
        
    server = UDPServer(int(sys.argv[1]), sys.argv[2])
    server.start()
    