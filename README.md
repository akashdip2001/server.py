# server.py

# ⛳ LAN

```perl
my-website/
│
├── index.html
├── serve.py  <- Python script goes here
```
---

## Features of the Script

- Port Scanning: Tries port 5500 and increments until it finds a free one.
- Cross-Platform Terminal Support:
    - On Windows: opens PowerShell or Command Prompt.
    - On Linux: opens the default terminal.

- Python Check:
    - On Windows: warns if Python is missing.
    - On Linux: offers to install Python via apt if not found.

- Live Logging in a dedicated terminal window.
- Clear access instructions for browser (local + LAN IP).

---

https://github.com/user-attachments/assets/4025ec9f-ca5a-4488-90cc-a901e14c2a7d


### 🟢 Step 1: Run the server

- Double-click the script, or
- From the terminal or command prompt, navigate to the folder and run:

```bash
python serve.py
```

This will:

* Serve files from the current directory.
* Make them accessible via:

  * `http://localhost:5500` (on the same machine)
  * `http://<your-laptop-IP>:5500` (from your mobile on the same network)

---

### 🟢 Step 2: Open it on your mobile

1. Make sure both devices are on the same Wi-Fi/LAN.
2. Use the IP address shown in the terminal on your mobile browser (e.g., `http://192.168.1.5:5500`).

---

# ⛳ WAN

I want to create a single smart Python script that:

* **Starts a local server**
* **Finds a free port**
* **Offers to expose via a secure HTTPS tunnel using LocalTunnel or Cloudflare**
* **Tells developer what features may/may not work based on their access method (like geolocation over HTTP)**
* **Provides CLI options like `--https` to force a tunnel for geolocation**

---

## Why `HTTPS` ?? not `HTTP` -- **Core Problem**

### Browsers block location (and other sensitive APIs) unless the site is:

* **Served over HTTPS**, or
* **Running on localhost**

So if i serving from `192.168.x.x:5500` over **HTTP**, the browser will **refuse to share geolocation** (and some other APIs like camera/mic access).

---

## **Goal**

1. Works on **both Windows & Linux**
2. Serves content on **localhost + LAN**
3. Also optionally exposes **HTTPS-secured public tunnel** (so geolocation, camera, or microphone access works)
4. Detects all this automatically and guides the developer clearly

---

## **WAN Dev Server Python Script**

Here’s a flexible and fully featured `perfect_dev_server.py`:

```python
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
```

---

## **How to Use ??**

1. Install dependencies:

   * `npm install -g localtunnel`
   * *(Optional)* Install Cloudflare Tunnel (`cloudflared`)

2. Run the script:

   ```bash
   python perfect_dev_server.py
   ```

3. If your project uses geolocation:

   ```bash
   python perfect_dev_server.py --https
   ```

4. Want Cloudflare instead?

   ```bash
   python perfect_dev_server.py --https --cloudflare
   ```

---
---

# ⛳ WAN 0.2

---

* Auto port detection
* Dual terminal (one for logs, one for control)
* Secure WAN tunneling via LocalTunnel
* CLI menu with full control

---

### Save this as: `server.py`

```python
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
```

---

## How to Use:

### 1. **Put `index.html` and files in the same folder**

### 2. **Run the script:**

* Double-click on Windows
* Or run from terminal:

  ```bash
  python server.py
  ```

### 3. **Use menu options to control**

* Stop/start tunnel
* Exit server
* Switch between WAN/LAN

---

## ⚠️ Let’s upgrade the server with auto-reload capability, so any file changes (like .html, .css, .js, etc.) in the project directory will automatically be reflected without restarting the server.


---

#### UPDATE REQUIRED 

1. Watch the project directory for file changes.

2. On change:

Reload the HTTP server (if required — usually browsers auto-refresh for static files).

Optional: Auto-refresh browser using WebSocket/live-reload script injection.

---

Best Option for Static File Monitoring in Python

We’ll use:

http.server for serving static files (already good)

watchdog (Python library) to detect changes

Optional: inject LiveReload for automatic browser refresh



---

Upgrade Strategy

- Option 1 — Basic Auto-Restart

Simplest: When a file changes:

Restart server


- Option 2 — Auto-Browser Reload (Best for UX)

LiveReload with:

livereload.Server.watch()

Browser auto-refreshes when any .html, .css, .js changes

