__author__ = 'ub1404'
import exceptions
from enum import Enum
class PlotType(Enum):
    PLOT_INVALID=0,
    PLOT_2D=1,
    PLOT_3D=2
# -simple
#     [t, q1]  => simple 2d plot
#     [t-q1,q2,qd] => simple 2d plot(3 fields). share t as x.
#     [t,q1][t,q2] => 2 figures
#     [t1,q1:t2,q2:t3,q3] => 1 figure 3 merged.
#
# 3d plot
#     [q1,qd1,qdd1] => simple 3d plot (phase plot)
#     [q1,qd1,qdd1][q2,qd2,qdd2] => 2 figures
#     [q1,qd1,qdd1:q2,qd2,qdd2] => 1 figure 2 merged 3d
#
# subplot
# -2d subplot
#     [[t,q1][t,q2][t,q3]] => 1 figure 3 subplots
#
# -3d subplot
#     [[q1,qd1,qdd1][q2,qd2,qdd2]] => 1 figure 2 subplots


class PlotInfo(object):
    def __init__(self):
        self.plot_type = None
        self.x_names = []
        self.y_names = []
        self.z_names = []

    def __add_fields(self, fields):
        if self.plot_type:
            if self.plot_type is PlotType.PLOT_INVALID:
                return

        if len(fields) is 2:
            if self.plot_type:
                if self.plot_type is not PlotType.PLOT_2D:
                    # plot_type conflict
                    self.plot_type = PlotType.PLOT_INVALID
                    return

            self.plot_type = PlotType.PLOT_2D
            self.x_names.append(fields[0])
            self.y_names.append(fields[1])
        elif len(fields) is 3:
            if self.plot_type:
                if self.plot_type is not PlotType.PLOT_3D:
                    # plot_type conflict
                    self.plot_type = PlotType.PLOT_INVALID
                    return

            self.plot_type = PlotType.PLOT_3D
            self.x_names.append(fields[0])
            self.y_names.append(fields[1])
            self.z_names.append(fields[2])
        else:
            self.plot_type = PlotType.PLOT_INVALID

    def __add_shared_fields(self, x_name, y_names):
        if self.plot_type:
            if self.plot_type is PlotType.PLOT_INVALID:
                return

        self.plot_type = PlotType.PLOT_2D
        for yn in y_names:
            self.x_names.append(x_name)
            self.y_names.append(yn)
    def parse(self, info=""):
        if getDepth(info) is not 0:
            return -1

        draws = info.split(":") # split into clusters
        for draw in draws:
            if draw.find("-") is -1:# arbitrary x
                fields = draw.split(",")
                self.__add_fields(fields)
            else:   #shared x(supports only 2D plot)
                x, ys = draw.split("-")
                ys = ys.split(",")
                self.__add_shared_fields(x, ys)

    def print_info(self):
        print "Type : %s" % self.plot_type.name
        print "Fields : "
        if self.plot_type is PlotType.PLOT_2D:
            for i,_ in enumerate(self.x_names):
                print "\t x : %s\t y : %s\n" % (self.x_names[i], self.y_names[i])
        elif self.plot_type is PlotType.PLOT_3D:
            for i,_ in enumerate(self.x_names):
                print "\t x : %s\t y : %s\t z : %s\n" \
                      % (self.x_names[i], self.y_names[i], self.z_names[i])
        else:
            print "\tInvalid Fields"



'''
a:b,c,d
a,b:c,d:e,f
a,b,c:d,e,f
a-b,c:a-e,f
'''


class FigInfo(object):
    def __init__(self):
        self.subplots_list = []

    def parse(self, info=""):
        depth = getDepth(info)
        if depth not in [0, 1]:
            return -1

        if depth is 1: # subplots
            raw_info_list = parsePlotInfo(info)
            for raw_info in raw_info_list:
                self.__add_subplot(raw_info)
        else:   # single plot
            self.__add_subplot(info)

    def __add_subplot(self, info):
        subplot = PlotInfo()
        if subplot.parse(info) is not -1:
            self.subplots_list.append(subplot)
        else:
            print "Failed to parse subplot => %s" % info

    def print_info(self):
        for subplt in self.subplots_list:
            subplt.print_info()

class FigManager(object):
    def __init__(self):
        self.figs_list = []

    def parse(self, info=""):
        if getDepth(info) not in [1,2]:
            return -1

        raw_info_list = parsePlotInfo(info)
        for raw_info in raw_info_list:
            self.__add_figure(raw_info)

    def __add_figure(self, info):
        fig = FigInfo()
        if fig.parse(info) is not -1:
            self.figs_list.append(fig)
        else:
            print "Failed to parse figure => %s" % info

    def print_info(self):
        for fig in self.figs_list:
            fig.print_info()

_open_mark = "["
_close_mark= "]"

def getDepth(info_str=""):
    idx1 = info_str.find(_open_mark)
    idx2 = info_str.find(_close_mark)

    if idx1 is -1:
        if idx2 is -1:
            return 0    # no hierarchy

    max_depth = 0
    depth = 0
    for c in info_str:
        if c is _open_mark:
            depth += 1
            if max_depth < depth:
                max_depth = depth

        if c is _close_mark:
            depth -= 1

    # depth must end up with 0
    if depth is not 0:
        return -1

    return max_depth

def parsePlotInfo(info_str=""):
    idx = info_str.find(_open_mark)
    if idx == -1:
        raise exceptions.Exception("Cannot find opening bracket(%c)"%_open_mark)

    if idx > info_str.find(_close_mark):
        raise exceptions.Exception("String starts with closing bracket(%c)"%_close_mark)

    top_level = []
    depth = 0
    start_idx = 0
    end_idx = 0
    for i,c in enumerate(info_str):
        if c is _open_mark:
            if depth is 0:
                start_idx=i
            depth += 1
        if c is _close_mark:
            depth -= 1
        if depth is 0:
            end_idx = i
            top_level.append(info_str[start_idx+1:end_idx])

    return top_level

if __name__=="__main__":
    examples = ["[t, q1]","[t-q1,q2,qd]","[t,q1][t,q2]","[q1,qd1,qdd1]",
                "[q1,qd1,qdd1][q2,qd2,qdd2]","[[t,q1][t,q2][t,q3]]",
                "[[q1,qd1,qdd1][q2,qd2,qdd2]]"]

    for ex in examples:
        print "-"*5,ex,"-"*5
        fig_man = FigManager()
        if fig_man.parse(ex) == -1:
            print "error"
            continue
        fig_man.print_info()