import socket
import sys
from sys import argv, stdout
from threading import Thread,Lock
from time import sleep, strftime
from Crypto.PublicKey import RSA
import crypto
from Crypto.Cipher import AES

class Peer:
	# initialize the peer
	# conf = id, name, connectTo
	def __init__(self, inPort, config, outPort): 
		self.isPeerActive 	= 1
		conf 				= config.split(',')		
		self.id 			= int(conf[0])
		self.name 			= conf[1]
		self.connectTo 		= int(conf[2])	
		self.outAddr 		= '127.0.0.1'
		self.outPort 		= int(outPort)
		self.inAddr 		= '127.0.0.1'
		self.inPort 		= int(inPort)
		self.handlers 		= {'J': self.addPeer, 'L': self.removePeer, 'I': self.listPeers, 'D': self.sendKey, 'M': self.recvChatMsg} #, 'C': self.isPeerAlive}

		self.rsaKey = crypto.getRSAKey()
		self.peersPK = -1

	# initialize the socket for incoming connections
	def initServer(self):
		self.inSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.inSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.inSocket.bind((self.inAddr, self.inPort))
		self.inSocket.listen(1)

	# Init socket and connect to another peer
	def connectToPeer(self, p):
		self.outSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
		self.outSocket.connect((self.outAddr, p))

	##### Demander Functions #####

	# connect to server peer, and send the message
	def sendMsg(self, p, message):
		self.connectToPeer(p)
		self.outSocket.send(message)
		data = self.outSocket.recv(1024)

		self.outSocket.close()

	# send another peer the join request
	def join(self, to, port):
		if (self.id != self.connectTo): # else it is the 1st node
			self.connectTo = to
			self.outPort = port
			message = 'J' + str(self.connectTo) + '|' + str(self.id) + '|' + self.name + '|' + str(self.inPort)
			self.sendMsg(self.outPort, message)
		else:
			print 'JOIN:', self.id, 'at', strftime("%H:%M:%S")

	# send another peer the leave request
	def leave(self):
		if self.id != self.connectTo:
			message = 'L' + str(self.connectTo) + '|' + str(self.id) + '|' + self.name + '|' + str(self.outPort)
			self.sendMsg(self.outPort, message)
		else:
			print 'LEAVE:', self.id, 'at', strftime("%H:%M:%S")

	# send another peer the list request
	def list(self):
		message = 'I' + str(self.id)
		self.sendMsg(self.outPort, message)

	# demand public key from a peer
	def demandKey(self, pid):
		message = 'D' + str(self.id) + '|' + str(pid) + '|' + '1'
		self.sendMsg(self.outPort, message)

	# encrypt the chat message and send to a specific peer
	def sendChatMsg(self, pid, chatMsg):
		# public key of the receiver
		self.demandKey(pid)
		sleep(1)

		# returns, iv + AES + encrypted padded message
		ct = crypto.encryptAES(chatMsg)

		encIvAes 	= ct[0 : AES.block_size+crypto.AES_KEY_SIZE]
		encMsg 		= ct[AES.block_size+crypto.AES_KEY_SIZE : ]
		
		# encrypt iv + aes with RSA
		encIvAes = crypto.encryptRSA(encIvAes, self.peersPK)


		encIvAesMsg = encIvAes + encMsg

		message = 'M' + str(self.id) + '|' + str(pid) + '|' + encIvAesMsg


		self.sendMsg(self.outPort, message)

	#### Doers Functions ####

	# handle the incoming requests
	def threadHandler(self):
		data = self.inCon.recv(1024)
		self.inCon.send('ACK') 
		self.inCon.close()

		msgType = data[0]
		self.handlers[msgType]( data )

	# add peer to the network
	def addPeer(self, msg):
		parsed = msg[1:].split('|')
		newNodeCt = int(parsed[0])
		newNodeId = int(parsed[1])
		newNodeN  = parsed[2]
		newNodeP  = int(parsed[3])

		#sleep(1)
		#self.listOfPeers.append(int(msg[2]))
		# update finger table
		#for i in range(1, len(self.fingerTable)+1):
		#	if ( (self.id + (2 ** (i-1)))%(int(msg[2])+1) == int(msg[2])):
		#		self.fingerTable[i] = int(msg[2])
		#		break

		if ( self.connectTo == newNodeCt ):
			self.connectTo = newNodeId
			self.outPort = newNodeP
			print 'JOIN:', newNodeId, 'at', strftime("%H:%M:%S")
		else:
			self.sendMsg(self.outPort, msg)
		

	# remove peer from the network
	def removePeer(self, msg):
		parsed = msg[1:].split('|')
		remNodeCt  = int(parsed[0])
		remNodeId  = int(parsed[1])
		remNodeN   = parsed[2]
		remNodeCtP = int(parsed[3])

		#if (int(msg[2]) in self.listOfPeers):
		#	self.listOfPeers.remove(int(msg[2]))

		if ( self.connectTo == remNodeId ):
			self.connectTo = remNodeCt
			self.outPort = remNodeCtP
			# Adr is local host, no need to change
			print 'LEAVE:', remNodeId, 'at', strftime("%H:%M:%S")
		else:	
			self.sendMsg(self.outPort, msg)

	# list all peers
	def listPeers(self, msg):
		parsed = msg[1:].split('|')
		rcvr = int(parsed[0])

		#print self.id ,sendee

		if ( self.id == rcvr ):
			# parse msg and print
			strOfPeers = msg[1:]
			listOfPeers = strOfPeers.split('|')
			stdout.write('LIST: ')
			stdout.write('|'.join(listOfPeers))
			print ' at', strftime("%H:%M:%S")
		else: 
			newMsg = msg + '|' + str(self.id)
			#print 'PEERPEER', self.outPort, self.connectTo, newMsg
			self.sendMsg(self.outPort, newMsg)

		# finger table solution
		# if  (p+2^(e-1) > table[e-1]+1 
		#	switch to that node
		# else
		#	print table[e]

	def sendKey(self, msg):
		parsed = msg[1:].split('|')
		sender = int(parsed[0])
		rcvr   = int(parsed[1])
		isDemanding = int(parsed[2])
		key = parsed[-1] # last one, it is not used while returning an answer, in this case it is equal to isDemanding,
		

		if (self.id == rcvr):
			if isDemanding == 1:
				pk = self.rsaKey.publickey().exportKey("PEM")
				newMsg = 'D' + str(self.id) + '|' + str(sender) + '|' + '0' + '|' + pk
				#print "sendKey", self.id, newMsg, self.rsaKey.publickey()
				self.sendMsg(self.outPort, newMsg)
			else:
				self.peersPK = RSA.importKey(key)
				#print "setKey", self.id, key, self.peersPK
		else:
			self.sendMsg(self.outPort, msg)

	def recvChatMsg(self, msg):
		parsed 	= msg[1:].split('|')
		sender 	= int(parsed[0])
		rcvr 	= int(parsed[1])
		ct 		= parsed[2]


		if (self.id == rcvr):
			encIvAes 	= ct[0 : 128]
			encMsg 		= ct[128 : ]

			ivAes = crypto.decryptRSA(encIvAes, self.rsaKey)

			decMsg = crypto.decryptAES(ivAes+encMsg)

			print decMsg
		else:
			self.sendMsg(self.outPort, msg)
	    




	# main loop to accept incoming connections, runs as a seperate thread as long as the peer is alive
	def mainLoop(self):
		# initialize server socket, connenct server peer from client socket
		self.initServer()

		# main loop to accept connections
		while(self.isPeerActive):	# OR TIMEOUT???	
			self.inCon, addr = self.inSocket.accept()

			if (self.isPeerActive):
				t = Thread( target = self.threadHandler)
				t.start()
		#print 'mainloop Exits'

	# close socket if neccesary
	def terminateCon(self):
		self.isPeerActive = 0
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect( (self.inAddr, self.inPort))
		self.inSocket.close()
		#print 'connection terminated'
		





	def set(self, id, port):
		self.id = id
		self.connectTo = id
		self.outPort = port

	def setSocket(self, id, port):
		self.id = id
		self.outPort = port

	# print the finger table
	def printInfo(self):
		print self.id, self.connectTo, self.outPort, self.inPort
		#print self.id, self.fingerTable, self.listOfPeers
		#print self.id, 'is connecnted to', self.connectTo, 'whose port is', self.outPort

	#def isPeerLive(self, msg):
	#	port = int(msg[0:4])
	#	e = int(msg[4])
	#	root = int(msg[5:])

	#	# i many nodes away from the sendee, live or dead
	#	if (self.id > root):
	#		i = self.id - root
	#	else:
	#		i = self.id + self.biggestPeer - root

	#	while ( 2**e <= i and e < 6 ):
	#		# sendmessage to port
			# 	send e id and port
	#		self.sendMsg(port, response)
	#		e += 1

	#	if ( e < 6 ):
	#		newMsg = msg[0:4] + str(e) + msg[5:]
			# sendmessage to next peer
	#		self.sendMsg(port, newMsg)


