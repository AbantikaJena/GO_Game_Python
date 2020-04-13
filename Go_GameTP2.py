# Kelby Kramer - kbkramer
#Some code adapted from 15-110 Maze solver 
#Board game and events starter code are used for some framework elements

from tkinter import *

import math

NORTH = (-1,0)
SOUTH = (1,0)
EAST  = (0,1)
WEST  = (0,-1)


###Misc Helpers###

#Color Picker
def rgbString(red, green, blue):
    return '#%02x%02x%02x' % (red, green, blue)
    
#Go Stone
class Stone(object):
    def __init__(stone,cx,cy,r,color,directions):
        stone.cx = cx
        stone.cy = cy
        stone.r = r
        stone.color = color
        stone.directions = directions
        
#Create Stone
def createStone(canvas,stone):
    canvas.create_oval(stone.cx-stone.r,stone.cy-stone.r,stone.cx+stone.r,stone.cy+stone.r, fill = stone.color)
    
#Remove Stones
def removeStone(data,cell):
    data.stones[cell.row][cell.col].color = "empty"

###Place Stone###

#Placing Stones
def placeStone(data,cell):
    data.anchorRow = cell.row
    data.anchorCol = cell.col
    data.visited = []
    data.capturedStones = []
    #Check if the Spot is Full
    if data.stones[data.anchorRow][data.anchorCol].color == "empty":
        #Check If Legal Move
        if isLegalMove(data,data.anchorRow,data.anchorCol):
            
            #Try to capture some stones!
            topStonesCapture(data)
            if data.blacksTurn:
                data.stones[data.anchorRow][data.anchorCol].color = "black"
                #Change Player Turn
                if not data.adminMode:
                    data.blacksTurn = not data.blacksTurn
            else:
                data.stones[data.anchorRow][data.anchorCol].color = "white"
                #Change Player Turn
                if not data.adminMode:
                    data.blacksTurn = not data.blacksTurn
        else:
            data.illegalMove =True 
            data.stones[data.anchorRow][data.anchorCol].color = "empty"
    #Replace Directions
    for row in range(data.vertexGrid.rows):
        for col in range(data.vertexGrid.cols):
            data.stones[row][col].directions = data.allDirections.copy()

###Legal Move?###

#Top Stones Captured Function (For legal move)
def topStonesCaptureLegalMove(data):
    #Check to see if oppiste color stone around
    for drow,dcol in [NORTH,WEST,SOUTH,EAST]:
        #New Captured List
        data.capturedStones = []
        #Temp Stone at anchor
        if data.blacksTurn:
            data.stones[data.anchorRow][data.anchorCol].color = "black"     
        else:
            data.stones[data.anchorRow][data.anchorCol].color = "white"
        #Replace Directions
        for row in range(data.vertexGrid.rows):
            for col in range(data.vertexGrid.cols):
                data.stones[row][col].directions = data.allDirections.copy()
        #See if there is an adjacent stone
        if adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol)) != False:
            color = adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol)).color
            #Check what Color it is 
            if color != "empty" and adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol)).color != data.stones[data.anchorRow][data.anchorCol].color:
        
                #For the opposite color stones, Get the row and col
                stone = adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol))
                cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                if [cell.row,cell.col] not in data.capturedStones:
                    data.capturedStones = data.capturedStones + [[cell.row,cell.col]]
                if stonesCaptured(data,cell.row,cell.col):
                    captureStones(data,data.capturedStones)
                    return True

#Get Adjacent Stones
def adjacentStone(data, row,col,direction):
    stones = data.stones
    rows,cols = len(stones),len(stones[0])
    drow,dcol = direction
    if not (0<=row+drow<rows and 0<=col+dcol<cols): 
        return False
    if direction==EAST: 
        return stones[row][col+1]
    if direction==SOUTH: 
        return stones[row+1][col]
    if direction==WEST: 
        return stones[row][col-1]
    if direction==NORTH:    
        return stones[row-1][col]
    assert False

#Check for open liberties
def hasOpenLiberties(data,baseStoneRow,baseStoneCol):
    for drow,dcol in [NORTH,WEST,SOUTH,EAST]:
        stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions
        if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) != False:
            #Check to see if there are empty stones around
            if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "empty":
                return True
    
