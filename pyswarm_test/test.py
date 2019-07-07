from pyswarm import pso
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def banana(x):
    x1 = x[0]
    x2 = x[1]
    return x1**4 - 2*x2*x1**2 + x2**2 + x1**2 - 2*x1 + 5


def banana2(x):
    x1 = x[0]
    x2 = x[1]
    return x1**4 - 2*x2*x1**2 + x2**2 + x1**2 - 2*x1 + 5

def con(x):
    x1 = x[0]
    x2 = x[1]
    return [-(x1 + 0.25)**2 + 0.75*x2]


if __name__=="__main__":
    lb = [-3, -1]
    ub = [2, 6]

    xopt, fopt = pso(banana, lb, ub, f_ieqcons=con)
    print xopt, fopt

    inputs_x, inputs_y, outputs_graph = [], [], []

    for i in range(-3, 6, 1):
        for j in range(-3, 6, 1):
            inputs_x.append(i)
            inputs_y.append(j)
            outputs_graph.append(banana(([i, j])))

    X, Y = np.meshgrid(inputs_x, inputs_y)
    Z = banana(X)

    ax = Axes3D(plt.gcf())
    ax.plot_surface(X, Y, Z)
    ax.set_zlim(-3, 70)
    ax.set_xlim(-3, 6)
    ax.set_ylim(-3, 6)
    plt.show()