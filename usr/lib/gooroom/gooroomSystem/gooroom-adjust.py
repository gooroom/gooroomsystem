#!/usr/bin/python

import os
import commands
import sys
from time import strftime

# Prepare the log file
global logfile
logfile = open("/var/log/gooroomsystem.log", "w")

def log (string):
    logfile.writelines("%s - %s\n" % (strftime("%Y-%m-%d %H:%M:%S"), string))
    logfile.flush()

log("gooroomSystem started")

try:
    # Read configuration
    sys.path.append('/usr/lib/gooroom/common')
    from configobj import ConfigObj
    config = ConfigObj("/etc/gooroom/gooroomSystem.conf")

    # Default values
    if ('global' not in config):
        config['global'] = {}
    if ('enabled' not in config['global']):
        config['global']['enabled'] = "True"
    if ('restore' not in config):
        config['restore'] = {}
    if ('lsb-release' not in config['restore']):
        config['restore']['lsb-release'] = "True"
    if ('etc-issue' not in config['restore']):
        config['restore']['etc-issue'] = "True"
    config.write()


    # Exit if disabled
    if (config['global']['enabled'] == "False"):
        log("Disabled - Exited")
        sys.exit(0)

    adjustment_directory = "/etc/gooroom/adjustments/"

    # Perform file execution adjustments
    for filename in os.listdir(adjustment_directory):
        basename, extension = os.path.splitext(filename)
        if extension == ".execute":
            full_path = adjustment_directory + "/" + filename
            os.system(full_path)
            log("%s executed" % full_path)

    # Restore LSB information
    if (config['restore']['lsb-release'] == "True"):
        if os.path.exists("/etc/lsb-release"):
            lsbfile = open("/etc/lsb-release", "w")
            if (commands.getoutput("grep DISTRIB_ID /etc/gooroom/info").strip() != ""):
                lsbfile.writelines(commands.getoutput("grep DISTRIB_ID /etc/gooroom/info") + "\n")
            else:
                lsbfile.writelines("DISTRIB_ID=Gooroom\n")
            lsbfile.writelines("DISTRIB_" + commands.getoutput("grep \"RELEASE=\" /etc/gooroom/info") + "\n")
            lsbfile.writelines("DISTRIB_" + commands.getoutput("grep CODENAME /etc/gooroom/info") + "\n")
            lsbfile.writelines("DISTRIB_" + commands.getoutput("grep DESCRIPTION /etc/gooroom/info") + "\n")
            lsbfile.close()
            log("/etc/lsb-release overwritten")

    # Restore /etc/issue and /etc/issue.net
    if (config['restore']['etc-issue'] == "True"):
        issue = commands.getoutput("grep DESCRIPTION /etc/gooroom/info").replace("DESCRIPTION=", "").replace("\"", "")
        if os.path.exists("/etc/issue"):
            issuefile = open("/etc/issue", "w")
            issuefile.writelines(issue + " \\n \\l\n")
            issuefile.close()
            log("/etc/issue overwritten")
        if os.path.exists("/etc/issue.net"):
            issuefile = open("/etc/issue.net", "w")
            issuefile.writelines(issue)
            issuefile.close()
            log("/etc/issue.net overwritten")


except Exception, detail:
    print detail
    log(detail)

log("gooroomSystem stopped")
logfile.close()
