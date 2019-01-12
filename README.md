# Overview
This tool provides a collection of scripts that enable to extract raw counters from [atop](http://www.atoptool.nl/), 
aggregate them to generate high level performance metrics, which are then injected into a [Graphite](https://graphiteapp.org/) database 
to be finally visualized through the Graphite Web UI, or even better, through [Grafana](http://grafana.org/), the widely-used  open source visualization tool.

![](./atop-grafana-dashboard.png)

# Before you start
You will need to have:
* A working Graphite installation.
  And specifically, the Carbon Cache Daemon (carbon-cache.py) should be reachable through the following environement variables:
  * `CARBON_CACHE_SERVER`: should be set with the IP address or the hostname of the server hosting Carbon Cache.
  * `CARBON_CACHE_PICKLE_PORT`: should be set with the port of the pickle receiver of Carbon Cache.
* A working Grafana installation, if you want to use Grafana instead of the native Graphine UI.

# Getting Started Collecting Metrics
Log in to the machine where you want to collect performance metrics and run the following command:
```
$ atop -P NET,MEM,CPU,cpu | \
	collect_atop_counters.sh | \
	push_graphite_formatted_data_live.py
```

Then to the visualization to watch colllected metrics.

# Visualize Dashboard
* Log into Grafana
* If not yet the case, configure your Graphite installation as data source.
* If not yet the case, import [this dashboard template](https://grafana.com/dashboards/465) which is already configured to enable the visualization of the collected metrics out-of-the-box.
* Open the dashboard and enjoy!
