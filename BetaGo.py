import tkinter as tk
import copy as copy
import time
import random
import math
import sys
import queue
import cProfile
import operator


class MCTSNode:
    def __init__(self, state, player):
        self.state = state #type State
        self.player = player #black or white
        self.children = [] #list of MCTSNode
        self.parent = None
        self.noOfSimulations = 0
        self.wins = 0
        self.completed = False
        self.play = ("", 0, 0)
class MonteCarloSearchTree:
    def __init__(self, root, startTurn):
##        #assume win when score difference > 20
##        self.maxScoreDifference = 20
        self.turn = startTurn #"black" or "white"
        self.root = root
        self.depth = 1
    """
        Finds the best move to play from the root of the tree
        by running the 4 stages of the Monte Carlo Tree Search
    """
    def findNextMove(self):
        start = int(round(time.time()))
        end = start + 120
        nodesSearched = 0
        while(int(round(time.time())) < end):
            #Selection
            bestNode = self.selectBestNode(self.root)
            #Expansion
            #check if game ended:
            self.checkGameOver(bestNode)
            if bestNode.completed == False:
                self.expandNode(bestNode)
            #Simulation
            simulateNode = bestNode
            #if children, pick random child
            if len(simulateNode.children) > 0:
                randomIndex = random.randint(0,len(simulateNode.children)-1)
                simulateNode = simulateNode.children[randomIndex]
            result = self.simulatePlay(simulateNode)
            #Update
            self.backPropogation(simulateNode, result)
            
###Code that runs each simulation 50 times, takes the average and counts
###a win if more wins happened than losses.
##            while simulations < 50:
##                result = self.simulatePlay(simulateNode)
####                print(result)
##                simulations += 1
##                if result == True:
##                    wins += 1
##                else:
##                    losses += 1
##                simulateNode.won = False
##                simulateNode.lost = False
##            if wins > losses:
##                #Update
##                self.backPropogation(simulateNode, True)
##                simulateNode.wins += 1
##            else:
##                #Update
##                self.backPropogation(simulateNode, False)
##            simulateNode.noOfSimulations += 1
##            simulateNode.completed = True
            
        #get winner
        winnerPlay = self.getMaxChild()
        #store level order traversal for debugging
        self.levelOrderTraversal()
        return winnerPlay.play
    """
        Checks if there are any valid moves left for black and white.
        If not, marks node as terminal.
    """
    def checkGameOver(self, node):
        copyNode = [list(x) for x in node.state.pieces]
        playHistory = [list(x) for x in node.state.history]
        rows = len(copyNode)
        columns = len(copyNode[0])
        lenOfBlack = 0
        lenOfWhite = 0
        #white turn
        validWhite = []
        for r in range(rows):
            for c in range(columns):
                if copyNode[r][c] == "empty":
                    #check for suicide and kill
                    aCopy = [list(x) for x in copyNode]
                    scoreBefore = gameScore(aCopy)
                    aCopy[r][c] = "white"
                    #store deleted pieces (if any)
                    deleted = []
                    #check all surroundings of row, column
                    for x in _getSurrounding(aCopy, r, c):
                        #if surrounding = color of next player's turn and no liberties
                        if (x[2] == "black" and len(getLiberties(aCopy, x[0], x[1])) == 0):
                            #kill group
                            group = getGroup(aCopy, x[0], x[1])
                            for g in group:
                                aCopy[g[0]][g[1]] = "empty"
                                deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
                    #if not suicide or filling in an eye
                    if len(getLiberties(aCopy, r, c)) > 1:
                        scoreAfter = gameScore(aCopy)
                        scoreDifference = scoreAfter[1] - scoreBefore[1]
                        if len(playHistory) < 2:
                            validWhite.append((r, c, scoreDifference, deleted))
                        else:
                            #check for ko
                            if aCopy != playHistory[-2]:
                                validWhite.append((r, c, scoreDifference, deleted))
        lenOfWhite = len(validWhite)
        #black turn
        validBlack = []
        for r in range(rows):
            for c in range(columns):
                if copyNode[r][c] == "empty":
                    #check for suicide and kill
                    aCopy = [list(x) for x in copyNode]
                    scoreBefore = gameScore(aCopy)
                    aCopy[r][c] = "black"
                    #store deleted pieces (if any)
                    deleted = []
                    #check all surroundings of row, column
                    for x in _getSurrounding(aCopy, r, c):
                        #if surrounding = color of next player's turn and no liberties
                        if (x[2] == "white" and len(getLiberties(aCopy, x[0], x[1])) == 0):
                            #kill group
                            group = getGroup(aCopy, x[0], x[1])
                            for g in group:
                                aCopy[g[0]][g[1]] = "empty"
                                deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
                    #if not suicide or filling in an eye
                    if len(getLiberties(aCopy, r, c)) > 1:
                        scoreAfter = gameScore(aCopy)
                        scoreDifference = scoreAfter[0] - scoreBefore[0]
                        if len(playHistory) < 2: 
                            validBlack.append((r, c, scoreDifference))
                        else:
                            #check for ko
                            if aCopy != playHistory[-2]:
                                validBlack.append((r, c, scoreDifference, deleted))
        lenOfBlack = len(validBlack)
        if lenOfBlack == 0 or lenOfWhite == 0:
            #mark node as terminal
            node.completed = True
            return True
        node.completed = False
        return False
    """
        Method gets root child with highest wins/simulations ratio.
    """
    def getMaxChild(self):
        best = self.root.children[0]
        random.shuffle(self.root.children)
        for x in self.root.children:
            if x.wins / (x.noOfSimulations+1) > best.wins / (best.noOfSimulations+1):
                best = x
        return best
    """
        Updates all nodes leading up to current node that was just simulated.
    """
    def backPropogation(self, node, result):
        nodeCopy = node
        while nodeCopy:
            nodeCopy.wins += result
            nodeCopy.noOfSimulations += 1
            nodeCopy = nodeCopy.parent
    """
        Stores level order traversal of the Monte Carlo Search Tree to out.txt
    """
    def levelOrderTraversal(self):
        orig_stdout = sys.stdout
        f = open('out.txt', 'w')
        sys.stdout = f
        q = queue.Queue()
        q.put(self.root)
        q.put("delimiter")
        while(not q.empty()):
            top = q.get()
            if top == "delimiter":
                if not q.empty():
                    q.put("delimiter")
                    print("========================", "\n", "\n", "\n")
            else:
                for child in top.children:
                    q.put(child)
            if top != "delimiter":
                print(top.player[0] +'(' +str(top.play[1]) + ", " + str(top.play[2]) + '),', top.wins, "/", top.noOfSimulations, end='\t')
        sys.stdout = orig_stdout
        f.close()
    """
        Heavy playout of a game from current node state. The simulation
        continues until one of the two players runs out of moves or the number
        of moves exceeds N * N * 3 (where N * N is board size).

        Heavy playout means black and white will choose the move that results in
        the highest score increase. If any player has a chance to imprison a
        stone or surround territory they will.

    """
    def simulatePlay(self, node):
        #Checks if terminal node reached. Immediately stop simulation
        #and propogate score up
        if node.completed == True:
            score = gameScore(node.state.pieces)
            if score[0] > score[1]:
                if node.parent:
                    node.parent.wins = -sys.maxsize
                else:
                    node.wins = -sys.maxsize
                return score[1] - score[0]
            return score[0] - score[1]
