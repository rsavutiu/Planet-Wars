import sys
import subprocess
from os import remove

def runGame(player1, player2, map):
    # todo store these in a sensible place
    statusFileName = "status_one.log"
    gameFileName = "game_file_one.log"

    status = open(statusFileName, 'w')
    game = open(gameFileName, 'w')

    p = subprocess.Popen(['java', '-jar', 'tools/PlayGame.jar', map, \
                          '180000', '200', 'log.txt', \
                          player1, player2], stderr=status, stdout=game)

    p.wait()
    game.close()
    status.close()
    # remove(gameFileName)
    status = open(statusFileName, 'r')
    lines = status.readlines()
    status.close()
    # remove(statusFileName)
    if lines[len(lines)-1].split()[1] == '1':
        return 1
    else:
        return 2

def usage():
    print("python Runner.py [player1] [player2] [map]")

if __name__=="__main__":
    if len(sys.argv) != 4:
        usage()
    else:
        p1 = sys.argv[1]
        p2 = sys.argv[2]
        map = sys.argv[3]
        p1wins = 0
        if runGame(p1, p2, map) == 1:
            p1wins += 1
            print('won on ' + map)
        else:
            print('lost on ' + map)
        #endif
    # endif
