from . import natural_time_parser as ntp
# import natural_time_parser as ntp

def natural_time(st):
    return ntp.natural_time_parser().parse_string(st)