##        #simulated board
        copyNode = [list(x) for x in node.state.pieces]
        playHistory = [list(x) for x in node.state.history]
##        copyNode = copy.deepcopy(node.state.pieces)
        rows = len(copyNode)
        columns = len(copyNode[0])
        #move one turn forward from state
        turn = ""
        if node.player == "black":
            turn = "white"
        else:
            turn = "black"
        lenOfBlack = 0
        lenOfWhite = 0
        moves = 0
        maxGameLength = rows * columns * 3
        score = 0
        whitePlayed = False
        blackPlayed = False
        #While there are valid moves or maxGameLength is not reached
        while True:
            #update history
            playHistory.append([list(x) for x in copyNode])

            #play white move
            if turn == "white":
                #find all valid white plays
                valid = []
                for r in range(rows):
                    for c in range(columns):
                        if copyNode[r][c] == "empty":
                            #check for suicide, ko and kill
                            aCopy = [list(x) for x in copyNode]
                            scoreBefore = gameScore(aCopy)
                            aCopy[r][c] = "white"
                            #store deleted pieces (if any)
                            deleted = []
                            #check all surroundings of row, column
                            for x in _getSurrounding(aCopy, r, c):
                                #if surrounding = color of next player's turn and no liberties
                                if (x[2] == "black" and len(getLiberties(aCopy, x[0], x[1])) == 0):
                                    #kill group
                                    group = getGroup(aCopy, x[0], x[1])
                                    for g in group:
                                        aCopy[g[0]][g[1]] = "empty"
                                        deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
                            #if not suicide or filling in an eye
                            if len(getLiberties(aCopy, r, c)) > 1:
                                scoreAfter = gameScore(aCopy)
                                scoreDifference = scoreAfter[1] - scoreBefore[1]
                                if len(playHistory) < 2:
                                    valid.append((r, c, scoreDifference, deleted))
                                else:
                                    #check for ko
                                    if aCopy != playHistory[-2]:
                                        valid.append((r, c, scoreDifference, deleted))

                lenOfWhite = len(valid)
                if len(valid) > 0:
                    #pick highest value play
                    #shuffle for random max pick
                    random.shuffle(valid)
                    bestPlay = max(valid,key=operator.itemgetter(2))
                    row = bestPlay[0]
                    col = bestPlay[1]
                    copyNode[row][col] = "white"
                    if len(bestPlay) == 4:
                        for deletedStone in bestPlay[3]:
                            copyNode[deletedStone[1]][deletedStone[2]] = "empty"
                whitePlayed = True
            #play black move
            else:
                valid = []
                for r in range(rows):
                    for c in range(columns):
                        if copyNode[r][c] == "empty":
                            #check for suicide, ko and kill
                            aCopy = [list(x) for x in copyNode]
                            scoreBefore = gameScore(aCopy)
                            aCopy[r][c] = "black"
                            #store deleted pieces (if any)
                            deleted = []
                            #check all surroundings of row, column
                            for x in _getSurrounding(aCopy, r, c):
                                #if surrounding = color of next player's turn and no liberties
                                if (x[2] == "white" and len(getLiberties(aCopy, x[0], x[1])) == 0):
                                    #kill group
                                    group = getGroup(aCopy, x[0], x[1])
                                    for g in group:
                                        aCopy[g[0]][g[1]] = "empty"
                                        deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
                            #if not suicide or filling in an eye
                            if len(getLiberties(aCopy, r, c)) > 1:
                                scoreAfter = gameScore(aCopy)
                                scoreDifference = scoreAfter[0] - scoreBefore[0]
                                if len(playHistory) < 2: 
                                    valid.append((r, c, scoreDifference))
                                else:
                                    if aCopy != playHistory[-2]:
                                        valid.append((r, c, scoreDifference, deleted))
                            
                lenOfBlack = len(valid)
                if len(valid) > 0:
                    #pick highest value play
                    #shuffle array for random max
                    random.shuffle(valid)
                    bestPlay = max(valid, key=operator.itemgetter(2))
                    row = bestPlay[0]
                    col = bestPlay[1]
                    copyNode[row][col] = "black"
                    if len(bestPlay) == 4:
                        for deletedStone in bestPlay[3]:
                            copyNode[deletedStone[1]][deletedStone[2]] = "empty"
                blackPlayed = True
            #switch turn
            if turn == "black":
                turn = "white"
            else:
                turn = "black"
            #increment move counter
            moves += 1
            #loop end condition
            if moves > maxGameLength or ((lenOfBlack == 0 or lenOfWhite == 0) and (blackPlayed == True and whitePlayed == True)):
                break
            if blackPlayed == True and whitePlayed == True:
                whitePlayed = False
                blackPlayed = False
                       
        score = gameScore(copyNode)
        if (abs(score[0] - score[1]) >= 0.5):
            if score[1] > score[0]:
                return abs(score[0] - score[1])
            else:
