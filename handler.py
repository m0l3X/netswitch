import socket
import os
import logging
#import psutil
import sys
import hashlib
import json


PORT = 11250
ENDPOINT_PORT = 11251
INTERFACE_NAME = 'Ethernet'
SUBNET_BROADCAST = "255.255.255.255"

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# netswitch ip ippass com keyword
# netswitch ip com keyword

IP_PASS = None

nettable = {}
try:
    with open('nettable.json', 'r') as file:
        nettable = json.load(file)
except:
    nettable = {}

if("IP_PASS" in nettable): # put your HASHED password in there!!!!!!!!!!
    IP_PASS = nettable["IP_PASS"]

def hashstr(st):
    return hashlib.sha256(st.encode('utf-8')).hexdigest()

def checkpass(st, pw):
    if st == pw:
        return True
    else: return False

def beatify_msg(msg):
    s = msg.split('&')
    out = "Output:\n"
    for i in range(0,len(s)):
        out += f"{i}: {s[i]} \n"
    return out
    
def waitformessage():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', PORT))
    #logger.info(f'Listening on :{PORT}')
    logger.info(f'Listening on {PORT}')
    while True:
        data, addr = server_socket.recvfrom(1024)

        req = data.decode("utf-8")
        if(req):
            logger.info(f'Aqquired some data: {req} from {addr}')
            line = req.split('&')
            if IP_PASS == None:
                if len(line) != 2:
                    msg = b"Incorrect amount of arguments, perhaps the net doesn't have a password?"
                    server_socket.sendto(msg, addr)
                    continue
                
                    
            if IP_PASS != None:
                if len(line) != 3:
                    msg = b"Incorrect amount of arguments, perhaps the net DOES have a password?"
                    server_socket.sendto(msg, addr)
                    continue
                if checkpass(line[0], IP_PASS) == False:
                    msg = b"Incorrect net password"
                    server_socket.sendto(msg, addr)
                    continue
                del line[0]
            match(line[1]):
                case "status":
                    msg = sendtodev(line, server_socket, line[1])
                    server_socket.sendto(beatify_msg(msg).encode('utf-8'), addr)
                    continue
                case "shut":
                    msg = sendtodev(line, server_socket, line[1])
                    server_socket.sendto(beatify_msg(msg).encode('utf-8'), addr)
                    continue

                case "wake":
                    if line[0] not in nettable:
                        msg = b"Specified device doesn't have assigned MAC address to send WOL packet to. Try status-ing it while it's awake to acquire MAC \n or type netswitch <net> <netpass> wakemac <mac> "
                    else:
                        send_wol(nettable[line[0]]["MAC"])
                        msg = b"Sent WOL packet to device"
                    server_socket.sendto(msg, addr)
                case "wakemac":
                    send_wol(line[0])
                    msg = b"Sent WOL packet to mac (unsafe)"
                    server_socket.sendto(msg, addr)
                case _:
                    msg = b"Unknown command"
                    server_socket.sendto(msg, addr)
                    continue
                        

def send_wol(mac_address):
    clean_mac = mac_address.replace('-', '').replace(':', '')
    mac_bytes = bytes.fromhex(clean_mac)
    
    packet = b'\xff' * 6 + mac_bytes * 16
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(packet, (SUBNET_BROADCAST, 9))
        logger.info(f"Sent WOL packet to {mac_address}")
    
def sendtodev(line, server_socket, com):
    if line[0] not in nettable:
    #msg = b"Yo i'm fine, how are you?"\
        logger.info(f"didn't find {line[0]} in net table, broadcasting for such device")
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       
        send = line[0]+'&'+com
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(2)
        logger.info(f'sent to 255.255.255.255 {ENDPOINT_PORT}')
        try:
            while True:
                s.sendto(send.encode('utf-8'), (SUBNET_BROADCAST, ENDPOINT_PORT))
                data = s.recv(1024)
                if data:
                    msg = data.decode('utf-8')
    
                    break
                    
        except socket.timeout:
            msg = "Couldn't get response from keyword device, Is desired device is online or perhaps it doesn't even exist?"
        s.close()
        if('&' in msg):
            ass = msg.split('&')
            nettable[line[0]] = {'IP':ass[1], 'MAC':ass[2]}
            with open("nettable.json", "w") as fp:
                json.dump(nettable, fp)
    else:
        logger.info(f"found {line[0]} in net table, trying to reach via ip")
       
        send = line[0]+'&'+com
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                ip = nettable[line[0]]["IP"]
                s.settimeout(1)
                s.connect((ip, ENDPOINT_PORT))  # Connect to the server
                logger.info(f"sent to {(ip, ENDPOINT_PORT)}")
                while True:
                    s.sendall(send.encode('utf-8'))
                    data = s.recv(1024)
                    if(data):
                        msg = data.decode('utf-8')
                        break                    
        except socket.timeout:
            s.close()
            msg = "Couldn't get response from keyword device, Is desired device is online or perhaps it doesn't even fucking exist?"
            logger.info("Ip didn't work, so we try broadcasting again")
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       
            send = line[0]+'&'+com
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(2)
            logger.info(f"sent to 192.168.1.255 {ENDPOINT_PORT}")
            try:
                while True:
                    s.sendto(send.encode('utf-8'), (SUBNET_BROADCAST, ENDPOINT_PORT))
                    data = s.recv(1024)
                    if data:
                        msg = data.decode('utf-8')
        
                        break
                        
            except socket.timeout:
                msg = "Couldn't get response from keyword device, Is desired device is online or perhaps it doesn't even exist?"
            s.close()


    logger.info(beatify_msg(msg))
    return msg
    
            
waitformessage()
