#!/usr/bin/env python

import librato
import ConfigParser
import sys

config = ConfigParser.ConfigParser()
try:
    config.read('./librato.conf')
    librato_user = config.get('librato', 'user')
    librato_token = config.get('librato', 'token')
except Exception as e:
    print "Problem with Librato config file. Exiting..."
    sys.exit(1)

api = librato.connect(librato_user, librato_token, sanitizer=librato.sanitize_metric_name)

# Create a new Space directly via API
space = api.create_space("PF Statistics-Hackday", tags=True)
print("Created '%s'" % space.name)
# bnin = space.add_bignumber_chart('IPv4 Bandwidth In', 'pf.In4_bytes_Pass', '*')
bnin = api.create_chart('Download BW',
                        space,
                        type='bignumber',
                        streams=[
                            {
                                "metric": "pf.In4_bytes_Pass-md",
                                "period": 60,
                                "transform_function": '(x/p)*8',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            }],
                        thresholds=[
                            {
                                "operator": ">",
                                "value": 30000000,
                                "type": "red"
                            }]
                        )
ipv4io = api.create_chart('IPv4 I/O',
                          space,
                          type='line',
#                          label='bps',
                          streams=[
                            {
                                "metric": "pf.In4_bytes_Pass-md",
                                "period": 60,
                                "name": "IPv4 In",
                                "units_long": "bps",
                                "color": "#8dfc06",
                                "transform_function": '(x/p)*8',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.Out4_bytes_Pass-md",
                                "period": 60,
                                "name": "IPv4 Out",
                                "units_long": "bps",
                                "color": "#0054a4",
                                "transform_function": '(x/p)*8',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.current_entries-md",
                                "period": 60,
                                "color": "#fef200",
                                "name": "Current states",
                                "units_long": "states",
                                "split_axis": True,
                                "tags": [{"name": "host", "values": ["*"]}]
                            }]
                         )
packets = api.create_chart('Packets',
                           space,
                           type='line',
                           label='packets/s',
                           streams=[
                            {
                                "metric": "pf.In4_packets_Block-md",
                                "period": 60,
                                "name": "IPv4 In Blocked",
                                "color": "#ed1b23",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.In4_packets_Pass-md",
                                "period": 60,
                                "name": "IPv4 In Passed",
                                "color": "#8dfc06",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.Out4_packets_Block-md",
                                "period": 60,
                                "name": "IPv4 Out Blocked",
                                "color": "#ffc20f",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.Out4_packets_Pass-md",
                                "period": 60,
                                "name": "IPv4 Out Passed",
                                "color": "#0054a4",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            }]
                         )
counts = api.create_chart('Counts',
                          space,
                          type='line',
                          streams=[
                            {
                                "metric": "pf.fragment-md",
                                "period": 60,
                                "name": "fragments",
                                "color": "#6a439b",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.congestion-md",
                                "period": 60,
                                "name": "congestion",
                                "color": "#0092ce",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.ip-option-md",
                                "period": 60,
                                "name": "ip-option",
                                "color": "#0054a4",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.state-mismatch-md",
                                "period": 60,
                                "name": "state-mismatch",
                                "color": "#ed1b23",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.match-md",
                                "period": 60,
                                "name": "match",
                                "color": "#8dfc06",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.proto-cksum-md",
                                "period": 60,
                                "name": "proto-cksum",
                                "color": "#f37020",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            }]
                         )
States = api.create_chart('States',
                           space,
                           type='line',
                           label='states',
                           streams=[
                            {
                                "metric": "pf.inserts-md",
                                "period": 60,
                                "name": "inserts",
                                "color": "#8dfc06",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.removals-md",
                                "period": 60,
                                "name": "removals",
                                "color": "#0054a4",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            },
                            {
                                "metric": "pf.searches-md",
                                "period": 60,
                                "name": "searches",
                                "color": "#ed1b23",
                                "transform_function": '(x/p)',
                                'summary_function': 'derivative',
                                "tags": [{"name": "host", "values": ["*"]}]
                            }]
                         )
