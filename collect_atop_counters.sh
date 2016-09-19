#!/bin/bash

##############################################################################
# This script allows to extract performance counters from atop, parse and    #
# format them as Graphite metrics, which can be visualized using Grafana     #
#                                                                            #
# Copyright 2016 by Rodrigue Chakode <rodrigue.chakode@realopinsight.com>    #
##############################################################################


# We first start by settings some global variables used throughout the script.

# Set atop command
ATOP_CMD=atop

# Set the labels of resource types to retrieve from atop
ATOP_COUNTER_LABELS="MEM,NET,CPU,cpu"

# Set the update interval for atop
ATOP_UPDATE_INTERVAL=${ATOP_UPDATE_INTERVAL-1} 

# We used awk to parse and format the atop output as Graphite metrics
AWK_CMD=awk

# Set a root prefix for your data. Default is 'graphite'
METRIC_PREFIX=${METRIC_PREFIX-"graphite"}

# We just output the Graphite metrics to the console
EXTERNAL_PROCESSING_COMMAND=cat

# We can use netcat to directly send data to graphite (through carbon daemon). 
# But this is not performant. As the script generates a many entries at each interval, 
# said every second, we will end up with a huge amount of consecutive network requests to 
# the graphite carbon daemon. The daemon will be quickly satured, in addition to the 
# huge amount of small network trafic. 
# By uncommenting the following settings, you can experience a direct data forward to graphite 
# through netcat
#GRAPHITE_CARBON_SERVER=${GRAPHITE_CARBON_SERVER-perfviz}
#GRAPHITE_CARBON_PORT=${GRAPHITE_CARBON_PORT-2003}
#EXTERNAL_PROCESSING_COMMAND="nc -w 5 $GRAPHITE_CARBON_SERVER $GRAPHITE_CARBON_PORT 2>&2"

$ATOP_CMD -P $ATOP_COUNTER_LABELS  $ATOP_UPDATE_INTERVAL | \
  $AWK_CMD -v METRIC_PREFIX=$METRIC_PREFIX 'BEGIN {DATA_TYPE="RESET"}
  {
    if (NF == 1) {
      DATA_TYPE = $0
    } else {
        if (DATA_TYPE == "SEP" && NF > 6) {
          data = ""
          indicator = $1
          machine = $2
          timestamp = $3
          interval_length = $6
          metric_key = $7
          if (indicator == "NET") {
            pcksrecv = $8
            pckssent = $10
            data = (data sprintf("%s.timeseries.%s.%s.%s.packetsrecv %s %s\n",  METRIC_PREFIX, machine, indicator, metric_key, pcksrecv, timestamp));
            data = (data sprintf("%s.timeseries.%s.%s.%s.packetssent %s %s\n", METRIC_PREFIX, machine, indicator, metric_key, pckssent, timestamp));
            bytesrecv = $9
            bytessent = $11
            recvthroughput = (bytesrecv * 8) / interval_length
            sendthroughput = (bytessent * 8) / interval_length
            data = (data sprintf("%s.timeseries.%s.%s.%s.recvthroughput %2.2f %d\n", METRIC_PREFIX, machine, indicator, metric_key, recvthroughput, timestamp));
            data = (data sprintf("%s.timeseries.%s.%s.%s.sendthroughput %2.2f %d\n", METRIC_PREFIX, machine, indicator, metric_key, sendthroughput, timestamp));
          } else if (indicator == "CPU" || indicator == "cpu") {
              indicator="CPU"
              total_clock_ticks_per_second = $7
              metric_key=$8
              interval_system_clock_ticks = $9
              interval_user_clock_ticks = $10
              utilization = 100 * (interval_system_clock_ticks + interval_user_clock_ticks) / (interval_length * total_clock_ticks_per_second)
              data = (data sprintf("%s.timeseries.%s.%s.%s.utilization %2.2f %s\n", METRIC_PREFIX, machine, indicator, metric_key, utilization, timestamp))
            } else if (indicator == "MEM") {
                page_size = $7
                total_mem = $8 * page_size
                free_mem = $9 * page_size
                used_mem = total_mem - free_mem
                used_mem_percent = (100 * used_mem) / total_mem
                data = (data sprintf("%s.timeseries.%s.%s.used_mem_percent %2.2f %d\n", METRIC_PREFIX, machine, indicator, used_mem_percent, timestamp))
              }
           printf data
        }    
    }

  } ' | $EXTERNAL_PROCESSING_COMMAND
