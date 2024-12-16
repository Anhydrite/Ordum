from code import interact
import random
from typing import Dict, List, Optional
from matplotlib.colors import hex2color
import networkx as nx
import matplotlib.pyplot as plt

from gns3_connector import GNS3Connector
from interface import HyperInterface


class TopologyNode:
    def __init__(self, name: str, area: "TopologyArea", type_: str = "Standard"):
        self.area = area
        self.name = area.name + "-" + name
        self.type = type_
        self.links = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class TopologyAreaInLink:
    def __init__(self, source: TopologyNode, target: TopologyNode):
        self.name: str = source.name + "-" + target.name
        self.source: TopologyNode = source
        self.target: TopologyNode = target


class TopologyArea:
    def __init__(self, global_topology: "GlobalTopology", name: str):
        self.global_topology = global_topology
        self.name = name
        self.nodes: List[TopologyNode] = []
        self.links: List[TopologyAreaInLink] = []
        self.central_node = TopologyNode("Central", self)

    def add_node(self, node: TopologyNode) -> bool:
        if node not in self.nodes:
            self.nodes.append(node)
            return True

        return False

    def create_node(self, name: str, link_to_central: bool = True) -> TopologyNode:
        new_node = TopologyNode(name, self)
        if new_node not in self.nodes:
            self.nodes.append(new_node)
            if link_to_central:
                self.create_link(self.central_node, new_node)
            return new_node
        raise ValueError(f"Node {name} already exists")

    def get_node(self, name: str) -> TopologyNode:
        for node in self.nodes:
            if node.name == name:
                return node
        raise ValueError(f"Node {name} not found")

    def remove_node(self, node: TopologyNode) -> bool:
        if node in self.nodes:
            self.nodes.remove(node)
            return True
        return False

    def add_link(self, link: TopologyAreaInLink) -> bool:
        if link not in self.links:
            self.links.append(link)
            return True
        return False

    def create_link(self, source: TopologyNode, target: TopologyNode) -> TopologyAreaInLink:
        new_link = TopologyAreaInLink(source, target)
        new_link2 = TopologyAreaInLink(target, source)
        if new_link not in self.links:
            self.add_link(new_link)
            self.add_link(new_link2)
            return new_link
        raise ValueError(f"Link {source.name}-{target.name} already exists")

    def remove_link(self, source: str, target: str) -> bool:
        for link in self.links:
            if link.source == source and link.target == target:
                self.links.remove(link)
                return True
        return False

    def get_neighbors(self, node: TopologyNode) -> List[TopologyNode]:
        neighbors = []
        for link in self.links:
            if link.source == node:
                neighbors.append(link.target)
            elif link.target == node:
                neighbors.append(link.source)

        return neighbors


class TopologyMediumNode:
    def __init__(self, links: List[TopologyArea]):
        self.links: List[TopologyArea] = links
        concat_name = "-".join(map(lambda node: node.name, links))
        self.name = f"Medium-{concat_name}"


class TopologyLink:
    def __init__(
        self,
        source: "TopologyArea",
        target: "TopologyArea",
        source_node: TopologyNode,
        target_node: TopologyNode,
        medium_node: Optional[TopologyMediumNode] = None,
    ):
        self.name = source.name + "-" + target.name
        self.source_area: TopologyArea = source
        self.target_area: TopologyArea = target
        self.source_node: TopologyNode = source_node
        self.target_node: TopologyNode = target_node
        self.medium_node: Optional[TopologyMediumNode]
        if medium_node:
            self.medium_node = medium_node
        else:
            self.medium_node = None