##                return score[1] - score[0]
                return 0
        else:
            return 0
##"""
##    Below code can be used to stop simulation prematurely if the score
##    difference becomes too high
##"""
####            score = gameScore(copyNode)
####            
####            if (abs(score[0] - score[1]) >= 6):
####                if score[1] > score[0]:
######                    print("================", node.play, "========================")
######                    print('\n'.join([''.join(['{:6}'.format(item) for item in row]) 
######                    for row in copyNode]))
######                    print("========================================")
####                    return 1
####                else:
####                    return 0
####        return 0
##            
##            
    """
        Expansion phase. Generate all valid moves from current state
        and add each move as a child of that state in the tree.
    """
    def expandNode(self, bestNode):
        boardCopy = [list(x) for x in bestNode.state.pieces]
        rows = len(boardCopy)
        columns = len(boardCopy[0])
        if bestNode.player == "black":
            empty = []
            #find all possible states
            for r in range(rows):
                for c in range(columns):
                    if boardCopy[r][c] == "empty":
                        #check for suicide
                        aCopy = [list(x) for x in boardCopy]
                        aCopy[r][c] = "white"
                        #store deleted pieces (if any)
                        deleted = []
                        #check all surroundings of row, column
                        for x in _getSurrounding(aCopy, r, c):
                            #if surrounding = color of next player's turn and no liberties
                            if (x[2] == "black" and len(getLiberties(aCopy, x[0], x[1])) == 0):
                                #kill group
                                group = getGroup(aCopy, x[0], x[1])
                                for g in group:
                                    aCopy[g[0]][g[1]] = "empty"
                                    deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
                        #ensure not killing own eye or suicide
                        if len(getLiberties(aCopy, r, c)) > 1:
                            empty.append((r, c, deleted))
            for pos in empty:
                currCopy = [list(x) for x in boardCopy]
                row = pos[0]
                col = pos[1]
                currCopy[row][col] = "white"
                if len(pos) == 3:
                    for deletedStone in pos[2]:
                            currCopy[deletedStone[1]][deletedStone[2]] = "empty"
                if bestNode.parent:
                    #check for Ko by checking parent board
                    if currCopy != bestNode.parent.state.pieces:
                        isBlackTurn = (bestNode.player == "white")
                        #create MCTSNode and push to children
                        newNode = MCTSNode(State(currCopy), "white")
                        #update node history
                        nodeHistory = [list(x) for x in bestNode.parent.state.history]
                        nodeHistory.append(currCopy)
                        newNode.state.history = nodeHistory
                        newNode.play = ("white", row, col)
                        newNode.player = "white"
                        newNode.parent = bestNode
                        bestNode.children.append(newNode)

                else:
                    isBlackTurn = (bestNode.player == "white")
                    #create MCTSNode and push to children
                    newNode = MCTSNode(State(currCopy), "white")
                    #update node history
                    newNode.state.history.append([list(x) for x in boardCopy])
                    newNode.state.history.append([list(x) for x in currCopy])
                    newNode.play = ("white", row, col)
                    newNode.player = "white"
                    newNode.parent = bestNode
                    bestNode.children.append(newNode)
        else:
            empty = []
            #find all possible states
            for r in range(rows):
                for c in range(columns):
                    if boardCopy[r][c] == "empty":
                        #check for suicide
                        aCopy = [list(x) for x in boardCopy]
                        aCopy[r][c] = "black"
                        #store deleted pieces (if any)
                        deleted = []
                        #check all surroundings of row, column
                        for x in _getSurrounding(aCopy, r, c):
                            #if surrounding = color of next player's turn and no liberties
                            if (x[2] == "white" and len(getLiberties(aCopy, x[0], x[1])) == 0):
                                #kill group
                                group = getGroup(aCopy, x[0], x[1])
                                for g in group:
                                    aCopy[g[0]][g[1]] = "empty"
                                    deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
                        #ensure not suicide or killing own eye
                        if len(getLiberties(aCopy, r, c)) > 1:
                            empty.append((r, c, deleted))
            for pos in empty:
                currCopy = [list(x) for x in boardCopy]
                row = pos[0]
                col = pos[1]
                currCopy[row][col] = "black"
                if len(pos) == 3:
                    for deletedStone in pos[2]:
                            currCopy[deletedStone[1]][deletedStone[2]] = "empty"
                if bestNode.parent:
                    #check for Ko by checking parent board
                    if currCopy != bestNode.parent.state.pieces:
                        isBlackTurn = (bestNode.player == "white")
                        #create MCTSNode and push to children
                        newNode = MCTSNode(State(currCopy), "black")
                        #update node history
                        nodeHistory = [list(x) for x in bestNode.parent.state.history]
                        nodeHistory.append(currCopy)
                        newNode.state.history = nodeHistory
                        newNode.play = ("black", row, col)
                        newNode.player = "black"
                        newNode.parent = bestNode
                        bestNode.children.append(newNode)

                else:
                    isBlackTurn = (bestNode.player == "white")
                    #create MCTSNode and push to children
                    newNode = MCTSNode(State(currCopy), "black")
                    #update node history
                    newNode.state.history.append([list(x) for x in boardCopy])
                    newNode.state.history.append([list(x) for x in currCopy])
                    newNode.play = ("black", row, col)
                    newNode.player = "black"
                    newNode.parent = bestNode
                    bestNode.children.append(newNode)
    """
        This method selects the most promising candidate to expand, simulate
        and update. It does this by a multi-bandit method called UCB1 or UCT.
        Once "black" is allowed to play (i.e. it is the opponents turn) then
        the UCB1 value is negated to minimize opponent best moves.
    """
    def selectBestNode(self, root):
        nodeCopy = root
        while len(nodeCopy.children) > 0:
            if nodeCopy.player == "black":
                #white turn so maximize UCT
                #find highest UCT
                nodesUCT = {}
                completedChildren = 0
                for child in nodeCopy.children:
                    if child.completed == False:
                        completedChildren += 1
                        childUCT = 0
                        if child.noOfSimulations == 0:
                            childUCT = sys.maxsize
                        else:
                            childUCT = (child.wins) / child.noOfSimulations \
                        + math.sqrt(2 * math.log(child.parent.noOfSimulations) / child.noOfSimulations)
                        nodesUCT[child] = childUCT
                if completedChildren == 0:
                    return nodeCopy
                mv = max(nodesUCT.values())
                nodeCopy = random.choice([k for (k, v) in nodesUCT.items() if v == mv])
            else:
                #black turn so minimize UCT
                nodesUCT = {}
                completedChildren = 0
                #find lowest UCT
                for child in nodeCopy.children:
                    if child.completed == False:
                        childUCT = 0
                        completedChildren += 1
                        if child.noOfSimulations == 0:
                            childUCT = -sys.maxsize
                        else:
                            childUCT = (child.wins) / child.noOfSimulations \
                        + math.sqrt(2 * math.log(child.parent.noOfSimulations) / child.noOfSimulations)
                        nodesUCT[child] = childUCT
                if completedChildren == 0:
                    return nodeCopy
                mv = min(nodesUCT.values())
                nodeCopy = random.choice([k for (k, v) in nodesUCT.items() if v == mv])
        return nodeCopy
