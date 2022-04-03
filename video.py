import cv2
import numpy as np
import math

frameCounter = 0
minArea = 2300
maxArea = 2850
squareIndex = 0
cap = cv2.VideoCapture('resources/forward_trimmed_720_3.mp4')

while cap.isOpened():
    success, img = cap.read()
    if success == True:
        frameCounter += 1
    elif success == False:
        print('frame not ready')
    img = img[0:720, 160:1130]
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # преобразование картинки в бинарную
    ret, thresh = cv2.threshold(imgGray, 140, 255, cv2.THRESH_BINARY)  # и поиск контуров
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])  # поиск квадрата по его предполагаемой площади
        if minArea < area < maxArea:
            squareIndex = i
            print(area)
            print('*'*100)
            if area < 2000:
                print(' ALARM ' * 10)

    cv2.drawContours(img, contours, squareIndex, (0, 255, 0), 4)
    cv2.imshow('video', img)
    #cv2.imshow('i', thresh)
    length = int(cap.get(cv2.CAP_PROP_FPS))
    print(frameCounter)
    cv2.waitKey(100)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break