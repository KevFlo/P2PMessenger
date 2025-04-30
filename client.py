import socket, select, string, sys
from datetime import datetime

#Helper function (formatting)
def display() :
	you="\33[33m\33[1m"+" You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def log_message(msg):
    if log_enabled:
        with open("client_chat_log.txt","a") as f:
            f.write(msg + "\n")

log_enabled = True
def main():
    global log_enabled
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

                    decoded = data.decode().strip()
                    if decoded == "__ping__":
                        s.send("__pong__\n".encode("utf-8"))
                        continue

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg = f"[{timestamp}] {decoded}"
                    print(f"\r{msg}")
                    log_message(msg)
                    display()
                else:
                    msg = sys.stdin.readline().strip()
                    if msg == "/help":
                        print("""
                        \33[36m\33[1mAvailable Commands:
                        /users           - Show list of online users
                        /msg <user> <msg> - Send a private message
                        /nick <newname>  - Change your nickname
                        /log on|off      - Enable or disable chat logging
                        /exit or /quit   - Exit the chat
                        /help            - Show this help message
                        \33[0m
                        """)
                        display()
                        continue
                    elif msg == "/exit" or msg == "/quit":
                        print("\33[31m\33[1mExiting...\33[0m")
                        s.close()
                        sys.exit()
                    elif msg == "/log off":
                        log_enabled = False
                        print("\33[33m\33[1mLogging disabled.\33[0m")
                        display()
                        continue
                    elif msg == "/log on":
                        log_enabled = True
                        print("\33[33m\33[1mLogging enabled.\33[0m")
                        display()
                        continue
                    elif msg.startswith("/users"):
                        s.send("/users\n".encode("utf-8"))  # send plain
                    elif msg.startswith("/msg "):
                        s.send((msg + "\n").encode("utf-8"))
                    elif msg:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        s.send((msg + "\n").encode("utf-8"))
                        log_message(f"[{timestamp}] You: {msg}")
                    display()
                
    except KeyboardInterrupt:
        print("\n\33[31m\33[1m Client exiting... \33[0m")
        s.close()
        sys.exit()

if __name__ == "__main__":
    main()