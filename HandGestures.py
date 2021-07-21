import cv2
import mediapipe as mp
import time
import mouse
import pyautogui
import time
from pynput.mouse import Button
from pynput.mouse import Controller as mouseController
from pynput.keyboard import Key, Controller as keyController

mouse = mouseController()
keyCont = keyController()

class HandDetection():
    def __init__(self, mode = False, maxHands = 1, detect_confidence = 0.5, track_confidence = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detect_confidence = detect_confidence
        self.track_confidence = track_confidence


        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, #detects image - tracks only if there is a high confidence: setting True makes program very slow
                                self.maxHands,
                                self.detect_confidence,
                                self.track_confidence) #if this param value goes below 0.5, the module will start detection again instead of tracking
        self.mpDraw = mp.solutions.drawing_utils

    def findGestures(self):
        cap = cv2.VideoCapture(0)

        pTime = 0
        cTime = 0


        while(True):
            key = ""
            self.success, self.frame = cap.read()
            imgRGB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(imgRGB)
            #print(results.multi_hand_landmarks)
            self.landmark = []
            yval = []
            xval = []
            if self.results.multi_hand_landmarks:
                for handLm in self.results.multi_hand_landmarks:
                    for id, lm in enumerate(handLm.landmark):
                        height, width, channels = self.frame.shape
                        realx ,realy = int(lm.x*width), int(lm.y * height) #landmark coordinates are given as proportions of the actual image instead of pixel - have to be converted
                        #print("Landmark: {}, X: {}, Y: {}".format(id, realx, realy))
                        self.landmark.append(id)
                        yval.append(realy)
                        xval.append(realx)
                        #can use if statements pertaining to landmark numbers to test their movement/status
                        # for example: for thumbs up, check whether the y position of landmark 4 (thumb tip) is higher than landmark 3 (lower thumb landmark), etc.
                        self.mpDraw.draw_landmarks(self.frame, handLm, self.mpHands.HAND_CONNECTIONS)

                    if (self.thumbDown(yval)):
                        print("thumb down")
                        mouse.scroll(0, -2)

                    elif (self.thumbUp(yval)):
                        print("thumb up")
                        mouse.scroll(0, 2)
                    elif(self.pointFor(xval)):
                        print("forward")
                        keyCont.press(Key.ctrl)
                        keyCont.press(Key.ctrl)
                        keyCont.press(Key.tab)
                        keyCont.release(Key.ctrl)
                        keyCont.release(Key.tab)
                        time.sleep(1)
                    elif (self.leftClick(yval)):
                        print("left click")
                        mouse.press(Button.left)
                        mouse.release(Button.left)
                        time.sleep(0.5)
                    elif(self.rightClick(yval)):
                        print("right click")
                        mouse.press(Button.right)
                        mouse.release(Button.right)
                        time.sleep(0.5)
                    elif(self.pointBack(xval)):
                        print("backward")
                        key = "ctrl+shift+tab"
                        keyCont.press(Key.ctrl)
                        keyCont.press(Key.shift)
                        keyCont.press(Key.tab)
                        keyCont.release(Key.ctrl)
                        keyCont.release(Key.shift)
                        keyCont.release(Key.tab)
                        time.sleep(1)
                    elif(self.palm(yval)):
                        print("mouse")
                        mouse.position = (realx*5, realy*5)
                    else:
                        print("none")
            #cTime = time.time()
            #fps = 1/(cTime - pTime)
            #pTime = cTime

            #cv2.putText(self.frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 5)

            cv2.imshow("Frame", self.frame)
            cv2.waitKey(10)

    def thumbUp(self, yval):
        if len(yval) != 0:
            if self.landmark[yval.index(min(yval))] == 4:
                return True

    def palm(self, yval):
        if len(yval) != 0:
            if(self.landmark[yval.index(max(yval))]) == 0 and self.landmark[yval.index(min(yval))] == 12 and yval[17]>yval[20]and yval[13]>yval[16] and yval[9]>yval[12] and yval[5]>yval[8]:
                return True

    def pointBack(self, xval):
        if len(xval) != 0:
            if (self.landmark[xval.index(max(xval))]) == 8 and self.landmark[xval.index(min(xval))] == 0:
                return True

    def pointFor(self, xval):
        if len(xval) != 0:
            if (self.landmark[xval.index(max(xval))]) == 0 and self.landmark[xval.index(min(xval))] == 8:
                return True

    def thumbDown(self, yval):
        if len(yval) != 0:
            if self.landmark[yval.index(max(yval))] == 4:
                return True

    def rightClick(self, yval):
        if len(yval)!= 0:
            if(self.landmark[yval.index(min(yval))] == 12 and yval[17]<yval[20]and yval[13]<yval[16] and yval[5]>yval[8]): #5,9,13,17 - knuckles
                return True
    def leftClick(self, yval):
        if len(yval) != 0:
            if(yval[5]<yval[8] and yval[17]>yval[20]and yval[13]>yval[16]):
                return True
if __name__ == "__main__":
    hand = HandDetection()
    hand.findGestures()