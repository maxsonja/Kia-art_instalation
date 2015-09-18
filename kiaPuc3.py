import pygame, kiaGame, threading ,cv, json

res = [1024,768]
folder="clips1/"
mode="full"
position=[0,0]

def save():
	kiaGame.save()
	cv.save()
	sData = {"KiaGame":kiaGame.settings, "openCV":cv.settings, "General":{"res":res, "folder":folder,"mode":mode,"Position":position}}
	print "saving data", sData
	sFile=open("settings.txt", "w")
	sFile.write(json.dumps(sData, sort_keys=True, indent=4))
	sFile.close()

def load():
	global res, folder, mode, position
	lFile=open("settings.txt","r")
	lData=json.loads(lFile.read())
	lFile.close()

	kiaGame.load(lData["KiaGame"])
	#cv.load(lData["openCV"])

	res = lData["General"]["res"]
	folder = lData["General"]["folder"]
	mode = lData["General"]["mode"]
	position = lData["General"]["Position"]

class myThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):	
		global exitT
		while(1):
			if exitT:
				cv.cv2.destroyAllWindows()
				break
			kiaGame.update()
			clock.tick(25)
load()



kiaGame.init(folder=folder, numb=7, mod=mode, resolution=res)
kiaGame.startGame()
cv.init()
clock = pygame.time.Clock()
pygame.key.set_repeat(250)
exitT=False			

thread1 = myThread(1, "Thread-1", 1)
# Start new Threads
thread1.start()
while True:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:

			if event.key == 27 or event.key == 113: #q
				save()
				kiaGame.stopAll()
				pygame.quit()
				cv.cv2.destroyAllWindows()
				exitT=True
				exit()
				break
			if event.key == 116: #t
				pygame.display.set_mode([0,0],pygame.FULLSCREEN)
			if event.key == 114: #r
				kiaGame.reset()
			if event.key == 103: #g
				print  kiaGame.gc.collect()
			if event.key == 100: #d
				kiaGame.debug()
			if event.key == 108: #l
				load()
			else:
				pass
				#print event
				kiaGame.keyEvent(event.key)

		if event.type == pygame.QUIT:
			save()
			kiaGame.stopAll()
			pygame.quit()
			cv.cv2.destroyAllWindows()
			exitT=True
			exit()
			break

	if cv.see():
		kiaGame.hit(cv.pos)
	if cv.val != kiaGame.maxClips:
		kiaGame.maxClips=cv.val