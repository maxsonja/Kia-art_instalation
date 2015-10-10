import cv2
import numpy as np

def bla(x):
	pass
val = 1

camera = 0

pos=[0,0]
npos=[0,0]

cam = 0
raw = 0

cv2.namedWindow('raw')
cv2.namedWindow('bar')
cv2.createTrackbar('Enable','bar',0,1,bla)
cv2.createTrackbar('Mode','bar',0,1,bla)
cv2.createTrackbar('Tlow','bar',0,255,bla)
cv2.createTrackbar('Thigh','bar',0,20,bla)
cv2.createTrackbar('Erode','bar',0,5,bla)
cv2.createTrackbar('Display','bar',0,3,bla)
cv2.createTrackbar('blur','bar',5,50,bla)
cv2.createTrackbar('glich','bar',3,5,bla)


#style & colors
lineC  = (10,100,50)
lineS = 1
dotC = (200,200,255)
dotS = 3
crosC = (100,100,100)
crosS = 10
crosW = 1

mode = "Light"

resolution = (254, 254)
pts = np.float32([[50,50], [150,50], [50,150],[150,150]])
pts2 = np.float32([[0,0],[resolution[0],0],[0,resolution[1]],[resolution[0],resolution[1]]])
npts = [[0,0],[0,0],[0,0],[0,0]]
sel = -1


transform = cv2.getPerspectiveTransform(pts,pts2)
kernel = np.ones((5,5),np.uint8)

Tlow = 5

glich_tresh = 1
glich_counter = 0
detect = False
x=0
y=0
h=0
w=0

settings = {"Colors":{"Lines":lineC, "Dots":dotC, "crosC":crosC, },"mode":mode ,"resolution":resolution, "glich_tresh":glich_tresh}

def init():
	global cam, raw
	cam = cv2.VideoCapture(camera)
	raw = cam.read()[1]

def save():
	global settings
	settings = {"Colors":{"Lines":lineC, "Dots":dotC, "crosC":crosC, },"mode":mode ,"resolution":resolution, "glich_tresh":glich_tresh}

def load(data):

	global lineC, dotC, crosC, mode, resolution, glich_tresh, camera
	#camera = data["Camera"]
	lineC=data["Colors"]['Lines']
	dotC = data["Colors"]["Dots"]
	crosC = data["Colors"]["crosC"]
	mode = data["mode"]
	resolution = data["resolution"]
	glich_tresh = data["glich_tresh"]

def drawPoly():
	global raw
	cv2.line(raw,(pts[0][0],pts[0][1]), (pts[1][0],pts[1][1]),lineC,lineS)
	cv2.line(raw,(pts[1][0],pts[1][1]), (pts[3][0],pts[3][1]),lineC,lineS)
	cv2.line(raw,(pts[2][0],pts[2][1]), (pts[0][0],pts[0][1]),lineC,lineS)
	cv2.line(raw,(pts[3][0],pts[3][1]), (pts[2][0],pts[2][1]),lineC,lineS)
	cv2.circle(raw,(pts[0][0],pts[0][1]), dotS, dotC, -1)
	cv2.circle(raw,(pts[1][0],pts[1][1]), dotS, dotC, -1)
	cv2.circle(raw,(pts[2][0],pts[2][1]), dotS, dotC, -1)
	cv2.circle(raw,(pts[3][0],pts[3][1]), dotS, dotC, -1)

def normalCords(input):
	global npts, npos, lineC, lineS, raw
	npts[0]=[0,0]
	frame = [[0,0],[0,0],[0,0],[0,0]]

	#print "-----------------"
	for i in range(1,4):
		npts[i]=[pts[i][0]-pts[0][0], pts[i][1]-pts[0][1]]
		#print i, int(npts[i][0]),int(npts[i][1]), "||" , pts[i]

	#print input
	
	frame[0][0] = (npts[1][0]-npts[0][0]) * input[0]
	frame[0][1] = (npts[1][1]-npts[0][1]) * input[0]

	frame[1][0] = npts[0][0] + ((npts[2][0]-npts[0][0]) * input[1])
	frame[1][1] = npts[0][1] + ((npts[2][1]-npts[0][1]) * input[1])

	frame[2][0] = npts[2][0] + ((npts[3][0]-npts[2][0]) * input[0])	
	frame[2][1] = npts[2][1] + ((npts[3][1]-npts[2][1]) * input[0])

	frame[3][0] = npts[1][0] + ((npts[3][0]-npts[1][0]) * input[1])
	frame[3][1] = npts[1][1] + ((npts[3][1]-npts[1][1]) * input[1])

	cv2.line(raw,(int(pts[0][0]+frame[0][0] ),int(pts[0][1]+frame[0][1])),(int(pts[0][0]+frame[2][0]),int(pts[0][1]+frame[2][1])),lineC,lineS)
	cv2.line(raw,(int(pts[0][0]+frame[1][0] ),int(pts[0][1]+frame[1][1])),(int(pts[0][0]+frame[3][0]),int(pts[0][1]+frame[3][1])),lineC,lineS)
	"""
	cv2.circle(raw,(int(pts[0][0]+cordx),int(pts[0][1]+cordy)), dotS, dotC, -1)
	cv2.circle(raw,(int(pts[0][0]+cordx2),int(pts[0][1]+cordy2)), dotS, dotC, -1)
	cv2.circle(raw,(int(pts[0][0]+cordx),int(pts[0][1]+cordy)), dotS, dotC, -1)


	cordx= cordx + ((cordx2-cordx)*input[1])
	cordx = pts[0][0] + cordx

	cordy=(npts[1][1]-npts[0][1]) * input[1]
	cordy2=npts[2][1] + ((npts[3][1]-npts[2][1]) * input[1])
	cordy=cordy + (cordy2-cordy)*input[0]
	cordy = pts[0][1] + cordy
	print cordx, cordy
	npos = [int(cordx), int(cordy)]
	print "position: ", npos
	"""