##    """
##        This method selects the most promising candidate to expand, simulate
##        and update. It does this by a multi-bandit method called UCB1 or UCT.
##        Once "black" is allowed to play (i.e. it is the opponents turn) then
##        the UCB1 value is negated to minimize opponent best moves.
##    """
##    def selectBestNode(self, root):
##        nodeCopy = root
##        while (len(nodeCopy.children) > 0):
##            #find highest UCT
##            maxUCT = (-sys.maxsize, nodeCopy.children[0])
##            for child in nodeCopy.children:
##                if child.completed == False and child.wins > -sys.maxsize:
##                    childUCT = None
##                    if child.noOfSimulations == 0:
##                        childUCT = sys.maxsize
##                    else:
##                        if nodeCopy.player == "white":
##                            #black children
##                            childUCT = (child.wins) / child.noOfSimulations \
##                    + math.sqrt(2 * math.log(child.parent.noOfSimulations) / child.noOfSimulations)
##                        else:
##                            childUCT = (-1*(child.wins / child.noOfSimulations)) \
##                    + math.sqrt(2 * math.log(child.parent.noOfSimulations) / child.noOfSimulations)
##                    if childUCT >= maxUCT[0]:
##                        maxUCT = (childUCT, child)
##            nodeCopy = maxUCT[1]
##        return nodeCopy

