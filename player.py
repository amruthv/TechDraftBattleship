import requests
import json
import numpy as np
import random

boardSize = 10
letterToNumber = {'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,'J':10}
numberToLetter = dict (zip(letterToNumber.values(),letterToNumber.keys()))
#1 is carrier, 2 is battleship, 3 is submarine or destroyer, 4 is patrol
shipNameToType = {'carrier':1, 'battleship':2,'submarine':3,'destroyer':3,'patrol':4}
shipTypeToSize = {1:5, 2:4, 3:3, 4:2}
remainingTypes = [1,2,3,3,4]
mode = 'Random'
testBoard = 'https://student.people.co/api/challenge/battleship/7fb737e702b2/boards/test_board_1'
boardURL = testBoard
targetStack = []

# 0 means not shot at 
# 1 means shot at 
# 2 means a hit
board = np.zeros([boardSize,boardSize], dtype ='int')
def playGame():
    while len(remainingTypes) != 0:
        print board
        if mode == 'Random':
            # print 'doing random'
            probabilityDist = computeProbabilityDistribution()
            # print 'computed dist'
            prob = random.random()
            summed = 0.0
            index = 0
            while summed < prob:
                row, col = indexToPair(index)
                summed += probabilityDist[row,col]
                index += 1
            hitRowCol(row,col)
        else:
            # we are in Target Mode so figure out what to hit
            print 'IN TARGET MODE'
            row, col = targetStack.pop(0)
            hitRowCol(row, col)


def computeCountForType(shipType):
    shipSize = shipTypeToSize[shipType]
    boardCount = np.zeros([boardSize,boardSize], dtype = 'int')
    for row in range(boardSize):
        for col in range(boardSize):
            #check to see if ship could start at this location and go right from here
            if canFitRight(row,col, shipSize):
                for i in range(shipSize):
                    boardCount[row, col + i] += 1
            if canFitDown(row,col, shipSize):
                for j in range(shipSize):
                    boardCount[row + j, col] += 1
    return boardCount

def canFitRight(row,col,shipSize):
    for i in range(shipSize):
        if (col + i >= boardSize) or board[row, col + i] != 0:
            return False
    return True

def canFitDown(row,col,shipSize):
    for j in range(shipSize):
        if (row + j >= boardSize) or board[row + j, col] != 0:
            return False
    return True
def computeProbabilityDistribution():
    totalFitCount = np.zeros([boardSize, boardSize])
    for shipType in remainingTypes:
        boardCount = computeCountForType(shipType)
        np.add(totalFitCount, boardCount, totalFitCount)
    totalCount = np.sum(np.sum(totalFitCount, axis=1), axis = 0)
    return totalFitCount/totalCount

def indexToPair(index):
    row = index / boardSize
    col = index % boardSize
    return row,col

def addNeighborsToStack(row, col):
    if (row - 1 >= 0 and board[row-1,col] == 0 and (row-1,col) not in targetStack):
        targetStack.insert(0,(row-1,col))
    if (row + 1 < boardSize and board[row+1,col] == 0 and (row+1,col) not in targetStack):
        targetStack.insert(0,(row+1,col))
    if (col - 1 >= 0 and board[row,col -1 ] == 0 and (row,col - 1) not in targetStack):
        targetStack.insert(0,(row,col-1))
    if (col + 1 < boardSize and board[row,col + 1] == 0 and (row,col + 1) not in targetStack):
        targetStack.insert(0,(row,col+1))

def hitRowCol(row, col):
    boardRow = row + 1
    boardCol = numberToLetter[col + 1]
    print 'trying to hit boardRow', boardRow
    print 'trying to boardCol', boardCol
    r = requests.get(boardURL+'/'+ str(boardCol) + str(boardRow))
    result = json.loads(r.text or r.content)
    print result
    if result['is_hit'] == True:
        board[row,col] = 2
        if result['sunk'] != None:
            # we sunk the ship
            remainingTypes.remove(shipNameToType[result['sunk']])
            targetStack = []
            mode = 'Random'
        else:
            # now we target this ship
            addNeighborsToStack(row,col)
            targetStack = []
            mode = 'Target'
    else:
        print 'no hit'
        board[row, col] = 1


playGame()
