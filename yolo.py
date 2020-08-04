# USAGE
# python yolo.py --image images/baggage_claim.jpg --yolo yolo-coco

# import the necessary packages
import numpy as np
import argparse
import time
import cv2
import os
from PIL import Image
import math

def conventPNG2JPEG(spth,tpth):
    im = Image.open(spth)
    rgb_im=im.convert('RGB')
    rgb_im.save(tpth)

#计算两点间距离
def getDistance(v1,v2):
    dis = math.sqrt(math.pow(v1[0]-v2[0],2) + math.pow(v1[1]-v2[1],2))
    return int(dis)
   

#所有锚点的坐标偏移都为x方向为宽度一半,y方向上:f和c为向下半个宽度,r为向上半个宽度,s的x,y为w,h的一半

msPerDistence = 1.48  #每个像素坐表示多常时间的毫秒延时

def getTouchTimeDelay(boxes):
    rbox = {}       #跳一跳小人坐标盒子
    fboxes = []     #所有方块的坐标盒子
    # cbox = []       #所有圆型块坐标盒子
    sbox = {}       #开始游戏坐标盒子
    for i,v in boxes.items():
        # v={'x':x,'y':y,'w':w,'h':h,'t':self.LABELS[classIDs[i]],'s':confidences[i]}
        if v['t'] == 'r':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + (v['h'] - v['w']/2.0))
            rbox = v
            rbox['p'] = [Px,Py]
        elif v['t'] == 'f':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + v['w']/2.0)
            tmpv = v
            tmpv['p'] = [Px,Py]
            fboxes.append(tmpv)
        elif v['t'] == 'c':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + v['w']/2.0)
            tmpv = v
            tmpv['p'] = [Px,Py]
            fboxes.append(tmpv)
        elif v['t'] == 's':
            Px = int(v['x'] + v['w']/2.0)
            Py = int(v['y'] + v['h']/2.0)
            sbox = v
            sbox['p'] = [Px,Py]
        else:
            print('fand type erro....')
            return -2
    #计算所有块与小人距离,以及下一个人跳到的块是那一个
    nextBox = 0
    nextdis = 0
    minPy = 10000
    mindis = 10000
    rindex = 0
    if sbox:
        print('is start UI...')
        return -1
    try:
    # if True:
        for i,v in enumerate(fboxes):
            dis = getDistance((v['p']), rbox['p'])
            if dis <= mindis:
                rindex = i
                mindis = dis
        
        rfbox = fboxes.pop(rindex)
        for i,v in enumerate(fboxes):
            dis = getDistance((v['p']), rbox['p'])
            if v['p'][1] < rbox['p'][1]:
                tmppy = rbox['p'][1] - v['p'][1]
                if tmppy < minPy:
                    minPy = tmppy
                    nextBox = i
                    nextdis = dis
        print(minPy,mindis,rindex,nextBox)
        print(rbox['p'],rfbox['p'],fboxes[nextBox]['p'],nextdis)
        #计算距离转换为延时间
        dtime = int(nextdis*msPerDistence)
        print('delytime:%d'%(dtime))
        return dtime
    except Exception as e:
        print(e)
        print('getDistance erro...')

def showImg():
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required=True,
		help="path to input image")
	ap.add_argument("-y", "--yolo", required=True,
		help="base path to YOLO directory")
	ap.add_argument("-c", "--confidence", type=float, default=0.5,
		help="minimum probability to filter weak detections")
	ap.add_argument("-t", "--threshold", type=float, default=0.3,
		help="threshold when applyong non-maxima suppression")
	args = vars(ap.parse_args())

	# load the COCO class labels our YOLO model was trained on
	labelsPath = os.path.sep.join([args["yolo"], "my.names"])
	LABELS = open(labelsPath).read().strip().split("\n")

	# initialize a list of colors to represent each possible class label
	np.random.seed(42)
	COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
		dtype="uint8")

	# derive the paths to the YOLO weights and model configuration
	weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
	configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])

	# load our YOLO object detector trained on COCO dataset (80 classes)
	print("[INFO] loading YOLO from disk...")
	net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

	# load our input image and grab its spatial dimensions
	imgpth = args["image"]
	namepth,formatimg = os.path.splitext(imgpth)
	argpth = imgpth
	if  formatimg.lower() == '.png':
		tpth = namepth + '.jpg'
		conventPNG2JPEG(imgpth, tpth)
		argpth = tpth
	image = cv2.imread(argpth)
	(H, W) = image.shape[:2]

	# determine only the *output* layer names that we need from YOLO
	ln = net.getLayerNames()
	ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	# construct a blob from the input image and then perform a forward
	# pass of the YOLO object detector, giving us our bounding boxes and
	# associated probabilities
	blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
		swapRB=True, crop=False)
	net.setInput(blob)
	start = time.time()
	layerOutputs = net.forward(ln)
	end = time.time()

	# show timing information on YOLO
	print("[INFO] YOLO took {:.6f} seconds".format(end - start))

	# initialize our lists of detected bounding boxes, confidences, and
	# class IDs, respectively
	boxes = []
	confidences = []
	classIDs = []

	
	# loop over each of the layer outputs
	for output in layerOutputs:
		# loop over each of the detections
		for detection in output:
			# extract the class ID and confidence (i.e., probability) of
			# the current object detection
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]

			# filter out weak predictions by ensuring the detected
			# probability is greater than the minimum probability
			if confidence > args["confidence"]:
				# scale the bounding box coordinates back relative to the
				# size of the image, keeping in mind that YOLO actually
				# returns the center (x, y)-coordinates of the bounding
				# box followed by the boxes' width and height
				box = detection[0:4] * np.array([W, H, W, H])
				(centerX, centerY, width, height) = box.astype("int")

				# use the center (x, y)-coordinates to derive the top and
				# and left corner of the bounding box
				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))

				# update our list of bounding box coordinates, confidences,
				# and class IDs
				boxes.append([x, y, int(width), int(height)])
				
				confidences.append(float(confidence))
				classIDs.append(classID)

	# apply non-maxima suppression to suppress weak, overlapping bounding
	# boxes
	print(boxes)
	idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
		args["threshold"])

	outbox = {}
	
	# ensure at least one detection exists
	if len(idxs) > 0:
		# loop over the indexes we are keeping
		for i in idxs.flatten():
			# extract the bounding box coordinates
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])

			# draw a bounding box rectangle and label on the image
			color = [int(c) for c in COLORS[classIDs[i]]]
			cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
			text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
			cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
				0.5, color, 2)
			outbox[i] = {'x':x,'y':y,'w':w,'h':h,'t':LABELS[classIDs[i]],'s':confidences[i]}
	for k,v in outbox.items():
		tmpv = {'p':[v['x'],v['y']],'size':[v['w'],v['h']],'t':v['t'],'s':v['s']}
		print(tmpv)
	dtime = getTouchTimeDelay(outbox)
	print(dtime)
	scalefloat = 0.3
	w = int(image.shape[1]*scalefloat)
	h = int(image.shape[0]*scalefloat)
	resizeimg = cv2.resize(image, (w,h), interpolation = cv2.INTER_AREA)

	cv2.imshow("Image", resizeimg)
	cv2.moveWindow('Image',500,0)
	cv2.waitKey(0)

def main():
	showImg()

if __name__ == '__main__':
	main()