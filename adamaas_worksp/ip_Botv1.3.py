#____________________________________________________________________________________________________________________________________________________

from pyfirmata import Arduino, util
import time 

import numpy as np
import argparse
import cv2
import math

#___________________________________________________________Setup for py firmata_______________________________________________________________
board = Arduino("/dev/ttyACM0") # "/dev/ttyACM0" is the communication port for the arduino usb , it may vary , in Windows use "COM0" 

iterator = util.Iterator(board) 
iterator.start()


LeftM1 = board.get_pin('d:5:p')# 'd' stands for digital '5' is the pin no. on arduino 'p' is for pwd singal 
LeftM2 = board.get_pin('d:6:p')
RightM1 = board.get_pin('d:10:p')
RightM2 = board.get_pin('d:11:p')


#---------------------------------------------------------------------------------------------------------------------------------------------
def constrn(value,Llim,Ulim):# Llim is Lower bound,Ulim is Uower bound
	if (value>Ulim):
		value=Ulim
	if (value<Llim):
		value=Llim
	else : 
		value = value
	return value	
	
	
  
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help = "path to the (optional) video file")
args = vars(ap.parse_args())
 
# define the upper and lower boundaries of the HSV pixel
# intensities to be considered for red color


lower = np.array([0, 100, 100], dtype = "uint8")
upper = np.array([255, 255, 255], dtype = "uint8")


# if a video path was not supplied, grab the reference
# to the gray
if not args.get("video", False):
     camera = cv2.VideoCapture(0)
 
# otherwise, load the video
else:
     camera = cv2.VideoCapture(args["video"])
# keep looping over the frames in the video
#_____________________________________________________Main loop for execution__________________________________________________________________________
while True:
     # grab the current frame
     (grabbed, frame) = camera.read()
 
     # if we are viewing a video and we did not grab a
     # frame, then we have reached the end of the video
     if args.get("video") and not grabbed:
         break
 
     # resize the frame, convert it to the HSV color space,         
     # and determine the HSV pixel intensities that fall into
     # the speicifed upper and lower boundaries

     frame = cv2.resize(frame,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
     

     converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     objectMask = cv2.inRange(converted, lower, upper)
 
     # apply a series of erosions and dilations to the mask
     # using an elliptical kernel
     kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
     objectMask = cv2.erode(objectMask, kernel, iterations = 2)
     objectMask = cv2.dilate(objectMask, kernel, iterations = 2)
 
     # blur the mask to help remove noise, then apply the
     # mask to the frame
     objectMask = cv2.GaussianBlur(objectMask, (3, 3), 0)
     objectd = cv2.bitwise_and(frame, frame, mask = objectMask)
     
     # converting to gray scale
     gray = cv2.cvtColor(objectd, cv2.COLOR_BGR2GRAY)
     height, width = gray.shape

     linePixSum = 0
     threshold = 5000
	
     wall1 = 0
     wall2 = 0
     #_______________________________________Algorithm for detection of the centre of the block________________________________________________________
     for x1  in range(0,width):
	for y1 in range(0,height):
 		linePixSum += gray[y1,(width-x1-1)]
	if (linePixSum > threshold):
		cv2.line(gray,(width-x1-1,0),(width-x1-1,height),(255,0,0),2)
		wall1 = width-x1-1	
		break	
	linePixSum = 0	 
     linePixSum = 0	
     
     for x2 in range(0,width):
	for y2 in range(0,height):
 		linePixSum += gray[y2,x2]
	if (linePixSum > threshold):
		cv2.line(gray,(x2,0),(x2,height),(255,0,0),2)
		wall2 = x2				
		break
	linePixSum = 0	 
     linePixSum = 0
    	
     
     #print("The left wall is at  ",wall1," and right wall is at",wall2,"\n")
     
     center = (wall1 + wall2)/2
     pitch = 160-abs(wall1 - wall2)
     pitch = pitch/2
     pitch = 1.4*pitch
      
     if pitch == 112 :
        pitch = 0	
     yaw = center-(width/2)
     yaw = 0.7*yaw
     
     if yaw == -112:
     	yaw = 0
     
     if yaw>-0.2 and yaw <0.2:
	yaw = 0	
     #-------------------------------------------------------------------------------------------------------------------------------------------
     
     r_motor = (pitch+yaw)/200.0
     l_motor = (pitch-yaw)/200.0
     
     r_motor1 = constrn(r_motor,0.0,1.0)
     l_motor1 = constrn(l_motor,0.0,1.0)
     
     r_motor2 = abs(constrn(r_motor,-1.0,0.0))
     l_motor2 = abs(constrn(l_motor,-1.0,0.0))
     
     # print("Rm1",r_motor1,"Rm2",r_motor2,"Lm1",l_motor1,"Lm2",l_motor2,"\n")
     
     print 'RM1 = %(Rm1).2f RM2 = %(Rm2).2f LM1 =  %(Lm1).2f LM2 = %(Lm2).2f ' % {
     'Rm1': r_motor1,
     'Rm2': r_motor2,
     'Lm1': l_motor1,
     'Lm2': l_motor2,
     }
     
     # commands for motors--------------------------------------------------------- 
     LeftM1.write(l_motor1)
     LeftM2.write(l_motor2)
     RightM1.write(r_motor1)
     RightM2.write(r_motor2)

     # show the objectd in the image along with the mask
     cv2.imshow("images", np.hstack([frame, objectd]))
     cv2.imshow("detection", gray)
  
     # if the 'q' key is pressed, stop the loop
     if cv2.waitKey(1) & 0xFF == ord("q"):
	  LeftM1.write(0)
     	  LeftM2.write(0)
     	  RightM1.write(0)
     	  RightM2.write(0)
	  break

   	 	

board.exit()
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

def jas(name)
	print("Hello, " + name + ". Testing!")
	
