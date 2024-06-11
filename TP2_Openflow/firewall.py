'''
Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment: Layer-2 Firewall Application

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
'''

from pox.core import core
from pox.lib.util import dpidToStr
from pox.lib.revent.revent import EventMixin
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
import os
import json
''' Add your imports here ... '''

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ['HOME']

''' Add your global variables here ... '''
FILE_NAME = "firewall_rules.json"


class Firewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp(self, event):
        log.info(f"EVENT: {event.dpid}")
        message = of.ofp_flow_mod()

        self.firewall_rules = self.get_firewall_rules(FILE_NAME)
        if event.dpid == self.firewall_rules['firewall_switch']:
            self.set_firewall_rules(event, message)
            log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

    def set_firewall_rules(self, event, message):
        rules = self.firewall_rules['rules']
        for rule in rules:
            message.match.dl_type = ethernet.IP_TYPE
            # Descarta el paquete con src ip == a 10.0.0.1 y dst ip == 10.0.0.3
            message.match.nw_src = rule["nw_src"]
            message.match.nw_dst = rule["nw_dst"]
            event.connection.send(message)

    def get_firewall_rules(self, file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data


def launch():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
