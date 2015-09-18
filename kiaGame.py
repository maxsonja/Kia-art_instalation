import random, pygame, gc, time, os

##--clip stuff--##
#clip menagment
index = 0
clips = {}
rawClips = []
maxClips = 1
numClips = 1

#audio stuff
shoot=[]
channel=[]
chId=0

#clip size
maxSize=600
minSize=300

#game stuff
kills = 0
killTable = {1:2 , 2:2 , 3:3 , 4:4, 5:5, 6:6,7:2,8:2}
defoultKills = 2
lvl = 1

##--displey stuff--##
screen = 0;
#size
xFrame = 1024
yFrame = 768
floor = 50

##--general--##
needGc = False
old = False
trash = []
debugFlag = False
menu = 0

#tajminzi
timeout = 1
startDelay = 2

#settings fajl
settings={"maxClips": maxClips, "maxSize":maxSize, "minSize": minSize, "xFrame":xFrame, "yFrame": yFrame, "floor":floor, "timeout": timeout, "startDalay":startDelay}

def save():
	global settings
	settings={"maxClips": maxClips, "maxSize":maxSize, "minSize": minSize, "xFrame":xFrame, "yFrame": yFrame, "floor":floor, "timeout": timeout, "startDalay":startDelay}

def load(data):
	print "loading game data:", data
	global maxClips, maxSize, minSize, xFrame,yFrame, floor, timeout, startDelay
	maxClips = data["maxClips"]
	maxSize = data["maxSize"]
	minSize = data["minSize"]
	xFrame = data["xFrame"]
	yFrame = data["yFrame"]
	floor = data["floor"]
	timeout = data["timeout"]
	startDalay = data["startDalay"]

#inicalizacija
def init(**kwargs):
	global screen, shoot, xFrame, yFrame
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
	pygame.init()
	#sound staff
	pygame.mixer.pre_init(buffer=4096)
	pygame.mixer.init()
	shoot.append(pygame.mixer.Sound("gun1-1.wav"))
	pygame.mixer.set_num_channels(10)
	pygame.mixer.set_reserved(8)

	for i in range(0,7):
		channel.append(pygame.mixer.Channel(i))

	gc.enable()							#garbig kolektor
	gc.set_threshold(1,1,1)
	for i in range(0, kwargs["numb"]):
		rawClips.append(videoClip( folder=kwargs["folder"] , name = repr(i)))
	
	#displej stuff
	if kwargs["mod"] == "full":
		screen = pygame.display.set_mode(kwargs["resolution"],pygame.FULLSCREEN)
		xFrame = screen.get_width()
		yFrame = screen.get_height()

	else:
		screen = pygame.display.set_mode(kwargs["resolution"], pygame.NOFRAME)
		xFrame = kwargs["resolution"][0]
		yFrame = kwargs["resolution"][1]

	print xFrame, yFrame
	pygame.display.set_caption('KIA game')
	screen.fill((235,235,235))

def startGame():
	while len(clips)<numClips:
		if not spawnClip():
			break

#update tick func
def update():
	global old, needGc, trash

	screen.fill((235,235,235))
	#chk mouse
	if pygame.mouse.get_pressed()[0] and not old:
		old = True
		isHit(pygame.mouse.get_pos())
	elif not pygame.mouse.get_pressed()[0] and old:
		old = False

	#iterate players
	for clip in clips:
		if clips[clip].play(): 			#update and chk if need del
			needGc = True					
			trash.append(clips[clip].id)	#mark for deletion
			print "to trash", clips[clip].id

	#garbig kolekt & spawn
	if needGc:
		print "deleting", trash
		for i in trash:					#delete everything on the list
			del clips[i]
			print i, "deleted"

		trash=[]						#collect the garbage
		gc.collect()
		needGc = False

		while len(clips) < numClips: 	#chk and spawn new clips
			if not spawnClip():
				break

	if debugFlag:
		drawDebug()

	pygame.display.update()

