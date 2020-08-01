# USAGE
# python yolo.py --image images/baggage_claim.jpg --yolo yolo-coco

# import the necessary packages
import numpy as np
import time
import cv2
import os,sys


class YOLONet(object):
    """docstring for YOLONet"""
    def __init__(self, pWeightPth,pCfgPth,pNamePth,pConfidence = 0.5,pThreshold = 0.3):
        super(YOLONet, self).__init__()
        self.weightsPath = pWeightPth
        self.configPath = pCfgPth
        self.labelsPath = pNamePth
        self.confidence = pConfidence
        self.threshold = pThreshold
        self.net = None
        self.layerNames = None
        self.LABELS = []
        self.COLORS = []
        self.loadYoloNet()
    def loadYoloNet(self):
        self.LABELS = open(self.labelsPath).read().strip().split("\n")

        # initialize a list of colors to represent each possible class label
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3),
            dtype="uint8")
        print("[INFO] loading YOLO from disk...")
        self.net = cv2.dnn.readNetFromDarknet(self.configPath, self.weightsPath)
        ln = self.net.getLayerNames()
        self.layerNames = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        np.random.seed(42)
        
    def fandObjects(self,image):
        (H, W) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
        swapRB=True, crop=False)
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(self.layerNames)
        end = time.time()
        # show timing information on YOLO
        print("[INFO] YOLO took {:.6f} seconds".format(end - start))
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
                if confidence > self.confidence:
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
        idxs = cv2.dnn.NMSBoxes(boxes, confidences,self.confidence,
            self.threshold)

        # ensure at least one detection exists
        outboxes = {}
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                outboxes[i] = {'x':x,'y':y,'w':w,'h':h,'t':classIDs[i],'s':confidences[i]}
                # draw a bounding box rectangle and label on the image
                color = [int(c) for c in self.COLORS[classIDs[i]]]
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(self.LABELS[classIDs[i]], confidences[i])
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)

        return image,outboxes


# def yoloImg(net,image):
#     # construct the argument parse and parse the arguments

#     # load the COCO class labels our YOLO model was trained on
#     # labelsPath = os.path.sep.join([args["yolo"], "my.names"])
#     os.getcwd()
#     labelsPath = os.getcwd() + os.sep + 'my.names'
#     LABELS = open(labelsPath).read().strip().split("\n")

    

#     # derive the paths to the YOLO weights and model configuration
#     # weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
#     # configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])
#     weightsPath = os.getcwd() + os.sep + "yolov3.weights"
#     configPath = os.getcwd() + os.sep + "yolov3.cfg"
#     # load our YOLO object detector trained on COCO dataset (80 classes)
#     print("[INFO] loading YOLO from disk...")
#     net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

#     # load our input image and grab its spatial dimensions
#     image = cv2.imread(args["image"])
#     (H, W) = image.shape[:2]

#     # determine only the *output* layer names that we need from YOLO
#     ln = net.getLayerNames()
#     ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

#     blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
#         swapRB=True, crop=False)
#     net.setInput(blob)
#     start = time.time()
#     layerOutputs = net.forward(ln)
#     end = time.time()

#     # show timing information on YOLO
#     print("[INFO] YOLO took {:.6f} seconds".format(end - start))

#     # initialize our lists of detected bounding boxes, confidences, and
#     # class IDs, respectively
#     boxes = []
#     confidences = []
#     classIDs = []

#     # loop over each of the layer outputs
#     for output in layerOutputs:
#         # loop over each of the detections
#         for detection in output:
#             # extract the class ID and confidence (i.e., probability) of
#             # the current object detection
#             scores = detection[5:]
#             classID = np.argmax(scores)
#             confidence = scores[classID]

#             # filter out weak predictions by ensuring the detected
#             # probability is greater than the minimum probability
#             if confidence > args["confidence"]:
#                 # scale the bounding box coordinates back relative to the
#                 # size of the image, keeping in mind that YOLO actually
#                 # returns the center (x, y)-coordinates of the bounding
#                 # box followed by the boxes' width and height
#                 box = detection[0:4] * np.array([W, H, W, H])
#                 (centerX, centerY, width, height) = box.astype("int")

#                 # use the center (x, y)-coordinates to derive the top and
#                 # and left corner of the bounding box
#                 x = int(centerX - (width / 2))
#                 y = int(centerY - (height / 2))

#                 # update our list of bounding box coordinates, confidences,
#                 # and class IDs
#                 boxes.append([x, y, int(width), int(height)])
#                 confidences.append(float(confidence))
#                 classIDs.append(classID)

#     # apply non-maxima suppression to suppress weak, overlapping bounding
#     # boxes
#     idxs = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"],
#         args["threshold"])

#     # initialize a list of colors to represent each possible class label
#     np.random.seed(42)
#     COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
#         dtype="uint8")
#     # ensure at least one detection exists
#     outboxes = {}
#     if len(idxs) > 0:
#         # loop over the indexes we are keeping
#         for i in idxs.flatten():
#             # extract the bounding box coordinates
#             (x, y) = (boxes[i][0], boxes[i][1])
#             (w, h) = (boxes[i][2], boxes[i][3])
#             outboxes[i] = {'x':x,'y':y,'w':w,'h':h,'t':classIDs[i],'s':confidences[i]}
#             # draw a bounding box rectangle and label on the image
#             color = [int(c) for c in COLORS[classIDs[i]]]
#             cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
#             text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
#             cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
#                 0.5, color, 2)

#     return image,outboxes
    # scalefloat = 0.2
    # w = int(image.shape[1]*scalefloat)
    # h = int(image.shape[0]*scalefloat)
    # resizeimg = cv2.resize(image, (w,h), interpolation = cv2.INTER_AREA)

    # cv2.imshow("Image", resizeimg)
    # cv2.moveWindow('Image',500,0)
    # cv2.waitKey(0)

def main(imgPth):
    labelsPath = os.getcwd() + os.sep +'yolo-net' +os.sep + 'my.names'
    weightsPath = os.getcwd() + os.sep +'yolo-net'+ os.sep + "yolov3.weights"
    configPath = os.getcwd() + os.sep +'yolo-net' + os.sep + "yolov3.cfg"
    inImgPth = imgPth 
    # if not inImgPth:
    #     inImgPth = os.getcwd() + os.sep + 'images' + os.sep +'IMG_1614.jpg'
    yolonet = YOLONet(weightsPath, configPath, labelsPath)
    imImg = cv2.imread(inImgPth)
    image,outboxes = yolonet.fandObjects(imImg)
    scalefloat = 0.2
    w = int(image.shape[1]*scalefloat)
    h = int(image.shape[0]*scalefloat)
    resizeimg = cv2.resize(image, (w,h), interpolation = cv2.INTER_AREA)

    cv2.imshow("Image", resizeimg)
    cv2.moveWindow('Image',500,0)
    cv2.waitKey(0)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print('please input image path')