import configparser
import json


def ConfigFileWriter(config):

    # # lets create that config file for next time...
    cfgfile = open("telemetry.ini",'w')

    # add the settings to the structure of the file, and lets write it out...
    config.add_section("Serial")
    config.set("Serial","portName","COM4")
    config.set('Serial','baudRate', '19200')
    config.add_section("Display")
    config.set("Display","key","sonh")
    config.write(cfgfile)
    cfgfile.close()


def ConfigSectionMap(section, config):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = json.loads(config.get(section, option))
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            try:
                dict1[option] = config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
    return dict1