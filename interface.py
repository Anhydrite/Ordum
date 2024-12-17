from gns3_connector import GNS3Connector


class HyperInterface:
    def __init__(self, connector: GNS3Connector) -> None:
        self.connector: GNS3Connector = connector

    def create_switch(self, name: str):
        self.connector.create_switch(name)

    def create_vpcs(self, name: str):
        self.connector.create_vpcs(name)

    def create_router(self, router_name: str):
        self.connector.create_router(router_name)

    def create_link(self, first_node_name: str, second_node_name: str):
        try:
            print(f"Je crée entre {first_node_name} et {second_node_name}")
            first_node_port = self.connector.get_free_port_for_node(self.connector.project_id, first_node_name)
            second_node_port = self.connector.get_free_port_for_node(self.connector.project_id, second_node_name)
            self.connector.create_link(first_node_name, second_node_name, first_node_port, second_node_port)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    connector = GNS3Connector("http://localhost:3080", "gns3", "gns3")
    interface = HyperInterface(connector)
