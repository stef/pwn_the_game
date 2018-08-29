#!/usr/bin/env python

from random import shuffle, sample
from decks.attacker import deck as adeck
from decks.defender import deck as ddeck
from hosts import HOSTS

class Player(object):
    def __init__(self, name):
        self.name=name

class Attacker(Player):
    def __init__(self, name):
        self.deck = shuffle(list(adeck))
        self.known_hosts = []
        self.owned_hosts = []
        return super(Attacker, self).__init__(name)

    def winner(self):
        #todo define win condition for attacker
        return None

    def recon(self):
        # todo
        pass

    def attack(self):
        # todo
        pass

class Defender(Player):
    def __init__(self, name, hosts):
        self.deck = shuffle(list(ddeck))
        self.hosts = hosts
        return super(Defender, self).__init__(name)

    def winner(self):
        #todo define win condition for defender
        return None

    def detect(self):
        # todo
        pass

    def defend(self):
        # todo
        pass

class Game:
    def __init__(self, attacker, defender, hosts):
        self.attacker=attacker
        self.defender=defender
        self.hosts = sample(HOSTS, hosts)
        print self.hosts

    def winner(self):
        # todo define win condition
        if self.attacker.winner(): return self.attacker
        if self.defender.winner(): return self.defender
        return None

    def play(self):
        while not self.winner():
            self.attacker.recon()
            self.defender.detect()
            self.attacker.attack()
            self.defender.defend()

a = Attacker("hacker")
d = Defender("admin", 5)
g = Game(a, d, 8)
