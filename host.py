import socket, select, threading, time, json
from datetime import datetime
import re

# File to store users' persistent data
USER_DATA_FILE = "users.json"

def format_message(msg):
	msg = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", msg)  # Bold
	msg = re.sub(r"\*(.*?)\*", r"\033[3m\1\033[0m", msg)  # Italic
	msg = re.sub(r"__(.*?)__", r"\033[4m\1\033[0m", msg)  # Underline
	return msg

def emoji_format(msg):
	msg = msg.replace(":)", "😊").replace(":D", "😁").replace(":P", "😜")
	return msg

# Save user data to file
def save_users(user_data):
	with open(USER_DATA_FILE, "w") as f:
		json.dump(user_data, f, indent=4)

# Load user data from file
def load_users():
	try:
		with open(USER_DATA_FILE, "r") as f:
			return json.load(f)
	except FileNotFoundError:
		return {}

def heartbeat_monitor():
	while True:
		now = time.time()
		to_remove = []
		for sock in list(last_seen.keys()):
			if now - last_seen[sock] > pong_timeout:
				try:
					addr = sock.getpeername()
					print(f"[{datetime.now().strftime('%H:%M:%S')}] No response from {record.get(addr, 'Unknown')} — disconnecting")
					send_to_all(sock, f"{record.get(addr, 'Unknown')} timed out")
					sock.close()
					connected_list.remove(sock)
					del last_seen[sock]
					del record[addr]
				except:
					continue
		for sock in connected_list:
			if sock != server_socket:
				try:
					sock.send("__ping__\n".encode("utf-8"))
				except:
					continue
		time.sleep(ping_interval)

def log_message(msg):
    with open("host_chat_log.txt", "a") as f:
        f.write(msg + "\n")

def send_to_all (sock, message):
	#Message not forwarded to server and sender itself
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message.encode("utf-8"))
			except :
				# if connection not available
				socket.close()
				connected_list.remove(socket)

# Save user data when user disconnects
def on_disconnect(user_ip):
	if user_ip in user_data:
		del user_data[user_ip]  # Remove the user from memory
		save_users(user_data)  # Save the updated list to file
		print(f"User {user_ip} disconnected. User data saved.")

# Add user on connect
def add_user(user_ip, username):
	if user_ip not in user_data:
		user_data[user_ip] = username
		save_users(user_data)
		print(f"User {username} added.")
# Initialize the user data (either from file or an empty dictionary)
user_data = load_users()

##TODO: Check this tomake sure it works 
# def handle_new_connection(sockfd, addr):
# 	print("addr",addr)
#     # Check if the user is already in the persistent data
# 	if addr in user_data:
# 		username = user_data[addr]
# 		print(f"Restoring session for {username}")
# 		sockfd.send(f"Welcome back, {username}".encode("utf-8"))
# 	else:
# 		username = sockfd.recv(buffer).decode("utf-8").strip()
# 		print(f"Received username from client: {username}")
# 		while username in record.values():
# 			print(f"Username {username} is already taken. Asking for a new one...")
# 			sockfd.send("\r\33[31m\33[1mUsername already taken! Please choose a different one.\n\33[0m".encode("utf-8"))
# 			username = sockfd.recv(buffer).decode("utf-8").strip()
# 			print(f"Username changed to: {username}")
        
# 		user_data[addr] = username  # Save to persistent storage
# 		save_users(user_data)
# 		sockfd.send(f"Your username {username} is now active.".encode("utf-8"))
# 		print(f"User {username} accepted and added.")

#     # Proceed with the rest of the connection
# 	connected_list.append(sockfd)
# 	print(f"User {username} connected from {addr}")
# 	sockfd.send(f"Welcome to the chat room, {username}. Enter 'clos3' or '3xit' anytime to exit.".encode("utf-8"))
def handle_new_connection(sockfd, addr):
	# Check if the user is already in the persistent data
	if addr in user_data: 
		# Restore previous session or username
		username = user_data[addr]
		print(f"Restoring session for {username}")
		sockfd.send(f"Welcome back, {username}".encode("utf-8"))
	else:
		# Ask the user to set a new username
		username = sockfd.recv(buffer).decode("utf-8").strip()
		print(f"Received username from client: {username}")
		while username in record.values():
			print(f"Username {username} is already taken. Asking for a new one...")
			sockfd.send("\r\33[31m\33[1mUsername already taken! Please choose a different one.\n\33[0m".encode("utf-8"))
			username = sockfd.recv(buffer).decode("utf-8").strip()
			print(f"Username changed to: {username}")
		user_data[addr] = username  # Save to persistent storage
		save_users(user_data)

		sockfd.send(f"Your username {username} is now active.".encode("utf-8"))
		print(f"User {username} accepted and added.")

    # Proceed with the rest of the connection
	connected_list.append(sockfd)
	print(f"User {username} connected from {addr}")
	sockfd.send(f"Welcome back, {username}".encode("utf-8"))
	sockfd.send(f"Your username {username} is now active.".encode("utf-8"))  # Confirm the username is active

