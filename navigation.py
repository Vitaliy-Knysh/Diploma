import math

def module(num):  # модуль числа
    if num < 0:
        return num * -1
    else: return num

def angleDiff(robotAngle, robotX, robotY, targetX, targetY):  # вычисление угла рассогласования
    angle = round(math.atan((robotX - targetX) /
                    (robotY - targetY)) * 57.2958)  # угол наклона линии между роботом и целью
    print('dierction towards target: ', angle)
    if angle < 0:  # вынужденная заплатка: при угле ориентации до -40 градусов угол отрицательный, при угле больше -40
        angle += 360  # при угле больше -40 градусов угол определяется как 360 градусов минус текущий угол
    angle = 360 - angle  # главное что работает
    angle1 = module(angle - robotAngle)
    angle2 = 360 - angle1
    if angle1 <= angle2:
        return 'l', angle1
    elif angle2 < angle1:
        return 'r', angle2

'''Прототип функции движения к цели. Робот двигается шагами длиной в 2,5 секунды, время движения установлено на сторне 
робота. Я бы сделал П-регулятор, но минмиальная скорость поворта равна 60 град/с. Если уменьшить подаваемое напряжение,
робот может застрять на возвышенности и остановиться. Пока единственный рабочий вариант - останавливаться и 
поворачивать на месте. Если робот "смотрит" на цель с погрешностью в 10 градусов, он делает шаг вперед, в противном 
случае робот доворачивает в сторону цели'''
def moveSimple(angleDiff):
    if angleDiff > 25:
        return 'l'
    elif angleDiff < -25:
        return 'r'
    else: return 'f'

'''Проверка на близость к цели. Если робот находится рядом с целью в пределах 20 пикселей, цель достигнута. 
Из-за искажений невозможно однозначно перевести пиксели в сантиметры.'''
def proxCheck(robotX, robotY, targetX, targetY):
    if module(targetX - robotX) <= 20 and module(targetY - robotY) <= 20:
        return True
    else: return False
