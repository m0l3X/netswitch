import socket
import threading
import time
import logging
import subprocess
import sys
import hashlib

class Spinner:
    busy = False
    delay = 0.25

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False

PORT = 11250

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# netswitch ip ippass com keyword
# netswitch ip com keyword

IP_PASS = None

if(len(sys.argv) == 5):
    IP = sys.argv[1]
    IP_PASS = sys.argv[2]
    COM = sys.argv[3]
    KEY = sys.argv[4]
elif(len(sys.argv) == 4):
    IP = sys.argv[1]
    COM = sys.argv[2]
    KEY = sys.argv[3]
else:
    raise Exception("""Incorrect arguments 
    Usage: netswitch <network ip> <network password (if exists)> <command> <device keyword>
    Avaiable commands: status, shut, wake, wakemac
                    """)


def allow_port_windows(port, name, protocol="UDP"):
    try:
        # Command for modern Windows (Vista onwards)
        cmd = f'netsh advfirewall firewall add rule name="{name}" dir=in action=allow protocol={protocol} localport={port}'
        subprocess.run(cmd, check=True, shell=True)
        print(f"Rule '{name}' added successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add rule: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
#allow_port_windows(11250,"netswitch")

def hashstr(st):
    return hashlib.sha256(st.encode('utf-8')).hexdigest()



def send(add,encrypt_name=True,ip=IP,port=PORT,ip_pass=IP_PASS,key=KEY):
    skey = hashstr(key) if encrypt_name else key
    if ip_pass != None:
        send = hashstr(ip_pass) + "&" + skey+"&"+add  #mac_address.replace('-', '').replace(':', '')
    else:
        send = skey+"&"+add  #mac_address.replace('-', '').replace(':', '')

    packet = send.encode('utf-8')

    data = b"Couldn't get response! Is desired net is online or perhaps yours may not?"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(10)
        s.connect((ip, port))  # Connect to the server
        print(f"Sent a {add} signal to {key} on {ip}:{port}... ", end='')
        with Spinner():
            try:
                while True:
                    s.sendall(packet)
                    data = s.recv(1024)
                    if(data): 
                        break   
            except socket.timeout:
                print("Timed out")           
    return data.decode("utf-8")
    
    
try:
    match(COM):
        case "status":
            out = send("status")
            print(out)
        case "shut":
            out = send("shut")
            print(out)
        case "wake":
            out = send("wake")
            print(out)
        case "wakemac":
            out = send("wakemac",False)
            print(out)
except KeyboardInterrupt:
    print("stopped")