#Check if Move is Legal
def isLegalMove(data,row,col):
    stones = data.stones
    rows,cols = len(stones),len(stones[0])
    baseStoneRow, baseStoneCol = row,col

    #Temp Stone at anchor
    if data.blacksTurn:
        data.stones[data.anchorRow][data.anchorCol].color = "black"     
    else:
        data.stones[data.anchorRow][data.anchorCol].color = "white"

    #Base Case
    if hasOpenLiberties(data,baseStoneRow,baseStoneCol):
        return True
        
    #Check to see if there are stones of the same color with empty stones around them (Reccursive)
    stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions.copy()
    def checkSameColor(stoneDirections):
        #Temp Stone at anchor
        if data.blacksTurn:
            data.stones[data.anchorRow][data.anchorCol].color = "black"     
        else:
            data.stones[data.anchorRow][data.anchorCol].color = "white"
            
        #For Loop
        for element in stoneDirections:
            drow,dcol = element
            stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions
            if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) == False:
                data.stones[drow][dcol].directions.discard((drow,dcol))
            if (drow,dcol) in stoneDirections and adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) != False :
                stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                L = [cell.row,cell.col]
                if L not in data.visited or (len(stoneDirections)) < 2:
                    #Remove Direction
                    data.stones[row][col].directions.discard((drow,dcol))
            
                    if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "white" and not data.blacksTurn:
                        #Set as new base stone
                        stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                        cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                        data.visited = data.visited + [[baseStoneRow,baseStoneCol]]    
                        if isLegalMove(data,cell.row,cell.col):
                            return True
                        
                    if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "black" and data.blacksTurn:
                        #Set as new base stone
                        stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                        cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                        data.visited = data.visited + [[baseStoneRow,baseStoneCol]]  
                        if isLegalMove(data,cell.row,cell.col):
                            return True
                    
        data.stones[data.anchorRow][data.anchorCol].color = "empty"

    data.stones[data.anchorRow][data.anchorCol].color = "empty"
    return True if checkSameColor(data.allDirections) or topStonesCaptureLegalMove(data) else False 

###Stones Captured?###

#Top Stones Captured Function (For Capture)
def topStonesCapture(data):
    #Check to see if oppiste color stone around
    for drow,dcol in [NORTH,WEST,SOUTH,EAST]:
        #New Captured List
        data.capturedStones = []
        #Temp Stone at anchor
        if data.blacksTurn:
            data.stones[data.anchorRow][data.anchorCol].color = "black"     
        else:
            data.stones[data.anchorRow][data.anchorCol].color = "white"
        #Replace Directions
        for row in range(data.vertexGrid.rows):
            for col in range(data.vertexGrid.cols):
                data.stones[row][col].directions = data.allDirections.copy()
        #See if there is an adjacent stone
        if adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol)) != False:
            color = adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol)).color
            #Check what Color it is 
            if color != "empty" and adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol)).color != data.stones[data.anchorRow][data.anchorCol].color:
        
                #For the opposite color stones, Get the row and col
                stone = adjacentStone(data,data.anchorRow,data.anchorCol,(drow,dcol))
                cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                if [cell.row,cell.col] not in data.capturedStones:
                    data.capturedStones = data.capturedStones + [[cell.row,cell.col]]
                if stonesCaptured(data,cell.row,cell.col):
                    captureStones(data,data.capturedStones)
                    
#Check for captured stones (returns True if stones are captured)
def stonesCaptured(data,row,col):
    stones = data.stones
    rows,cols = len(stones),len(stones[0])
    baseStoneRow, baseStoneCol = row,col
    
    #Temp Stone at anchor
    if data.blacksTurn:
        data.stones[data.anchorRow][data.anchorCol].color = "black"     
    else:
        data.stones[data.anchorRow][data.anchorCol].color = "white"
    
    #Check Base:
    if data.stones[baseStoneRow][baseStoneCol].color != data.stones[data.anchorRow][data.anchorCol].color:
        if hasOpenLiberties(data,baseStoneRow,baseStoneCol):
            return False
    
    #Check to see if there are stones of the same color with empty stones around them (Reccursive)
    stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions.copy()

    #For Loop
    for element in stoneDirections:
        drow,dcol = element
        stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions
        if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) == False:
            data.stones[drow][dcol].directions.discard((drow,dcol))
        if (drow,dcol) in stoneDirections and adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) != False :
            stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
            cell = getCell(data.vertexGrid,stone.cx,stone.cy)
            L = [cell.row,cell.col]
            if L not in data.capturedStones or (len(stoneDirections)) < 2:
                #Remove Direction
                data.stones[row][col].directions.discard((drow,dcol))
                if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "white" and data.blacksTurn:
                    #Set as new base stone
                    stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                    cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                    if [cell.row,cell.col] not in data.capturedStones:
                        data.capturedStones = data.capturedStones + [[cell.row,cell.col]]   
                    if stonesCaptured(data,cell.row,cell.col) == False:
                        return False
                    
                if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "black" and not data.blacksTurn:
                    #Set as new base stone
                    stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                    cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                    if [cell.row,cell.col] not in data.capturedStones:
                        data.capturedStones = data.capturedStones + [[cell.row,cell.col]]
                    if stonesCaptured(data,cell.row,cell.col) == False:
                        return False
                
    data.stones[data.anchorRow][data.anchorCol].color = "empty"
    return True #if stonesCaptured2(data,baseStoneRow,baseStoneCol) else False
         