def drawCross():
	global npos

	cv2.line(raw, (npos[0], npos[1] - crosS) , ( npos[0] , npos[1] + crosS) ,crosC,crosW)
	cv2.line(raw, (npos[0] - crosS, npos[1]) , (npos[0] + crosS, npos[1] ) ,crosC,crosW)


def inRage(pos):
	bla = len(pts)
	for i in range(0, len(pts)):
		if(abs(pts[i][0]-pos[0])<10 and abs(pts[i][1]-pos[1])<5):
			return i
	return -1

def click(event,x,y,flags,param):
	global sel, pts, transform
	if event == cv2.EVENT_LBUTTONDOWN:
		point = inRage((x,y))
		if point >=0:
			sel=point

	elif event == cv2.EVENT_LBUTTONUP:
		sel=-1

	elif sel>=0:
		pts[sel]=(x,y)
		transform = cv2.getPerspectiveTransform(pts,pts2)

cv2.setMouseCallback('raw',click)

def see():
	global detect, glich_tresh, glich_counter, x,y,h,w, raw,pos, val

	#capture frame
	raw = cam.read()[1]
	
	enable =cv2.getTrackbarPos('Enable','bar')
	err = cv2.getTrackbarPos('Erode','bar')
	disp = cv2.getTrackbarPos('Display','bar')

	Blur=cv2.getTrackbarPos('blur', 'bar')
	if Blur%2 == 0:
		Blur = 5

	mode = cv2.getTrackbarPos('Mode','bar')
	if mode == 0:
		Tlow=cv2.getTrackbarPos('Tlow','bar')
	else:
		Tlow=cv2.getTrackbarPos('Thigh', 'bar')

	img = cv2.warpPerspective(raw, transform, (300, 300))
	img = cv2.medianBlur(raw, Blur)

	#cv2.rectangle(raw,(x-5,y-5),(x+w+5,y+h+5),(50,50,50),2)
	drawPoly()
	blax = float(cv2.getTrackbarPos('x','bar'))/100
	blay = float(cv2.getTrackbarPos('y','bar'))/100
	normalCords(pos)
	drawCross()
	cv2.imshow('raw',raw)
	img = cv2.warpPerspective(img,transform,resolution)
	if disp == 0:
		cv2.imshow('detect',img)

	#light mode
	if mode == 1:
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
		img = cv2.absdiff(img, gray)
	
	#make mask	
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = cv2.threshold(img,Tlow,255,cv2.THRESH_BINARY)[1]
	if disp == 1:
		cv2.imshow('detect', img)

	#clean mask
	img = cv2.erode(img,kernel,iterations = err)
	if disp == 2:
		cv2.imshow('detect', img)
	img = cv2.dilate(img,kernel,iterations = 2)
	if disp == 3:
		cv2.imshow('detect', img)
	

	contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	if len(contours) > 0:
		glich_counter = 0
		if not detect:
			detect = True
			x,y,w,h = cv2.boundingRect(contours[0])
			#raw = cv2.rectangle(raw,(x,y),(x+w,y+h),(50,50,50),2)
			pos[0] = (x+(w/2))/float(resolution[0]) 
			pos[1] = (y+(h/2))/float(resolution[1])
			
			if enable:
				return True
			else:
				print "disabled, pos: ", pos 
	elif len(contours)>1:
		print "error"

	elif detect :
		if glich_counter<glich_tresh:
			glich_counter+=1
			#print "glich:", glich_counter
		elif glich_counter==glich_tresh:
			detect=False

	return False








		


			




