import logging

import zwbrlib.bits as bits
from zwbrlib.controller import Controller as Controller
from zwbrlib.controllerdetails import ControllerDetails as ControllerDetails
import zwbrlib.message as message

def get_node(controller: Controller, node_id):
    return controller.request(message.request_GetNodeProtocolInfo(node_id), 'reply_GetNodeProtocolInfo', node_id)

class NodeList:

    def __init__(self, controller: Controller, controller_details: ControllerDetails, full_scan):
        """ List the nodes of the controller """
        logging.info("")
        self.nodes = list()
        nodes_ids = controller_details.nodes
        for node_id in range(1, 234):
            if full_scan or bits.is_id_set(nodes_ids, node_id):
                node = get_node(controller, node_id)
                if node != None:
                    self.nodes.append(node)

    def log(self):
        logging.info("--- nodes -------")
        for node in self.nodes:
            node.log()
            logging.info("-----------------")
