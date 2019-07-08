from pyswarm import pso
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

def banana(x):
    x1 = x[0]
    x2 = x[1]
    return np.sqrt(x1**2 + x2**2)


def randrange(n, vmin, vmax):
    '''
    Helper function to make an array of random numbers having shape (n, )
    with each number distributed Uniform(vmin, vmax).
    '''
    return (vmax - vmin) * np.random.rand(n) + vmin


if __name__=="__main__":

    lb = [-10, -10]
    ub = [10, 10]

    # xopt, fopt = pso(banana, lb, ub, f_ieqcons=con)
    xopt, fopt = pso(banana, lb, ub)
    print xopt, fopt

    inputs_x, inputs_y, outputs_graph = [], [], []
    n = 100
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # For each set of style and range settings, plot n random points in the box
    # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].

    xs = np.arange(-10., 10., 0.1)
    ys = np.arange(-10., 10., 0.1)
    X, Y = np.meshgrid(xs, ys)
    zss = np.sqrt(X**2 + Y**2)
    # ax.plot_wireframe(X, Y, zss)
    surf = ax.plot_surface(X, Y, zss, rstride=1, cstride=1, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_zlim(-20, 20)
    fig.colorbar(surf, shrink=0.5, aspect=10)


    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()