#!/usr/bin/env python3

from random import shuffle, sample, random, choice, randint, gauss
import sys, copy, socket
import socket

HOST = '127.0.0.1'
PORT = 4242
starting_known_hosts_value = 20
starting_unknown_hosts_value = 5
winning_hosts_value = 10
cards_in_hand = 5

# todo implement event cards, like a
# - "new exploit is found for <target>",
# - new unknown host has been found at player,
# - discruntled coworker sabotages infrastructure

# todo hide value/defense, only show defense for own hosts when detected/defended
class Card():
    def __init__(self, type, name, duration, fail, win, target, slots, desc):
        self.name = name
        if type not in ('recon', "hack", "detect", "defend"): raise ValueError("bad type in card: %s" % type)
        self.type = type
        self.duration = duration    # in rounds
        self._duration = duration    # in rounds
        self.fail = fail            # chance to fail
        self.win = win              # chance to succeed
        self.target = target        # what kind of host can be targeted with this card?
        self._target = target        # what kind of host can be targeted with this card?
        self.desc = desc
        self.slots = slots

    def __str__(self):
        return "%8s %20s %sT %sF %sW %sC target: %20s    | %s " % (self.type, self.name, self.duration, self.fail, self.win, self.slots, self.target, self.desc)

    def check(self, player):
        if player.max_slots - sum(c.slots for c in player.active_cards) < self.slots:
            player.send("you don't have enough capacities for this action")
            return False
        if self.target=="network": return True
        if self.type in ['recon', 'hack']:
            targets = player.known_hosts
        else:
            targets = player.own_hosts
        if not self.target=="any":
            targets = (t for t in targets if t.type == self.target)
        if not targets: return False
        self.target=choose(player.sock, "please select host against you want to deploy %s" % self.name, targets)
        return True

    def activate(self, player):
        player.send("activating %s" % str(self))
        res = randint(0,10)
        if isinstance(self.target, Host) and self.type in ['hack', 'recon']:
            res+=self.target.defense
        if res <= self.fail: self.lame(player)
        elif res >= self.win: self.leet(player)
        else: player.send("nothing happens")
        self.duration = self._duration
        self.target = self._target

    def leet(self, player):
        if self.type=='recon':
            if self.target=='network':
                # reveal one host of the opponent
                tmp = [h for h in player.opponents()[0].own_hosts+player.opponents()[0].unknown_hosts if h not in player.known_hosts]
                if tmp:
                    player.known_hosts.append(choice(tmp))
            elif isinstance(self.target, Host):
                self.target.defense-=int(gauss(2,1))
            else:
                player.send("leet failed for %s" % self)

        elif self.type=='hack':
            if not isinstance(self.target, Host):
                player.send('oops target "%s" is not a host, how can you hack it?' % self.target)
            if self.target not in player.pwned_hosts:
                player.pwned_hosts.append(self.target)
                player.known_hosts.remove(self.target)
                player.send("PWNd!")
            else:
                player.send("%s is already pwned by you." % self.target)

        elif self.type=='detect':
            if self.target=='network':
                h = None
                # reveal one unknown host
                tmp = [h for h in player.unknown_hosts]
                if tmp:
                    h = choice(tmp)
                if h:
                    player.own_hosts.append(h)
                    player.unknown_hosts.remove(h)
                    player.send("found a new %s" % h)
            elif isinstance(self.target, host):
                player.send("%s has $%s value and [%s] defense" % (self.target.name, self.target.value, self.target.defense))
            else:
                player.send("leet failed for %s" % self)

        elif self.type=='defend':
            if self.target in player.opponents()[0].pwned_hosts:
                player.opponents()[0].pwned_hosts.remove(self.target)
                player.opponents()[0].known_hosts.append(self.target)
                player.send("denied!")
            elif self.target == 'network':
                factor = int(gauss(2,1))
                for h in player.own_hosts:
                    h.defense+=factor
            else:
                self.target.defense+=int(gauss(2,1))

    def lame(self, player):
        if self.type=='recon':
            if self.target=='network':
                for h in player.opponents()[0].own_hosts:
                    h.defense+=int(gauss(1,1))
            elif isinstance(self.target, Host):
                self.target.defense-=int(gauss(2,1))
            else:
                player.send("leet failed for %s" % self)
        elif self.type=='hack':
            if not isinstance(self.target, Host):
                player.send('oops target "%s" is not a host, how can you hack it?' % self.target)
            if self.target not in player.pwned_hosts:
                self.target.defense-=int(gauss(2,1))
            else:
                player.send("%s is already pwned by you." % self.target)
        elif self.type=='detect':
            h=None
            if self.target=='network':
                tmp = player.own_hosts
                if tmp:
                    h = choice(tmp)
            elif isinstance(self.target, Host):
                h = self.target
            if h:
                player.own_hosts.remove(h)
                player.unknown_hosts.append(h)
        elif self.type=='defend':
            h=None
            if self.target=='network':
                tmp = player.own_hosts
                if tmp:
                    h = choice(tmp)
            elif isinstance(self.target, Host):
                h = self.target
            if h:
                h.defense-=int(gauss(1,1))

    # DoS, bruteforce passwords (hydra) against www/wordpress, rce, lpe, rp(rivileged)ce
