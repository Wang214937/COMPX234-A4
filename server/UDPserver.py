import socket 
import threading
import os


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
        if not os.path.exists(self.file_path):
            err = f"ERROR File not found: {self.filename}"
            self.sock.sendto(err.encode('utf-8'), self.addr)
            return
        
        file_size = os.path.getsize(self.file_path)
        with open(self.file_path, 'rb') as f:
            while True:
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
                try:
                    start_index = parts.index("START") + 1
                    end_index = parts.index("END") + 1
                    start = int(parts[start_index])
                    end = int(parts[end_index])
                except ValueError:
                    print(f"Invalid request: {decodeed}")
                    continue    




class UDPServer:
    def __init__(self, port, file_list):
        self.port = port
        self.file_list = self._load_file_list(file_list)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        print(f"UDP Server started on port {self.port}")

    def start(self):
        threading.Thread(target=self._listen_for_requests, daemon=True).start()
        print(f"UDP Server is listening on port {self.port}")
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                decoded_data = data.decode('utf-8')
                print(f"Received request from {addr}: {decoded_data}")

                if decoded_data.startswith("DOWNLOAD"):
                    filename = decoded_data.split()[1]
                    file_path = os.path.join(os.path(), filename)

                    if os.path.isfile(file_path):
                        port = 51234
                        size = os.path.getsize(file_path)
                        response = f"DOWNLOAD {filename} {port} {size}"
                        self.sock.sendto(response.encode('utf-8'), addr)
                        self._send_file(filename, addr, port)
                    else:
                        response = f"ERROR File not found: {filename}"
                        self.sock.sendto(response.encode('utf-8'), addr)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    port = 12345
    file_list = ['file1.txt', 'file2.txt']  # Example file list
    server = UDPServer(port, file_list)
    server.start()