def handle_disconnect(sockfd, addr):
	if addr in user_data:
		del user_data[addr]  # Remove from memory
		save_users(user_data)  # Save the updated list to file
		print(f"User {addr} disconnected.")
	sockfd.close()
	connected_list.remove(sockfd)


if __name__ == "__main__":
	user_data = load_users()  # Load user data when the server starts
	record={} 			#dictionary to store address corresponding to username
	user_status = 	{}  # Store user statuses by address
	last_seen = {}  	# Tracks last time we heard from each client
	connected_list = [] # List to keep track of socket descriptors
	buffer = 4096
	port = 5001
	ping_interval = 30  # How often to send __ping__
	pong_timeout = 400   # Max time to wait for __pong__

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("localhost", port))
	server_socket.listen(10) #listen atmost 10 connection at one time

	# Add server socket to the list of readable connections
	connected_list.append(server_socket)
	print("\33[32m \t\t\t\tChat Server Started \33[0m")
	#Start heartbeat thread
	threading.Thread(target=heartbeat_monitor, daemon=True).start()
	try:
		while True:
			rList, _, _ = select.select(connected_list, [], [])
			for sock in rList:
				if sock == server_socket:
					sockfd, addr = server_socket.accept()
					name = sockfd.recv(buffer).decode("utf-8").strip()
					record[addr] = name
					connected_list.append(sockfd)
					print(f"Client {addr} [{name}] connected")
					join_msg = f"{name} joined the conversation"
					send_to_all(sockfd, join_msg)
					log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {join_msg}")
				else:
					try:
						data1 = sock.recv(buffer).decode("utf-8")
						if not data1:
							#Client clean disconnect
							i, p = sock.getpeername()
							disconnect_msg = f"{record[(i,p)]} disconnected"
							send_to_all(sock, disconnect_msg)
							print(f"[{datetime.now().strftime('%H:%M:%S')}] {disconnect_msg}")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {disconnect_msg}")
							del record[(i, p)]
							connected_list.remove(sock)
							sock.close()
							continue

						data = data1.strip()
						
						if data == "__pong__":
							last_seen[sock] = time.time()
							continue  # Don't process further

						i, p = sock.getpeername()
						if data in ("clos3", "3xit"):
							leave_msg = f"{record[(i, p)]} left the conversation"
							send_to_all(sock, leave_msg)
							print(f"Client ({i}, {p}) [{record[(i, p)]}] disconnected")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {leave_msg}")
							del record[(i, p)]
							connected_list.remove(sock)
							del last_seen[sock]
							sock.close()
						elif data.startswith("/users"):
							users_list = "\n".join([f"{record.get(addr)} ({user_status.get(addr, 'Online')})" for addr in record.keys()])  # Join all the usernames from the record dictionary
							sock.send(f"Online users:\n{users_list}\n".encode("utf-8"))
							continue
						elif data.startswith("/nick "):
							new_name = data.split(" ", 1)[1].strip()
							record[addr] = new_name
							sock.send(f"Your nickname has been changed to {new_name}".encode("utf-8"))
							send_to_all(sock, f"{record[addr]} changed their nickname to {new_name}")
						elif data.startswith("/status "):
							status = data.split(" ", 1)[1].strip()
							user_status[addr] = status
							sock.send(f"Your status is now: {status}".encode("utf-8"))
							send_to_all(sock, f"{record[addr]} is now {status}")
						elif data.startswith("/sendfile "):
							filename = data.split(" ", 1)[1].strip()
							file_data = sock.recv(4096)  # Receive the file data
							with open(filename, 'wb') as f:
								f.write(file_data)
							sock.send(f"File {filename} received.".encode("utf-8"))
						elif data.startswith("/msg "):
							parts = data.split(" ", 2)  # Split into /msg, user, message
							if len(parts) > 2:
								recipient_name = parts[1]
								private_message = parts[2]
								recipient_socket = None
								for s in connected_list:
									addr = s.getpeername()
									if record.get(addr) == recipient_name:
										print("s",s)
										print("addr",addr)
										recipient_socket = s
										break
								if recipient_socket:
									recipient_socket.send(f"Private message from {record.get(sock.getpeername())}: {private_message}".encode("utf-8"))
									sock.send(f"Private message to {recipient_name}: {private_message}".encode("utf-8"))
								else:
									sock.send(f"User {recipient_name} not found.".encode("utf-8"))
						else:
							chat_msg = f"{record[(i, p)]}: {data}"
							formatted_msg = format_message(chat_msg)
							formatted_msgE = emoji_format(formatted_msg)
							send_to_all(sock, formatted_msg)
							# send_to_all(sock, chat_msg)
							print(f"[{datetime.now().strftime('%H:%M:%S')}] {formatted_msgE}")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {formatted_msgE}")
							last_seen[sock] = time.time()
					except:
						try:
							i, p = sock.getpeername()
							error_msg = f"{record[(i, p)]} left unexpectedly"
							send_to_all(sock, error_msg)
							print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
							del record[(i, p)]
							connected_list.remove(sock)
							del last_seen[sock]
							sock.close()
						except:
							continue
	except KeyboardInterrupt:
		print("\n\33[31m\33[1m Server shutting down... \33[0m")
		server_socket.close()