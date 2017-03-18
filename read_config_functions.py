# reads from .config file
import configparser


def configsectionmap(fname, section):
    dict1 = {}
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config.read(filenames=fname)
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option, raw=True)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
