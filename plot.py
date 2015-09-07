__author__ = 'jaejunlee'
'''
shared_x  y1, y2, y3, y4....

ex)
t q1 q2 q3 q4...


python plot.py
--version
--file a.csv

default


--cluster   => cluster q*, qd*, qdd* to 1 figure subplots
--only      => q1, qd1, qdd1


2d plot
-simple
    [t, q1]  => simple 2d plot
    [t:q1,q2,qd] => simple 2d plot(3 fields)
    [t,q1][t,q2] => 2 figures

3d plot
    [q1,qd1,qdd1] => simple 3d plot (phase plot)
    [q1,qd1,qdd1][q2,qd2,qdd2] => 2 figures

subplot
-2d subplot
    [[t,q1][t,q2][t,q3]] => 1 figure 3 subplots
    [t:q1;q2;q3]         => 1 figure 3 subplots(t is shared)
-3d subplot
    [[q1,qd1,qdd1][q2,qd2,qdd2]] => 1 figure 2 subplots

'''

import matplotlib.pyplot as plt
import numpy as np
import optparse as opt
import csv
import sys

def parseOpt():
    pass

if __name__=="__main__":
    # plt.close('all')
    print sys.argv[1:]
    parser = opt.OptionParser()
    parser.add_option('')
    options, remainder = parser.parse_args()


