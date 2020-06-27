from .natural_time_parser import natural_time_parser as ntp

def natural_time(st):
    return ntp().parse_string(st)