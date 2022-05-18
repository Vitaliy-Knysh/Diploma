import cv2
import numpy as np
import time
import math

width = 800
height = 550
startPoint = (0, 1)  # здесь находится робот в начале пути
endPoint = (3, 1)
tileSize = 120  # расстояние между вершинами по горизонтали и вертикали  в пикселях
robotRaduis = 30  # радиус робота, добавляется к координатам препятствия для нормального маневрирования
map = 255 * np.ones(shape=[height, width, 3], dtype=np.uint8)
tilesX = width // tileSize
tilesY = height // tileSize  # общее число вершин по осям
graphCoord = [[[0] * 2 for i in range(tilesX)]for j in range(tilesY)]  # список с координатами каждого узла графа
graphPath = [[0 * 1 for i in range(tilesX)]for j in range(tilesY)]  # список с путем до каждой точки в графе
graphList = [[[0] * 1 for k in range(tilesX)]for m in range(tilesY)]  # список с вершинами графа и их связями
# я мог бы объединить эти три списка, но так проще разобраться в них. ПО-ХОРОШЕМУ ЗДЕСЬ НУЖЕН КЛАСС
pathFin = []  # список, содержащий путь через граф
bigNum = max(tilesY, tilesX) + 10  # это число используется чтобы обозначить пройденную связь
                                    # или связь, заблокированную препятствием
obstacleLine = [[200, 300], [100, 55]]
stepCounter = 1  # счетчик для функции нахождения пути. Функция рекурсивная, так что я перестрахуюсь


for x in range(tilesX):  # присвоение координат вершинам графа
    for y in range(tilesY):
        graphCoord[y][x] = (40 + (tileSize * x), 40 + (tileSize * y))
print(graphCoord)
for x in range(tilesX):  # определение возможных связей без учёта препятствий
    for y in range(tilesY):
        connections = []
        if x > 0:
            connections.append((x - 1, y))
            if y > 0:
                connections.append((x - 1, y - 1))
            if y < (tilesY - 1):
                connections.append((x - 1, y + 1))

        if y > 0:
                connections.append((x, y - 1))
        if y < (tilesY - 1):
                connections.append((x, y + 1))

        if x < (tilesX - 1):
            connections.append((x + 1, y))
            if y < (tilesY - 1):
                connections.append((x + 1, y + 1))
            if y > 0:
                connections.append((x + 1, y - 1))

        i = 0
        while i < len(connections):
            line1 = (graphCoord[y][x], graphCoord[connections[i][1]][connections[i][0]])
            line2 = obstacleLine
            xCross = yCross = 0
    
            a1 = line1[0][1] - line1[1][1]  # коэфициенты уравнений прямых, проверяемых на пересечение
            b1 = line1[1][0] - line1[0][0]
            c1 = (line1[0][0] * line1[1][1]) - (line1[1][0] * line1[0][1])
    
            a2 = line2[0][1] - line2[1][1]
            b2 = line2[1][0] - line2[0][0]
            c2 = (line2[0][0] * line2[1][1]) - (line2[1][0] * line2[0][1])
    
            dMain = a1 * b2 - a2 * b1  # главный определитель
            if dMain != 0:
                xCross = -(c1 * b2 - c2 * b1) / dMain  # dx/d и dy/d
                yCross = -(a1 * c2 - a2 * c1) / dMain  # это точка пересечения прямых
                # принадлежит ли точка пересечения отрезку?
                if min(line1[0][0], line1[1][0]) <= xCross <= max(line1[0][0], line1[1][0]) and \
                        min(line2[0][0], line2[1][0]) <= xCross <= max(line2[0][0], line2[1][0]) and \
                        min(line1[0][1], line1[1][1]) <= yCross <= max(line1[0][1], line1[1][1]) and \
                        min(line2[0][1], line2[1][1]) <= yCross <= max(line2[0][1], line2[1][1]):
                    connections.pop(i)
                    i -= 1
            i += 1

        graphList[y][x] = connections

