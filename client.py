import socket, select, string, sys, os, json
from datetime import datetime
from plyer import notification

#Helper function (formatting)
def display() :
	you="\33[33m\33[1m"+" You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def notify_user(message):
    notification.notify(
        title="New Message",
        message=message,
        timeout=10,
        # sound="ping"
    )

def log_message(msg):
    if log_enabled:
        with open("client_chat_log.txt","a") as f:
            f.write(msg + "\n")

def load_previous_session():
    # Check if a saved session file exists (e.g., username.json)
    if os.path.exists("session.json"):
        with open("session.json", "r") as f:
            return json.load(f)  # Return the saved session data (username, etc.)
    return None

def save_session(username):
    # Save the current session (username)
    with open("session.json", "w") as f:
        json.dump({"username": username}, f)

def reconnect():
    previous_session = load_previous_session()
    if previous_session:
        print(f"Reconnecting with previous session: {previous_session['username']}")
        return previous_session["username"]
    else:
        print("No previous session found. Please create a new username.")
        username = input("Enter username: ")
        save_session(username)  # Save the session for next time
        return username

log_enabled = True
def main():
    typing = False  # Initially, the user is not typing.
    global log_enabled
    username = reconnect()
    if len(sys.argv) < 2:
        host = input("Enter host ip address: ")
    else:
        host = sys.argv[1]
    port = 5001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
    except:
        print("\33[31m\33[1m Can't connect to the server \33[0m")
        sys.exit()

    #TODO: implement unique names and checking if username is being used
    
    s.send(username.encode("utf-8"))
    display()
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
                    # When receiving a message:
                    if not typing:  # check if user is typing
                        notify_user(f"New message: {decoded}")
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
                    elif msg.startswith("/status "):
                        s.send((msg + "\n").encode("utf-8"))
                    elif msg.startswith("/sendfile "):
                        filename = msg.split(" ", 1)[1].strip()
                        try:
                            with open(filename, 'rb') as file:
                                file_data = file.read()
                                s.send(file_data)
                        except Exception as e:
                            print(f"Error: {e}")
                    elif msg:
                        typing = True
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        s.send((msg + "\n").encode("utf-8"))
                        log_message(f"[{timestamp}] You: {msg}")
                    display()
                    typing = False
                
    except KeyboardInterrupt:
        print("\n\33[31m\33[1m Client exiting... \33[0m")
        s.close()
        sys.exit()

if __name__ == "__main__":
    main()