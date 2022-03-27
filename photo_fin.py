import cv2
import numpy as np
import math

minArea = 120000  # в этих рамках находится площадь искомого квадрата
maxArea = 140000
squareIndex = 0  # инекс контура квадрата в массиве контуров
yMin = xMax = 0  # на самом деле так удобнее

source = cv2.imread("Resources/mark1_15_deg.png")
img = cv2.resize(source, (600, 600))
# img = source.copy()  # для отладки
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # преобразование картинки в бинарную
ret, thresh = cv2.threshold(imgGray, 150, 255, 0)  # и поиск контуров
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

for i in range(len(contours)):
    area = cv2.contourArea(contours[i])  # поиск квадрата по его предполагаемой площади
    print(area)
    if minArea < area < maxArea:
        squareIndex = i

epsilon = 0.1 * cv2.arcLength(contours[squareIndex], True)  # определение угловых точек квадрата
approx = cv2.approxPolyDP(contours[squareIndex], epsilon, True)

# print(approx)
topLine = [[approx[0][0][0], approx[0][0][1]], [approx[1][0][0], approx[1][0][1]]]
for i in 2, 3:
    if approx[i][0][1] < topLine[1][1]:  # определение левого верхнего угла
        topLine[1][0] = approx[i][0][0]
        topLine[1][1] = approx[i][0][1]
        if approx[i][0][1] < topLine[0][1]:
            topLine[0][0] = approx[i][0][0]
            topLine[0][1] = approx[i][0][1]
print(topLine)
if topLine[0][0] > topLine[1][0]:
    topLine[0][0], topLine[1][0] = topLine[1][0], topLine[0][0]
    topLine[0][1], topLine[1][1] = topLine[1][1], topLine[0][1]

angleDeg = math.atan((topLine[1][1] - topLine[0][1]) /  # определение угла наклона квадрата в градусах
                     (topLine[1][0] - topLine[0][0])) * 57.2958
if angleDeg < 0:  # если угол больше 45 градусов, верхняя линия наклонена под отрицательным углом
    angleDeg += 90  # чтобы это парировать, прибавляем 90 градусов и получаем наклон верхней правой линии


center = [int((approx[0][0][0] + approx[2][0][0]) / 2), int((approx[2][0][1] + approx[0][0][1]) / 2)]
print(center)  # определение центра квадрата(середина линии между 2 противоположными углами)

for i in range(4):
    if approx[i][0][0] > xMax:
        xMax = approx[i][0][0]

if topLine[0][1] < topLine[1][1]:
    yMin = topLine[0][1]  # определение максимального Х и минимального У
else:
    yMin = topLine[1][1]
dx = xMax - center[0]
dy = center[1] - yMin
imgCrop = img[(center[1] - dy):(center[1] + dy), (center[0] - dx):(center[0] + dx)]  # первичная обрезка картинки
                                                                                     # чтобы не поворачивать всю
matrix = cv2.getRotationMatrix2D(((imgCrop.shape[0] / 2), (imgCrop.shape[1] / 2)), angleDeg, 1)
imgRotate = cv2.warpAffine(imgCrop, matrix, (imgCrop.shape[1], imgCrop.shape[0]))  # поворот картинки на полученный угол


img = cv2.drawContours(img, contours, squareIndex, (255, 0, 0), 2)
cv2.line(img, topLine[0], topLine[1], (0, 255, 0), 2)
img = cv2.circle(img, center, 10, (255, 0, 0), 2)
cv2.imshow("Image", img)
cv2.imshow("Cropped", imgRotate)
# cv2.imshow("Threshold", thresh)
cv2.waitKey(0)
