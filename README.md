# pflog-graphite

Send pflog statistics to Graphite (via statsd) for monitoring visualization.

## Requirements

* Python (at least 2.7.x)
* Statsd (for inclusion of statistics into Graphite)

## Installation

The pflog-graphite directory is expected to be deployed as /usr/local/pf-graphite.

The script itself is pflog_graphite_poller, running under the Python interpreter.

Included is an rc.d script so script can be included in system startup, and controlled via /etc/rc.d/pflog_graphite_poller.

## Configuration

In /etc/rc.conf.local, ensure `pflog_graphite_poller` is part of the `pkg_scripts` variable.

Also needed are several variable specifications:

    pflog_graphite_poller_user="root"
    pflog_graphite_poller_flags="--pflog pflog0 --statsd statsdhost:8125"

The script itself must run as root, since it initiates a tcpdump behind the scenes. We must also specify a pflog interface to read logged packages from pf. If you intend to sends the statistic to Statsd, that parameter must be passed a host:port pair.

Your pf.conf should include rules with a `log` argument if you intend for them to be parsed by this script and sent to stated.

rc.d-pflog_graphite_poller must be copied to /etc/rc.d as 'pflog_graphite_poller'.

Once all these files and configuration values are in place, start the poller:

    /etc/rc.d/pflog_graphite_poller start

## Example

Given the command line

    ./pflog_graphite_poller --pflog pflog0 --debug
    
Output on the command line, when displaying debug output, would display along the lines of the following:

    20130120T08:04:34 DEBUG Raw tcpdump output: Jan 20 08:04:34.527137 rule 1/(match) block in on em0: XXX.XXX.XXX.XXX.1234 > YYY.YYY.YYY.YYY.9876: S 462810291:462810291(0) win 14600 <mss 1460,sackOK,timestamp 955663583 0,nop,wscale 6> (DF) [tos 0x20]

    20130120T08:04:34 DEBUG Tcpdump dict: {'direction': 'in', 'rule_number': '1', 'src_ip': 'XXX.XXX.XXX.XXX.1234', 'datetime_stamp': 'Jan 20 08:04:34.527137', 'action': 'block', 'interface': 'em0', 'dest_ip': 'YYY.YYY.YYY.YYY.9876:'}

    20130120T08:04:34 INFO Incrementing statsd path: pf.fw1.em0.rule1.in.block

    20130120T08:04:34 DEBUG Done incrementing statsd.

This shows the raw tcpdump output, parsed tcpdump output into its relevant parts (if possible), and a composed metric for sending to statsd.