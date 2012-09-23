# python_example.py

# Steve Ivy <steveivy@gmail.com>
# http://monkinetic.com
# Originally borrowed from https://github.com/etsy/statsd

# this file expects local_settings.py to be in the same dir, with statsd host and port information:
#
# statsd_host = 'localhost'
# statsd_port = 8125

# Sends statistics to the stats daemon over UDP

class Statsd(object):

    @staticmethod
    def timing(stat, time, sample_rate=1):
        """
        Log timing information
        >>> from python_example import Statsd
        >>> Statsd.timing('some.time', 500)
        """
        stats = {}
        stats[stat] = "%d|ms" % time
        Statsd.send(stats, sample_rate)

    @staticmethod
    def increment(args, stats, sample_rate=1):
        """
        Increments one or more stats counters
        >>> Statsd.increment('some.int')
        >>> Statsd.increment('some.int',0.5)
        """
        Statsd.update_stats(args, stats, 1, sample_rate)

    @staticmethod
    def decrement(stats, sample_rate=1):
        """
        Decrements one or more stats counters
        >>> Statsd.decrement('some.int')
        """
        Statsd.update_stats(stats, -1, sample_rate)

    @staticmethod
    def update_stats(args, stats, delta=1, sampleRate=1):
        """
        Updates one or more stats counters by arbitrary amounts
        >>> Statsd.update_stats('some.int',10)
        """
        if (type(stats) is not list):
            stats = [stats]
        data = {}
        for stat in stats:
            data[stat] = "%s|c" % delta

        Statsd.send(args, data, sampleRate)

    @staticmethod
    def send(args, data, sample_rate = 1):
        """
        Squirt the metrics over UDP
        """
        host, port = args.statsd.split(":")
        addr = host, int(port)

        sampled_data = {}

        if(sample_rate < 1):
            import random
            if random.random() <= sample_rate:
                for stat in data.keys():
                    value = data[stat]
                    sampled_data[stat] = "%s|@%s" %(value, sample_rate)
        else:
            sampled_data=data

        from socket import socket, AF_INET, SOCK_DGRAM
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        try:
            for stat in sampled_data.keys():
                value = sampled_data[stat]
                send_data = "%s:%s" % (stat, value)
                udp_sock.sendto(send_data, addr)
        except:
            import sys
            from pprint import pprint
            print "Unexpected error:", pprint(sys.exc_info())
            pass # we don't care
