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
TCP_PROTOCOL = 6


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
            if "src_ip" in rule.keys():
                message.match.nw_src = rule["src_ip"]
            if "dst_ip" in rule.keys():
                message.match.nw_dst = rule["dst_ip"]
            # De aca para abajo no funcionan muy bien, chequear la docu
            if "dst_port" in rule.keys():
                if rule["dst_port"] == 80:
                    message.match.nw_proto = TCP_PROTOCOL
                message.match.tp_dst = rule["dst_port"]
            if "protocol" in rule.keys():
                message.match.nw_proto = rule["protocol"]

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
