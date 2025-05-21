import os
import socket
import subprocess
import sys
import shutil
import time
import argparse

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

def launch_server(port):
    script = f"""
import http.server
import socketserver
PORT = {port}
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('0.0.0.0', PORT), Handler) as httpd:
    print('Localhost:  http://localhost:{port}')
    print('LAN access: http://{get_local_ip()}:{port}')
    print('Note: Geolocation may not work without HTTPS.')
    httpd.serve_forever()
"""
    fname = "temp_server.py"
    with open(fname, "w") as f:
        f.write(script)

    if os.name == "nt":
        subprocess.Popen(["start", "cmd", "/k", f"python {fname}"], shell=True)
    else:
        subprocess.Popen(["gnome-terminal", "--", "python3", fname])

def launch_localtunnel(port):
    if not shutil.which("lt"):
        print("\nERROR: LocalTunnel not installed.\nInstall with: npm install -g localtunnel\n")
        return
    print("Launching secure tunnel (HTTPS)...")
    subprocess.Popen(["lt", "--port", str(port)])
    print("Public secure tunnel will be at: https://<random>.loca.lt")

def launch_cloudflared(port):
    if not shutil.which("cloudflared"):
        print("\nERROR: Cloudflare Tunnel not installed.\nInstall with: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install/\n")
        return
    print("Launching Cloudflare Tunnel (HTTPS)...")
    subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"])

def print_help(port):
    print("\nAccess Info:")
    print(f"  - Local:     http://localhost:{port}")
    print(f"  - LAN:       http://{get_local_ip()}:{port}")
    print("  - HTTPS:     Use --https to create secure public link for geolocation/camera")
    print("Note: Browsers require HTTPS to allow geolocation or camera access.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--https", action="store_true", help="Start secure HTTPS tunnel using LocalTunnel")
    parser.add_argument("--cloudflare", action="store_true", help="Use Cloudflare Tunnel instead of LocalTunnel")
    args = parser.parse_args()

    port = get_free_port()
    launch_server(port)
    time.sleep(2)
    print_help(port)

    if args.https:
        if args.cloudflare:
            launch_cloudflared(port)
        else:
            launch_localtunnel(port)
