__author__ = 'jaejunlee'


import matplotlib.pyplot as plt
import numpy as np
import optparse as opt
import csv
import sys


'''
parse csv file which contains data names on the first line.
returned 'names' variable is a list in same order of raw csv file.

example data)
d1,d2,d3,d4
1,2,3,4
5,6,7,8
1,2,3,4

names, data_dic = parseCSV(options.file)
print names[0], data_dic[names[0]]


-simple
    [t, q1]  => simple 2d plot
    [t-q1,q2,qd] => simple 2d plot(3 fields). share t as x.
    [t,q1][t,q2] => 2 figures
    [t1,q1:t2,q2:t3,q3] => 1 figure 3 merged.

3d plot
    [q1,qd1,qdd1] => simple 3d plot (phase plot)
    [q1,qd1,qdd1][q2,qd2,qdd2] => 2 figures
    [q1,qd1,qdd1:q2,qd2,qdd2] => 1 figure 2 merged 3d

subplot
-2d subplot
    [[t,q1][t,q2][t,q3]] => 1 figure 3 subplots

-3d subplot
    [[q1,qd1,qdd1][q2,qd2,qdd2]] => 1 figure 2 subplots
'''

#######################CSV format parsing########################
def parseCSV(file_name):
    # get headers
    with open(file_name,'rb') as csvfile:
        names = csvfile.readline()
        names = names.strip().split(",")

    # change csv data to dictionary({name:data_list})
    with open(file_name,'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        data_dic = {}
        for row in reader:
            for name in names:
                if not data_dic.has_key(name):
                    data_dic[name]=[row[name]]
                else:
                    data_dic[name].append(row[name])

    return names, data_dic

only_parsed = []
def optcallback_parse_only(option, opt_str, value, parser):
    global only_parsed
    if not value:
        return
    only_parsed = value.split(",")


#######################Figure Information containers########################
'''
Information container of 1 figure window
'''

import exceptions
from enum import Enum
class PlotType(Enum):
    PLOT_INVALID=0,
    PLOT_2D=1,
    PLOT_3D=2


class PlotInfo(object):
    def __init__(self):
        self.plot_type = None
        self.x_names = []
        self.y_names = []
        self.z_names = []

    def add_fields(self, fields):
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

    def add_shared_fields(self, x_name, y_names):
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
                self.add_fields(fields)
            else:   #shared x(supports only 2D plot)
                x, ys = draw.split("-")
                ys = ys.split(",")
                self.add_shared_fields(x, ys)

    def print_info(self):
        print "\t\tType : %s" % self.plot_type.name
        print "\t\tFields : "
        if self.plot_type is PlotType.PLOT_2D:
            for i,_ in enumerate(self.x_names):
                print "\t\t x : %s\t y : %s\n" % (self.x_names[i], self.y_names[i])
        elif self.plot_type is PlotType.PLOT_3D:
            for i,_ in enumerate(self.x_names):
                print "\t\t x : %s\t y : %s\t z : %s\n" \
                      % (self.x_names[i], self.y_names[i], self.z_names[i])
        else:
            print "\t\tInvalid Fields"

    def plot(self, ax, data):
        if self.plot_type == PlotType.PLOT_2D:
            for i in range(len(self.x_names)):
                ax.plot(data[self.x_names[i]], data[self.y_names[i]],
                        label=self.y_names[i])
            ax.legend(loc='upper right', shadow=True)
            # ax.set_xlabel(self.x_names[i])
        elif self.plot_type == PlotType.PLOT_3D:
            pass #TODO : 3d plot
        else:
            print "PlotInfo::plot error"

class FigInfo(object):
    def __init__(self):
        self.subplots_list = []
        self.subplots_grid = {1:[1,1], 2:[1,2], 3:[3,1], 4:[2,2],
                              5:[3,2], 6:[3,2], 7:[4,2], 8:[4,2],
                              9:[3,3], 10:[3,4], 11:[3,4], 12:[3,4]}

    def parse(self, info=""):
        depth = getDepth(info)
        if depth not in [0, 1]:
            return -1

        if depth is 1: # subplots
            raw_info_list = parsePlotInfo(info)
            for raw_info in raw_info_list:
                self.add_subplot(raw_info)
        else:   # single plot
            self.add_subplot(info)

    def add_subplot(self, info):
        subplot = PlotInfo()
        if subplot.parse(info) is not -1:
            self.subplots_list.append(subplot)
        else:
            print "Failed to parse subplot => %s" % info

    def print_info(self):
        for i, subplt in enumerate(self.subplots_list):
            print "\tSubplot %d : "%i
            subplt.print_info()

    def plot(self, data):
        n_subplt = len(self.subplots_list)
        grid = self.subplots_grid[n_subplt]

        fig, axarr = plt.subplots(grid[0],grid[1])

        if n_subplt == 1:
            self.subplots_list[0].plot(axarr, data)
        else:
            if grid[0]==1 or grid[1]==1:
                for i, subplt in enumerate(self.subplots_list):
                    subplt.plot(axarr[i], data)
            else:
                for i, subplt in enumerate(self.subplots_list):
                    subplt.plot(axarr[i/grid[1], i%grid[1]], data)

class FigManager(object):
    def __init__(self):
        self.figs_list = []

    def parse(self, info=""):
        if getDepth(info) not in [1,2]:
            return -1

        raw_info_list = parsePlotInfo(info)
        for raw_info in raw_info_list:
            self.add_figure(raw_info)

    def add_figure(self, info):
        fig = FigInfo()
        if fig.parse(info) is not -1:
            self.figs_list.append(fig)
        else:
            print "Failed to parse figure => %s" % info

    def print_info(self):
        for i, fig in enumerate(self.figs_list):
            print "Figure %d : " % i
            fig.print_info()

    def add_2d_simple_figure(self, x_name, y_name):
        template = "%s,%s" % (x_name, y_name)
        self.add_figure(template)

    def plot(self, data):
        for fig in self.figs_list:
            fig.plot(data)

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
    #######################Options Parsing########################
    parser = opt.OptionParser()
    parser.set_usage("Usage: %prog --file filename [options]")
    parser.add_option("--file",
                      dest="file",
                      help="Specify which file you want to plot")

    parser.add_option("--just-print",
                      dest="just_print",
                      default=False,
                      action="store_true",
                      help="Just print the data to the console")

    parser.add_option("--only",
                      dest="only",
                      type="string",
                      default="",
                      action="callback",
                      callback=optcallback_parse_only)

    parser.add_option("--conf",
                      dest="config",
                      type="string",
                      default=""
                      )

    parser.add_option("--conf-file",
                      dest="conf_file",
                      type="string",
                      default="")

    options, remainder = parser.parse_args()
    if not options.file:
        parser.print_help()
        sys.exit(-1)

    if not options.config:
        if options.conf_file:
            with open(options.conf_file, "r") as conf_file:
                options.config = conf_file.readline()

    options.only = only_parsed
    #########################CSV Parsing##########################
    names, data_dic = parseCSV(options.file)
    # print names
    # print data_dic

    if not options.config and options.only:
        tmp_names = [n for n in names]
        for i, name in enumerate(tmp_names):
            if i is 0:
                continue # first column is required at any circumstance
            if name not in options.only:
                del(data_dic[name])
                names.remove(name)



    ########################Parsing Figures#######################
    fig_man = FigManager()
    if not options.config: # default
        x_name = names[0]
        for idx in range(1,len(names)):
            fig_man.add_2d_simple_figure(x_name, names[idx])
    else:
        fig_man.parse(options.config)

    fig_man.print_info()

    ########################Plot Figures##########################

    fig_man.plot(data_dic)
    plt.show()