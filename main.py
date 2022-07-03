# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 22:32:16 2021

@author: ajuly
"""

import sys 
import argparse 
import json
import csv
import math
 
import cv2

# Save video frames to list 
#Args:
    # pathIn: path to video
def extractImages(pathIn): 
    frames = [] 
    cap = cv2.VideoCapture(pathIn) 
    ret = True 
     
    while ret: 
      ret, img = cap.read() # read one frame from the 'capture' object; img is (H, W, C) 
      if ret: 
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  
        frames.append(img) 
    return frames


# Function to draw head bbox or body bbox
#Args:
    # frame: current frame
    # centers: body or head centers
    # wh: W or H of body or head
def plotHeadBody(frame, centers, wh):
    
    if centers[0] != -1 and centers[1] != -1 and wh[0] != -1 and wh[1] != -1:
        cv2.rectangle(frame,(int(centers[0]-(wh[0]/2)),int(centers[1]+(wh[1]/2))),(int(centers[0]+(wh[0]/2)),int(centers[1]-(wh[1]/2))),(255,255,255),2)
   
    return 0

# Function to calculate unit vector and length
#Args:
    # list1: coordinates of 1st body part (x,y)
    # list2: coordinates of 2snd body part (x,y)
def unitVectorCalc(list1, list2):
    
    
    Xpoint1 = list1[0][0]
    YPoint1 = list1[0][1]
    
    Xpoint2 = list2[0][0]
    YPoint2 = list2[0][1]
    
    if any(i == -1 for i in [Xpoint1,YPoint1,Xpoint2,YPoint2]):
        return -1,-1, 0
    else:
        # Calculating an unit vector between 2 points
        distance = [Xpoint1 - Xpoint2, YPoint1 - YPoint2]
        norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
        
        # Unit vector vec_x, vec_y
        unitVector = [-(distance[0] / norm), -(distance[1] / norm)]
       
        length = math.sqrt((distance[0])**2 + (distance[1])**2)
        return unitVector[0],unitVector[1], length
    
# Create a CSV file and write down a header
def createCVSfile():
    # open the file in the write mode
    f = open('csv_file1.csv', 'w', newline='')
    
    # create the csv writer
    writer = csv.writer(f)
    
    header = ['frame_ID','person_ID','head_center_x','head_center_y','head_width','head_height','body_center_x','body_center_y','body_width','body_height','left_shoulder_x','left_shoulder_y','left_shoulder_vec_x','left_shoulder_vec_y','left_upper_arm_length','left_elbow_vec_x','left_elbow_vec_y','left_lower_arm_length','right_shoulder_x','right_shoulder_y','right_shoulder_vec_x','right_shoulder_vec_y','right_upper_arm_length','right_elbow_vec_x','right_elbow_vec_y','right_lower_arm_length','left_hip_x','left_hip_y','left_hip_vec_x','left_hip_vec_y','left_upper_leg_length','left_knee_vec_x','left_knee_vec_y','left_lower_leg_length','right_hip_x','right_hip_y','right_hip_vec_x','right_hip_vec_y','right_upper_leg_length','right_knee_vec_x','right_knee_vec_y','right_lower_leg_length']
    
    with open('csv_file1.csv', 'w', newline='') as f:
        # write the header
        writer.writerow(header)
    
    return f, writer

# Function to draw arms or legs on the frame
#Args:
    # frame: current frame
    # part: current body part
def plotArmsLegs(frame, part):
   
    if all(i != -1 for i in part[0][-1]) and all(i != -1 for i in part[1][-1]):
        cv2.line(frame,(int(part[0][-1][0]),int(part[0][-1][1])),(int(part[1][-1][0]),int(part[1][-1][1])),(255,255,225),2)

    if all(i != -1 for i in part[1][-1]) and all(i != -1 for i in part[2][-1]):        
        cv2.line(frame,(int(part[1][-1][0]),int(part[1][-1][1])),(int(part[2][-1][0]),int(part[2][-1][1])),(255,255,225),2)
                
    return 0

# Part 1 - generating a video and Part 2 - creating CSV
#Args:
    # videoframes: all video frames
    # jsonKeypoints: keypoints from JSON
    # onImgShow: TRUE if plot, FALSE if not
def generateBoxLines(videoframes,jsonKeypoints, onImgShow = False):
    
    #######ARMS#######
    # to store RShoulder (x,y), RElbow (x,y), RWrist(x,y)
    # [0] for RShoulder (x,y)
    # [1] for RElbow (x,y)
    # [2] for RWrist(x,y)
    ListRightArm = [[],[],[]]
    # to store LShoulder (x,y), LElbow (x,y), LWrist(x,y)
    # [0] for LShoulder (x,y)
    # [1] for LElbow (x,y)
    # [2] for LWrist(x,y)
    ListLeftArm = [[],[],[]]
    
    #######LEGS#######
    # to store RHip (x,y), RKnee (x,y), RAnkle(x,y)
    # [0] for RHip (x,y)
    # [1] for RKnee (x,y)
    # [2] for RAnkle(x,y)
    ListRightLeg = [[],[],[]]
    # to store LHip (x,y), LKnee (x,y), LAnkle(x,y)
    # [0] for LHip (x,y)
    # [1] for LKnee (x,y)
    # [2] for LAnkle(x,y)
    ListLeftLeg = [[],[],[]]
    
    #creare CVS file
    CVSf, CVCwriter = createCVSfile()
    
    for fr in range(len(videoframes)):
        
        #######HEAD#######
        #to store head_center_x and head_center_y
        head_center_x, head_center_y = 0, 0 
        #to store head_width and head_height
        head_w, head_h = 0, 0
        
        #######BODY#######
        # to store body_center_x and body_center_y
        body_center_x, body_center_y = 0, 0
        #to store body_width and body_height
        body_w, body_h = 0, 0
        
        PersonsperFrame = len(jsonKeypoints['frames'][str(fr)])
        
        for per in range(PersonsperFrame):
            if per < 10: pernum = str(per).zfill(2)

        
            #HEAD: 
            # head_center_x: considering that the X center is keypoint #33 - X value
            head_center_x = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(33)][0] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(33)][0] != -1 else -1
            # head_center_y: considering that the Y center is keypoint #33 - Y value
            head_center_y = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(33)][1] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(33)][1] != -1 else -1
    
            
            # head_width: distance between keypoint #16 and #0 as the widest distance, X values
            temp = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(16)][0] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(16)][0] != -1 else -1
            temp1 = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(0)][0] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(0)][0] != -1 else -1
            head_w = temp-temp1 if temp != -1 and temp1 != -1 else -1
            
            # head_height: distance between keypoint #19(or 24) and #8 as the heighest distance, Y values
            temp = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(8)][1] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(24)][1] != -1 else -1
            temp1 = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(24)][1] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['face_kpts'][str(8)][1] != -1 else -1
            head_h = temp-temp1 if temp != -1 and temp1 != -1 else -1
            
        
            #BODY:
             
            # body_center_x: considering that the X center is keypoint #1 - X value
            body_center_x = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(1)][0] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(1)][0] != 1 else -1
            
            # body_center_y: distance between keypoint #1 and #8 as the heighest distance
            temp = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(1)][1] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(1)][1] != -1 else -1
            temp1 = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(8)][1] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(8)][1] != -1 else -1
            body_center_y = (temp + temp1)/2 if temp != -1 and temp1 != -1 else -1
            
            # body_height: 
            body_h = temp1-temp  
           
                
            # body_width: distance between keypoint #5 and #2 as the widest distance, X values
            temp = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(5)][0] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(5)][0] != -1 else -1
            temp1 = jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(2)][0] if jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(2)][0] != -1 else -1
            body_w = temp - temp1 if temp != -1 and temp1 != -1 else -1
            
                
           
            # DRAW 
            if onImgShow == True:
                
                #plot Head
                plotHeadBody(videoframes[fr], [head_center_x,head_center_y], [head_w,head_h])
                # plot Body
                plotHeadBody(videoframes[fr], [body_center_x,body_center_y], [body_w,body_h])

            #ARMS:
                
            ListRightArm[0].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(2)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(2)][1]])
            ListRightArm[1].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(3)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(3)][1]])
            ListRightArm[2].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(4)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(4)][1]])
                
            ListLeftArm[0].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(5)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(5)][1]])
            ListLeftArm[1].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(6)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(6)][1]])
            ListLeftArm[2].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(7)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(7)][1]])
            
            
            
            # DRAW  
            if onImgShow == True:
                # plot right arm
                plotArmsLegs(videoframes[fr], ListRightArm)
                # plot left arm
                plotArmsLegs(videoframes[fr], ListLeftArm)
                
            
            #LEGS:
                
            ListRightLeg[0].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(9)][0],jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(9)][1]])
            ListRightLeg[1].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(10)][0],jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(10)][1]])
            ListRightLeg[2].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(11)][0],jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(11)][1]])
                
            ListLeftLeg[0].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(12)][0],jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(12)][1]])
            ListLeftLeg[1].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(13)][0],jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(13)][1]])
            ListLeftLeg[2].append([jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(14)][0], jsonKeypoints['frames'][str(fr)]["person_"+ pernum]['pose_kpts'][str(14)][1]])

            # DRAW 
            
            if onImgShow == True:
                # plot right leg
                plotArmsLegs(videoframes[fr], ListRightLeg)
                # plot left leg
                plotArmsLegs(videoframes[fr], ListLeftLeg)

            cv2.imwrite(str(fr)+".jpg", videoframes[fr])
            cv2.waitKey(0)
            
            
            # Unit vector and lenghts
            
            #ARMS vec_x, vec_y, length
            left_shoulder_vec_x, left_shoulder_vec_y, left_upper_arm_length  = unitVectorCalc(ListLeftArm[0],ListLeftArm[1])
            left_elbow_vec_x, left_elbow_vec_y, left_lower_arm_length = unitVectorCalc(ListLeftArm[1],ListLeftArm[2])
            right_shoulder_vec_x, right_shoulder_vec_y, right_upper_arm_length = unitVectorCalc(ListRightArm[0],ListRightArm[1])
            right_elbow_vec_x, right_elbow_vec_y, right_lower_arm_length = unitVectorCalc(ListRightArm[1],ListRightArm[2])
            
            
            #LEGS vec_x, vec_y, length
            left_hip_vec_x, left_hip_vec_y, left_upper_leg_length = unitVectorCalc(ListLeftLeg[0],ListLeftLeg[1])
            left_knee_vec_x, left_knee_vec_y, left_lower_leg_length = unitVectorCalc(ListLeftLeg[1],ListLeftLeg[2])
            right_hip_vec_x, right_hip_vec_y, right_upper_leg_length = unitVectorCalc(ListRightLeg[0],ListRightLeg[1])
            right_knee_vec_x, right_knee_vec_y, right_lower_leg_length = unitVectorCalc(ListRightLeg[1],ListRightLeg[2])
            
            
            # write a row to the CVS file:
            row = [str(fr),"person_"+ pernum, str(head_center_x), str(head_center_y), str(head_w), str(head_h), \
                   str(body_center_x), str(body_center_y), str(body_w), str(body_h), str(ListLeftArm[0][-1][0]), str(ListLeftArm[0][-1][1]), str(left_shoulder_vec_x),str(left_shoulder_vec_y),str(left_upper_arm_length), \
                           str(left_elbow_vec_x), str(left_elbow_vec_y), str(left_lower_arm_length), str(ListRightArm[0][-1][0]), str(ListRightArm[0][-1][1]), str(right_shoulder_vec_x), str(right_shoulder_vec_y), str(right_upper_arm_length), str(right_elbow_vec_x), \
                           str(right_elbow_vec_y), str(right_lower_arm_length), str(ListLeftLeg[0][-1][0]), str(ListLeftLeg[0][-1][1]),str(left_hip_vec_x), str(left_hip_vec_y), str(left_upper_leg_length),str(left_knee_vec_x), str(left_knee_vec_y), str(left_lower_leg_length), \
                               str(ListRightLeg[0][-1][0]), str(ListRightLeg[0][-1][1]),str(right_hip_vec_x), str(right_hip_vec_y), str(right_upper_leg_length),str(right_knee_vec_x), str(right_knee_vec_y), str(right_lower_leg_length)]                                                                                                                                              
                                                                                                                                                           
                                                              
            CVCwriter.writerow(row)
            ListRightArm = [[],[],[]]
            ListLeftArm = [[],[],[]]
            ListRightLeg = [[],[],[]]
            ListLeftLeg = [[],[],[]]
            
        print(fr)
    
    # close the file
    CVSf.close()
    
    return 0

if __name__=="__main__": 
   
   videoframes = extractImages("clip_05.mp4") 

   # Part 1: generate an output video with boxes and lines
   jsonFile = open("clip_05_pose.json")
   jsonKeypoints = json.load(jsonFile)
    
   onImgShow = True #True if show images with boxes and lines 
   generateBoxLines(videoframes, jsonKeypoints, onImgShow)


   print("done")