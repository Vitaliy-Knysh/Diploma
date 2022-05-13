import cv2
import numpy as np
import time


tileSize = 110  #расстояние между вершинами по горизонтали и вертикали  в пикселях
map = 255 * np.ones(shape=[600, 600, 3], dtype=np.uint8)
tilesX = map.shape[0] // tileSize
tilesY = map.shape[1] // tileSize  # общее число вершин по осям
graphCoord = [[[0] * 2 for i in range(tilesX)]for j in range(tilesY)]  # массив с координатами каждого узла графа
bigNum = max(tilesY, tilesX) + 10  # это число используется чтобы обозначить несуществующую связь между вершинами графа
graphList = [[[0] * 1 for k in range(tilesX)]for m in range(tilesY)]  # список с вершинами графа и их связями

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
        #graphList.append(connections)
        graphList[x][y] = connections

graphList[0][0] = [[bigNum, bigNum]]
graphList[1][1] = [[bigNum, bigNum]]
graphList[2][2] = [[bigNum, bigNum]]
graphList[3][3] = [[bigNum, bigNum]]
graphList[4][4] = [[bigNum, bigNum]]

for i in graphCoord:  # вывод на экран вершин графа
    for j in range(len(i)):
        cv2.circle(map, i[j], 2, (255, 0, 0), 2)

for x in range(tilesX):  # вывод на экран всех возможных связей в графе
    for y in range(tilesY):
        print('x: ', x, ' y: ', y)
        for conn in graphList[x][y]:
            print('conn: ', conn)
            if conn[0] != bigNum:
                cv2.line(map, graphCoord[x][y], (graphCoord[conn[0]][conn[1]]), (255, 0, 0), 1)
                print('current point: ', graphCoord[x][y])
                print('target point: ', graphCoord[conn[0]][conn[1]])
                print('---'*10)
                cv2.imshow('map', map)
                time.sleep(0.1)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    break



cv2.destroyAllWindows()
