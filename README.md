This repository provides a collection of scripts that enable to extract raw counters from atop [1], 
aggregate them to generate high level performance metrics, which are then injected into a Graphite [2] database 
to be finally visualized through the Graphite Web UI, or even better, through Grafana [3], the widely-used 
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
