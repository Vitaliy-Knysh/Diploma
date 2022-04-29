import cv2
import numpy as np
import math
#import my_server
#import navigation
#import threading

cap = cv2.VideoCapture('rtsp://admin:admin@192.168.0.91/stream1')
frameCounter = 0
minArea = 1500  # в этих рамках находится площадь искомого квадрата
maxArea = 3000
angleDeg = 0  # угол поворота в градусах, в пределах 0-90 градусов
squareIndex = 0  # инекс контура квадрата в массиве контуров
yMin = xMax = 0  # на самом деле так удобнее
direction = 0  # угол, кратный 90 градусам, определяющий направление движения робота
points = np.zeros((5, 2), dtype=int)  # здесь хранятся значения точек, проверяемых на цвет
anglePrev = angleCurr = 0  # предыдущий и текущий угол поворота
centerPrev = centerCurr = [0, 0]  # координаты предыдущего и текущего центра
centerArray = [[0, 0]]
targetPoint = [700, 350]
# проверка на цвет нужна для распознавания кода на картинке
Mtx = np.fromfile('resources/Calibrate.npy')
camera_matrix = np.array([[round(Mtx[0],2), round(Mtx[1],2), round(Mtx[2],2)], [round(Mtx[3],2), round(Mtx[4],2), round(Mtx[5],2)], [round(Mtx[6],2), round(Mtx[7],2), round(Mtx[8],2)]])
dist_coefs = np.array([[round(Mtx[9],2), round(Mtx[10],2), round(Mtx[11],2),round(Mtx[12],2),round(Mtx[13],2)]])
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (size[0], size[1]), 1, (size[0], size[1]))
x, y, w, h = roi
M = cv2.getRotationMatrix2D((size[0]/2,size[1]/2),5,1)

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
# кроме эффекта рыбьего глаза помех на картинке нет

def define_direction(picture, dir):
    global direction
    if (int(picture[points[0][1]][points[0][0]]) + int(picture[points[1][1]][points[1][0]]) +
        int(picture[points[2][1]][points[2][0]]) + int(picture[points[3][1]][points[3][0]]) +
        int(picture[points[4][1]][points[4][0]]) / 5) < 125:
        direction = 90 * (dir - 1)

