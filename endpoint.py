import socket
import os
import logging

import hashlib
from uuid import getnode as get_mac

PORT = 11251
INTERFACE_NAME = 'Ethernet'
SECRET_WORD = "server"
SECRET_WORD_SHA = "b3eacd33433b31b5252351032c9b3e7a2e7aa7738d5decdf0dd6c62680853c06"

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def hashstr(st):
    return hashlib.sha256(st.encode('utf-8')).hexdigest()

def checkpass(st):
    pw = hashstr(SECRET_WORD) if SECRET_WORD_SHA == "" else SECRET_WORD_SHA
    if st == pw:
        return True
    else: return False

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(('8.8.8.8', 80)) 
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def waitformessage():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', PORT))
    #logger.info(f'Listening on :{PORT}')
    print(f'Listening on {PORT}')
    try:
        while True:
            data, addr = server_socket.recvfrom(1024)

            req = data.decode("utf-8")
            if(req):
                logger.info(f'Aqquired some data: {req} from {addr}')
                line = req.split("&")
                if checkpass(line[0]) == True:
                    logger.info(f'{addr} passed keyword check')
                    match line[1]:
                        case "status":
                            ip_addr = get_local_ip()
                            mac_addr = get_mac()
                            msg = socket.gethostname() + '&' + ip_addr + '&' + ':'.join(("%012X" % mac_addr)[i:i+2] for i in range(0, 12, 2))
                            server_socket.sendto(msg.encode('utf-8'), addr)
                            logger.info("Sent info to your mum")
                            continue
                        case "shut":
                            msg = "ok bye"
                            server_socket.sendto(msg.encode('utf-8'), addr)
                            
                            if os.name == 'posix':
                                os.system('sudo shutdown -h now')
                                os.system('systemctl shutdown')
                            elif os.name == 'nt':
                                os.system('shutdown -s -t 0 -f')
    except KeyboardInterrupt:
        print("Finishing serving...")
                        
                

            
waitformessage()
