This repository provides a collection of scripts aiming at allowing to extract raw counters from atop [1], 
aggregate them to generate high level metrics, which are then injected into a Graphite database in order 
to be easily visualized through the Graphite [2] Web UI, or even better, through Grafana [3], the widely-used 
and popular open source visualization tool.

Easy-to-use
===========

```
$ atop -P NET,MEM,CPU,cpu | \
	collect_atop_counters.sh | \
	push_graphite_formatted_data_live.py
```


External Tools
===============
[1] Atop official site: http://www.atoptool.nl/
[2] Graphite official site: https://graphiteapp.org/
[3] Grafana official site: http://grafana.org/