'''thread = threading.Thread(target=my_server.start, args=()) #  старт сервера
thread.start()'''
#***************************************************  ОСНОВНОЙ ЦИКЛ  ***************************************************
#********************************************  НАЧАЛО БЛОКА ОБРАБОТКИ ВИДЕО  *******************************************
while cap.isOpened():
    success, img = cap.read()
    img = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)
    img = img[20:700, 170:1120]

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # преобразование картинки в бинарную
    ret, thresh = cv2.threshold(imgGray, 200, 255, cv2.THRESH_BINARY)  # и поиск контуров
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])  # поиск квадрата по его предполагаемой площади
        epsilon = 0.1 * cv2.arcLength(contours[i], True)  # определение угловых точек квадрата
        approx = cv2.approxPolyDP(contours[i], epsilon, True)  # поиск квадрата по форме
        if len(approx) == 4:
            if minArea < area < maxArea:
                squareIndex = i
                print(area)
                print(approx)
                print('*' * 100)
                break

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
    dy = center[1] - yMin  # метка квадратная, поэтому к центру по обеим осям прибавляется Ymax
    imgCrop = thresh[(center[1] - dy):(center[1] + dy), (center[0] - dy):(center[0] + dy)]  # первичная обрезка картинки
    # чтобы не поворачивать всю
    matrix = cv2.getRotationMatrix2D(((imgCrop.shape[0] / 2), (imgCrop.shape[1] / 2)), angleDeg, 1)
    imgRotate = cv2.warpAffine(imgCrop, matrix,
                               (imgCrop.shape[1], imgCrop.shape[0]))  # поворот картинки на полученный угол

    imgBackground = np.zeros_like(imgCrop)

    halfLine = int(math.sqrt(((approx[0][0][0] - approx[1][0][0]) ** 2) +
                             ((approx[0][0][1] - approx[1][0][1]) ** 2)) // 2)
    # половина длины линии между противоположными углами
    center = [int(imgRotate.shape[0] / 2), int(imgRotate.shape[1] / 2)]
    #print('halfLine: ', halfLine)
    #print('center coordinates: ', center)
    imgFin = imgRotate[(center[1] - halfLine):(center[1] + halfLine), (center[0] - halfLine):(center[0] + halfLine)]
    if imgFin.shape[0] == 0 or imgFin.shape[1] == 0:
        imgFin = imgRotate  # при малых углах поворота одна из осей может обнулиться, исправить позже
    '''print('shape of final image: ', imgFin.shape)
    print('angle: ', angleDeg)'''
    imgFin = cv2.resize(imgFin, (300, 300))

    unit = round(imgFin.shape[0] / 12)  # 1/12 картинки это ширина её рамки и половина ширины крайней линии
    find_points([unit * 6, unit * 3], unit, 1, 1)
    define_direction(imgFin, 1)  # определение направления поворота робота
    find_points([unit * 9, unit * 6], unit, 1, 2)
    define_direction(imgFin, 2)
    find_points([unit * 6, unit * 9], unit, 1, 1)
    define_direction(imgFin, 3)
    find_points([unit * 3, unit * 6], unit, 1, 2)
    define_direction(imgFin, 4)
    angleDeg += direction
    angleCurr = angleDeg
    #print(angleDeg)
    if angleCurr < 0:
        angleCurr += 360

    img = cv2.drawContours(img, contours, squareIndex, (255, 0, 0), 2)
    cv2.line(img, topLine[0], topLine[1], (0, 255, 0), 2)

    centerArray.append(centerCurr)
    if frameCounter > 2:
        for i in range(1, len(centerArray) - 1):
            if centerArray[i] != centerArray[i + 1]:
                cv2.line(img, centerArray[i], centerArray[i + 1], (0, 255, 0), 2)
    speed = round(math.sqrt(((centerCurr[0] - centerPrev[0]) ** 2) +
                  ((centerCurr[1] - centerPrev[1]) ** 2)))
    if speed != 0:
        print('speed: ', speed)
    angularVel = angleCurr - anglePrev
    if angularVel != 0:
        print('angular velocity: ', angularVel)
#********************************************  КОНЕЦ БЛОКА ОБРАБОТКИ ВИДЕО  ********************************************
#***********************************************  НАЧАЛО БЛОКА НАВИГАЦИИ  **********************************************
    '''if navigation.proxCheck(centerCurr[0], centerCurr[1], targetPoint[0], targetPoint[1]) == False:
        print('proximity check not passed')
        dir, angleDiff = navigation.angleDiff(angleCurr, centerCurr[0], centerCurr[1], targetPoint[0], targetPoint[1])
        print('angle of difference: ', angleDiff)
        my_server.serverReadyFlag = True
        my_server.command = navigation.moveSimple(angleDiff)'''

#************************************************  КОНЕЦ БЛОКА НАВИГАЦИИ  **********************************************
#***********************************************  НАЧАЛО БЛОКА ОТРИСОВКИ  **********************************************
    cv2.circle(imgFin, (points[0][0], points[0][1]), 2, (0, 0, 0), 2)  # показывает проверяемые точки
    cv2.circle(imgFin, (points[0][0], points[0][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[1][0], points[1][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[1][0], points[1][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[2][0], points[2][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[2][0], points[2][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[3][0], points[3][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[3][0], points[3][1]), 4, (255, 255, 255), 2)
    cv2.circle(imgFin, (points[4][0], points[4][1]), 2, (0, 0, 0), 2)
    cv2.circle(imgFin, (points[4][0], points[4][1]), 4, (255, 255, 255), 2)

    cv2.putText(img, str(angleCurr), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(img, str(angleCurr), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


    img = cv2.drawContours(img, contours, squareIndex, (255, 0, 0), 2)
    cv2.line(img, centerCurr, targetPoint, (255, 0, 255), 2)
    cv2.line(img, topLine[0], topLine[1], (0, 255, 0), 2)
    cv2.imshow("Image", img)
    cv2.imshow("Cropped", imgRotate)
    cv2.imshow("Fin", imgFin)
    print('frame ', frameCounter)
#************************************************  КОНЕЦ БЛОКА ОТРИСОВКИ  **********************************************
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
