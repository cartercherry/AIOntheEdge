#############################################################################################
# Lesson27_Proportional_Pan_Tilt.py    6/24/26                                              #
#  Follow an object of interest (OOI) using proportional control of pan tilt cam movement   #
#  The object of interest is being tracked by color                                         #
#  Reference to AI on the Edge Coourse:  https://www.youtube.com/watch?v=12Gdes_oMQk        #


import cv2
import time
from picamera2 import Picamera2
import numpy as  np
from pan_tilt_tracker import PanTiltTracker

# set up pan tilt mechanism
cam_mount = PanTiltTracker()
pan_angle = 0
tilt_angle = 0   
cam_mount.set_pan(pan_angle)  #look straight ahead
cam_mount.set_tilt(tilt_angle)

piCam = Picamera2(1)  # module 3 piCam
W=1280
H=720
SCREEN_CENTER = (int(W/2), int(H/2))    # center of screen and frame
tStart = time.time()
fps = 0

RES = (W,H)
piCam.preview_configuration.main.size = RES
piCam.preview_configuration.main.format = "RGB888"
piCam.preview_configuration.controls.FrameRate=60
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

textLowerLeft = (int(W*.01),int(H*.06))
fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontThickness = int(W/425)
fontScale = H*.0015
fontColor = (0,0,255)
xPos, yPos = 0, 0
textLowerLeft1 = (int(W*.01),int(H*.06)*2)
textLowerLeft2 = (int(W*.01),int(H*.06)*3)

hueLow, hueHigh = 179, 179  # first red range
hueLow2, hueHigh2 = 0,9     # second red range
satLow, satHigh = 97,255
valLow, valHigh = 138, 255

Hue, Sat, Val = 0,0,0

def onTrack1(val):
    global hueLow
    hueLow = val

def onTrack2(val):
    global hueHigh
    hueHigh = val

def onTrack7(val):
    global hueLow2
    hueLow2 = val

def onTrack8(val):
    global hueHigh2
    hueHigh2 = val


def onTrack3(val):
    global satLow
    satLow = val

def onTrack4(val):
    global satHigh
    satHigh = val

def onTrack5(val):
    global valLow
    valLow = val

def onTrack6(val):
    global valHigh
    valHigh = val

cv2.namedWindow('MyTracker')
cv2.moveWindow('MyTracker',0,H+60)

cv2.createTrackbar('Hue1 Low','MyTracker',hueLow,179,onTrack1)
cv2.createTrackbar('Hue1 High','MyTracker',hueHigh,179,onTrack2)
cv2.createTrackbar('Hue2 Low','MyTracker', hueLow2, 179, onTrack7)
cv2.createTrackbar('Hue2 High','MyTracker', hueHigh2, 179, onTrack8)
cv2.createTrackbar('Sat Low','MyTracker',satLow,255,onTrack3)
cv2.createTrackbar('Sat High','MyTracker',satHigh,255,onTrack4)
cv2.createTrackbar('Val Low','MyTracker',valLow,255,onTrack5)
cv2.createTrackbar('Val High','MyTracker',valHigh,255,onTrack6)

frame = None
def mouseAction(event, x, y, flags, param):
    global frame, xPos, yPos, Hue, Sat, Val
    if event == 0:
        xPos = x
        yPos = y
        if frame is not None:
            frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            Hue,Sat,Val = frameHSV[y,x]


cv2.namedWindow('Camera', cv2.WINDOW_GUI_NORMAL) 
cv2.moveWindow('Camera', 0, 65)
cv2.resizeWindow('Camera',W, H)

cv2.namedWindow('Mask', cv2.WINDOW_GUI_NORMAL)
cv2.moveWindow('Mask', W, 65)
cv2.resizeWindow('Mask',int(W/2), int(H/2))

cv2.namedWindow('Composite', cv2.WINDOW_GUI_NORMAL) 
cv2.moveWindow('Composite', W, 65+int(H/2)+ 25)
cv2.resizeWindow('Composite',int(W/2), int(H/2))


cv2.setMouseCallback('Camera',mouseAction)

try:
    while True:
        deltaT = time.time() - tStart
        tStart=time.time()
        fps = fps*.95 + (1/deltaT)*.05
        frame= piCam.capture_array()
        frame=cv2.flip(frame,-1)
        cv2.circle(frame,SCREEN_CENTER,5,(255,0,0),-1)

        frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)  
        lowerBound1 = np.array([hueLow,satLow, valLow])  
        upperBound1 = np.array([hueHigh, satHigh, valHigh])  
        lowerBound2 = np.array([hueLow2, satLow, valLow])  
        upperBound2 = np.array([hueHigh2, satHigh, valHigh])

        mask1 = cv2.inRange(frameHSV, lowerBound1, upperBound1) 
        mask2 = cv2.inRange(frameHSV, lowerBound2, upperBound2)

        mask = cv2.bitwise_or(mask1, mask2)  # OR mask1, mask2 for both red hue ranges!
        composite = cv2.bitwise_and(frame,frame,mask=mask)
        contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            #cv2.drawContours(frame, contours,-1, (255,0,0), 3)
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            if area > 150:
                #cv2.drawContours(frame, largest_contour,-1, (255,0,0), 3)
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),3)
                cv2.circle(frame,(int(x+w/2), int(y+h/2)),int(w/3),(255,0,0),1)   #circle around center of OOI
                pan_error = int(x+w/2) - int(W/2)
                #print(f'{pan_error=}',end='\r')   # DEBUG
                
                pan_angle = pan_angle - pan_error/95   # proportional control
                pan_angle = max(-90, min(pan_angle,90))  # constrain pan_angle
                if abs(pan_error) > 35:   
                    cam_mount.set_pan(pan_angle)

                tilt_error = int(y+h/2) - int(H/2)
                tilt_angle = tilt_angle - tilt_error/95  #proportional control 
                tilt_angle = max(-45, min(tilt_angle, 90)) # constrain tilt_angle
                if abs(tilt_error) >35:
                    cam_mount.set_tilt(tilt_angle)

        myText = "FPS: "+str(round(fps,1))
        cv2.putText(frame,myText,textLowerLeft,fontFace,fontScale,fontColor,fontThickness)
        
        text1 = "Mouse Pos: "+str((xPos,yPos))
        text2 = "Pixel HSV: "+str((Hue,Sat,Val))
        cv2.putText(frame,text1,textLowerLeft1,fontFace,fontScale,fontColor,fontThickness)    
        cv2.putText(frame,text2,textLowerLeft2,fontFace,fontScale,fontColor,fontThickness)    
        cv2.imshow("Camera", frame)
        cv2.imshow('Composite', composite)
        cv2.imshow('Mask',mask)
        if cv2.waitKey(1)==ord('q'):
            break
except KeyboardInterrupt:
    print('User terminating,  clean up!')
finally:
    cam_mount.set_pan(0)
    cam_mount.set_tilt(0)
    cv2.destroyAllWindows()
    piCam.stop()
    print('Program Terminated')