class BoardError(Exception):
    pass
class Player():
    def __init__(self, isBlack, points=0):
        self.points = points
        self.isBlack = isBlack
        if (self.isBlack):
            self.isTurn = True
        else:
            self.isTurn = False
class State():
    def __init__(self, pieces):
        self.pieces = pieces
        self.history = []
    
"""
    Board has a 2D array of pieces. Each pos is of "black", "white" or
    "empty".

    Sometimes pos becomes "black row col" ("black 5 7") for example.
    This is done to separate images on the canvas for drawing on screen.
"""
class GameBoard(tk.Frame):
    #rows and columns is the size of the board
    #4 rows and 4 columns = 5x5
    #8 rows and 8 columns = 9x9
    def __init__(self, parent, player1, player2, rows=4, columns=4, size=50, color1="tan", color2="blue"):
        '''size is the size of a square, in pixels'''

        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = [["empty" for x in range(self.columns+1)] \
                       for x in range(self.rows+1)]
        self.player1 = player1
        self.player2 = player2

        
        self._history = [] #array of States
        self.nextTurn = "black"

        canvas_width = (columns * size) + 50
        canvas_height = (rows * size) + 50

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=canvas_width, height=canvas_height, background="gray")
        self.canvas.pack(fill="both", expand=True)
        self.drawBoard()
        counter = 0
        #add placeholder buttons for user to click on to place player pieces
        placeholder = tk.PhotoImage(file="placeholder.gif")
        for m in range(0, self.rows+1):
            for n in range(0, self.columns+1):
                self.addplaceholder("placeholder" + str(m) + " " + str(n), placeholder, m, n)
    #when copying board class, avoid copying tkinter objects
    def __deepcopy__(self, memo):
        _dontcopy = ('canvas', 'widgetName', 'master', 'tk', '_tclCommands', '_name', '_w', '_last_child_ids', 'children')
