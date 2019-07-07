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
                          '18000', '100', 'log.txt', \
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
        result = 1
    elif lines[len(lines)-1].split()[1] == '2':
        result = -1
    else:
        result = 0
    #endif

    number_of_turns = eval(lines[len(lines) - 2].replace("Turn ", ""))

    return number_of_turns, result

def usage():
    print("python Runner.py [player1] [player2]")

if __name__=="__main__":
    import os
    import numpy
    from shutil import copyfile


    if len(sys.argv) != 3:
        usage()
    else:
        p1 = sys.argv[1]
        p2 = sys.argv[2]

        i = numpy.random.choice(range(1, 101, 1))
        map_name = "maps/map{0}.txt".format(i)
        for j in range(5000):
            turn, result = runGame(p1, p2, map_name)
            if result == 1:
                result = 100 - int(turn / 3) #100 - 77
                print('won on ' + map_name)
            elif result == 0:
                print('lost on ' + map_name)
                result = 50
                #endif
            else:
                print('lost on ' + map_name)
                result = int(turn / 3) #0 - 33
            #endif
            with open("results.txt", "a+") as f:
                f.write("{0}{1}".format(str(result), os.linesep))
            #endwith
        #endfor
        copyfile("results.txt", "results_map_{0}.txt".format(i))
        with open("results.txt", "w+") as f:
            f.write("")
    # endif
