## Main Game


import pygame as p
from Chess import ChessEngine


## Settings of the Game
HEIGHT = WIDTH = 800            ## Total pixels
DIMENSION = 8                   ## 8 by 8 board
Sq_Size = HEIGHT // DIMENSION   ## Size of square per size
MAX_FPS = 9000                  ## FPS FTW (Animation)
IMAGES = {}

## Load the Chess Pieces
def Chess_Set():
    pieces = ['wp', 'bp', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wQ', 'bQ', 'wK', 'bK']
    for i in pieces:
        IMAGES[i] = p.transform.scale(p.image.load("images/" + i + ".png"), (Sq_Size,Sq_Size))


## Handles Start up
def main():
    p.init()
    p.display.set_caption('Ghess Came')             ## Title of Game
    screen = p.display.set_mode((WIDTH, HEIGHT))     ## Window size
    clock = p.time.Clock()                          ## Current processor time
    screen.fill(p.Color("White"))                   ## BG color
    gs = ChessEngine.Engine()                        ## Load pieces
    running = True                       ## Access Game state from another file
    Chess_Set()
    SqSelected = ()                                 ## Tracks last input of user
    clicks = []                                     ## Keeps track of player clicks
    validMoves = gs.getValidMoves()
    moveMade = False                                ## When a move made by user takes place
    animate = False
    gameOver = False
    while running:
        for i in p.event.get():
            if i.type == p.QUIT:
                running = False
            ## Mouse Controls
            elif i.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()            ## Get mouse lccation
                    row = location[1]//Sq_Size
                    col = location[0]//Sq_Size
                    if SqSelected == (row,col):             ## Check if user clicks same square
                        SqSelected = ()                     ## Unselected
                        clicks = []
                    else:                                   ## If not equal to same square
                        SqSelected = (row, col)
                        clicks.append(SqSelected)           ## Append both selecteded square
                    if len(clicks) == 2:                    ## If 2nd time click
                        move = ChessEngine.Move(clicks[0], clicks[1], gs.board)
                        ## print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.moveMade(validMoves[i])
                                moveMade = True
                                animate = True
                                SqSelected = ()                 ## Reset user clicks
                                clicks = []
                        if not moveMade:
                            clicks = [SqSelected]

            ## Key Controls
            elif i.type == p.KEYDOWN:
                if i.key == p.K_z:                  ## Undo move using K_(Button)
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if i.key == p.K_r:              ## Resetting the board
                    gs = ChessEngine.Engine()        ## Copy board
                    validMoves = gs.getValidMoves()  ## Delete all moves from list
                    SqSelected = ()                  ## Delete Square selected
                    clicks = []                      ## Delete all player clicks
                    moveMade = False
                    animate = False
                if i.key == p.K_ESCAPE:
                    running = False

        if moveMade:
            if animate:
                AnimateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False                        ##Check if undo
            animate = False
        GameState(screen, gs, validMoves, SqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by CHECKMATE')
            else:
                drawText(screen, 'White wins by CHECKMATE')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'NOBODY WINS || STALEMATE!!')
        clock.tick(MAX_FPS)
        p.display.flip()


"""Highlight square and piece selected"""
def highlightSquares(screen, gs, validMoves, SqSelected):
    if SqSelected != ():
        row, col = SqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):       ##Square selected is piece that can be moved
            ## Highlight Selected Square
            s = p.Surface((Sq_Size, Sq_Size))
            s.set_alpha((100))                                              ## Transparency value 255 opaque || 0 = transparent
            s.fill(p.Color('green'))
            screen.blit(s, (col * Sq_Size, row * Sq_Size))
            ## Highlight moves from that square || piece
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (Sq_Size * move.endCol, Sq_Size * move.endRow))


## Handles Graphics
def GameState(screen, gs, validMoves, SqSelected):
    drawBoard(screen)                       #Draw squares on baord
    highlightSquares(screen, gs, validMoves, SqSelected)
    drawPieces(screen, gs.board)    #Draw pieces on top of board

## Draw squares
def drawBoard(screen):
    global colors               ## Global variable
    colors = [p.Color("White"), p.Color("light Blue")] ## Square color
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*Sq_Size, row*Sq_Size, Sq_Size, Sq_Size))

## Draw Pieces on the Board
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--": ## Check if has pieces
                screen.blit(IMAGES[piece], p.Rect(column*Sq_Size, row*Sq_Size, Sq_Size, Sq_Size))

""" Animating Moves """
def AnimateMove(move,screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    FramesPerSq = 10        ## 10 frames of animation per square
    frameCount = (abs(dR) + abs(dC)) * FramesPerSq
    for frame in range(frameCount + 1):
        row, col = ((move.startRow + dR*frame/frameCount, move.startCol + dC * frame / frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        ## erase piece moved from end square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol *  Sq_Size, move.endRow * Sq_Size, Sq_Size, Sq_Size )
        p.draw.rect(screen, color, endSquare)
        ## draw captured piece onto rectangle
        if move.Capture != '--':
            screen.blit(IMAGES[move.pieceMove], endSquare)
        ## draw moving piece
        screen.blit(IMAGES[move.pieceMove], p.Rect(col * Sq_Size, row * Sq_Size, Sq_Size, Sq_Size))
        p.display.flip()
        clock.tick(120)

""" Create Text """
def drawText(screen, text):
    font = p.font.SysFont("Arial", 42, True, True)
    ## Shadow
    textObject = font.render(text, 0, p.Color("Black"))
    ## Find the Center by finding the average
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    ## Front text
    textObject = font.render(text, 0, p.Color("Red"))
    screen.blit(textObject, textLocation.move(5,5))


if __name__ == "__main__":
    main()
