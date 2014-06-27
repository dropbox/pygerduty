#!/usr/bin/env python

import datetime
import getpass
import optparse
import pygerduty
import re
import sys

TIME_STRING_RE = re.compile(
    r'(?:(?P<days>\d+)d)?'
    r'(?:(?P<hours>\d+)h)?'
    r'(?:(?P<minutes>\d+)m)?'
    r'(?:(?P<seconds>\d+)s)?'
)


def parse_time_string(time_string):
    times = TIME_STRING_RE.match(time_string).groupdict()
    for key, value in times.iteritems():
        if value is None:
            times[key] = 0
        else:
            times[key] = int(value)

    return times


def get_times(time_string):
    times = parse_time_string(time_string)

    now = datetime.datetime.utcnow()
    then = datetime.timedelta(**times)

    return isoformat(now), isoformat(now + then)


def isoformat(dtime):
    return "%sZ" % dtime.isoformat()


def format_overrides(overrides):
    output = []
    format_str = "%-10s%-28s%-28s%-20s"
    output.append(format_str % ("ID:", "Start:", "End:", "User:"))
    for override in overrides:
        output.append(format_str % (
            override.id, override.start, override.end, override.user.name))
    return "\n".join(output)


def print_overrides(schedule):
    now = datetime.datetime.utcnow()
    since = isoformat(now)
    until = isoformat(now + datetime.timedelta(hours=2))
    overrides = schedule.overrides.list(
        editable=True, overflow=True, since=since, until=until)
    if not overrides:
        print "No Editable Overrides."
        sys.exit(1)
    print format_overrides(overrides)


def main():
    parser = optparse.OptionParser()

    parser.add_option("--list", default=False, action="store_true",
                      help="List editable overrides.")
    parser.add_option("--remove", default=None,
                      help="Remove <id> from list of overrides.")

    parser.add_option("--user", default=getpass.getuser(),
                      help="User to create the override for.")
    parser.add_option("--schedule", default=None,
                      help="Schedule to add the override to.")
    parser.add_option("--api_key", default=None,
                      help="Integration API key.")
    parser.add_option("--subdomain", default=None,
                      help="PagerDuty subdomain.")

    options, args = parser.parse_args()

    time_string = None
    if len(args) >= 1:
        time_string = args[0]

    required_options = [options.subdomain, options.api_key, options.schedule]
    if not all(required_options):
        parser.print_help()
        sys.exit(1)

    if not any([time_string, options.list, options.remove]):
        print "Please provide either a time_string, --list, or --remove"
        parser.print_help()
        sys.exit(1)

    if (time_string and
            any([options.list, options.remove]) or
            all([options.list, options.remove])):

        print "Please provide a single time string argument",
        print "OR action option (--list, --remove)."
        parser.print_help()
        sys.exit(1)

    pager = pygerduty.PagerDuty(options.subdomain, options.api_key)

    users = list(pager.users.list(query="%s" % options.user))
    if len(users) != 1:
        print "Expected 1 user. Found (%s)" % len(users)
        sys.exit(1)
    uid = users[0].id

    schedules = list(pager.schedules.list(query=options.schedule, limit=1))
    if len(schedules) != 1:
        print "Expected 1 schedule. Found (%s)" % len(schedules)
        sys.exit(1)
    schedule = schedules[0]

    if time_string:
        now, then = get_times(time_string)
        schedule.overrides.create(start=now, end=then, user_id=uid)
        print "Override created."
    elif options.list:
        print_overrides(schedule)
    elif options.remove:
        schedule.overrides.delete(options.remove)
        print "Removed Override."
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
