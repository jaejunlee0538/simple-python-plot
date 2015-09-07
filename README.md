# Usage

Plot data file in csv format.
Each fields **must** have field name on top of the file.

```
t,a,b,c,d
1,1,2,3,4
2,1,2,3,4
3,2,5,12,5
```
## Default

```shell
$ python simple_plot.py --file data.csv
$ python simple_plot.py --file data.csv --only q1,q2
```

**By default, the first field is considered as `x axis` data for every plots.**

## Subplots

```shell
$ python simple_plot.py --file data.csv --conf [[t,q1][t,q2]][[t,qd1],[t,qd2]]
```

## Superposition

```shell
$ python simple_plot.py --file data.csv --conf [t,q1:t,q2][t-q1,q2][[t-q1,q2][t-qd1,qd2]]
```

`[[t-q1,q2]]` means plot `q1` and `q2` on a single plot while sharing x data as `t`.


## config file

```shell
$ python simple_plot.py --file data.csv --conf-file my_conf.conf
```

**my_conf.conf**
```
[t,q1:t,q2][t-q1,q2][[t-q1,q2][t-qd1,qd2]]
```