#Capture Stones
def captureStones(data,L):
    if data.blacksTurn:
        data.capturedWhite += len(L)
    elif not data.blacksTurn:
        data.capturedBlack += len(L)
    for element in L:
        row = element[0]
        col = element[1]
        data.stones[row][col].color = "empty"
         
###End Game###

#Remove dead stones
def deadStone(data,cell):
    color = data.stones[cell.row][cell.col].color
    if color == "black":
        data.capturedBlack += 1
    if color == "white":
        data.capturedWhite += 1
    removeStone(data,cell)
    
#Calculate Score
def getScore(data):
    data.whiteTerritory = []
    data.blackTerritory = []
    data.neutralTerritory = []
    data.unknownTerritory = []
    data.touchWhite = False
    data.touchBlack = False
    #Check all cells
    for row in range(data.vertexGrid.rows):
        for col in range(data.vertexGrid.cols):
            stone = data.stones[row][col]
            #Check who's territory the empty spaces are
            if stone.color == "empty":
                if [row,col] in data.whiteTerritory or [row,col] in data.blackTerritory or [row,col] in data.neutralTerritory:
                    pass
                else:
                    data.unknownTerritory = data.unknownTerritory + [[row,col]]
                    data.anchorRow = row
                    data.anchorCol = col
                    checkTerritory(data,row,col)
                    if data.touchWhite and data.touchBlack:
                        data.neutralTerritory += data.unknownTerritory
                    elif data.touchBlack:
                        data.blackTerritory += data.unknownTerritory
                    elif data.touchWhite:
                        data.whiteTerritory += data.unknownTerritory
                    data.unknownTerritory = []
                    data.touchWhite = False
                    data.touchBlack = False
                    
    data.blackScore = len(data.blackTerritory) - data.capturedBlack
    data.whiteScore = len(data.whiteTerritory) - data.capturedWhite + data.seki

#Check for touching Black/White Stones (Scoring)
def touchingColor(data,baseStoneRow,baseStoneCol):
    for drow,dcol in [NORTH,WEST,SOUTH,EAST]:
        stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions
        if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) != False:
            #Check to see if there are empty stones around
            if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "white":
                data.touchWhite = True
            if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "black":
                data.touchBlack= True
            
#Check territory *reccursive
def checkTerritory(data,row,col):
    baseStoneRow = row
    baseStoneCol = col
    
        
    #Check for touching stones
    touchingColor(data,baseStoneRow,baseStoneCol)
 
    #Check for more empty stones
    stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions.copy()
    
    def checkEmpty(stoneDirections):
        #For Loop
        for element in stoneDirections:
            drow,dcol = element
            stoneDirections = data.stones[baseStoneRow][baseStoneCol].directions     
            if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) == False:
                data.stones[drow][dcol].directions.discard((drow,dcol))
            if (drow,dcol) in stoneDirections and adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)) != False :
                stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                L = [cell.row,cell.col]
                if L not in data.unknownTerritory or (len(stoneDirections)) < 2:
                    #Remove Direction
                    data.stones[row][col].directions.discard((drow,dcol))
                    if adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol)).color == "empty":
                        #Set as new base cell
                        stone = adjacentStone(data,baseStoneRow,baseStoneCol,(drow,dcol))
                        cell = getCell(data.vertexGrid,stone.cx,stone.cy)
                        if [cell.row,cell.col] not in data.unknownTerritory:
                            data.unknownTerritory = data.unknownTerritory + [[cell.row,cell.col]]     
                        
                        if stoneDirections == []:
                            return
                        else:
                            checkTerritory(data,cell.row,cell.col)
    checkEmpty(stoneDirections)

####Init############################