for i in graphCoord:  # вывод на экран вершин графа
    for j in range(len(i)):
        cv2.circle(map, i[j], 2, (255, 0, 0), 2)

for x in range(tilesX):  # вывод на экран всех возможных связей в графе
    for y in range(tilesY):
        for conn in graphList[y][x]:
            cv2.line(map, graphCoord[y][x], graphCoord[conn[1]][conn[0]], (255, 0, 0), 1)

connArr = graphList[startPoint[1]][startPoint[0]]
newConnList = []
#-----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------ПРОХОД ВОЛНЫ ИЗ НАЧАЛА В КОНЕЦ----------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
while graphPath[endPoint[1]][endPoint[0]] == 0:
      # список со связями для следующей волны
    checkList = []  # не отфильтрованный список со связями для следующей волны
    if stepCounter == 1:  # в начальный момент времени необходимо вручную задать связи
        newConnList = graphList[startPoint[1]][startPoint[0]]
    for conn in newConnList:
        print(conn)
        if graphPath[conn[1]][conn[0]] == 0 or graphPath[conn[1]][conn[0]] > stepCounter:
            graphPath[conn[1]][conn[0]] = stepCounter
            for singleConn in graphList[conn[1]][conn[0]]:  # добавление всех новых связей в нефильтрованный список
                checkList.append(singleConn)
    newConnList = []
    for check in checkList:  # исключение повторяющихся связей
        if check not in newConnList:
            newConnList.append(check)
    stepCounter += 1
'''    print('-------------------------PATH MATRIX-------------------------')
    for i in graphPath:
        print(i)'''

cv2.circle(map, graphCoord[startPoint[1]][startPoint[0]], 8, (255, 0, 255), 8)
cv2.circle(map, graphCoord[endPoint[1]][endPoint[0]], 8, (255, 0, 255), 8)

for x in range(tilesX):  # присвоение ненужным вершинам очень большого индекса
    for y in range(tilesY):
        if graphPath[y][x] == 0:
            graphPath[y][x] = 10
#-----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------ПРОХОД ВОЛНЫ ИЗ КОНЦА В НАЧАЛО-----------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
print('-'*100)
possibleSteps = []  # возможные шаги в узел с весом на 1 меньше текущего
currentPoint = endPoint  # текущая точка
while len(pathFin) < graphPath[endPoint[1]][endPoint[0]]:
    pathFin.append(currentPoint)
    for conn in graphList[currentPoint[1]][currentPoint[0]]:
        if graphPath[conn[1]][conn[0]] == (graphPath[currentPoint[1]][currentPoint[0]] - 1):
            possibleSteps.append(conn)
    distance = []  # список с расстоянием от узла до цели
    for conn in possibleSteps:
        distance.append(math.sqrt(((conn[0] - startPoint[0]) ** 2) + ((conn[1] - startPoint[1]) ** 2)))
    currentPoint = possibleSteps[distance.index(min(distance))]
pathFin.append(startPoint)
print(pathFin)

#-----------------------------------------------------------------------------------------------------------------------
#---------------------------------------------ОТРИСОВКА ИЗОБРАЖЕНИЯ----------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
graphPath[startPoint[1]][startPoint[0]] = 0
for x in range(tilesX):  # вывод на экран номеров связей
    for y in range(tilesY):
        cv2.putText(map, str(graphPath[y][x]), graphCoord[y][x], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

for i in range(len(pathFin) - 1):
    cv2.line(map, graphCoord[pathFin[i][1]][pathFin[i][0]],
             graphCoord[pathFin[i + 1][1]][pathFin[i + 1][0]], (0, 255, 0), 3)


cv2.line(map, obstacleLine[0], obstacleLine[1], (0, 0, 255), 2)

'''print('-------------------------PATH MATRIX-------------------------')
for i in graphPath:
    print(i)'''


cv2.line(map, obstacleLine[0], obstacleLine[1], (0, 0, 255), 2)
cv2.imshow('map', map)
cv2.waitKey(0)
cv2.destroyAllWindows()
