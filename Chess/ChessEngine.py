## Brain of Game
""" Chess Board """
import pygame

class Engine():                     ## Ready Chess board
    def __init__(self):
        #The Chess Board
        self.board = [
           ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
           ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
           ["--", "--", "--", "--", "--", "--", "--", "--"],
           ["--", "--", "--", "--", "--", "--", "--", "--"],
           ["--", "--", "--", "--", "--", "--", "--", "--"],
           ["--", "--", "--", "--", "--", "--", "--", "--"],
           ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
           ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveSet = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                        'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True         ##First move white
        self.moveLog = []               ## Move logs
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.enPassant = ()
        self.checkMate = False
        self.staleMate = False
        self.currentCastling = Castling(True, True, True, True)
        self.castleLog = [Castling(self.currentCastling.wks, self.currentCastling.wqs,
                                   self.currentCastling.bks, self.currentCastling.bqs)]

    """Takes move as PARAMETER"""
    ## For moving chess pieces *The engine*
    def moveMade(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMove
        self.moveLog.append(move)                       ## Logs the move to the History
        self.whiteToMove = not self.whiteToMove         ## For swap players when move is done
        ## Update King's Location
        if move.pieceMove == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMove == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        """Pawn Promotion"""
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMove[0] + 'Q'

        """En Passant"""
        if move.EnPassMove:
            self.board[move.startRow][move.endCol] = "--"  ## Capture the Pawn

        if move.pieceMove[1] == 'p' and abs(move.startRow - move.endRow) == 2:      ## Absolute value of start row and end row and made 2 advances
            self.enPassant = ((move.startRow + move.endRow) // 2, move.startCol)       ## Start column = end Column
        else:
            self.enPassant = ()

        """Castle Move"""
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: ## King side castle Move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]     ## Moves the King side rook
                self.board[move.endRow][move.endCol + 1] = "--"

            else:                                   ## Queen Side Castle Move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]     ## Queen side Rook
                self.board[move.endRow][move.endCol - 2] = "--"
                

        """Castling Rights"""
        self.updateCastleRights(move)
        self.castleLog.append(Castling(self.currentCastling.wks, self.currentCastling.wqs,
                                   self.currentCastling.bks, self.currentCastling.bqs))

    """Undo last move"""
    def undoMove(self):
        if len(self.moveLog) != 0:      ## Check to make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMove
            self.board[move.endRow][move.endCol] = move.Capture
            self.whiteToMove = not self.whiteToMove  ## Return to last player
            ## Undo king's Location
            if move.pieceMove == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMove == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            ##En Passant Undo
            if move.EnPassMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.Capture
                self.enPassant = (move.endRow, move.endCol)
            ## Undo a 2 advanced pawn
            if move.pieceMove[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassant = ()

            ## Undo Castling Rights
            self.castleLog.pop()
            self.currentCastling = self.castleLog[-1]


            ##Undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:        ## King Side Undo
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:       ## Queen Side Undo
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

    """Update Castle Rights"""
    def updateCastleRights(self, move):
        if move.pieceMove == 'wK':
            self.currentCastling.wks = False
            self.currentCastling.wqs = False
        elif move.pieceMove == 'bK':
            self.currentCastling.bks = False
            self.currentCastling.bqs = False
        elif move.pieceMove == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: ## Left Rook
                    self.currentCastling.wqs = False
                elif move.startCol == 7:    ## Right Rook
                    self.currentCastling.wks = False
        elif move.pieceMove == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: ## Left Rook
                    self.currentCastling.bqs = False
                elif move.startCol == 7:    ## Right Rook
                    self.currentCastling.bks = False

    def getValidMoves(self):                ## Check when king gets a Check
        tempEnPassant = self.enPassant
        tempCastleRights = Castling(self.currentCastling.wks, self.currentCastling.wqs,
                                    self.currentCastling.bks, self.currentCastling.bqs)
        moves = self.getPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1 , -1):        ##Reverse Iteration
            self.moveMade((moves[i]))
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])           ## Not available move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        """Check if no more moves available"""
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                print("CheckMate")
            else:
                self.staleMate = True
                print("StaleMate")
        else:
            self.checkMate = False
            self.staleMate = False

        self.enPassant = tempEnPassant
        self.currentCastling = tempCastleRights
        return moves


    """ If in Check"""
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """Attacked Square by an enemy piece"""
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove         ## Switch to opponent's turn
        oppMoves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove         ## Switch Turns back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:       ## tile is under Attack
                return True
        return False


    def getPossibleMoves(self):             ## Every moves possible except when in Check
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveSet[piece](row, col, moves)        ## Calls move definitions based on piece
        return moves

    """Individual Moves to set per piece"""
    ## Pawn Moves
    def getPawnMoves(self, row, col, moves):

        if self.whiteToMove:                    ## White turn to move
            if self.board[row-1][col] == "--":  ## 1 pawn advance       ## r-1 is movement upward for wHite
                moves.append(Move((row,col), (row-1,col), self.board))
                if row == 6 and self.board[row-2][col] == "--":   ## 2 pawn movement    ## row == 6 // White pawns
                    moves.append(Move((row,col), (row-2,col), self.board))

            if col-1 >= 0:                      ##Left Capture
                if self.board[row-1][col-1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enPassant:
                    moves.append(Move((row,col), (row - 1, col - 1), self.board, enPassant=True))

            if col+1 <= 7:                      ##Right Capture
                if self.board[row-1][col+1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enPassant:
                    moves.append(Move((row,col), (row - 1, col + 1), self.board, enPassant=True))

        else:                                   ##Black turn to move
            if self.board[row+1][col] == "--":
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board))



            if col-1 >= 0:                      ##Right Capture
                if self.board[row+1][col-1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enPassant:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, enPassant=True))
            if col+1 <= 7:                      ##Left Capture
                if self.board[row+1][col+1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col - 1) == self.enPassant:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, enPassant=True))

    ## Rook Moves
    def getRookMoves(self, row, col, moves):
        rookMovement = {(-1,0), (0,-1), (1,0), (0,1)}           ## 4 way Direction// Up, Left, Down, Right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in rookMovement:
            for i in range(1, 8):                   ## Range of the rook
                endRow = row + d[0] * i             ## Starting position + The rook's row * range
                endCol = col + d[1] * i             ## Starting position + The rook's column * range
                if 0 <= endRow < 8 and 0 <= endCol < 8:     ## Read if inside the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((row,col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break           ## Stop from reading spaces behind the enemy piece
                    else:       ## Friendly piece
                        break
                else:   ## Moving Off board
                    break

    ## Knight Moves
    def getKnightMoves(self, row, col, moves):
        knightMovement = {(-2, -1), (-2, 1), (-1, 2), (-1, -2), (2, -1), (2, 1), (1, -2), (1, 2)}
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMovement:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  ## Read if inside the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:        ## not an ally
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    ## Bishop Moves
    def getBishopMoves(self, row, col, moves):
        bishopMovement = {(-1, -1), (1, -1), (1, 1), (-1, 1)}  ## Quadrant 3, 4, 1, 2
        enemyColor = "b" if self.whiteToMove else "w"
        for d in bishopMovement:
            for i in range(1, 8):  ## Range of the Bishop
                endRow = row + d[0] * i  ## Starting position + The rook's row * range
                endCol = col + d[1] * i  ## Starting position + The rook's column * range

                if 0 <= endRow < 8 and 0 <= endCol < 8:  ## Read if inside the board
                      endPiece = self.board[endRow][endCol]
                      if endPiece == "--":
                          moves.append(Move((row, col), (endRow, endCol), self.board))
                      elif endPiece[0] == enemyColor:
                          moves.append(Move((row, col), (endRow, endCol), self.board))
                          break  ## Stop from reading spaces behind the enemy piece
                      else:  ## Friendly piece
                          break
                else:  ## Moving Off board
                    break

    ## Queen Moves
    def getQueenMoves(self, row, col, moves):       ## Rook && Bishop moveset
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    ## King Moves
    def getKingMoves(self, row, col, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):                  ## Omni direction
            endRow = row + kingMoves[i][0]
            endCol = col + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  ## Read if inside the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  ## not an ally
                    moves.append(Move((row, col), (endRow, endCol), self.board))

        """
        Valid Castle Moves for the king
        """

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return  ## Can't castle
        if (self.whiteToMove and self.currentCastling.wks) or (not self.whiteToMove and self.currentCastling.bks):
            self.getKingSideCM(row, col, moves)

        if (self.whiteToMove and self.currentCastling.wqs) or (not self.whiteToMove and self.currentCastling.bqs):
            self.getQueenSideCM(row, col, moves)

    """ Castle Moves at king side"""
    def getKingSideCM(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, row + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove= True))

    """ Castle moves at Queen Side"""
    def getQueenSideCM(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove= True))