#chk and make new player
def spawnClip():
	global index, clips
	tmpRect = getRect()
	
	if tmpRect == pygame.Rect(0,0,0,0):
		print "new clip", tmpRect, "nestane"
		return False
	else:
		index+=1
		rndClip = random.randint(0,len(rawClips)-1)
		clips[index]=player(rawClips[rndClip], tmpRect, index)

		print "new clip", tmpRect
		print "clip id", index
		print "clips on screen", len(clips), "of", numClips
		return True
		
def getRect():
	global maxSize, minSize, xFrame, yFrame, floor
	if len(clips) >0:
		tmp = chkLeft(xFrame) 					#start from right screen edge 
		space = []
		if tmp != (0,0,0):
			space.append(tmp)

		for obj in clips:
			tmp = chkLeft(clips[obj].place[0])
			if tmp != (0,0,0):					#chk every clip
				space.append(tmp)

		if len(space)==0:						#if no space left	
			return pygame.Rect(0,0,0,0)
		space = space[random.randint(0,len(space)-1)]		#randomly pick free space
	else:
		space = [0, xFrame, maxSize]

	ySize = random.randint(minSize, space[2])
	xSize = int(ySize/1.35)
	xPos = int(random.randint(space[0], space[1]-xSize))
	yPos = yFrame-floor-ySize
	random.seed(random.randint(0,10000))
	return pygame.Rect(xPos, yPos , xSize , ySize)

def chkLeft(pos):
	global clips, minSize, maxSize
	limit = 0
	for obj in clips:
		edge = clips[obj].place[0]+clips[obj].place[2]
		if edge < pos and edge > limit:
			limit = edge

	if pos-limit < minSize:
		return (0,0,0)

	else:
		if pos - limit<maxSize:
			maxS = pos-limit
		else:
			maxS = maxSize
		return (limit, pos, maxS)
def hit(pos):
	isHit((int(xFrame*pos[0]),int(yFrame*pos[1])))

#hit detection
def isHit(pos):
	global numClips, maxClips, clips, kills, killTable, defoultKills, shoot, chId, channel
	#play bangg
	pygame.mixer.init()
	channel[chId].play(shoot[0])
	if chId >= 8:
		chId = 0

	for i in clips:									#za svak iklip
		if clips[i].place.collidepoint(pos):		#ako hit u klipu
			if clips[i].hit(pos):					#ako pogoden
				if numClips <= len(clips):			#ako prosli lvl se popunio nastavi
					kills += 1
					if numClips +1 in killTable:
						print "kills", kills, "of", killTable[numClips+1]	
						if kills>=killTable[numClips+1]:
							kills = 0
							numClips += 1
							if numClips>maxClips:
								numClips=maxClips
							print "new lvl!", numClips
					elif kills>=defoultKills:		#ako nije setapano
							kills = 0
							numClips += 1
							if numClips>maxClips:
								numClips=maxClips

#control stuff
def stopAll():
	for i in clips:
		clips[i].stop()

def reset():
	global kills, numClips
	for i in clips:
		clips[i].close()

	kills = 0
	numClips = 1

def getScore():
	global kills, killTable, defoultKills, numClips
	lvl = numClips
	if lvl + 1 in killTable:
		goal=killTable[lvl+1]
	else:
		goal=defoultKills
	return (kills, goal, lvl)

def debug():
	global debugFlag
	debugFlag = not debugFlag

