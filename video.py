import cv2
import numpy as np
import math

cap = cv2.VideoCapture('resources/forward_trimmed_720_3.mp4')
frameCounter = 0
minArea = 2300  # в этих рамках находится площадь искомого квадрата
maxArea = 2850
angleDeg = 0  # угол поворота в градусах, в пределах 0-90 градусов
squareIndex = 0  # инекс контура квадрата в массиве контуров
yMin = xMax = 0  # на самом деле так удобнее
direction = 0  # угол, кратный 90 градусам, определяющий направление движения робота
points = np.zeros((5, 2), dtype=int)  # здесь хранятся значения точек, проверяемых на цвет
anglePrev = angleCurr = 0  # предыдущий и текущий угол поворота
centerPrev = centerCurr = [[0, 0], [0, 0]]  # координаты предыдущего и текущего центра
centerArray = [[0, 0]]

# проверка на цвет нужна для распознавания кода на картинке

def find_points(midPoint, distance, line_flag, direction):
    deltaX = deltaY = distance // 2  # эта функция вычисляет координаты точек слева и справа от исходной
    if line_flag == 1:
        if direction == 1 or direction == 3: deltaX = 0
        elif direction == 2 or direction == 4: deltaY = 0
        points[0] = [midPoint[0] - (2 * deltaX), midPoint[1] - (2 * deltaY)]
        points[4] = [midPoint[0] + (2 * deltaX), midPoint[1] + (2 * deltaY)]
    points[1] = [midPoint[0] - deltaX, midPoint[1] - deltaY]  # для линии используем 5 точек, для квадрата используем 3
    points[2] = [midPoint[0], midPoint[1]]
    points[3] = [midPoint[0] + deltaX, midPoint[1] + deltaY]
# я не встречал помехи на картинке с камеры, но для порядка не помешает

def define_direction(picture, dir):
    global direction
    if (int(picture[points[0][1]][points[0][0]]) + int(picture[points[1][1]][points[1][0]]) +
        int(picture[points[2][1]][points[2][0]]) + int(picture[points[3][1]][points[3][0]]) +
        int(picture[points[4][1]][points[4][0]]) / 5) > 125:
        direction = 90 * (dir - 1)

'''************************************************  ОСНОВНОЙ ЦИКЛ  ************************************************'''
while cap.isOpened():
    success, img = cap.read()
    if success == True:
        frameCounter += 1
    elif success == False:
        print('frame not ready')

    if frameCounter > 2:
        centerPrev = centerCurr

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

    epsilon = 0.1 * cv2.arcLength(contours[squareIndex], True)  # определение угловых точек квадрата
    approx = cv2.approxPolyDP(contours[squareIndex], epsilon, True)
    topLine = [[approx[0][0][0], approx[0][0][1]], [approx[1][0][0], approx[1][0][1]]]
    for i in 2, 3:
        if approx[i][0][1] < topLine[1][1]:  # определение левого верхнего угла
            topLine[1][0] = approx[i][0][0]
            topLine[1][1] = approx[i][0][1]
            if approx[i][0][1] < topLine[0][1]:
                topLine[0][0] = approx[i][0][0]
                topLine[0][1] = approx[i][0][1]

    if topLine[0][0] > topLine[1][0]:
        topLine[0][0], topLine[1][0] = topLine[1][0], topLine[0][0]
        topLine[0][1], topLine[1][1] = topLine[1][1], topLine[0][1]

    if topLine[1][0] == topLine[0][0]: angleDeg = 0  # заплатка: иногда верхняя линия определяется как вертикальная
    else:
        angleDeg = round(math.atan((topLine[1][1] - topLine[0][1]) /  # определение угла наклона квадрата в градусах
                    (topLine[1][0] - topLine[0][0])) * 57.2958)  # угол определяется в рамках от 0 до 90 градусов

    centerCurr = center = [int((approx[0][0][0] + approx[2][0][0]) / 2), int((approx[2][0][1] + approx[0][0][1]) / 2)]
    # определение центра квадрата(середина линии между 2 противоположными углами)

    for i in range(4):
        if approx[i][0][0] > xMax:
            xMax = approx[i][0][0]

    if topLine[0][1] < topLine[1][1]:
        yMin = topLine[0][1]  # определение максимального Х и минимального У
    else:
        yMin = topLine[1][1]
    dx = xMax - center[0]
    dy = center[1] - yMin
    imgCrop = thresh[(center[1] - dy):(center[1] + dy), (center[0] - dx):(center[0] + dx)]  # первичная обрезка картинки
    # чтобы не поворачивать всю
    matrix = cv2.getRotationMatrix2D(((imgCrop.shape[0] / 2), (imgCrop.shape[1] / 2)), angleDeg, 1)
    imgRotate = cv2.warpAffine(imgCrop, matrix,
                               (imgCrop.shape[1], imgCrop.shape[0]))  # поворот картинки на полученный угол

    halfLine = int(math.sqrt(((approx[0][0][0] - approx[1][0][0]) ** 2) +
                             ((approx[0][0][1] - approx[1][0][1]) ** 2)) // 2)
    # половина длины линии между противоположными углами
    center = [int(imgRotate.shape[0] / 2), int(imgRotate.shape[1] / 2)]
    print('halfLine: ', halfLine)
    print('center coordinates: ', center)
    imgFin = imgRotate[(center[1] - halfLine):(center[1] + halfLine), (center[0] - halfLine):(center[0] + halfLine)]
    if imgFin.shape[0] == 0 or imgFin.shape[1] == 0:
        imgFin = imgRotate  # при малых углах поворота одна из осей может обнулиться, исправить позже
    print('shape of final image: ', imgFin.shape)
    print('angle: ', angleDeg)
    imgFin = cv2.resize(imgFin, (300, 300))

    unit = round(imgFin.shape[0] / 12)  # 1/12 картинки это ширина её рамки и половина ширины крайней линии
    find_points([unit * 6, unit * 3], unit, 1, 1)
    define_direction(imgFin, 1)  # определение направления поворота робота
    '''find_points([unit * 9, unit * 6], unit, 1, 2)
    define_direction(imgFin, 2)
    find_points([unit * 6, unit * 9], unit, 1, 1)
    define_direction(imgFin, 3)
    find_points([unit * 3, unit * 6], unit, 1, 2)
    define_direction(imgFin, 4)'''
    angleDeg += direction
    print(angleDeg)

    img = cv2.drawContours(img, contours, squareIndex, (255, 0, 0), 2)
    cv2.line(img, topLine[0], topLine[1], (0, 255, 0), 2)

    centerArray.append(centerCurr)
    print(centerArray)
    if frameCounter > 2:
        for i in range(1, len(centerArray) - 1):
            if centerArray[i] != centerArray[i + 1]:
                cv2.line(img, centerArray[i], centerArray[i + 1], (0, 255, 0), 2)

    cv2.circle(imgFin, (points[0][0], points[0][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[0][0], points[0][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[1][0], points[1][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[1][0], points[1][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[2][0], points[2][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[2][0], points[2][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[3][0], points[3][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[3][0], points[3][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[4][0], points[4][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[4][0], points[4][1]), 4, (255, 255, 255), 2)

    img = cv2.drawContours(img, contours, squareIndex, (255, 0, 0), 2)
    cv2.line(img, topLine[0], topLine[1], (0, 255, 0), 2)
    cv2.imshow("Image", img)
    #imshow("Cropped", imgRotate)
    cv2.imshow("Fin", imgFin)
    print('frame ', frameCounter)
    cv2.waitKey(100)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
