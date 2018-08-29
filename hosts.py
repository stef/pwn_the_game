#!/usr/bin/env python

from random import random

class Host():
    # represents a host in the defenders network
    def __init__(self, name, type, value, protection=None, version=None):
        self.name=name              # a name for the host
        self.type=type              # the type of the host: domain controller, smtp server, http server, etc
        self.value=value            # value of the host: 0-8
        if not protection:
            self.protection = []
        else:
            self.protection=protection  # list of defenses installed
        if not version:
            self.version = int(random()*8)
        else:
            self.version=version        # delta from latest version

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

HOSTS = (
    Host("DC", "Domain Controller", 6),
    Host("smtp", "SMTP server", 2),
    Host("www", "Webserver", 3),
    Host("intra", "Intranet webserver", 3),
    Host("storage", "Fileserver", 5),
    Host("db", "Database server", 6),
    Host("pos", "POS terminal", 2),
    Host("dev", "Development Server", 2),
    Host("printer", "Printer", 2),
    Host("router", "Router", 4),
    Host("switch", "Switch", 4),
    Host("ap", "WiFi access point", 4),
    Host("desktop", "low-value Desktop", 1),
    Host("desktop", "medium-value Desktop", 2),
    Host("desktop", "high-value Desktop", 3),
    Host("ca", "Certificate Authority", 8),
)
