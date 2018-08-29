#!/usr/bin/env python

class Card():
    def __init__(self, type, name, duration, fail, win, target, desc):
        self.name = name
        if type not in ('recon', "hack", "detect", "defend"): raise ValueError("bad type in card: %s" % type)
        self.type = type
        self.duration = duration    # in rounds
        self.fail = fail            # chance to fail
        self.win = win              # chance to succeed
        self.target = target        # what kind of host can be targeted with this card?
        self.desc = desc