def drawDebug():
	global kills, killTable, yFrame, xFrame, floor,screen, menu
	rMargin=20
	tMargin=10
	yGap = 3
	
	score = getScore()
	
	font = pygame.font.Font("Code New Roman b.otf", 18)
	
	black = (10,10,10)
	gray = (100,100,100)
	cyan = (175, 238,238)
	
	lvlStat= font.render("lvl: %i" %score[2], 1,black)
	lvlStatPos = lvlStat.get_rect()
	lvlStatPos[0] += rMargin
	lvlStatPos[1] += tMargin
	
	killStatText="kills: %i of %i" % (score[0], score[1])
	killStat = font.render(killStatText, 1, black)
	killStatPos=killStat.get_rect()
	killStatPos[0]+= rMargin
	killStatPos[1]+= lvlStatPos[1]+lvlStatPos[3]+yGap
	
	clipStatText="clips: %i of %i" %(len(clips), score[2])
	clipStat= font.render(clipStatText, 1, black)
	clipStatPos=clipStat.get_rect()
	clipStatPos[0]+= rMargin
	clipStatPos[1]+=killStatPos[1]+killStatPos[3]+yGap

	maxStat = font.render("max Size: %i" % maxSize, 1,black)
	maxStatPos=maxStat.get_rect()
	maxStatPos[0] = xFrame - 150
	maxStatPos[1] = tMargin

	minStat = font.render("min Size: %i" % minSize, 1,black)
	minStatPos = minStat.get_rect()
	minStatPos[0]=xFrame - 150
	minStatPos[1]= maxStatPos[1]+maxStatPos[3]+yGap
	
	font = pygame.font.Font("Code New Roman b.otf", 12)

	minLine = font.render("min Size", 1,black)
	minLinePos = minLine.get_rect()
	minLinePos[0] = 5
	minLinePos[1] = yFrame-floor-minSize-10

	maxLine = font.render("max Size", 1, black)
	maxLinePos = maxLine.get_rect()
	maxLinePos[0]= 5
	maxLinePos[1]= yFrame-floor-maxSize-10

	floorLine = font.render("floor", 1, black)
	floorLinePos = floorLine.get_rect()
	floorLinePos[0]= 5
	floorLinePos[1]= yFrame-floor-10

	if menu == 1:
		pygame.draw.rect(screen, cyan, minStatPos,0)
	elif menu == 0:
		pygame.draw.rect(screen, cyan, maxStatPos,0)

	for i in clips:
		pygame.draw.rect(screen, black, clips[i].place, 1)
		if clips[i].status == clips[i].playIntro:
			stat=" intro"
		elif clips[i].status== clips[i].playLoop:
			stat=" loop"
		elif clips[i].status== clips[i].playOutro or clips[i].status== clips[i].finish:
			stat=" fin"
		else:
			stat=""
		clipName= font.render("clip: " + clips[i].rawClip.name+stat, 1,black)
		clipNamePos = clipName.get_rect()
		clipNamePos[0]=	clips[i].place[0]
		clipNamePos[1]= clips[i].place[1]-2-clipNamePos[3]
		screen.blit(clipName, clipNamePos)

	pygame.draw.line(screen, black,(0,yFrame-floor), (xFrame, yFrame-floor), 1)
	pygame.draw.line(screen, gray,(0,yFrame-floor-minSize), (xFrame, yFrame-floor-minSize), 1) 
	pygame.draw.line(screen, gray,(0,yFrame-floor-maxSize), (xFrame, yFrame-floor-maxSize), 1)  
	
	screen.blit(lvlStat, lvlStatPos)
	screen.blit(killStat, killStatPos)
	screen.blit(clipStat,clipStatPos)
	screen.blit(minStat, minStatPos)
	screen.blit(maxStat, maxStatPos)
	screen.blit(minLine, minLinePos)
	screen.blit(maxLine, maxLinePos)
	screen.blit(floorLine, floorLinePos)

def keyEvent(key):
	global menu, maxSize, minSize, yFrame, floor, drawDebug
	# 273, 275, 274, 276
	if drawDebug:
		#up key
		if key==273:
			menu = menu -1
			if menu <0:
				menu = 0
		#down key
		if key == 274:
			menu = menu +1
			if menu >1:
				menu = 1
		#right key
		if key== 275:
			if menu == 0:
				maxSize = maxSize +10
				if maxSize>yFrame-floor:
					maxSize=yFrame-floor
			if menu == 1:
				minSize = minSize +10
				if minSize > maxSize-50:
					maxSize = minSize +50
					if maxSize>yFrame-floor:
						maxSize=yFrame-floor
						minSize=maxSize-50
		#left key
		if key == 276:
			if menu == 0:
				maxSize = maxSize -10
				if maxSize<minSize+50:
					minSize=maxSize-50
					if minSize<200:
						minSize=200
						maxSize=minSize+50
			if menu == 1:
				minSize = minSize -10
				if minSize < 200:
					minSize = 200

