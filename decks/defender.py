#!/usr/bin/env python

from card import Card

deck = [
    #Card("detect|defend", name, duration, fail, win, target, ""),
    Card("detect", "Log analysis", 2, 0, 2, "any", "You stare at logs."),
    Card("detect", "nmap", 2, 0, 6, "any", "You nmap your own network."),
    Card("detect", "passive scanning", 7, 0, 9, "any", "You sniff your own network for unknown hosts."),
    Card("detect", "search", 7, 0, 9, "any", "You search for some google dorks."),
    Card("defend", "IDS", 2, 0, 2, "any", "You set up an IDS."),
    Card("defend", "Patch", 3, 0, 8, "any", "You upgrade one version."),
    Card("defend", "Secure", 2, 0, 7, "any", "You secure the configuration."),
    Card("defend", "Harden", 4, 0, 8, "any", "You harden the setup of the host."),
    Card("defend", "IDS accuracy", 5, 0, 4, "any", "You try to reduce your IDS false positive rate."),
    Card("defend", "Sniffing", 7, 0, 6, "any", "You sniff the traffic of a potential target."),
    Card("defend", "Honeypot", 7, 0, 6, "any", "You install a honeypot."),
    Card("defend", "Obscure Honeypot", 7, 0, 6, "any", "You try to make your honeypot less obvious."),
    Card("defend", "WAF", 3, 0, 4, "Web server", "You install a Web Application Firewal."),
]
