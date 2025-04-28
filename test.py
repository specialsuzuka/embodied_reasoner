import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

for port in range(50000, 51000):
    if not check_port(port):
        print(f"Port {port} is available")