from pyswarm import pso
import numpy as np
import matplotlib.pyplot as plt
from RunnerOneTime import runGame, usage

NUMBER_OF_FEATURES = 12
MAP_NUMBER = 10
SWARM_SIZE = 15
costs = []
MAX_ITERATIONS = 10

p2_list = [
            #"java -jar example_bots/DualBot.jar",
            # "java example_bots/BullyBot.java",
            #"java -jar example_bots/BullyBot.jar",
            #"java -jar example_bots/ProspectBot.jar", DOESN"T WORK
            #"java -jar example_bots/RageBot.jar",
            "python entries/2/MyBot.py",
            "python entries/3/MyBot.py",
            #"java -jar example_bots/ZerlingRush.jar",
        ]

def banana(theta):
    print theta
    theta_sausage = ""
    for i in range(NUMBER_OF_FEATURES):
        theta_sausage += str(theta[i]) + " "
    #endfor


    cost = 0
    for i in range(MAP_NUMBER):
        map_name = "maps/map{0}.txt".format(i + 1)
        for p2 in p2_list:
            try:
                turn, result = runGame("python entries/ai/MyBot.py {0}".format(theta_sausage),
                                       p2, map_name)
                if result == 1:
                    result = 100. - int(turn / 3.)# 100 - 77
                    print('won on {0} with bot {1}'.format(map_name, p2.split("/")[-1]))
                elif result == 0:
                    print('drew on {0} with bot {1}'.format(map_name, p2.split("/")[-1]))
                    result = 50.
                    # endif
                else:
                    print('lost on {0} with bot {1}'.format(map_name, p2.split("/")[-1]))
                    result = int(turn / 3.)#0 - 33
                # endif
                print "result: ", result
                result_to_add = (200 - 2 * result) / (100.0 * MAP_NUMBER * len(p2_list))
                print "cost/loss to add:", result_to_add
                cost += result_to_add

            except Exception, e:
                cost += 2.0
                print "Found error on map {0}. bot {1}".format(map_name, p2), str(e)
        #endfor
    #endfor
    print "total cost = ", cost
    global costs
    costs.append(cost)
    return cost


if __name__=="__main__":
    lb = [-5] * NUMBER_OF_FEATURES
    ub = [5] * NUMBER_OF_FEATURES

    xopt, fopt = pso(banana, lb, ub, maxiter=MAX_ITERATIONS, swarmsize=SWARM_SIZE)
    print xopt, fopt

    plt.scatter(range(0, len(costs)), costs, c='b')
    plt.legend(['Loss after each try, swarm and iteration'])
    plt.show()

    costs_per_iteration = []
    for i in range(SWARM_SIZE):
        cost = 0
        for j in range(i*SWARM_SIZE, (i+1)*SWARM_SIZE):
            cost += costs[j]
        #endfor
        costs_per_iteration.add(cost)
    #endfor

    plt.scatter(range(0, len(costs_per_iteration)), costs_per_iteration, c='b')
    plt.legend(['Loss, function of iteration number'])
    plt.show()

