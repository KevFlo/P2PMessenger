import socket, select, string, sys
from datetime import datetime

#Helper function (formatting)
def display() :
	you="\33[33m\33[1m"+" You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def log_message(msg):
    with open("client_chat_log.txt","a") as f:
        f.write(msg + "\n")

def main():

    if len(sys.argv)<2:
        host = input("Enter host ip address: ")
    else:
        host = sys.argv[1]

    port = 5001
    
    #asks for user name
    name = input("\33[34m\33[1m CREATING NEW ID:\n Enter username: \33[0m")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    try:
        s.connect((host, port))
    except:
        print("\33[31m\33[1m Can't connect to the server \33[0m")
        sys.exit()

    #if connected
    s.send(name.encode("utf-8"))
    display()


    ###Chatgpt code
    try:
        while True:
            socket_list = [sys.stdin, s]
            rList, _, _ = select.select(socket_list, [],[])

            for sock in rList:
                if sock == s:
                    data = sock.recv(4096)
                    if not data:
                        print('\33[31m\33[1m \rDISCONNECTED!!\n \33[0m')
                        sys.exit()
                    else:
                        decoded = data.decode()
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        msg = f"[{timestamp}] {decoded.strip()}"
                        print(f"\r{msg}")
                        log_message(msg)
                        display()
                else:
                    msg = sys.stdin.readline().strip()
                    if msg:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        s.send((msg + "\n").encode("utf-8"))
                        log_message(f"[{timestamp}] You: {msg}")
                    display()
    except KeyboardInterrupt:
        print("\n\33[31m\33[1m Client exiting... \33[0m")
        s.close()
        sys.exit()


    # while 1:
    #     socket_list = [sys.stdin, s]
        
    #     # Get the list of sockets which are readable
    #     rList, wList, error_list = select.select(socket_list , [], [])
        
    #     for sock in rList:
    #         #incoming message from server
    #         if sock == s:
    #             data = sock.recv(4096)
    #             if not data :
    #                 print('\33[31m\33[1m \rDISCONNECTED!!\n \33[0m')
    #                 sys.exit()
    #             else :
    #                 print("initial msg")
    #                 sys.stdout.write(data.decode())
    #                 display()
    #         #user entered a message
    #         else :
    #             msg=sys.stdin.readline().strip()
    #             # s.send("Typing...".encode("utf-8"))
    #             s.send((msg + "\n").encode("utf-8"))
    #             display()

if __name__ == "__main__":
    main()