##        _dontcopy = ('canvas', 'widgetName', 'master', 'tk', '_tclCommands', '_name', '_w', '_last_child_ids', 'children', 'size', 'color1', 'color2', 'player1', 'player2', '_history', 'nextTurn, score')
        clone = copy.copy(self) # Make a shallow copy
        for name, value in vars(self).items():
           if name not in _dontcopy:
               setattr(clone, name, copy.deepcopy(value, memo))
        return clone
    #actually add piece on board (visually)
    def addpiece(self, name, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)
    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[row][column] = name
        x0 = (column * self.size) + 15
        y0 = (row * self.size) + 15
        self.canvas.coords(name, x0, y0)
    #add invisible button on board
    def addplaceholder(self, name, image, row=0, column=0):
        '''Add a piece to the playing board'''
        ID = self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.canvas.tag_bind(ID, "<Button-1>", lambda event, name=name, row=row, column=column:
                             self.clickHandler(name, row, column))
        self.placeplaceholder(name, row, column)
    def placeplaceholder(self, name, row, column):
        '''Draw a piece at the given row/column'''
        x0 = (column * self.size) + 15
        y0 = (row * self.size) + 15
        self.canvas.coords(name, x0, y0)
    #check for illegal Ko
    def checkForKo(self, name, row, column, deleted):
        try:
            #if the current board looks like a previous board
            if self.pieces == self._history[-2].pieces:
                toSet = self._history.pop()
                #restore deleted pieces
                if (deleted[0][1] == 'b'):
                    black = tk.PhotoImage(file="white.gif")
                    for d in deleted:
                        self.addpiece(d[0], black, d[1], d[2])
                else:
                    white = tk.PhotoImage(file="black.gif")
                    for d in deleted:
                        self.addpiece(d[0], white, d[1], d[2])
                #delete added
                self.canvas.delete(name)
                self.pieces[row][column] = "empty"
                #player did not play their turn, do not flip turns
                if name[0] == "b":
                    self.player1.isTurn = True
                    self.player2.isTurn = False
                else:
                    self.player1.isTurn = False
                    self.player2.isTurn = True
                raise BoardError('Illegal Ko Move')
               
        except IndexError:
            #not enough history
            pass
    #check for suicide
    def checkForSuicide(self, name, row, column, deleted):
        #if placing the piece caused it to have 0 liberties
        if len(getLiberties(self.pieces, row, column)) == 0:
            toSet = self._history.pop()
            if len(deleted) > 0:
                #restore deleted pieces
                if (deleted[0][1] == 'b'):
                    black = tk.PhotoImage(file="white.gif")
                    for d in deleted:
                        self.addpiece(d[0], black, d[1], d[2])
                else:
                    white = tk.PhotoImage(file="black.gif")
                    for d in deleted:
                        self.addpiece(d[0], white, d[1], d[2])
            #delete added
            self.canvas.delete(name)
            self.pieces[row][column] = "empty"
            #player did not play their turn, do not flip turns
            if name[0] == "b":
                self.player1.isTurn = True
                self.player2.isTurn = False
            else:
                self.player1.isTurn = False
                self.player2.isTurn = True
            raise BoardError('Move is suicidal')
    """
            Method takes location of just played piece and enforces
            game rules. Checks for Ko, checks for suicide, etc...
    """       
    def enforceGameRules(self, row, column):
        #store deleted pieces (if any)
        deleted = []
        #check all surroundings of row, column
        for x in _getSurrounding(self.pieces, row, column):
            #if surrounding = color of next player's turn and no liberties
            if (x[2] == self.nextTurn and len(getLiberties(self.pieces, x[0], x[1])) == 0):
                #kill group
                group = getGroup(self.pieces, x[0], x[1])
                for g in group:
                    #delete from canvas
                    print("delete:", g[2] + " " + str(g[0]) + " " + str(g[1]))
                    self.canvas.delete(g[2] + " " + str(g[0]) + " " + str(g[1]))
                    currColor = ""
                    if self.pieces[g[0]][g[1]] == "white":
                        currColor = "black"
                    else:
                        currColor = "white"
                    #adjust pieces array
                    self.pieces[g[0]][g[1]] = "empty"
                    deleted.append((g[2] + " " + str(g[0]) + " " + str(g[1]), g[0], g[1]))
        """
            Check for illegal ko move and suicide move
            Pass in piece added and all pieces deleted for adjustment in
            checkForKo and checkForSuicide
        """
        if (self.player1.isTurn == False):
            self.checkForKo("black" + " " +str(row) + " " + str(column), row, column, deleted)
            self.checkForSuicide("black" + " " +str(row) + " " + str(column), row, column, deleted)
        elif self.player2.isTurn == False:
            self.checkForKo("white" + " " + str(row) + " " + str(column), row, column, deleted)
            self.checkForSuicide("white" + " " +str(row) + " " + str(column), row, column, deleted)
        