deck = [
    #Card(type, name, duration, fail, win, target, slots, ""),
    Card("recon", "nmap network", 5, 2, 4, "network", 1, "Runs an nmap scan on the target network"),
    Card("recon", "shodan", 2, 0, 6, "network", 1, "Attempts to find hosts using shodan"),
    Card("recon", "github", 3, 0, 6, "network", 1, "Attempts to find vectors using github"),
    Card("recon", "dns", 1, 1, 5, "network", 1, "Attempts to find hosts using dns recon"),

    #Card("hack", "sqlmap", 7, 5, 7, "db", 2, "Attempts an SQL injection on the target host"),
    #Card("hack", "burp", 8, 2, 6, "www", 2, "Applies Burp proxy on the target webserver"),
    #Card("hack", "zap", 7, 3, 7, "www", 2, "Applies OWASP Zap proxy on the target webserver"),
    Card("hack", "custom exploit", 9, 3, 4, "any", 4, "Develop and deploy a 0day"),
    Card("hack", "exploitdb", 3, 3, 5, "any", 2, "Adapt an exploitdb PoC"),
    Card("hack", "phish", 1, 1, 2, "desktop", 1, "Phish a desktop host"),
    Card("hack", "bruteforce passwords", 4, 0, 7, "any", 1, "Bruteforce passwords"),

    Card("detect", "Log analysis", 2, 0, 2, "network", 2, "You stare at logs."),
    Card("detect", "nmap", 2, 0, 5, "network", 1, "You nmap your own network."),
    Card("detect", "passive scanning", 5, 0, 2, "network", 2, "You sniff your own network for unknown hosts."),
    Card("detect", "gdorks", 1, 0, 6, "network", 1, "You search for some google dorks."),

    #Card("defend", "IDS", 3, 1, 4, "network", 2, "You set up an IDS."),    # TODO
    Card("defend", "Patch", 2, 0, 3, "any", 1, "You upgrade one version."),
    Card("defend", "Secure", 2, 1, 4, "any", 1, "You secure the configuration."),
    Card("defend", "Harden", 4, 1, 5, "any", 1, "You harden the setup of the host."),
    #Card("defend", "IDS accuracy", 2, 2, 4, "network", 1, "You try to reduce your IDS false positive rate."),    # TODO
    Card("defend", "Sniffing", 7, 0, 2, "any", 2, "You sniff the traffic of a potential target."),
    #Card("defend", "Honeypot", 3, 1, 4, "network", 1, "You install a honeypot."),    # TODO
    #Card("defend", "Obscure Honeypot", 3, 0, 3, "network", 1, "You try to make your honeypot less obvious."),    # TODO
    Card("defend", "WAF", 3, 1, 4, "www", 1, "You install a Web Application Firewall."),
]


class Host(): # todo tier: online/internal
    # represents a host in the defenders network
    def __init__(self, owner, type, name, value):
        self.name=name              # a name for the host
        self.type=type              # the type of the host: domain controller, smtp server, http server, etc
        self.value=value            # value of the host: 0-8
        self.defense = int(gauss(0,4))
        self.owner = owner

    def __str__(self):
        return "%s" % (self.name)

    def __repr__(self):
        return self.__str__()

HOSTS = (
    ("DC", "Domain Controller", 6),
    ("smtp", "SMTP server", 2),
    ("www", "Webserver", 3),
    ("www", "Wordpress instance", 2),
    ("www", "JBOSS application server", 2),
    ("www", "Intranet webserver", 3),
    ("storage", "Fileserver", 5),
    ("db", "Database server", 6),
    ("pos", "POS terminal", 2),
    ("www", "Development Server", 1),
    ("printer", "Printer", 2),
    ("router", "Router", 4),
    ("switch", "Switch", 4),
    ("ap", "WiFi access point", 4),
    ("desktop", "low-value Desktop", 1),
    ("desktop", "medium-value Desktop", 2),
    ("desktop", "high-value Desktop", 3),
    ("ca", "Certificate Authority", 8),
    ("www", "Acceptance test server", 2),
)

