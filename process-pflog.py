#!/usr/local/bin/python
"""Read an incoming pflog tcpdump stream, and act on its data."""

# TODO: convert print statements to logging statements
#         * handle error, info, debug log levels
#       set up graphite/whisper/carbon to test sending.
#       will it block on non-existent carbon?

# Apr 08 14:33:58.603146 rule 8/(match) block in on em0: \
    # 73.170.248.1 > 224.0.0.1: igmp query [tos 0xc0] [ttl 1]

import argparse
import logging
import os
import re
import socket
import subprocess
import sys

RE_TCPDUMP = re.compile(r"rule (?P<rule_number>\d+)/\(match\) (?P<action>\w+) (?P<direction>\w+) on (?P<interface>\w+):")
RE_HOSTNAME = re.compile(r"(?P<short_name>\w+).?")

HOSTNAME = RE_HOSTNAME.search(socket.gethostname()).group("short_name")

# def send_to_carbon(stat_path, stat_value):
#     """Given a stat path and value, send to carbon."""
    # if parsed_line:
    #     stat_path = "stat.%(hostname)s.pf.%(interface)s.rule%(rule_number)s.%(action)s.%(direction)s" % {
    #         "hostname" : HOSTNAME,
    #         "rule_number" : parsed_line.group("rule_number"),
    #         "action" : parsed_line.group("action"),
    #         "interface" : parsed_line.group("interface"),
    #         "direction" : parsed_line.group("direction") }
    #     logging.info("Pflog rule triggered.")
    #     logging.debug("Stat path: %s", stat_path)
#     to_carbon = "%(stat_path)s %(stat_value)s %(NOW)s" % {
#         "stat_path" : stat_path,
#         "stat_value" : stat_value,
#         "NOW" : time.time() }
#     print "sending to statsd incrementing: %s" % stat_path
#     statsd_lib.Statsd.increment(stat_path)
#     print "done sending"
#     print "to carbon: %s" % to_carbon
#     this_socket = socket.socket()
#     try:
#         this_socket.connect( (CARBON_HOST, CARBON_PORT) )
#     except:
#         print "unable to connect to carbon host/port"
#         return 1
#     formatted_message = to_carbon + "\n"
#     print "formatted message: %s" % formatted_message
#     this_socket.sendall(formatted_message)
#     return 0

def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process pflog for monitoring, alerting, etc.")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Enable debug output.")
    parser.add_argument("--pflog",
                        help="Pflog interface")
    parser.add_argument("--carbon_hostport",
                        help="Host:port for Carbon listening daemon.")
    args = parser.parse_args()
    return args

def parse_tcpdump_line(raw_tcpdump_line):
    """Given tcpdump output line, parse into a Graphite-friendly statistic."""
    current_line = raw_tcpdump_line.strip()
    parsed_line = RE_TCPDUMP.search(current_line)
    if parsed_line is None:
        return None

    tcpdump_dict = { "rule_number" : parsed_line.group("rule_number"),
                     "action" : parsed_line.group("action"),
                     "direction" : parsed_line.group("direction"),
                     "interface" : parsed_line.group("interface"),
                     }
    return tcpdump_dict


def main():
    """Main function. Check arguments and spawn pflog|tcpdump chain."""

    args = get_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y%m%dT%H:%M:%S")

    logging.debug("Command line args: %s", args)

    if os.getuid() != 0:
        logging.error("Required to run as root. Exiting.")
        sys.exit(1)

    if not args.pflog:
        logging.error("Missing required pflog interface argument.")
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
            if args.carbon_hostport:
                send_to_carbon(tcpdump_dict)
    except KeyboardInterrupt:
        logging.info("Process killed by keyboard interrupt.")
        sys.exit(0)

    process.wait()
    logging.info("Tcpdump exited. Exit status: %s", process.returncode)


if __name__ == "__main__":
    main()