##    """
##        This clickHandler is the method called when the user clicks
##        on a placeholder button (intersection) on the board. This is what
##        actually plays pieces
##        
##        Turn off AI and enable two player GO by commenting out
##        the other clickHandler and uncommenting out this one.
##        
##    """    
##    def clickHandler(self, name, row, column):
##        #Get score
##        self.score = gameScore(self.pieces)
##        #Store board history
##        currState = State(copy.deepcopy(self.pieces))
##        self._history.append(currState)
##        #images to represent black and white
##        black = tk.PhotoImage(file="black.gif")
##        white = tk.PhotoImage(file="white.gif")
##        #if black's turn, add black piece
##        if (self.player1.isTurn == True):
##            self.addpiece("black" + " " +str(row) + " " + str(column), black, row, column)
##            self.player2.isTurn = True
##            self.player1.isTurn = False
##        #if white's turn, add white piece
##        elif (self.player2.isTurn == True):
##            self.addpiece("white" + " " + str(row) + " " + str(column), white, row, column)
##            self.player2.isTurn = False
##            self.player1.isTurn = True
##        #store next player's turn
##        if (self.player1.isTurn == True):
##            self.nextTurn = "black"
##        else:
##            self.nextTurn = "white"
##        self.enforceGameRules(row, column)
##        #draw
##        root.mainloop()
    """
        This clickHandler is the method called when the user clicks
        on a placeholder button (intersection) on the board. This is what
        actually plays pieces
        
        Enable AI and disable two player GO by commenting out
        the other clickHandler and uncommenting out this one.
        
    """ 
    def clickHandler(self, name, row, column):
        #Get score
        self.score = gameScore(self.pieces)
        print(self.score)
        #Store board history
        currState = State(copy.deepcopy(self.pieces))
        self._history.append(currState)
        #images to represent black and white
        black = tk.PhotoImage(file="black.gif")
        white = tk.PhotoImage(file="white.gif")
        #if black's turn, add black piece
        if (self.player1.isTurn == True):
            self.addpiece("black" + " " +str(row) + " " + str(column), black, row, column)
            #Test case
##            self.addpiece("black" + " " +str(row+2) + " " + str(column), black, row+2, column)
##            self.addpiece("black" + " " +str(row+1) + " " + str(column+1), black, row+1, column+1)
##            self.addpiece("white" + " " +str(row+1) + " " + str(column), white, row+1, column)
##            self.addpiece("white" + " " +str(row) + " " + str(column-1), white, row, column-1)
            self.nextTurn = "white"
            #enforce game rules (i.e. delete pieces, check for ko, etc...)
            self.enforceGameRules(row, column)
            self.player2.isTurn = True
            self.player1.isTurn = False
            
        newState = State(copy.deepcopy(self.pieces))
        newState.history.append(currState.pieces)

        #White's turn, start AI
        node = MCTSNode(newState, "black")
        node.play = ("black", row, column)
        tree = MonteCarloSearchTree(node, "black")
        play = tree.findNextMove()
        print("Picked: ", play)
        self.addpiece("white" + " " + str(play[1]) + " " + str(play[2]), white, play[1], play[2])
        self.nextTurn = "black"
        self.player2.isTurn = False
        self.player1.isTurn = True

        """
            Code below is a more robust but slower way of running simulations.
            It runs 10 independent simulations and plays the
            most recurring move.
            
        """
##        dictionary = {}
##        simulations = 0
##        while simulations < 10:
##            node = MCTSNode(newState, "black")
##            node.play = ("black", row, column)
##            tree = MonteCarloSearchTree(node, "black")
##            play = tree.findNextMove()
##            simulations += 1
##            if play not in dictionary:
##                dictionary[play] = 1
##            else:
##                dictionary[play] += 1
##            print(play)
##        play = max(dictionary.items(), key=operator.itemgetter(1))[0]

        #enforce game rules (i.e. delete pieces, check for ko, etc...)
        self.enforceGameRules(play[1], play[2])
        #draw
        root.mainloop()
        
    def drawBoard(self):
        color = self.color2
        for row in range(self.rows):
            color = self.color1
            for col in range(self.columns):
                x1 = (col * self.size) + 15
                y1 = (row * self.size) + 15
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1
                
"""
    This function takes in a 2D array (board) and calculates the score of the
    board. It uses Area Scoring.

    TODO: This method needs a lot of improvement. It cannot account
    for dead pieces after a game is over. For example, if white plays in black
    territory and the game is over, this function will give points to white
    for having pieces on the board and will not count that territory as black
    territory.
"""
def gameScore(pieces):
    #1. find empty group, see if it borders two colors or just one!
    #2. if it borders just black, then whole empty group belongs to black
    #3. if it borders just white, then whole empty group belongs to white 
    #4. count all black and white pieces on the board
    blackScore = 0
    whiteScore = 0
    visited = []
    rows = len(pieces)
    columns = len(pieces[0])
    numberOfPieces = 0
    #todo: have a self.turn and use that to save time
    for row in range(rows):
        for col in range(columns):
            if pieces[row][col].partition(' ')[0] == "black" or pieces[row][col].partition(' ')[0] == "white":
                numberOfPieces += 1
            
    for row in range(rows):
        for col in range(columns):
            if (pieces[row][col] == "empty") and ((row, col) not in visited):
                emptyGroup = getEmptyGroup(pieces, row, col)
                colorsEncountered = set()
                for pos in emptyGroup:
                    visited.append((pos[0], pos[1]))
                    surrounding = _getSurrounding(pieces, pos[0], pos[1])
                    for s in surrounding:
                        if s[2] != "empty":
                            colorsEncountered.add(s[2])
                if "black" in colorsEncountered and "white" not in colorsEncountered:
                    if numberOfPieces > 1:
                        blackScore += len(emptyGroup)
                elif "black" not in colorsEncountered and "white" in colorsEncountered:
                    if numberOfPieces > 1:
                        whiteScore += len(emptyGroup)
    for row in range(rows):
        for col in range(columns):
            if pieces[row][col].partition(' ')[0] == "black":
                blackScore += 1
            elif pieces[row][col].partition(' ')[0] == "white":
                whiteScore += 1
    return (blackScore-0.5, whiteScore)
