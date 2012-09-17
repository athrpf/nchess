"""
This module is for testing how to plot a board
"""

import numpy as np
import cmath
import matplotlib.pyplot as plt

def plot_line(x1, x2, args):
    plt.plot(np.array([x1[0],x2[0]]), np.array([x1[1],x2[1]]), args)

class Rectangle:
    def __init__(self, x1, x2, x3, x4):
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.x4 = x4

    def plot(self, color='k'):
        plot_line(self.x1,self.x2, color)
        plot_line(self.x2,self.x3, color)
        plot_line(self.x3,self.x4, color)
        plot_line(self.x4,self.x1, color)


class CornerBoard(Rectangle):
    def __init__(self, x1, x2, x3, x4):
        Rectangle.__init__(self, x1, x2, x3, x4)
        self.rectangles = []

    def rectanglify(self, n_intervals_x=4, n_intervals_y=4):
        points1 = [float(k)/n_intervals_x*self.x1+float(n_intervals_x-k)/n_intervals_x*self.x4 for k in range(n_intervals_x+1)]
        points2 = [float(k)/n_intervals_x*self.x2+float(n_intervals_x-k)/n_intervals_x*self.x3 for k in range(n_intervals_x+1)]
        for k in range(n_intervals_x):
            for j in range(n_intervals_y):
                p1 = points1[k]*float(j)/n_intervals_y + points2[k]*float(n_intervals_y-j)/n_intervals_y
                p2 = points1[k]*float(j+1)/n_intervals_y + points2[k]*float(n_intervals_y-j-1)/n_intervals_y
                p3 = points1[k+1]*float(j+1)/n_intervals_y + points2[k+1]*float(n_intervals_y-j-1)/n_intervals_y
                p4 = points1[k+1]*float(j)/n_intervals_y + points2[k+1]*float(n_intervals_y-j)/n_intervals_y
                self.rectangles.append(Rectangle(p1, p2, p3, p4))

    def plot(self, color='k'):
        Rectangle.plot(self, color)
        for r in self.rectangles:
            r.plot()

def plot_board(n_players=3):
    # 1. compute the cornerpoints of the board
    n = n_players*2
    alpha = np.pi/n_players
    cornerpoints = []
    for k in range(n):
        c = cmath.rect(1,k*alpha)
        cornerpoints.append( np.array([c.real, c.imag]) )
    midpoints = []
    for k in range(-1,n-1):
        midpoints.append(0.5*(cornerpoints[k] + cornerpoints[k+1]))
    # 2. create cornerboards
    cornerboards = [CornerBoard(cornerpoints[k-1], midpoints[k], np.zeros(2), midpoints[k-1]) for (k,c) in enumerate(cornerpoints)]
    for c in cornerboards:
        c.rectanglify()
        c.plot()

    # rectangles = []
    # for k in range(n_players):
    #     basepoints = []
    #     sidepoints = []
    #     for i in range(4):
    #         for j in range(4):
    #             pass
    #         #r1 = ...
    #         basepoints1.append(i/4.0*midpoints[2*k+1]+ (4.0-i)/4.0*cornerpoints[2*k])
    #         sidepoints.append(i/4.0*midpoints[2*k+1]+ (4.0-i)/4.0*cornerpoints[2*k])

    cx = np.array([i[0] for i in cornerpoints])
    cy = np.array([i[1] for i in cornerpoints])
    mx = np.array([i[0] for i in midpoints])
    my = np.array([i[1] for i in midpoints])
    plt.plot(cx,cy, 'x')
    plt.plot(mx,my, 'o')
    plt.show()


def test_plot_board():
    plot_board()


if __name__=='__main__':
    test_plot_board()
