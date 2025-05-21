import os
import socket
import subprocess
import sys
import shutil
import time
import platform
import threading

def get_free_port(start=5500):
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports available.")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def launch_server_script(port, log_mode=False):
    script = f'''
import http.server
import socketserver
PORT = {port}
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('0.0.0.0', PORT), Handler) as httpd:
    print('Server running on http://localhost:{port}')
    httpd.serve_forever()
'''
    fname = "temp_server.py"
    with open(fname, "w") as f:
        f.write(script)

    if log_mode:
        if os.name == "nt":
            subprocess.Popen(["start", "cmd", "/k", f"python {fname}"], shell=True)
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", f"python3 {fname}"])
    else:
        return subprocess.Popen([sys.executable, fname])

def check_dependencies():
    node_installed = shutil.which("node") is not None
    npm_installed = shutil.which("npm") is not None
    lt_installed = shutil.which("lt") is not None
    if not node_installed or not npm_installed:
        print("ERROR: Node.js and npm are required for tunneling. Please install them from https://nodejs.org/")
        return False
    if not lt_installed:
        print("Installing LocalTunnel...")
        subprocess.call(["npm", "install", "-g", "localtunnel"])
    return True

def start_localtunnel(port):
    print("Starting LocalTunnel...")
    return subprocess.Popen(["lt", "--port", str(port)])

def interactive_menu(port, tunnel_proc):
    while True:
        print("\n--- Control Menu ---")
        print(f"[1] Stop Tunnel ({'Active' if tunnel_proc else 'Inactive'})")
        print("[2] Stop Server")
        print("[3] Restart Server")
        print("[4] Return to LAN Only")
        print("[5] Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1" and tunnel_proc:
            print("Stopping tunnel...")
            tunnel_proc.terminate()
            tunnel_proc = None
        elif choice == "2":
            print("Stopping server...")
            os._exit(0)
        elif choice == "3":
            print("Restarting server...")
            os._exit(100)
        elif choice == "4" and tunnel_proc:
            print("Returning to LAN only...")
            tunnel_proc.terminate()
            tunnel_proc = None
        elif choice == "5":
            print("Exiting...")
            if tunnel_proc:
                tunnel_proc.terminate()
            os._exit(0)
        else:
            print("Invalid option or tunnel not active.")

def main():
    port = get_free_port()
    local_ip = get_local_ip()

    print(f"Launching HTTP server on port {port}...")
    launch_server_script(port, log_mode=True)  # Logging terminal
    server_proc = launch_server_script(port)   # Internal use

    print(f"Localhost:  http://localhost:{port}")
    print(f"LAN:       http://{local_ip}:{port}")
    print("Note: Browsers block geolocation on HTTP (except localhost).")

    wan_option = input("Do you want to enable public internet access via secure HTTPS tunnel? (Y/n): ").strip().lower()
    tunnel_proc = None

    if wan_option == "y":
        if check_dependencies():
            tunnel_proc = start_localtunnel(port)
            print("Tunnel running. Public HTTPS link will appear in the new terminal or your browser.")

    interactive_menu(port, tunnel_proc)

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code == 100:
            print("Restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)