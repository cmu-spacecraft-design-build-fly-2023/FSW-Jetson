import matplotlib.pyplot as plt
import numpy as np


def plot3D(X):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.scatter(0, 0, 0, c="g", label="Central body", marker="o", s=300)

    ax.plot3D(X[:, 0], X[:, 1], X[:, 2], c="b", label="Free Rigid Body")

    plt.legend()
    plt.show()


def scatter3D(X, equal=False):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.scatter(0, 0, 0, c="g", label="Central point", marker="o", s=300)

    ax.scatter3D(X[:, 0], X[:, 1], X[:, 2], c="b")

    if equal:
        set_axes_equal(ax)

    plt.legend()
    plt.show()


def set_axes_equal(ax):
    """
    https://stackoverflow.com/questions/13685386/how-to-set-the-equal-aspect-ratio-for-all-axes-x-y-z

    Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


def splot(x):
    plt.plot(x)
    plt.show()


def compare(x, y1, y2):
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.show()
