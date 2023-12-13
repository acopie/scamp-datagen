import logging

from anytree import PreOrderIter

log = logging.getLogger("main")


class SanityChecker:
    found = False

    def __init__(self, node, metainfo):
        self.node = node
        self.metainfo = metainfo

    def walk(self, node):
        """
        Walks through the tree and checks if the current node's product id belongs to the list of product/machines pairs
        :return:
        """
        for crt_node in PreOrderIter(node):
            self.check(crt_node)

        if SanityChecker.found:
            print("Sanity check passed")

    def check(self, node):
        found = False

        # get all the product/machines pairs
        prod_machines = self.metainfo.get("prod_machines")

        # iterate through all the product/machines pairs and see if the current node product id is in the list
        for crt_prod_machines in prod_machines:
            if crt_prod_machines.productid == node.productid:
                SanityChecker.found = True

                break
            else:
                continue

            if not SanityChecker.found:
                log.info(f"Product id {node.productid} not found in the list of product/machines pairs")
