#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from myo_raw import MyoRaw


import pygame, sys, time
from pygame.locals import *
from pygame.event import Event 
from colours import *
from random import *
import uuid
from time import ctime,sleep

import numpy as np
import os
import os.path


TOTAL_POINTS = 0
DEFAULT_SCORE = 2
BOARD_SIZE = 4

class PrintPoseListener(object ):

    def __init__(self ,  mMyo , host = '127.0.0.1', port = 1234 , listenerNumber = 1):

        self.mMyo = mMyo
        self.actionClass = 0
        self.pose = 0
        self.eventId = USEREVENT + 1 
        self.event_data = {"action" : self.actionClass}
        

    def proc_pose(self, pose):
        pose_type = pose
        self.pose = pose_type.name
        print("the pose is :" ,self.pose )
        self.mEvent = Event(self.eventId,self.event_data)
        pygame.event.post(self.mEvent)

def printMatrix():

    SURFACE.fill(BLACK) #背景填充黑色

    global BOARD_SIZE
    global TOTAL_POINTSds
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            pygame.draw.rect(SURFACE, getColour(tileMatrix[i][j]), (i*(600/BOARD_SIZE), j*(600/BOARD_SIZE) + 100, 600/BOARD_SIZE, 600/BOARD_SIZE))
            
            label = myfont.render(str(tileMatrix[i][j]), 1, WHITE)
            label2 = scorefont.render("Score: " + str(TOTAL_POINTS), 1, WHITE)

            offset = 0

            if tileMatrix[i][j] < 10:
                offset = -10
            elif tileMatrix[i][j] < 100:
                offset = -15
            elif tileMatrix[i][j] < 1000:
                offset = -20
            else:
                offset = -25

            if tileMatrix[i][j] > 0:
                SURFACE.blit(label, (i*(600/BOARD_SIZE) + (300/BOARD_SIZE) +offset, j*(600/BOARD_SIZE) + 100 + 300/BOARD_SIZE - 15))
            SURFACE.blit(label2, (10, 20))

def printGameOver():

    global TOTAL_POINTS

    SURFACE.fill(BLACK)

    label = scorefont.render("Game Over!", 1, (255,255,255))
    label2 = scorefont.render("Score: " + str(TOTAL_POINTS), 1, (255,255,255))
    label3 = myfont.render("Press r to restart!", 1, (255,255,255))

    SURFACE.blit(label, (150, 100))
    SURFACE.blit(label2, (150, 300))
    SURFACE.blit(label3, (150, 500))

#随机产生方块
def placeRandomTile():
    count = 0
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if tileMatrix[i][j] == 0:
                count += 1

    k = floor(random() * BOARD_SIZE * BOARD_SIZE)

    while tileMatrix[floor(k / BOARD_SIZE)][k % BOARD_SIZE] != 0:
        k = floor(random() * BOARD_SIZE * BOARD_SIZE)

    tileMatrix[floor(k / BOARD_SIZE)][k % BOARD_SIZE] = 2

def floor(n):
    return int(n - (n % 1))

def moveTiles():
    # We want to work column by column shifting up each element in turn.
    for i in range(0, BOARD_SIZE): # Work through our 4 columns.
        for j in range(0, BOARD_SIZE - 1): # Now consider shifting up each element by checking top 3 elements if 0.
            while tileMatrix[i][j] == 0 and sum(tileMatrix[i][j:]) > 0: # If any element is 0 and there is a number to shift we want to shift up elements below.
                for k in range(j, BOARD_SIZE - 1): # Move up elements below.
                    tileMatrix[i][k] = tileMatrix[i][k + 1] # Move up each element one.
                tileMatrix[i][BOARD_SIZE - 1] = 0

def mergeTiles():
    global TOTAL_POINTS

    for i in range(0, BOARD_SIZE):
        for k in range(0, BOARD_SIZE - 1):
                if tileMatrix[i][k] == tileMatrix[i][k + 1] and tileMatrix[i][k] != 0:
                    tileMatrix[i][k] = tileMatrix[i][k] * 2
                    tileMatrix[i][k + 1] = 0
                    TOTAL_POINTS += tileMatrix[i][k]
                    moveTiles()

def checkIfCanGo():

    for i in range(0, BOARD_SIZE ** 2):
        if tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE] == 0:
            return True

    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE - 1):
            if tileMatrix[i][j] == tileMatrix[i][j + 1]:
                return True
            elif tileMatrix[j][i] == tileMatrix[j + 1][i]:
                return True
    return False

def reset():
    global TOTAL_POINTS
    global tileMatrix

    TOTAL_POINTS = 0
    SURFACE.fill(BLACK)

    tileMatrix = [[0 for i in range(0, BOARD_SIZE)] for j in range(0, BOARD_SIZE)]

    main()

def canMove():
    for i in range(0, BOARD_SIZE):
        for j in range(1, BOARD_SIZE):
            if tileMatrix[i][j-1] == 0 and tileMatrix[i][j] > 0:
                return True
            elif (tileMatrix[i][j-1] == tileMatrix[i][j]) and tileMatrix[i][j-1] != 0:
                return True

    return False

def saveGameState():
    f = open("savedata", "w")

    tiles = " ".join([str(tileMatrix[floor(x / BOARD_SIZE)][x % BOARD_SIZE]) for x in range(0, BOARD_SIZE**2)])
    
    f.write(str(BOARD_SIZE)  + "\n")
    f.write(tiles + "\n")
    f.write(str(TOTAL_POINTS))
    f.close()

