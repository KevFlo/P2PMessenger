import socket, select
from datetime import datetime


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
	#dictionary to store address corresponding to username
	record={}
	# List to keep track of socket descriptors
	connected_list = []
	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("localhost", port))
	server_socket.listen(10) #listen atmost 10 connection at one time

	# Add server socket to the list of readable connections
	connected_list.append(server_socket)
	print("\33[32m \t\t\t\tChat Server Started \33[0m")

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
						i, p = sock.getpeername()
						if data in ("clos3", "3xit"):
							leave_msg = f"{record[(i, p)]} left the conversation"
							send_to_all(sock, leave_msg)
							print(f"Client ({i}, {p}) [{record[(i,p)]}] disconnected")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {leave_msg}")
							del record[(i, p)]
							connected_list.remove(sock)
							sock.close()
						else:
							chat_msg = f"{record[(i, p)]}: {data}"
							send_to_all(sock, chat_msg)
							print(f"[{datetime.now().strftime('%H:%M:%S')}] {chat_msg}")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {chat_msg}")	
					except:
						try:
							i, p = sock.getpeername()
							error_msg = f"{record[(i, p)]} left unexpectedly"
							send_to_all(sock, error_msg)
							print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
							log_message(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
							del record[(i, p)]
							connected_list.remove(sock)
							sock.close()
						except:
							continue
	except KeyboardInterrupt:
		print("\n\33[31m\33[1m Server shutting down... \33[0m")
		server_socket.close()

	###

	# while 1:
    #     # Get the list sockets which are ready to be read through select
	# 	rList,wList,error_sockets = select.select(connected_list,[],[])

	# 	for sock in rList:
	# 		#New connection
	# 		if sock == server_socket:
	# 			# Handle the case in which there is a new connection recieved through server_socket
	# 			sockfd, addr = server_socket.accept()
	# 			name=sockfd.recv(buffer).decode("utf-8")
	# 			connected_list.append(sockfd)
	# 			record[addr]= ""
	# 			#print "record and conn list ",record,connected_list
                
    #             #if repeated username
	# 			if name in record.values():
	# 				sockfd.send("\r\33[31m\33[1m Username already taken!\n\33[0m".encode("utf-8"))
	# 				del record[addr]
	# 				connected_list.remove(sockfd)
	# 				sockfd.close()
	# 				continue
	# 			else:
    #                 #add name and address
	# 				record[addr] = name
	# 				print("Client (%s, %s) connected" % addr," [",record[addr],"]")
	# 				sockfd.send("\33[32m\r\33[1m Welcome to chat room. Enter 'clos3 or 3xit' anytime to exit\n\33[0m".encode("utf-8"))
	# 				send_to_all(sockfd, "\33[32m\33[1m\r "+name.decode()+" joined the conversation \n\33[0m")

	# 		#Some incoming message from a client
	# 		else:
	# 			# Data from client
	# 			try:
	# 				data1 = sock.recv(buffer).decode("utf-8")
	# 				#print "sock is: ",sock
	# 				data=data1.strip()
	# 				print ("\ndata received: ",data)
                    
    #                 #get addr of client sending the message
	# 				i,p=sock.getpeername()
	# 				if data == "clos3" or data =="3xit":
	# 					msg="\r\33[1m"+"\33[31m "+record[(i,p)]+" left the conversation \33[0m\n"
	# 					send_to_all(sock,msg)
	# 					print("Client (%s, %s) is offline" % (i,p)," [",record[(i,p)],"]")
	# 					del record[(i,p)]
	# 					connected_list.remove(sock)
	# 					sock.close()
	# 					continue

	# 				else:
	# 					msg="\r\33[1m"+"\33[35m "+record[(i,p)]+": "+"\33[0m"+data+"\n"
	# 					send_to_all(sock,msg)
            
    #             #abrupt user exit
	# 			except:
	# 				(i,p)=sock.getpeername()
	# 				send_to_all(sock, "\r\33[31m \33[1m"+record[(i,p)]+" left the conversation unexpectedly\33[0m\n")
	# 				print("Client (%s, %s) is offline (error)" % (i,p)," [",record[(i,p)],"]\n")
	# 				del record[(i,p)]
	# 				connected_list.remove(sock)
	# 				sock.close()
	# 				continue

	# server_socket.close()
