import sys
import argparse
from collections import defaultdict

import configargparse
import apache_log_parser
from pytool.cmd import Command, opt, run


# Default options
APACHE_FORMAT = ("%v:%p %h[%{X-Forwarded-For}i] %l %u %t \"%r\" %>s %O "
                 "\"%{Referer}i\" \"%{User-Agent}i\"")
APACHE_FIELDS = 'request_header_x_forwarded_for,remote_host'


class Main(Command):
    def set_opts(self):
        self.describe("Parse a log file with a apache log parser and output "
                      "statistics.")
        self.opt('--format', '-f', default=APACHE_FORMAT,
                 help="Apache log format string")
        self.opt('--fields', '-l', default=APACHE_FIELDS,
                 help="Apache fields to search for IP")
        self.opt('--quiet', '-q', action='store_true', help="Quieter output")
        self.opt('file', type=argparse.FileType('r'), default='-', nargs='?',
                 help="Filename to parse")

    def parser_opts(self):
        # This lets us use env vars for options
        return dict(auto_env_var_prefix='parse_')

    def run(self):
        """ Main run method. """
        quiet = self.args.quiet
        lines = self.args.file.read()
        if not lines:
            self.stderr("Log file is empty")
            sys.exit(1)

        # Work line by line
        lines = lines.split('\n')

        # Build our parser
        line_parser = apache_log_parser.make_parser(self.args.format)

        if not quiet:
            self.stderr(f"Parsing {len(lines)} lines...")

        # Hold the stats per value
        stats = defaultdict(int)
        # Use dynamic fields for fun and profit
        fields = self.args.fields.split(',')

        # Parse each line
        for line in lines:
            if not line or not line.strip():
                # Ignore completely blank lines
                continue

            # Print a dot when we parse a line
            if not quiet:
                # Print dots to follow progress on very large files
                sys.stderr.write('.')

            # Do the parsing using our handy library
            try:
                values = line_parser(line)
            except apache_log_parser.LineDoesntMatchException:
                self.stderr(f"Could not parse line: {line}")
                stats['-'] += 1
                continue

            # Find a field that has a good value - this lets us handle both
            # X-Forwarded-For (the IP of a remote client) and remote_host (the
            # IP of a load balancer doing healtchecks)
            for field in fields:
                value = values.get(field, None)
                if value and value != '-':
                    stats[value] += 1
                    break

            # Maybe we didn't find a good IP, but we just log and count it
            if not value or value == '-':
                self.stderr(f"Could not parse line: {line}")
                stats['-'] += 1

        if not quiet:
            # Print a newline to end the dots if we printed them
            self.stderr('')
        self.print_stats(stats)

    def print_stats(self, stats):
        """
        Prints out the stats dictionary.

        :param dict stats: Dict mapping value to count

        """
        # List of tuples for easy sorting
        stats = [(v, k) for k, v in stats.items()]
        stats = sorted(stats, reverse=True)

        # Total count
        count = sum([v for v, k in stats])

        self.stdout("field_value\tcount\tpercent")
        for num, value in stats:
            percent = 100.0 * num / count
            percent = round(percent, 4)
            self.stdout(f"{value}\t{num}\t{percent}")

    def stderr(self, msg):
        sys.stderr.write(f'{msg}\n')
        sys.stderr.flush()

    def stdout(self, msg):
        sys.stdout.write(f'{msg}\n')
        sys.stdout.flush()


if __name__ == '__main__':
    Main().start(sys.argv[1:])