class videoClip():
	def __init__(self, *args, **kwargs):
		self.name = kwargs["name"]
		if kwargs == None:
			self.intro = args[0]
			self.loop = args[1]
			self.outro = args[2]
			self.mask = args[3]
		elif "name" in kwargs:
			self.intro = kwargs["folder"]+kwargs["name"]+"_1.mpg"	
			self.loop = kwargs["folder"]+kwargs["name"]+"_2.mpg"
			self.outro = kwargs["folder"]+kwargs["name"]+"_3.mpg"
			self.mask = kwargs["folder"]+kwargs["name"]+"_m.jpg"	

class player():

	def __init__(self, clip, rect, index):
		self.intro = pygame.movie.Movie(clip.intro)
		self.loop = pygame.movie.Movie(clip.loop)
		self.outro = pygame.movie.Movie(clip.outro)
		self.place = rect
		self.surf = pygame.Surface((self.place[2],self.place[3])).convert()
		self.surf.fill((235,235,235))

		self.intro.set_volume(0)
		self.loop.set_volume(0)
		self.outro.set_volume(0)

		self.id = index
		self.rawClip = clip

		self.status = self.delayStart
		self.time =0

		self.cmd = {0:self.start, 1:self.playIntro, 2:self.playLoop, 3:self.playOutro, 4:self.finish, 5:self.pause, 6:self.delayStart}

	def play(self):
		global screen
		self.status()
		#pygame.transform.smoothscale(self.surf, (self.place[2],self.place[3]),self.surf) 
		screen.blit(self.surf, (self.place[0],self.place[1]))
		if self.status == self.nothing:
			return True
		else:
			return
		
	def delayStart(self):
		if self.time==0:
			self.time = time.time() + random.uniform(0, startDelay)
		elif self.time<=time.time():
			self.status = self.start
		else:
			pass

	def start(self):
		self.intro.set_display(self.surf, (0,0, self.place[2],self.place[3]))
		self.loop.set_display(self.surf, (0,0, self.place[2],self.place[3]))
		self.outro.set_display(self.surf, (0,0, self.place[2],self.place[3]))
		self.intro.play()

		self.status = self.playIntro

	def playIntro(self):
		if self.intro.get_time() >= self.intro.get_length():
			self.intro.stop()
			self.intro.rewind()
			self.loop.play()
			self.status = self.playLoop

	def playOnlyIntro(self):
		if self.intro.get_time() >= self.intro.get_length():
			self.intro.stop()
			self.intro.rewind()
			self.status = self.playOutro

	def playLoop(self):
		if not self.loop.get_busy():
			self.loop.rewind()
			self.loop.play()

	def hit(self, pos):
		if self.status == self.playLoop:
			pos = (pos[0]-self.place[0], pos[1]-self.place[1])
			if self.surf.get_at(pos) != (235,235,235):
				print "hit!", self.id
				self.status = self.playOutro
				return True
		return False

	def playOutro(self):
		self.loop.stop()
		self.outro.play()
		self.loop.rewind()
		self.status = self.finish

	def finish(self):
		if not self.outro.get_busy():
			self.outro.stop()
			self.outro.rewind()
			self.surf.fill((235,235,235))
			self.time = time.time() + timeout
			self.status = self.pause

	def pause(self):
		if self.time<=time.time():
			self.status = self.nothing
			print "gotovo", self.id
		else:
			pass
				
	def nothing(self):
		pass

	def close(self):
		if self.status == self.delayStart or self.status == self.start:
			self.status = self.nothing
		elif self.status == self.playIntro:
			self.status = self.playOnlyIntro
		elif self.status == self.playLoop:
			self.status = self.playOutro

	def stop(self):
		self.intro.stop()
		self.loop.stop()
		self.outro.stop()
