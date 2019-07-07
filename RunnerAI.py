import sys
import subprocess
from os import remove
import tensorflow as tf
import os
import numpy
import time

class Model(object):
    def __init__(self):
        # Initialize variable to (5.0, 0.0)
        # In practice, these should be initialized to random values.
        self.theta = self.readFromFile()

    def __call__(self, player1, player2, n=1):
        current_loss = 10
        # p1wins = 0
        # for game_number in range(n):
        #     turn, ret = runGame(player1, player2, game_number)
        #     if ret == 1:
        #         p1wins += 1
        #         print('won on map {0}'.format(game_number))
        #         current_loss += float(turn / 20)
        #     else:
        #         print('lost on map {0}'.format(game_number))
        #         current_loss += 20 - float(turn / 20)
        #     # endif
        # #endfor
        num = [[float(current_loss - n + self.theta[0].numpy()[0]), 1.]]
        num = tf.matmul(num, [[1.0], [1.0]])
        print "Num=", num
        return num

    @staticmethod
    def readFromFile():
        abs_path = os.path.dirname(os.path.abspath(__file__))
        print "cwd:", os.path.dirname(os.path.abspath(__file__))
        print "\r\n\r\n"
        with open(os.path.join(abs_path, "entries/ai/theta.txt")) as f:
            line = f.readline().strip().split(" ")
            theta = []
            for charr in line:
                theta.append([float(charr)])
            #endfor
            return tf.Variable(theta)
        #endwith


def runGame(player1, player2, game_number):
    # todo store these in a sensible place
    status_file_name = "status_{0}.log".format(game_number)
    game_file_name = "game_file_{0}.log".format(game_number)

    status = open(status_file_name, 'w')
    game = open(game_file_name, 'w')

    abs_path = os.path.dirname(os.path.abspath(__file__))
    map_name = os.path.join(abs_path, "maps/map{0}.txt".format(game_number + 1))
    p = subprocess.Popen(['java', '-jar', 'tools/PlayGame.jar', map_name, '180000', '80', 'log.txt',
                          player1, player2], stderr=status, stdout=game)
    p.wait()
    game.close()
    status.close()
    # remove(game_file_name)
    status = open(status_file_name, 'r')
    lines = status.readlines()
    status.close()
    # remove(status_file_name)
    if lines[len(lines) - 1].split()[1] == '1':
        ret = 1
    else:
        ret = 0
    # endif
    turn = int(lines[len(lines) - 2].replace("Turn ", ""))
    return turn, ret


def train(model, p1, p2, learning_rate):
    with tf.GradientTape(persistent=True) as tt:
        current_loss = loss(model(p1, p2))

    dTheta = tt.gradient(current_loss, model.theta)
    model.theta.assign_sub(learning_rate * dTheta)


def loss(losses_reported):
    ret = tf.reduce_mean(tf.square(losses_reported))
    return ret


def usage():
    print("python Runner.py [player1] [player2] [map]")


if __name__ == "__main__":

    tf.compat.v1.enable_eager_execution()

    learning_rate = 0.15
    if len(sys.argv) != 3:
        usage()
    else:
        p1 = sys.argv[1]
        p2 = sys.argv[2]

        model = Model()
        for epoch in range(1):
            print "Epoch {0}".format(epoch)
            print "training"
            time.sleep(2)
            train(model, p1, p2, learning_rate=0.05)
            print "training done, write down in configuration file the new THETAS"
        #endfor
        print "model is: ", str(model)
        print model.theta
        print model.theta.numpy()
    #endif