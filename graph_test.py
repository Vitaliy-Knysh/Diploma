import cv2
import numpy as np
import time

startPoint = (0, 1)  # здесь находится робот в начале пути
endPoint = (3, 4)
tileSize = 120  # расстояние между вершинами по горизонтали и вертикали  в пикселях
robotRaduis = 30  # радиус робота, добавляется к координатам препятствия для нормального маневрирования
map = 255 * np.ones(shape=[600, 600, 3], dtype=np.uint8)
tilesX = map.shape[0] // tileSize
tilesY = map.shape[1] // tileSize  # общее число вершин по осям
graphCoord = [[[0] * 2 for i in range(tilesX)] for j in range(tilesY)]  # список с координатами каждого узла графа
graphPath = [[0 * 1 for i in range(tilesX)] for j in range(tilesY)]  # список с путем до каждой точки в графе
graphList = [[[0] * 1 for k in range(tilesX)] for m in range(tilesY)]  # список с вершинами графа и их связями
# я мог бы объединить эти три списка, но так проще разобраться в них. ПО-ХОРОШЕМУ ЗДЕСЬ НУЖЕН КЛАСС
bigNum = max(tilesY, tilesX) + 10  # это число используется чтобы обозначить пройденную связь
# или связь, заблокированную препятствием
obstacleLine = [[300, 55], [100, 400]]
stepCounter = 1  # счетчик для функции нахождения пути. Функция рекурсивная, так что я перестрахуюсь

for x in range(tilesX):  # присвоение координат вершинам графа
    for y in range(tilesY):
        graphCoord[x][y] = (50 + tileSize * x, 50 + tileSize * y)

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
            line1 = (graphCoord[x][y], graphCoord[connections[i][0]][connections[i][1]])
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
        graphList[x][y] = connections

for i in graphCoord:  # вывод на экран вершин графа
    for j in range(len(i)):
        cv2.circle(map, i[j], 2, (255, 0, 0), 2)

for x in range(tilesX):  # вывод на экран всех возможных связей в графе
    for y in range(tilesY):
        for conn in graphList[x][y]:
            if conn[0] != bigNum:
                cv2.line(map, graphCoord[x][y], (graphCoord[conn[0]][conn[1]]), (255, 0, 0), 1)

connArr = graphList[startPoint[0]][startPoint[1]]
newConnList = []
# ------------------------------------------ПРОХОД ВОЛНЫ В СТОРОНУ ЦЕЛИ-------------------------------------------------
while graphPath[endPoint[0]][endPoint[1]] == 0:
    # список со связями для следующей волны
    checkList = []  # не отфильтрованный список со связями для следующей волны
    if stepCounter == 1:  # в начальный момент времени необходимо вручную задать связи
        newConnList = graphList[startPoint[0]][startPoint[1]]
    for conn in newConnList:
        print(conn)
        if graphPath[conn[0]][conn[1]] == 0 or graphPath[conn[0]][conn[1]] > stepCounter:
            graphPath[conn[0]][conn[1]] = stepCounter
            for singleConn in graphList[conn[0]][conn[1]]:  # добавление всех новых связей в нефильтрованный список
                checkList.append(singleConn)
    newConnList = []
    for check in checkList:  # исключение повторяющихся связей
        if check not in newConnList:
            newConnList.append(check)
    stepCounter += 1
    print('-------------------------PATH MATRIX-------------------------')
    for i in graphPath:
        print(i)

cv2.circle(map, graphCoord[startPoint[0]][startPoint[1]], 8, (255, 0, 255), 8)
cv2.circle(map, graphCoord[endPoint[0]][endPoint[1]], 8, (255, 0, 255), 8)

for x in range(tilesX):  # присвоение ненужным вершинам очень большого индекса
    for y in range(tilesY):
        if graphPath[y][x] == 0:
            graphPath[y][x] = 10

graphPath[startPoint[0]][startPoint[1]] = 0
for x in range(tilesX):  # вывод на экран номеров связей
    for y in range(tilesY):
        cv2.putText(map, str(graphPath[y][x]), graphCoord[y][x], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)


cv2.line(map, obstacleLine[0], obstacleLine[1], (0, 0, 255), 2)

print('-------------------------PATH MATRIX-------------------------')
for i in graphPath:
    print(i)

cv2.imshow('map', map)
cv2.waitKey(0)
cv2.destroyAllWindows()