"""
    This function finds all surroundings of a current piece.
    It adds them to an array and returns that array.

    Each element in the array is of the following structure: (a, b, c)
    where a is the row, b is the column and c is the color of piece.
"""
def _getSurrounding(pieces, x, y):
    positions = ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))
    arr = []
    rows = len(pieces)
    columns = len(pieces[0])
    for a, b in positions:
        if a < rows and a >= 0 and b < columns and b >= 0:
            #a is row
            #b is column
            #c is color of piece
            arr.append((a, b, pieces[a][b].partition(' ')[0]))
    return arr
"""
    This method takes in a board, a position, a visited set and a liberties set.
    It checks for position on the board and finds how many liberties that
    piece/empty spot or group has.

    Returns a set (liberties) that contains all the liberties of the current
    piece/group of pieces.

    Each element in liberties is a tuple with [0] as the element's x pos
    [1] as the element's y pos and [2] as the element's color.

    It does this recursively. Checks current color, if empty add to liberties.
    Otherwise checks all surroundings and if same color as current color
    then recursively call getLiberties on those pieces.
"""
def _getLiberties(pieces, x, y, visited, liberties):
    color = pieces[x][y].partition(' ')[0]
    if color == "empty":
        #empty position around initial piece
        liberties.add((x, y, color))
        return liberties
    else:
        #recursively check liberties of group
        locations = set()
        for pos in _getSurrounding(pieces, x, y):
            if ((pos[2] == color or pos[2] == "empty") and (pos[0], pos[1]) not in visited):
                locations.add(pos)
        #mark visited
        visited.add((x, y))
        #repeat for same color pieces or empty pos around initial piece
        if locations:
            for x in locations:
                _getLiberties(pieces, x[0], x[1], visited, liberties)
        return liberties
                   
def getLiberties(pieces, x, y):
    liberties = set()
    visited = set()
    return _getLiberties(pieces, x, y, visited, liberties)

"""
    This method takes in a board, a position, a visited set and a group set.
    It checks for position on the board and finds how many liberties that
    piece/empty spot has.

    Returns a set (group) that has a piece at board[x][y]

    Each element in group is a tuple with [0] as the element's x pos
    [1] as the element's y pos and [2] as the element's color.

    It does this recursively. Add's current piece to group, and checks
    surrounding pieces. If any are the same color, recursively call
    getGroup on them.
"""
def _getGroup(pieces, x, y, visited, group):
    color = pieces[x][y].partition(' ')[0]
    #add piece to group
    group.add((x, y, color))
    locations = set()
    #check surrounding and store all similar color pieces in the vicinity
    for pos in _getSurrounding(pieces, x, y):
        if ((pos[2] == color) and (pos[0], pos[1]) not in visited):
            locations.add(pos)
    visited.add((x, y))
    if locations:
        for x in locations:
            _getGroup(pieces, x[0], x[1], visited, group)
    return group
    
def getGroup(pieces, x, y):
    """
        group is a set containing pieces in a group represented as (a, b, c)
        a is row
        b is column
        c is color
    """
    group = set()
    visited = set()
    return _getGroup(pieces, x, y, visited, group)
"""
    Same as getGroup. Used to find all empty groups to calculate score.
"""
def _getEmptyGroup(pieces, x, y, visited, group):
    color = pieces[x][y].partition(' ')[0]
    #add piece to group
    group.add((x, y, color))
    locations = set()
    #check surrounding and store all similar color pieces in the vicinity
    for pos in _getSurrounding(pieces, x, y):
        if ((pos[2] == "empty") and (pos[0], pos[1]) not in visited):
            locations.add(pos)
    visited.add((x, y))
    if locations:
        for x in locations:
            _getEmptyGroup(pieces, x[0], x[1], visited, group)
    return group
def getEmptyGroup(pieces, x, y):
    """
        group is a set containing pieces of a group represented as (a, b, c)
        a is row
        b is column
        c is color
    """
    group = set()
    visited = set()
    return _getEmptyGroup(pieces, x, y, visited, group)
if __name__ == "__main__":
    root = tk.Tk()
    root.title("BetaGo")
    player1 = Player(True) #black
    player2 = Player(False) #white
    board = GameBoard(root, player1, player2)
    board.pack()

    
    root.mainloop()