class Player(object):
    def __init__(self, name, game, sock):
        self.name=name
        # known hosts to defend
        self.own_hosts = self.hosts(starting_known_hosts_value)
        # unknown hosts to defend
        self.unknown_hosts = self.hosts(starting_unknown_hosts_value)
        # target hosts
        self.known_hosts = []
        self.pwned_hosts = []
        self.active_cards = []
        self.max_slots = 4
        self.game = game
        self.hand = []
        self.sock = sock
        self.deck = copy.deepcopy(deck)
        shuffle(self.deck)

    def hosts(self,val):
        res = []
        while sum(h.value for h in res)<val:
            h = copy.deepcopy(Host(self, *choice(HOSTS)))
            h.value = int(gauss(h.value, h.value/2))
            res.append(h)
        return res

    def winner(self):
        return sum(h.value for h in self.pwned_hosts) >= winning_hosts_value

    def display(self):
        self.send("%s(score: %s) has %s\n...and knows about %s" % (self.name, sum(h.value for h in self.pwned_hosts), self.own_hosts, self.known_hosts))
        if self.pwned_hosts:
            self.send("pwned: %s" % self.pwned_hosts)
        self.send("cards in play:\n\t%s" % '\n\t'.join(str(c) for c in self.active_cards))

    def turn(self):
        self.send("-"*120)
        self.send('')
        ac = []
        for c in self.active_cards:
            c.duration -= 1
            if c.duration < 1:
                c.activate(self)
                self.deck.append(c)
            else:
                ac.append(c)
        self.active_cards = ac

        self.display()
        # if playing cards from hand
        draw_cards = []
        while cards_in_hand > len(self.hand)+len(draw_cards):
            draw_cards.append(self.deck.pop(0))
        #self.send("cards in hand:\n\t%s" % '\n\t'.join("%s\t%s" % (c.type,str(c)) for c in self.hand))
        if draw_cards:
            self.send("drawn cards:\n\t%s" % '\n\t'.join(str(c) for c in draw_cards))
            self.hand.extend(draw_cards)

        r = False
        while not r:
            cmd = choose(self.sock, "choose your action",[c for c in self.hand if self.max_slots - sum(x.slots for x in self.active_cards) >= c.slots]+['discard', 'pass'])
            if cmd=='pass':
                break
            elif cmd=='discard':
                c = choose(self.sock, "please select card you want to discard", self.hand)
                if c:
                    self.hand.remove(c)
                    self.deck.append(c)
                    break
            else:
                r = self.play_card(cmd)

    def play_card(self, c0):
        c = copy.deepcopy(c0)
        if not c.check(self):
            self.send("sorry this card cannot be played, try again.")
            return False
        self.active_cards.append(c)
        self.hand.remove(c0)
        return True

    def __str__(self):
        return "%s\n\town:%s\n\tunknown:%s\n\tactions:%s" % (self.name, self.own_hosts, self.unknown_hosts, self.active_cards)

    def opponents(self):
        return [p for p in self.game.players if p != self]

    def send(self, msg):
        self.sock.send(("%s\n"%msg).encode("utf8"))

class Game:
    def __init__(self, players, debug=False):
        socks = get_players()
        self.players=[Player(p, self, sock) for p,sock in zip(players,socks)]
        shuffle(self.players)
        self.round = 0
        self.debug = debug
        if self.debug:
            print('\n'.join(str(p) for p in self.players))

    def play(self):
        while True:
            self.round+=1
            for p in self.players:
                p.turn()
                if p.winner():
                    print("%s wins the game in round %s having pwned: %s" % (p.name, self.round, p.pwned_hosts))
                    p.send("you win!")
                    p.sock.close()
                    for p1 in self.players:
                        if p1 == p: continue
                        p1.send("you loose")
                        p1.sock.close()
                    return p

def get_players():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the port
    server_address = (HOST, PORT)
    print('starting up on {} port {}'.format(*server_address))

    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    # Wait for a connection
    print('waiting for a players')
    player1, address = sock.accept()
    print("player1 from %s" % repr(address))
    player2, address = sock.accept()
    print("player2 from %s" % repr(address))
    sock.close()
    return player1, player2

def choose(sock, msg, opts):
    res = None
    try:
        while sock.recv(4096,socket.MSG_DONTWAIT): pass
    except BlockingIOError: pass
    opts = {str(i):c for i, c in enumerate(opts)}
    while res not in opts.keys():
        #print(msg)
        #print("\t%s" % '\n\t'.join("%s %s" % (i,str(c)) for i, c in opts.items()))
        #print("> ", end="")
        #sys.stdout.flush()
        #res = sys.stdin.readline().strip()

        sock.send('\n'.join((msg,
                            "\t%s" % '\n\t'.join("%s %s" % (i,str(c)) for i, c in opts.items()),
                             '> ')).encode('utf8'))
        res = sock.recv(1).decode('utf8')
        # empty out anything else in the socket
        try:
            while sock.recv(4096,socket.MSG_DONTWAIT): pass
        except BlockingIOError: pass
    return opts[res]

g = Game(("hacker", "admin"), True)
g.play()
