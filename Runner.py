import sys
import subprocess
from os import remove

def runGame(player1, player2, map):
    # todo store these in a sensible place
    statusFileName = 'status.log'
    gameFileName = 't.log'
    status = open(statusFileName, 'w')
    game = open(gameFileName, 'w')
    p = subprocess.Popen(['java', '-jar', 'tools/PlayGame.jar', map, \
                          '200', '200', 'log.txt', \
                          player1, player2], stderr=status, stdout=game)
    p.wait()
    game.close()
    status.close()
    remove(gameFileName)
    status = open(statusFileName, 'r')
    lines = status.readlines()
    status.close()
    remove(statusFileName)
    if lines[len(lines)-1].split()[1] == '1':
        return 1
    else:
        return 2

def usage():
    print("python Runner.py [player1] [player2]")

def main():
    if len(sys.argv) != 3:
        usage()

    # p1 = "python entries/radu/RaduBot.py"
    # p2 = "java -jar example_bots/DualBot.jar"

    p1 = sys.argv[1]
    print "p1 ",p1
    p2= sys.argv[2]
    print "p2 ", p2

    p1wins = 0
    for g in range(1, 100):
        if runGame(p1,p2,'maps/map'+str(g)+'.txt') == 1:
            print('won on maps/map' + str(g) + '.txt')
            p1wins += 1
        else:
            print('lost on maps/map'+str(g)+'.txt')
        #endif
    #endfor

    print('P1 wins ' + str(100*p1wins/100.0) + '%')

if __name__=="__main__":
    main()
