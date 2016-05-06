from Peer import Peer
from time import strftime, sleep
from threading import Thread

if __name__ == "__main__":
	#print "test2"

	p = 5090

	nodeA = Peer(p, "1,A,1", p)
	nodeB = Peer(p+1, "2,B,1", p)
	nodeC = Peer(p+2, "3,C,2", p+1)
	

	tA = Thread( target = nodeA.mainLoop )
	tA.start()
	tB = Thread( target = nodeB.mainLoop )
	tB.start()
	tC = Thread( target = nodeC.mainLoop )
	tC.start()

	try:
		# A joins
		nodeA.join(0, 0)
		sleep(1)
		nodeA.list()
		sleep(1)
		# B joins
		nodeB.join(1, p)
		sleep(1)
		nodeA.list()
		sleep(1)
		# C joins
		nodeC.join(2, p+1)
		sleep(1)
		nodeA.list()
		sleep(1)

		#nodeA.demandKey(2)
		nodeA.sendChatMsg(2, 'hey dude!')
		sleep(1)

		# C leaves
		nodeC.leave()
		sleep(1)
		nodeA.list()
		sleep(1)
		# B leaves
		nodeB.leave()
		sleep(1)
		nodeA.list()
		sleep(1)

		


		#sleep(2)
		#nodeA.printFT()
		#sleep(1)
		#nodeB.printFT()
		#sleep(1)
		#nodeC.printFT()
		#sleep(1)
		#nodeD.printFT()
		#sleep(1)
		#nodeE.printFT()
		#sleep(1)
		#nodeF.printFT()
		#sleep(1)	
	
	except Exception as inst:
		print inst.args

	finally: 
		nodeA.terminateCon()
		nodeB.terminateCon()
		nodeC.terminateCon()
		

	