def loadGameState():
    if os.path.isfile("savedata"):
        global TOTAL_POINTS
        global BOARD_SIZE
        global tileMatrix
        f = open("savedata", "r")

        BOARD_SIZE = int(f.readline())
        mat = (f.readline()).split(' ', BOARD_SIZE ** 2)
        TOTAL_POINTS = int(f.readline())

        tileMatrix = [[0 for i in range(0, BOARD_SIZE)] for j in range(0, BOARD_SIZE)]

        for i in range(0, BOARD_SIZE ** 2):
            tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE] = int(mat[i])

        f.close()

        main(True)

def rotateMatrixClockwise():
    for i in range(0, int(BOARD_SIZE/2)):
        for k in range(i, BOARD_SIZE- i - 1):
            temp1 = tileMatrix[i][k]
            temp2 = tileMatrix[BOARD_SIZE - 1 - k][i]
            temp3 = tileMatrix[BOARD_SIZE - 1 - i][BOARD_SIZE - 1 - k]
            temp4 = tileMatrix[k][BOARD_SIZE - 1 - i]

            tileMatrix[BOARD_SIZE - 1 - k][i] = temp1
            tileMatrix[BOARD_SIZE - 1 - i][BOARD_SIZE - 1 - k] = temp2
            tileMatrix[k][BOARD_SIZE - 1 - i] = temp3
            tileMatrix[i][k] = temp4

#键值对应
def isArrow(k):
    return(k == pygame.K_UP or k == pygame.K_DOWN or k == pygame.K_LEFT or k == pygame.K_RIGHT)

#判断是哪个按键按下
def getRotations(k):
    if k == pygame.K_UP:
        return 0
    elif k == pygame.K_DOWN:
        return 2
    elif k == pygame.K_LEFT:
        return 1
    elif k == pygame.K_RIGHT:
        return 3
        
def convertToLinearMatrix():
    mat = []

    for i in range(0, BOARD_SIZE ** 2):
        mat.append(tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE])

    mat.append(TOTAL_POINTS)

    return mat

def addToUndo():
    undoMat.append(convertToLinearMatrix())

def undo():
    if len(undoMat) > 0:
        mat = undoMat.pop()

        for i in range(0, BOARD_SIZE ** 2):
            tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE] = mat[i]

        global TOTAL_POINTS
        TOTAL_POINTS = mat[BOARD_SIZE ** 2]

        printMatrix()

if __name__ == '__main__':

    global theadList , rotations

    pygame.init()
    SURFACE = pygame.display.set_mode((600, 700), 0, 32)
    pygame.display.set_caption("2048")
    myfont = pygame.font.SysFont("monospace", 25)
    scorefont = pygame.font.SysFont("monospace", 50)
    tileMatrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    undoMat = []
    rotations = 0
    mClassType = 0

    placeRandomTile()
    placeRandomTile()
    printMatrix()


    m = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
    listener = PrintPoseListener( m)
    m.add_pose_handler(listener.proc_pose)

    m.connect()

    try:
        while True:
            m.run()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if checkIfCanGo() == True:
                    if event.type == listener.eventId:
                        if listener.pose == "WAVE_OUT":
                            print("左")
                            rotations = 1
                        elif listener.pose == "WAVE_IN":
                            print("右")
                            rotations = 3
                        elif listener.pose == "FIST":
                            print("下")
                            rotations = 2
                        elif listener.pose =="FINGERS_SPREAD":
                            print("上")
                            rotations = 0
                        addToUndo() #保存当前的游戏的状态
                        for i in range(0, rotations):
                            rotateMatrixClockwise()
                            if canMove():
                                moveTiles()
                                mergeTiles()
                                placeRandomTile()
                            for j in range(0, (4 - rotations) % 4):
                                rotateMatrixClockwise() #移动方块
                            printMatrix()#画出面板
                else:
                    printGameOver() #程序结束
                #其他操作
                if event.type == KEYDOWN:
                    global BOARD_SIZE
                    if event.key == pygame.K_r:
                        reset()
                    if 50 < event.key and 56 > event.key: #设置块的个数（3-7）个
                        BOARD_SIZE = event.key - 48
                        reset()
                    if event.key == pygame.K_s: #状态保存
                        saveGameState()
                    elif event.key == pygame.K_l:#状态载入
                        loadGameState()
                    elif event.key == pygame.K_u: #撤销操作
                        undo()
            pygame.display.update() #更新画布      
    except KeyboardInterrupt:
        m.disconnect()
        print ("done!!")




BLACK = (0, 0, 0)
RED = (244, 67, 54)
PINK = (234, 30, 99)
PURPLE = (156, 39, 176)
DEEP_PURPLE = (103, 58, 183)
BLUE = (33, 150, 243)
TEAL = (0, 150, 136)
L_GREEN = (139, 195, 74)
GREEN = (60, 175, 80)
ORANGE = (255, 152, 0)
DEEP_ORANGE = (255, 87, 34)
BROWN = (121, 85, 72)
WHITE = (255, 255, 255)

colour_dict = { 0:BLACK, 2:RED, 4:PINK, 8:PURPLE, 16:DEEP_PURPLE, 32:BLUE, 64:TEAL, 128:L_GREEN, 256:GREEN, 512:ORANGE, 1024: DEEP_ORANGE, 2048:BROWN, 4096:RED, 8192:PINK, 16384:PURPLE, 32768:DEEP_PURPLE}

def getColour(i):
    if i in colour_dict:
        return colour_dict[i]
    else:
        return DEEP_PURPLE
