#!/usr/bin/env python

from card import Card

deck = (
    #Card(type, name, duration, fail, win, target, ""),
    Card("recon", "nmap", 5, 3, 8, "any", "Runs an nmap scan on the target network"),
    Card("recon", "shodan", 3, 1, 3, "any", "Attempts to find hosts using shodan"),
    Card("hack", "sqlmap", 7, 5, 2, "Database server", "Attempts an SQL injection on the target host"),
    Card("hack", "custom exploit", 9, 3, 4, "any", "Develop and deploy a 0day"),
)
