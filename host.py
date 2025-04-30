import socket, select, threading, time
from datetime import datetime


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

#Function to send message to all connected clients
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



if __name__ == "__main__":
	
	record={} 			#dictionary to store address corresponding to username
	connected_list = [] # List to keep track of socket descriptors
	last_seen = {}  	# Tracks last time we heard from each client
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
	##chat GPT code
	try:
		while True:
			rList, _, _ = select.select(connected_list, [], [])
			for sock in rList:
				if sock == server_socket:
					sockfd, addr = server_socket.accept()
					name = sockfd.recv(buffer).decode("utf-8").strip()
					if name in record.values():
						sockfd.send("\r\33[31m\33[1m Username already taken!\n\33[0m".encode("utf-8"))
						sockfd.close()
						continue
					record[addr] = name
					connected_list.append(sockfd)
					print(f"Client {addr} [{name}] connected")
					sockfd.send("\33[32m\r\33[1m Welcome to chat room. Enter 'clos3 or 3xit' anytime to exit\n\33[0m".encode("utf-8"))
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
							users_list = "\n".join(record.values())  # Join all the usernames from the record dictionary
							sock.send(f"Online users:\n{users_list}\n".encode("utf-8"))
							continue
						elif data.startswith("/msg "):
							parts = data.split(" ", 2)  # Split into /msg, user, message
							if len(parts) > 2:
								recipient_name = parts[1]
								private_message = parts[2]

								# Find the recipient's socket
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
							send_to_all(sock, chat_msg)
							print(f"[{datetime.now().strftime('%H:%M:%S')}] {chat_msg}")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {chat_msg}")
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