class Castling():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

## For moving chess pieces *The structure*
class Move():
    ## Map values like A1, B1 (Chess moves)
    rowNum = {"1": 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6" : 2, "7" : 1, "8" : 0,}   ##Row Identifier
    rowRanks = {r: k for k, r in rowNum.items()}
    col_Let = {"A": 0, "B" : 1, "C" : 2, "D" : 3, "E" : 4, "F" : 5, "G" : 6, "H" : 7,}  ##Col Identifier
    colFiles = {c: j for j, c in col_Let.items()}

    ##For clicks
    def __init__(self, start, end, tiles, enPassant = False, isCastleMove = False):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMove = tiles[self.startRow][self.startCol]    ##1st click
        self.Capture = tiles[self.endRow][self.endCol]         ##2nd click

        """Pawn Promotion"""
        self.isPawnPromotion = False
        if (self.pieceMove == 'wp' and self.endRow == 0) or \
                (self.pieceMove == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True
        """Em Passant Moves"""
        self.EnPassMove = enPassant
        if self.EnPassMove:
            self.Capture = 'wp' if self.pieceMove == 'bp' else 'bp'
        """Castle Move"""
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol       ##Unique ID per piece move

    """ Overrides equals method"""
    def __eq__(self,other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):         ##Get exact coordinates of click
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):    ##Get rank and file // Where Ranks = rows; Files = Col
        return self.colFiles[col] + self.rowRanks[row]