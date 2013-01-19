#!/usr/bin/env python
"""Read an incoming pflog tcpdump stream, and act on its data.

usage: process-pflog.py [-h] [--debug] [--pflog PFLOG] [--statsd STATSD]

Process pflog for monitoring, alerting, etc.

optional arguments:
  -h, --help       show this help message and exit
  --debug          Enable debug output.
  --pflog PFLOG    Pflog interface
  --statsd STATSD  Optional Statsd host:port to send statistics.
"""

import argparse
import logging
import os
import re
import socket
import subprocess
import sys

import statsd_client


RE_HOSTNAME = re.compile(r"(?P<short_name>\w+).?")
RE_TCPDUMP_IPV4 = re.compile(r"""(?P<datetime_stamp>.*?) rule (?P<rule_number>\d+)/\(match\) (?P<action>(block|pass)) (?P<direction>(in|out)) on (?P<interface>\w+): (?P<src_ip>([0-9]{1,3}\.){3}[0-9]{1,3})\.?(?P<src_port>\d{1,5})? > (?P<dest_ip>([0-9]{1,3}\.){3}[0-9]{1,3})\.?(?P<dest_port>\d{1,5})?""")

HOSTNAME = RE_HOSTNAME.search(socket.gethostname()).group("short_name")


def send_to_statsd(args, tcpdump_dict):
    """Given a stat path, increment statistic in statsd."""
    stat_path = "%(hostname)s.pf.%(interface)s.rule%(rule_number)s.%(direction)s.%(action)s" % tcpdump_dict
    logging.info("Incrementing statsd path: %s", stat_path)
    statsd_client.Statsd.increment(args, stat_path)
    logging.debug("Done incrementing statsd.")


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process pflog for monitoring, alerting, etc.")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Enable debug output.")
    parser.add_argument("--pflog",
                        help="Pflog interface")
    parser.add_argument("--statsd",
                        action="store",
                        help="Optional Statsd host:port to send statistics.")
    args = parser.parse_args()

    return args


def parse_tcpdump_line(raw_tcpdump_line):
    """Given tcpdump output line, parse into a Graphite-friendly statistic."""
    current_line = raw_tcpdump_line.strip()
    parsed_line = RE_TCPDUMP_IPV4.search(current_line)
    if parsed_line is None:
        return None

    tcpdump_dict = { "datetime_stamp" : parsed_line.group("datetime_stamp"),
                     "rule_number" : parsed_line.group("rule_number"),
                     "action" : parsed_line.group("action"),
                     "direction" : parsed_line.group("direction"),
                     "interface" : parsed_line.group("interface"),
                     "src_ip" : parsed_line.group("src_ip"),
                     "src_port" : parsed_line.group("src_port"),
                     "dest_ip" : parsed_line.group("dest_ip"),
                     "dest_port" : parsed_line.group("dest_port"),
                     }
    return tcpdump_dict


def main():
    """Main function. Check arguments and spawn pflog|tcpdump chain."""

    args = get_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y%m%dT%H:%M:%S")

    logging.debug("Command line args: %s", args)

    if os.getuid() != 0:
        logging.error("Required to run as root.")
        sys.exit(1)

    if not args.pflog:
        logging.error("Required pflog interface argument missing.")
        sys.exit(1)

    logging.info("Starting tcpdump.")
    try:
        process = subprocess.Popen("/usr/sbin/tcpdump -n -e -ttt -i %s -l" %
                                   args.pflog,
                                   shell = True,
                                   stdout = subprocess.PIPE,
                                   stderr = subprocess.STDOUT)
        
        for current_line in iter(process.stdout.readline, ""):
            logging.debug("Raw tcpdump output: %s", current_line.strip())
            tcpdump_dict = parse_tcpdump_line(current_line)
            logging.debug("Tcpdump dict: %s", tcpdump_dict)
            if tcpdump_dict:
                tcpdump_dict["hostname"] = HOSTNAME
                logging.info("Matching pflog entry found.")
                if args.statsd:
                    send_to_statsd(args, tcpdump_dict)
    except KeyboardInterrupt:
        logging.info("Process killed by keyboard interrupt.")
        sys.exit(0)

    process.wait()
    logging.info("Tcpdump exited. Exit status: %s", process.returncode)


if __name__ == "__main__":
    main()
