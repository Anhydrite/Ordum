from typing import Dict, List
import networkx as nx
import matplotlib.pyplot as plt


class TopologyNode:
    def __init__(self, name: str, area: "TopologyArea"):
        self.area = area
        self.name = name
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


class TopologyLink:
    def __init__(
        self, source: "TopologyArea", target: "TopologyArea", source_node: TopologyNode, target_node: TopologyNode
    ):
        self.name = source.name + "-" + target.name
        self.source_area: TopologyArea = source
        self.target_area: TopologyArea = target
        self.source_node: TopologyNode = source_node
        self.target_node: TopologyNode = target_node


class TopologyArea:
    def __init__(self, global_topology: "GlobalTopology", name: str):
        self.global_topology = global_topology
        self.name = name
        self.nodes: List[TopologyNode] = []
        self.links: List[TopologyAreaInLink] = []

    def add_node(self, node: TopologyNode):
        if node not in self.nodes:
            self.nodes.append(node)
            return True

        return False

    def create_node(self, name: str):
        new_node = TopologyNode(name, self)
        if new_node not in self.nodes:
            self.nodes.append(new_node)
            return new_node
        raise ValueError(f"Node {name} already exists")

    def get_node(self, name: str):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def remove_node(self, node: TopologyNode):
        if node in self.nodes:
            self.nodes.remove(node)
            return True
        return False

    def add_link(self, link: TopologyAreaInLink):
        if link not in self.links:
            self.links.append(link)
            return True
        return False

    def create_link(self, source: TopologyNode, target: TopologyNode):
        new_link = TopologyAreaInLink(source, target)
        new_link2 = TopologyAreaInLink(target, source)
        if new_link not in self.links:
            self.add_link(new_link)
            self.add_link(new_link2)
            return new_link
        return None

    def remove_link(self, source: str, target: str):
        for link in self.links:
            if link.source == source and link.target == target:
                self.links.remove(link)
                return True
        return False

    def get_neighbors(self, node: TopologyNode):
        neighbors = []
        for link in self.links:
            if link.source == node:
                neighbors.append(link.target)
            elif link.target == node:
                neighbors.append(link.source)

        return neighbors


class GlobalTopology:
    def __init__(self):
        self.areas: List[TopologyArea] = []
        self.links: List[TopologyLink] = []

    def create_area(self, name: str):
        new_area = TopologyArea(self, name)
        if new_area not in self.areas:
            self.areas.append(new_area)
            return new_area
        raise ValueError(f"Area {name} already exists")

    def get_area(self, name: str):
        for area in self.areas:
            if area.name == name:
                return area
        return None

    def add_link(
        self,
        source_area: TopologyArea,
        target_area: TopologyArea,
        source_node: TopologyNode,
        target_node: TopologyNode,
    ):
        new_link = TopologyLink(source_area, target_area, source_node, target_node)
        new_link2 = TopologyLink(target_area, source_area, target_node, source_node)
        if new_link not in self.links:
            self.links.append(new_link)
            self.links.append(new_link2)
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
                final_dict["area_links"].setdefault(area.name, {}).setdefault(link.source_node.name, []).append(
                    link.target_node.name
                )
        return final_dict


class TopologyGenerator:
    def __init__(self) -> None:
        self.graph = nx.Graph()

    def generate(self):
        pass

    def show_from_dict(self, graph_dict):
        graph = nx.Graph()
        for area_name, area_dict in graph_dict.items():
            for node_name, node_neighbors in area_dict.items():
                graph.add_node(node_name)
                for neighbor in node_neighbors:
                    graph.add_edge(node_name, neighbor)

        for area_name, area_links in graph_dict["area_links"].items():
            for source_node, target_nodes in area_links.items():
                for target_node in target_nodes:
                    graph.add_edge(source_node, target_node)

        a = nx.draw(graph, with_labels=True)
        plt.show()


def main():
    topo = GlobalTopology()
    area_a = topo.create_area("A")
    a1 = area_a.create_node("A1")
    a2 = area_a.create_node("A2")
    a3 = area_a.create_node("A3")
    a4 = area_a.create_node("A4")

    a1a2 = area_a.create_link(a1, a2)
    a1a3 = area_a.create_link(a1, a3)
    a1a4 = area_a.create_link(a1, a4)

    area_b = topo.create_area("B")
    b1 = area_b.create_node("B1")
    b2 = area_b.create_node("B2")
    b3 = area_b.create_node("B3")
    b4 = area_b.create_node("B4")

    b1b2 = area_b.create_link(b1, b2)
    b1b3 = area_b.create_link(b1, b3)
    b1b4 = area_b.create_link(b1, b4)

    area_b.create_link(b1, b2)
    area_b.create_link(b1, b3)
    area_b.create_link(b1, b4)

    topo.add_link(area_a, area_b, a1, b1)

    data = topo.to_json()
    print(data)
    TopologyGenerator().show_from_dict(data)


if __name__ == "__main__":
    main()