def init(data):
    #General
    data.margin = data.height*.1
    data.titleScreen = True
    data.gameSize = None
    data.gidSize = None
    data.titleTextSize = int(min(data.height,data.width)//15)
    data.buttonTextSize = int(min(data.height,data.width)//25)
    data.blacksTurn = True 
    data.adminMode = False
    data.gameStarted = False
    data.mouseStone = None
    data.cx = None
    data.cy = None
    data.r = None
    data.removeStone = False 
    data.passCount = 0
    data.showGridBox = False
    data.showCursorStone = True 
    #Board
    data.boardGame = None
    data.vertexGrid = None
    data.stones = None
    data.anchorRow = None
    data.anchorCol = None
    data.visited = []
    data.allDirections = set([NORTH,WEST,SOUTH,EAST])
    data.capturedStones = []
    #Scoring
    data.whiteTerritory = []
    data.blackTerritory = []
    data.neutralTerritory = []
    data.unknownTerritory = []
    data.touchWhite = False
    data.touchBlack = False
    data.seki = 6.5
    #In Game
    data.capturedBlack = 0
    data.capturedWhite = 0
    data.scoreGame = False
    data.gameOver = False
    data.blackScore = 0
    data.whiteScore = 0
    
    data.illegalMove = False 
    
####Mouse Moved#####################
def mouseMoved(event, data):
    if data.gameStarted:
        data.cx = event.x
        data.cy = event.y
        
    if data.gameStarted:
        data.illegalMove = False 
        
####Key Pressed#####################
def keyPressed(event, data):
    if not data.gameOver:
        if data.adminMode and event.key == "g":
            data.showGridBox = not data.showGridBox
            
        if data.gameStarted and event.key == "o":
            data.showCursorStone = not data.showCursorStone
    
    elif data.gameOver and event.key == "m":
        init(data)
        
####Mouse Pressed###################

def mousePressed(event, data):
    x=event.x
    y=event.y
    
    ###Title Screen###
    if data.titleScreen:
        #Beginner Button
        if (x>data.width*.2) and  (y>((data.height*.4) - data.buttonTextSize)) and (x<data.width*.8) and (y<(data.height*.4) + data.buttonTextSize):
            data.gameSize = 8
            
        #Intermediate Button
        if (x>data.width*.2) and  (y>((data.height*.6) - data.buttonTextSize)) and (x<data.width*.8) and (y<(data.height*.6) + data.buttonTextSize):
            data.gameSize = 12
            
        #Advances Button
        if (x>data.width*.2) and  (y>((data.height*.8) - data.buttonTextSize)) and (x<data.width*.8) and (y<(data.height*.8) + data.buttonTextSize):
            data.gameSize = 18
               
        #Create Game
        if data.gameSize != None:
            
            #Visible Board
            data.titleScreen = False
            data.boardGame = BoardGame(data.gameSize, data.gameSize, data.margin, data.margin+50,data.width-data.margin, data.height-data.margin+50)
            #Vertex Grid
            data.gridSize = data.gameSize + 1
            data.vertexGrid = BoardGame(data.gridSize,data.gridSize,(data.boardGame.x0-data.boardGame.cellWidth//2),(data.boardGame.y0-data.boardGame.cellHeight//2),(data.boardGame.x1+data.boardGame.cellWidth//2),(data.boardGame.y1+data.boardGame.cellWidth//2))
            #Create Stones List
            data.r = (data.boardGame.cellWidth)//2.5
            data.stones = make2dList(data.vertexGrid.rows,data.vertexGrid.cols,"None")
            for row in range(data.vertexGrid.rows):
                for col in range(data.vertexGrid.cols):
                    bounds = getCellBounds(data.vertexGrid,row,col)
                    stone = Stone(bounds.x0+(data.vertexGrid.cellWidth//2),bounds.y0+(data.vertexGrid.cellHeight//2),data.r,"empty", data.allDirections.copy() )
                    data.stones[row][col] = stone 

    ###In Game###
    elif not data.gameOver:
        #Main Menu
        if not data.adminMode and not data.scoreGame:
            if (x>data.width*.4) and  (y>((data.height*.05) - (data.buttonTextSize//2))) and (x<data.width*.6) and (y<(data.height*.05) + (data.buttonTextSize//2)):
                init(data)
            
        #Admin Mode
        if (x>data.width*.4) and  (y>((data.height*.1) - (data.buttonTextSize//2))) and (x<data.width*.6) and (y<(data.height*.1) + (data.buttonTextSize//2)) and not data.scoreGame:
            data.adminMode = not data.adminMode
            if data.adminMode:
                data.removeStone = False
        if data.adminMode:
            if (x>data.width*.4) and  (y>((data.height*.05) - (data.buttonTextSize//2))) and (x<data.width*.6) and (y<(data.height*.05) + (data.buttonTextSize//2)):
                data.removeStone = not data.removeStone
            if data.removeStone and (x>data.vertexGrid.x0) and (y>data.vertexGrid.y0) and (x<data.vertexGrid.x1) and (y<data.vertexGrid.y1):
                cell = getCell(data.vertexGrid,x,y)
                removeStone(data,cell)
            
        #Toggle in Admin Mode
        if data.adminMode:
            if (x>data.width*.1) and  (y>((data.height*.05) - (data.buttonTextSize//2))) and (x<data.width*.3) and (y<(data.height*.05) + (data.buttonTextSize//2)):
                data.blacksTurn = True
            if (x>data.width*.7) and  (y>((data.height*.05) - (data.buttonTextSize//2))) and (x<data.width*.9) and (y<(data.height*.05) + (data.buttonTextSize//2)):
                data.blacksTurn = False
                
            #Click On Board
            if not data.removeStone and (x>data.vertexGrid.x0) and (y>data.vertexGrid.y0) and (x<data.vertexGrid.x1) and (y<data.vertexGrid.y1):
                #Place a Stone
                cell = getCell(data.vertexGrid,x,y)
                placeStone(data,cell)
            
        #Regular Game-Play
        if not data.adminMode and data.gameStarted and not data.scoreGame:
            
            #Pass Buttons
            if data.blacksTurn and (x>(data.width*.25)) and (y>((data.height*.1)-(data.buttonTextSize//2))) and (x<(data.width*.35)) and (y<(data.height*.1)+(data.buttonTextSize//2)):
                data.passCount +=1
                if (data.passCount >= 2):
                    data.scoreGame = True
                    
                #Change Player Turn 
                data.blacksTurn = not data.blacksTurn
            elif not data.blacksTurn and (x>(data.width*.65)) and (y>((data.height*.1)-(data.buttonTextSize//2))) and (x<(data.width*.75)) and (y<(data.height*.1)+(data.buttonTextSize//2)):
                data.passCount +=1
                if (data.passCount >= 2):
                    data.scoreGame = True
                    
                #Change Player Turn 
                data.blacksTurn = not data.blacksTurn
            else:
                data.passCount = 0
             
            #Click On Board
            if (x>data.vertexGrid.x0) and (y>data.vertexGrid.y0) and (x<data.vertexGrid.x1) and (y<data.vertexGrid.y1):
                #Place a Stone
                cell = getCell(data.vertexGrid,x,y)
                placeStone(data,cell)
                
        #Score Game
        if data.scoreGame:
            
            #Click On Board
            if (x>data.vertexGrid.x0) and (y>data.vertexGrid.y0) and (x<data.vertexGrid.x1) and (y<data.vertexGrid.y1):
                #Place a Stone
                cell = getCell(data.vertexGrid,x,y)
                deadStone(data,cell)
                
            #Score Game! button 
            if (x>data.width*.4) and  (y>((data.height*.1) - (data.buttonTextSize//2))) and (x<data.width*.6) and (y<(data.height*.1) + (data.buttonTextSize//2)):
                getScore(data)
                data.gameOver = True
            
        #Start Button
        if not data.gameStarted and (x>0) and  (y>((data.height*.95) - (data.titleTextSize//2))) and (x<data.width) and (y<(data.height)):
            data.gameStarted = True
            data.blacksTurn = True
            data.cx = x
            data.cy = y
        
#####Draw All########################

def drawAll(canvas, data):
    #Draw Background
    tan = rgbString(255, 231, 147)
    canvas.create_rectangle(0,0,data.width,data.height, fill=tan , width=0)
    
    ##Draw Title Screen##
    if data.titleScreen:
        
        ##Draw Title##
        canvas.create_text(data.width//2,data.height*.2,text='Grab a friend and GO!',fill='black', font='Helvetica ' + str(data.titleTextSize) + ' bold')
                       
        ##Draw Buttons##
        
        #Beginner
        canvas.create_rectangle(data.width*.2,(data.height*.4) - data.buttonTextSize,data.width*.8,(data.height*.4) + data.buttonTextSize, fill= "green")
        canvas.create_text(data.width//2,data.height*.4,text='GO Beginner',fill='black', font='Helvetica ' + str(data.buttonTextSize) + ' bold')
        #Intermediate
        canvas.create_rectangle(data.width*.2,(data.height*.6) - data.buttonTextSize,data.width*.8,(data.height*.6) + data.buttonTextSize, fill = "yellow")
        canvas.create_text(data.width//2,data.height*.6,text='GO Intermediate',fill='black', font='Helvetica ' + str(data.buttonTextSize) + ' bold')
        #Advanced
        canvas.create_rectangle(data.width*.2,(data.height*.8) - data.buttonTextSize,data.width*.8,(data.height*.8) + data.buttonTextSize, fill = "red")
        canvas.create_text(data.width//2,data.height*.8,text='GO Advanved',fill='black', font='Helvetica ' + str(data.buttonTextSize) + ' bold')
                       
    ##Draw the Board Game##
    else:
        #Draw Board
        for row in range(data.boardGame.rows):
            for col in range(data.boardGame.cols):
                bounds= getCellBounds(data.boardGame, row, col)
                canvas.create_rectangle(bounds.x0, bounds.y0, bounds.x1, bounds.y1, fill=tan, outline='black')
                
        #Draw Vertex Grid 
        if data.adminMode and data.showGridBox:
            for row in range(data.vertexGrid.rows):
                for col in range(data.vertexGrid.cols):
                    bounds= getCellBounds(data.vertexGrid, row, col)
                    canvas.create_rectangle(bounds.x0, bounds.y0, bounds.x1, bounds.y1, outline='cyan')
        
        #Draw Stones
        for row in range(data.vertexGrid.rows):
            for col in range(data.vertexGrid.cols):
                stone = data.stones[row][col]
                if stone.color == "black":
                    createStone(canvas,stone)
                elif stone.color == "white":
                    createStone(canvas,stone)
                
        #Main Menu Button
        if not data.adminMode and not data.scoreGame:
            canvas.create_rectangle(data.width*.4,(data.height*.05) - (data.buttonTextSize//2),data.width*.6,(data.height*.05) + (data.buttonTextSize//2), fill = tan)
            canvas.create_text(data.width//2,data.height*.05,text='Main Menu',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
                    
        #Admin Mode
        if not data.scoreGame:
            if data.adminMode:
                #Button Turns Green
                canvas.create_rectangle(data.width*.4,(data.height*.1) - (data.buttonTextSize//2),data.width*.6,(data.height*.1)+(data.buttonTextSize//2), fill = "green")
                canvas.create_text(data.width//2,data.height*.1,text='Admin Mode',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
                #Remove Stone Button
                canvas.create_rectangle(data.width*.4,(data.height*.05) - (data.buttonTextSize//2),data.width*.6,(data.height*.05)+(data.buttonTextSize//2), fill = tan)
                canvas.create_text(data.width//2,data.height*.05,text='Remove Stone',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
                if data.removeStone:
                    canvas.create_rectangle(data.width*.4,(data.height*.05)-(data.buttonTextSize//2),data.width*.6,(data.height*.05)+(data.buttonTextSize//2),fill = "red")
                    canvas.create_text(data.width//2,data.height*.05,text='Remove Stone',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            else:
                canvas.create_rectangle(data.width*.4,(data.height*.1) - (data.buttonTextSize//2),data.width*.6,(data.height*.1) + (data.buttonTextSize//2), fill = tan)
                canvas.create_text(data.width//2,data.height*.1,text='Admin Mode',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            
        #Score Game Button
        if data.scoreGame:
            canvas.create_text(data.width//2,data.height*.05,text='Click Dead Stones Before Scoring',fill='black', font='Helvetica ' + str(int(data.buttonTextSize//2.5)) + ' bold')
            canvas.create_rectangle(data.width*.4,(data.height*.1) - (data.buttonTextSize//2),data.width*.6,(data.height*.1) + (data.buttonTextSize//2), fill = tan)
            canvas.create_text(data.width//2,data.height*.1,text='Score Game!',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            
        #Illegal Move Text
        if data.illegalMove:
            canvas.create_text(data.width//2,data.height//2,text='Illegal Move! Try Again',fill='red', font='Helvetica ' + str(data.titleTextSize) + ' bold')
    
        #Black's Side (Left)
        canvas.create_text(data.width*.2,data.height*.05,text='Black',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
        canvas.create_text(data.width*.1,data.height*.1,text='Captures: ' + str(data.capturedWhite),fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
        if data.blacksTurn:
            #Black Header
            canvas.create_rectangle(data.width*.1,(data.height*.05)-(data.buttonTextSize//2),data.width*.3,(data.height*.05)+(data.buttonTextSize//2),fill="black")
            canvas.create_text(data.width*.2,data.height*.05,text='Black',fill='white', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            #Black Pass Button
            if not data.adminMode and not data.scoreGame:
                canvas.create_rectangle(data.width*.25,(data.height*.1)-(data.buttonTextSize//2),data.width*.35,(data.height*.1)+(data.buttonTextSize//2),fill=tan)
                canvas.create_text(data.width*.3,data.height*.1,text='Pass',fill='Black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            
        #White's Side (Right) 
        canvas.create_text(data.width*.8,data.height*.05,text='White',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
        canvas.create_text(data.width*.9,data.height*.1,text='Captures: ' + str(data.capturedBlack),fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
        if not data.blacksTurn:
            #White Header
            canvas.create_rectangle(data.width*.7,(data.height*.05)-(data.buttonTextSize//2),data.width*.9,(data.height*.05)+(data.buttonTextSize//2),fill="white")
            canvas.create_text(data.width*.8,data.height*.05,text='White',fill='black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            
            #White Pass Button
            if not data.adminMode and not data.scoreGame:
                canvas.create_rectangle(data.width*.65,(data.height*.1)-(data.buttonTextSize//2),data.width*.75,(data.height*.1)+(data.buttonTextSize//2),fill=tan)
                canvas.create_text(data.width*.7,data.height*.1,text='Pass',fill='Black', font='Helvetica ' + str(data.buttonTextSize//2) + ' bold')
            
        #Start Button
        if not data.gameStarted:
            canvas.create_rectangle((0) ,0,data.width,data.height, fill = "white")
            canvas.create_rectangle((0) ,((data.height*.95) - (data.titleTextSize//2)),data.width,data.height, fill = "green")
            canvas.create_text(data.width//2,data.height*.95,text='Click Start!',fill='black', font='Helvetica ' + str(data.titleTextSize//2) + ' bold')
            
            #Rules
            canvas.create_text(data.width//2,data.height*.05,text='Basic Rules of Go',fill='black', font='Helvetica ' + str(data.titleTextSize//2) + ' bold')
            # Lines
            canvas.create_text(data.width//2,data.height*.1,text='1.) Players take turns placing stones on empty vertexes',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.15,text='2.) Stones, or groups of stones, must have an adjacent empty vertex (liberty), or else the stone/s are captured',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.2,text='3.) The goal of Go is to surround territory, a player’s territory are empty vertexes that their stones surround',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.25,text='4.) A player can “pass” if they feel they have no advantageous moves',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.3,text='5.) “Dead” stones, stones that would likely be captured if the game continued, are removed before scoring',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            
            #Interface Guide
            canvas.create_text(data.width//2,data.height*.5,text='Interface Guide',fill='black', font='Helvetica ' + str(data.titleTextSize//2) + ' bold')
            #Lines
            canvas.create_text(data.width//2,data.height*.55,text='• Click on empty vertexes to place stones ',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.6,text='• Press “o” to toggle the cursor stone',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.65,text='• Click “Menu” to return to board selection',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.7,text='• After both players pass in succession, click on dead stones to remove them from the board and then click “Score Game”',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.75,text='• Click “Admin Mode” to freely add and remove stones from the board',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.8,text='- In admin mode click “White” or “Black” to place stones of those colors',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            canvas.create_text(data.width//2,data.height*.85,text='- In admin mode click “Remove Stones” to remove stones from the board',fill='black', font='Helvetica ' + str(data.buttonTextSize//3) + ' bold')
            
        #Draw Cursor Stone
        elif data.showCursorStone and not data.gameOver: 
            data.r = (data.boardGame.cellWidth)//2.5
            if data.removeStone and data.adminMode:
                color = "red"
                stone = Stone(data.cx,data.cy,data.r,color,data.allDirections)
                createStone(canvas,stone)
            elif data.blacksTurn:
                color = "black"
                stone = Stone(data.cx,data.cy,data.r,color,data.allDirections)
                createStone(canvas,stone)
            else: 
                color = "white"
                stone = Stone(data.cx,data.cy,data.r,color,data.allDirections)
                createStone(canvas,stone)
        
        #Game Over Screen       
        if data.gameOver:
            #Heading and Box
            canvas.create_rectangle((data.width*.05) ,(data.height*.25),data.width*.95,data.height*.75, fill = "white")
            canvas.create_text(data.width//2,data.height//3,text='Game Over!',fill='black', font='Helvetica ' + str(data.titleTextSize) + ' bold')
            canvas.create_text(data.width//2,(data.height//3)+(data.titleTextSize),text='Press "m" to return to main menu',fill='black', font='Helvetica ' + str(data.titleTextSize//4) + ' bold')
            #Display Scores
            canvas.create_text(data.width*.25,data.height*.5,text='Black Score: ' + str(data.blackScore),fill='black', font='Helvetica ' + str(data.titleTextSize//2) + ' bold')
            canvas.create_text(data.width*.75,data.height*.5,text='White Score: ' + str(data.whiteScore),fill='black', font='Helvetica ' + str(data.titleTextSize//2) + ' bold')
            
            #Display Winner
            if data.blackScore > data.whiteScore:
                winner = "Black"
            elif data.whiteScore >= data.blackScore:
                winner = "White"
            canvas.create_text(data.width//2,data.height*.6,text= winner + ' Wins!',fill='black', font='Helvetica ' + str(data.titleTextSize//2) + ' bold')
      
        
####################################
# Do not edit code below here!
####################################

####################################
# BoardGame class and functions
# (Note: these functions should be methods inside the BoardGame class,
# but we've not yet learned how to do that, so for now, they are functions
# outside that class.)
####################################

class Cell(object):
    def __init__(cell, row, col):
        cell.row = row
        cell.col = col

class Bounds(object):
    def __init__(bounds, x0, y0, x1, y1):
        bounds.x0 = x0
        bounds.y0 = y0
        bounds.x1 = x1
        bounds.y1 = y1

class BoardGame(object):
    def __init__(boardGame, rows, cols, x0, y0, x1, y1):
        boardGame.rows = rows
        boardGame.cols = cols
        boardGame.x0 = x0
        boardGame.y0 = y0
        boardGame.x1 = x1
        boardGame.y1 = y1
        boardGame.width = x1 - x0
        boardGame.height = y1 - y0
        boardGame.cellWidth = boardGame.width / boardGame.cols
        boardGame.cellHeight = boardGame.height / boardGame.rows
        # load the board, a 2d list of cells
        boardGame.board = make2dList(boardGame.rows, boardGame.cols)
        for row in range(boardGame.rows):
            for col in range(boardGame.cols):
                boardGame.board[row][col] = Cell(row, col)

def getCellBounds(boardGame, row, col):
    # aka "modelToView"
    x0 = boardGame.x0 + boardGame.cellWidth * col
    y0 = boardGame.y0 + boardGame.cellHeight * row
    x1 = x0 + boardGame.cellWidth
    y1 = y0 + boardGame.cellHeight
    return Bounds(x0, y0, x1, y1)

def getCell(boardGame, x, y):
    # aka "viewToModel"
    if ((x < boardGame.x0) or (x >= boardGame.x1) or
        (y < boardGame.y0) or (y >= boardGame.y1)):
        return None
    row = int((y - boardGame.y0) / boardGame.cellHeight)
    col = int((x - boardGame.x0) / boardGame.cellWidth)
    return boardGame.board[row][col]

def make2dList(rows, cols, defaultValue=None):
    a = [ ]
    for row in range(rows): a.append([defaultValue]*cols)
    return a

####################################
# Animation Framework:
####################################

class Struct(object): pass

def run(width=600, height=600):
    def drawAllWrapper():
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, width, height, fill='white', width=0)
        drawAll(canvas, data)
        canvas.update()

    def callFn(fn, event=None):
        if (fn == 'mousePressed'): data._mouseIsPressed = True
        elif (fn == 'mouseReleased'): data._mouseIsPressed = False
        if ('mouse' in fn): data._lastMousePosn = (event.x, event.y)
        if (fn in globals()):
            if (fn.startswith('key')):
                c = event.key = event.char
                if ((c in [None, '']) or (len(c) > 1) or (ord(c) > 255)):
                    event.key = event.keysym
                elif (c == '\t'): event.key = 'Tab'
                elif (c in ['\n', '\r']): event.key = 'Enter'
                elif (c == '\b'): event.key = 'Backspace'
                elif (c == chr(127)): event.key = 'Delete'
                elif (c == chr(27)): event.key = 'Escape'
                elif (c == ' '): event.key = 'Space'
                if (event.key.startswith('Shift')): return
            args = [data] if (event == None) else [event, data]
            globals()[fn](*args)
            drawAllWrapper()

    def timerFiredWrapper():
        callFn('timerFired')
        data._afterId1 = root.after(data.timerDelay, timerFiredWrapper)

    def mouseMotionWrapper():
        if (((data._mouseIsPressed == False) and (data._mouseMovedDefined == True)) or
            ((data._mouseIsPressed == True ) and (data._mouseDragDefined == True))):
            event = Struct()
            event.x = root.winfo_pointerx() - root.winfo_rootx()
            event.y = root.winfo_pointery() - root.winfo_rooty()
            if ((data._lastMousePosn !=  (event.x, event.y)) and
                (event.x >= 0) and (event.x <= data.width) and
                (event.y >= 0) and (event.y <= data.height)):
                fn = 'mouseDragged' if (data._mouseIsPressed == True) else 'mouseMoved'
                callFn(fn, event)
        data._afterId2 = root.after(data.mouseMovedDelay, mouseMotionWrapper)

    # Set up data and call init
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    data.mouseMovedDelay = 50 # ditto
    data._mouseIsPressed = False
    data._lastMousePosn = (-1, -1)
    data._mouseMovedDefined = 'mouseMoved' in globals()
    data._mouseDragDefined = 'mouseDragged' in globals()
    data._afterId1 = data._afterId2 = None
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event: callFn('mousePressed', event))
    # root.bind("<B1-Motion>", lambda event: callFn('mouseDragged', event))
    root.bind("<B1-ButtonRelease>", lambda event: callFn('mouseReleased', event))
    root.bind("<Key>", lambda event: callFn('keyPressed', event))
    # initialize, start the timer, and launch the app
    callFn('init')
    if ('timerFired' in globals()): timerFiredWrapper()
    if (data._mouseMovedDefined or data._mouseDragDefined): mouseMotionWrapper()
    root.mainloop()  # blocks until window is closed
    if (data._afterId1): root.after_cancel(data._afterId1)
    if (data._afterId2): root.after_cancel(data._afterId2)
    print("bye!")

run(700, 700)
