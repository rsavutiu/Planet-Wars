import sys
import subprocess


def runGame(player1, player2, map, game_number):
    # todo store these in a sensible place

    statusFileName = "status" + str(game_number) + ".log"
    gameFileName = "t" + str(game_number) + ".log"

    status = open(statusFileName, 'w')
    game = open(gameFileName, 'w')

    p = subprocess.Popen(['java', '-jar', 'tools/PlayGame.jar', map, \
                          '20000', '200', 'log.txt', \
                          player1, player2], stderr=status, stdout=game)

    p.wait()
    game.close()
    status.close()
    # remove(gameFileName)
    status = open(statusFileName, 'r')
    lines = status.readlines()
    status.close()
    # remove(statusFileName)
    if lines[len(lines) - 1].split()[1] == '1':
        return 1
    else:
        return 2


def usage():
    print("python Runner.py [player1] [player2]")


def main():
    if len(sys.argv) != 3:
        usage()
        return
    p1 = sys.argv[1]
    p2 = sys.argv[2]
    p1wins = 0
    for g in range(1, 100):
        # print "run game ", g
        if runGame(p1, p2, 'maps/map' + str(g) + '.txt', g) == 1:
            p1wins += 1
            print('won on maps/map' + str(g) + '.txt')
        else:
            print('lost on maps/map' + str(g) + '.txt')

    print('P1 wins ' + str(100 * p1wins / 100.0) + '%')


if __name__ == "__main__":
    import os
    print os.getcwd()
    main()
# endif
