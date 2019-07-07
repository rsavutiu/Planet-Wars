import sys
import subprocess
import random
import time
from tensorflow.python.ops import custom_gradient


class Model(object):
    def __init__(self):
        # Initialize variable to (5.0, 0.0)
        # In practice, these should be initialized to random values.
        self.theta = self.read_from_file()

    @staticmethod
    def read_from_file():
        theta = []
        abs_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(abs_path, "entries/ai/theta.txt")) as f:
            line = f.readline().strip().split(" ")
            theta = []
            for charr in line:
                theta.append([float(charr)])
            # endfor
        # endwith
        return tf.Variable(theta)

    def __call__(self):
        # p1wins = 0
        # loss = 0
        # for i in range(N):
        #     map_name = "maps/map{0}.txt".format(str(i + 1))
        #     turn, result = run_game(p1, bots[i], map_name, i)
        #
        #     if result == 1:
        #         loss += float(turn / 20.0)
        #         p1wins += 1
        #     else:
        #         loss += 100 - (turn / 20.0)
        #     # endif
        # # endfor
        # print('P1 wins ' + str(100.0 * p1wins / N) + '%')
        # print('total loss: ' + str(loss))
        loss = tf.reduce_mean(tf.square(1.324))
        return loss


def run_game(player1, player2, map, game_number):
    # todo store these in a sensible place

    status_file_name = "status" + str(game_number) + ".log"
    game_file_name = "t" + str(game_number) + ".log"

    status = open(status_file_name, 'w')
    game = open(game_file_name, 'w')

    p = subprocess.Popen(['java', '-jar', 'tools/PlayGame.jar', map, \
                          '8000', '80', 'log.txt', \
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
        result = 1
    else:
        result = 0
    # endif

    number_of_turns = eval(lines[len(lines) - 2].replace("Turn ", ""))

    return number_of_turns, result


def usage():
    print("python Runner.py [player1]")


if __name__ == "__main__":
    import os
    import tensorflow as tf
    tf.enable_eager_execution()
    print "cwd: ", os.getcwd()
    model = Model()
    if len(sys.argv) != 2:
        usage()
    else:
        p1 = sys.argv[1]

        p2_list = [
            "java -jar example_bots/DualBot.jar",
            "java example_bots/BullyBot.java",
            "java -jar example_bots/BullyBot.jar",
            #"java -jar example_bots/ProspectBot.jar", DOESN"T WORK
            "java -jar example_bots/RageBot.jar",
            "java -jar example_bots/ZerlingRush.jar",
        ]

        abs_path = os.path.dirname(os.path.abspath(__file__))
        print "absolute path:", os.path.dirname(os.path.abspath(__file__))
        print "\r\n\r\n"

        learning_rate = 0.3

        EPOCHS = 5
        N = 1  # Number of maps
        bots = []
        for i in range(N):
            b = random.choice(p2_list)
            bots.append(b)
            print "Iteration {0} is using the bot: {1}".format(i, b)
        #endfor

        JOMABOT_ITERATIONS = 1
        for i in range(JOMABOT_ITERATIONS):
            bots.append("python jomabot2/MyBot.py")
        #endfor

        N += JOMABOT_ITERATIONS

        for epoch in range(EPOCHS):
            with tf.GradientTape() as t:
                loss = model()
                dTheta = t.gradient(loss, model.theta)
                model.theta.assign_sub(learning_rate * dTheta)
                print model.theta

            # endwith

            print "changed inputs:", model

            with open(os.path.join(abs_path, "entries/ai/theta.txt"), "w") as f:
                model_numpy = model.numpy()
                for mdl in model_numpy:
                    f.write(str(mdl) + " ")
                # endfor
                f.write(os.linesep)
                f.write(os.linesep)
                f.write(os.linesep)
                f.write("growth rate" + os.linesep)
                f.write("distance to my center" + os.linesep)
                f.write("distance to enemy center" + os.linesep)
                f.write("ships on planet to be invaded" + os.linesep)
                f.write("planet to be invaded owner (neutral or enemy) "
                        "(using owner-1 where enemy is 2, neutral is 0 - mine 1)" + os.linesep)
            # endwith
        # endfor
    # endif