class GlobalTopology:
    def __init__(self):
        self.areas: List[TopologyArea] = []
        self.links: List[TopologyLink] = []
        self.medium_nodes: List[TopologyMediumNode] = []

    def create_area(self, name: str) -> TopologyArea:
        new_area = TopologyArea(self, name)
        if new_area not in self.areas:
            self.areas.append(new_area)
            return new_area
        raise ValueError(f"Area {name} already exists")

    def get_area(self, name: str) -> TopologyArea:
        for area in self.areas:
            if area.name == name:
                return area
        raise ValueError(f"Area {name} not found")

    def create_link(
        self,
        source_area: TopologyArea,
        target_area: TopologyArea,
        source_node: Optional[TopologyNode] = None,
        target_node: Optional[TopologyNode] = None,
        create_medium_node: bool = True,
    ):
        if not source_node:
            source_node = source_area.central_node
        if not target_node:
            target_node = target_area.central_node

        medium_node = None
        if create_medium_node:
            medium_node = TopologyMediumNode([source_area, target_area])
            self.medium_nodes.append(medium_node)

        new_link = TopologyLink(source_area, target_area, source_node, target_node, medium_node)
        if new_link not in self.links:
            self.links.append(new_link)
            return True
        return False

    def get_neighbors(self, source_area: TopologyArea) -> Dict[TopologyArea, List[TopologyNode]]:
        neighbors = {}
        for link in self.get_links_from_area(source_area):
            if link.source_area == source_area:
                neighbors.setdefault(link.target_area, []).append(link.target_node)
        return neighbors

    def get_links_from_area(self, area: TopologyArea) -> List[TopologyLink]:
        area_links = []
        for link in self.links:
            if link.source_area.name == area.name:
                area_links.append(link)
        return area_links

    def to_json(self):
        final_dict = {}
        for area in self.areas:
            for node in area.nodes:
                node_neighbors = area.get_neighbors(node)
                final_dict.setdefault(area.name, {})[node.name] = set(map(lambda node: node.name, node_neighbors))

        final_dict["area_links"] = {}
        for area in self.areas:
            for link in self.get_links_from_area(area):
                if link.medium_node:
                    final_dict["area_links"].setdefault(area.name, {}).setdefault(link.source_node.name, []).append(
                        link.medium_node.name
                    )
                    final_dict["area_links"].setdefault(area.name, {}).setdefault(link.medium_node.name, []).append(
                        link.target_node.name
                    )
                else:
                    final_dict["area_links"].setdefault(area.name, {}).setdefault(link.source_node.name, []).append(
                        link.target_node.name
                    )

        return final_dict


class TopologyGenerator:
    def __init__(self) -> None:
        self.graph = nx.Graph()

    def show_from_dict(self, graph_dict):
        graph = nx.Graph()
        for area_name, area_dict in graph_dict.items():
            if area_name == "area_links":
                continue
            for node_name, node_neighbors in area_dict.items():
                graph.add_node(node_name)
                for neighbor in node_neighbors:
                    graph.add_edge(node_name, neighbor)

        for area_name, area_links in graph_dict["area_links"].items():
            for source_node, target_nodes in area_links.items():
                for target_node in target_nodes:
                    graph.add_edge(source_node, target_node)

        color_save = {}
        colors = []
        for node in graph.nodes:
            colors.append(color_save.setdefault(node[0], [random.random(), random.random(), random.random()]))

        plt.figure(figsize=(10, 10))
        nx.draw(graph, node_color=colors, with_labels=True, font_size=18, width=2, node_size=800)
        plt.show()

    def deploy(self, interface: HyperInterface, topology: GlobalTopology):
        for area in topology.areas:
            for node in area.nodes:
                print(node)
                interface.create_vpcs(node.name)
            interface.create_switch(area.central_node.name)

        for medium_node in topology.medium_nodes:
            interface.create_router(medium_node.name)

        for area in topology.areas:
            for link in area.links:
                interface.create_link(link.source.name, link.target.name)

        for area_link in topology.links:
            if area_link.medium_node:
                interface.create_link(area_link.source_node.name, area_link.medium_node.name)
                interface.create_link(area_link.medium_node.name, area_link.target_node.name)
            else:
                interface.create_link(area_link.source_node.name, area_link.target_node.name)


def main():
    topo = GlobalTopology()
    area_a = topo.create_area("A")
    a1 = area_a.create_node("A1")
    a2 = area_a.create_node("A2")
    a3 = area_a.create_node("A3")
    a4 = area_a.create_node("A4")

    # a1a2 = area_a.create_link(a1, a2)
    # a1a3 = area_a.create_link(a1, a3)
    # a1a4 = area_a.create_link(a1, a4)

    area_b = topo.create_area("B")
    b1 = area_b.create_node("B1")
    b2 = area_b.create_node("B2")
    b3 = area_b.create_node("B3")
    b4 = area_b.create_node("B4")

    area_c = topo.create_area("C")
    c1 = area_c.create_node("C1")
    c2 = area_c.create_node("C2")
    c3 = area_c.create_node("C3")
    c4 = area_c.create_node("C4")

    # b1b2 = area_b.create_link(b1, b2)
    # b1b3 = area_b.create_link(b1, b3)
    # b1b4 = area_b.create_link(b1, b4)

    # area_b.create_link(b1, b2)
    # area_b.create_link(b1, b3)
    # area_b.create_link(b1, b4)

    topo.create_link(area_a, area_b)
    topo.create_link(area_a, area_c)
    topo.create_link(area_b, area_c, create_medium_node=False)

    connector = GNS3Connector("http://localhost:3080", "gns3", "gns3")
    interface = HyperInterface(connector)

    TopologyGenerator().deploy(interface, topo)

    return

    data = topo.to_json()
    TopologyGenerator().show_from_dict(data)


if __name__ == "__main__":
    main()
