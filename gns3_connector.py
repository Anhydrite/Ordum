from pprint import pprint
from sqlite3 import connect
from typing import Dict, List, Optional
from numpy import full
import requests

from data_structure.computes import ComputeInput, ComputeOutput, ComputesResponse
from data_structure.links import LinkNode, LinkRequest, LinkResponse, LinksResponse
from data_structure.nodes import Node, NodesResponse, Port
from data_structure.projects import LoadProjectResponse, Project, ProjectsResponse
from data_structure.templates import Template, TemplatesResponse


class GNS3Connector:

    vpcs_symbol_path = ":/symbols/vpcs_guest.svg"
    ethernet_switch_symbol_path = ":/symbols/ethernet_switch.svg"
    router_symbol_path: str = ":/symbols/classic/router.svg"

    def __init__(self, url, username, password, project_name="untitled"):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.project_id = self.load_project(project_name).project_id
        self.compute_id = self.get_computes().computes[0].compute_id

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        # print(response.content)
        try:
            response.raise_for_status()
        except Exception as e:
            print(f"Warning: {str(e)}")
        return response.json()

    # Appliance Endpoints
    def get_appliances(self):
        return self._make_request("GET", "/v2/appliances")

    def get_compute(self, compute_id):
        return self._make_request("GET", f"/v2/computes/{compute_id}")

    # Drawing Endpoints
    def get_drawings(self, project_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/drawings")

    def get_drawing(self, project_id, drawing_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/drawings/{drawing_id}")

    # GNS3 VM Endpoints
    def get_gns3_vm(self):
        return self._make_request("GET", "/v2/gns3vm")

    def get_gns3_vm_engines(self):
        return self._make_request("GET", "/v2/gns3vm/engines")

    # Link Endpoints
    def get_all_links(self, project_id: str) -> LinksResponse:
        data = self._make_request("GET", f"/v2/projects/{project_id}/links")
        return LinksResponse(links=[LinkResponse(**link) for link in data])

    def get_link(self, project_id, link_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/links/{link_id}")

    # Project Endpoints
    def get_projects(self):
        data = self._make_request("GET", "/v2/projects")
        print(data)
        return ProjectsResponse(projects=[Project(**project) for project in data])

    def get_project(self, project_id):
        return self._make_request("GET", f"/v2/projects/{project_id}")

    # Server Endpoints
    def get_version(self):
        return self._make_request("GET", "/v2/version")

    def shutdown_server(self):
        return self._make_request("POST", "/v2/shutdown")

    # Snapshot Endpoints
    def get_snapshots(self, project_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/snapshots")

    def restore_snapshot(self, project_id, snapshot_id):
        return self._make_request("POST", f"/v2/projects/{project_id}/snapshots/{snapshot_id}/restore")

    # Template Endpoints
    def get_templates(self):
        data = self._make_request("GET", "/v2/templates")
        return TemplatesResponse(templates=[Template(**template) for template in data])

    def get_template(self, template_id):
        return self._make_request("GET", f"/v2/templates/{template_id}")

    # /v2/projects/load¶
    def load_project(self, project_name):
        projects = self.get_projects()
        full_path = None
        for project in projects.projects:
            if project_name in project.name:
                print(project.name)
                full_path = f"{project.path}/{project.name}.gns3"
                break
        if not full_path:
            raise ValueError(f"Project {project_name} not found")

        data = self._make_request("POST", "/v2/projects/load", json={"path": full_path})
        return LoadProjectResponse(**data)

    def create_node(self, project_id: str, compute_id, node_name: str, node_type: str, symbol: str) -> Node:
        #  cloud, nat, ethernet_hub, ethernet_switch, frame_relay_switch, atm_switch, docker, dynamips, vpcs, traceng, virtualbox, vmware, iou, qemu
        data = self._make_request(
            "POST",
            f"/v2/projects/{project_id}/nodes",
            json={"name": node_name, "symbol": symbol, "node_type": node_type, "compute_id": compute_id},
        )
        return Node(**data)

    def get_nodes(self, project_id: str) -> List[Node]:
        data = self._make_request("GET", f"/v2/projects/{project_id}/nodes")
        return NodesResponse(nodes=[Node(**node) for node in data]).nodes

    def get_node(self, project_id: str, node_id: str) -> Node:
        data = self._make_request("GET", f"/v2/projects/{project_id}/nodes/{node_id}")
        return Node(**data)

    def get_node_by_name(self, node_name: str):
        nodes = self.get_nodes(self.project_id)
        for node in nodes:
            if node.name == node_name:
                return node
        return None

    def register_compute(self, compute_data: ComputeInput) -> ComputeOutput:
        data = self._make_request("POST", "/v2/computes", json=compute_data.model_dump())
        return ComputeOutput(**data)

    def get_computes(self) -> ComputesResponse:
        data = self._make_request("GET", "/v2/computes")
        return ComputesResponse(computes=[ComputeOutput(**compute) for compute in data])

    def create_switch(self, name: str) -> Node:
        return self.create_node(
            self.project_id, self.compute_id, name, "ethernet_switch", GNS3Connector.ethernet_switch_symbol_path
        )

    def create_vpcs(self, name: str) -> Node:
        return self.create_node(self.project_id, self.compute_id, name, "vpcs", GNS3Connector.vpcs_symbol_path)

    def create_link(
        self, first_node_name: str, second_node_name: str, first_node_port: LinkNode, second_node_port: LinkNode
    ) -> LinkResponse | Dict:
        nodes_request: List[LinkNode] = []
        node = self.get_node_by_name(first_node_name)
        if not node:
            raise ValueError(f"Must have a node but {first_node_name} didn't match any known node.")
        nodes_request.append(
            LinkNode(
                **{
                    "node_id": node.node_id,
                    "adapter_number": first_node_port.adapter_number,
                    "port_number": first_node_port.port_number,
                }
            )
        )
        node = self.get_node_by_name(second_node_name)
        if not node:
            raise ValueError(f"Must have a node but {second_node_name} didn't match any known node.")
        nodes_request.append(
            LinkNode(
                **{
                    "node_id": node.node_id,
                    "adapter_number": second_node_port.adapter_number,
                    "port_number": second_node_port.port_number,
                }
            )
        )

        link_data = LinkRequest(nodes=nodes_request).model_dump()
        data = self._make_request("POST", f"/v2/projects/{self.project_id}/links", json=link_data)
        if data.get("message"):
            return data
        else:
            return LinkResponse(**data)

    def create_router(self, router_name: str):
        return self.create_node(
            self.project_id, self.compute_id, router_name, "ethernet_switch", GNS3Connector.router_symbol_path
        )

    def get_links_from_node(self, project_id: str, node_id: str) -> LinksResponse:
        data = self._make_request("GET", f"/v2/projects/{project_id}/links")
        links = [link for link in data if any(node["node_id"] == node_id for node in link["nodes"])]
        return LinksResponse(links=[LinkResponse(**link) for link in links])

    def get_free_port_for_node(self, project_id: str, node_name: str) -> Optional[Port]:
        node = self.get_node_by_name(node_name)
        # used_ports = {port["port_number"] for port in data["ports"]}
        # max_ports = data.get("port_segment_size", 16)  # Default maximum ports
        all_links = self.get_all_links(self.project_id)
        node_links: List[LinkNode] = []
        for link in all_links.links:
            for link_node in link.nodes:
                if link_node.node_id == node.node_id:
                    node_links.append(link_node)

        for port in node.ports:
            if not node_links:
                return port
            for node_link in node_links:
                if port.port_number == node_link.port_number and port.adapter_number == node_link.adapter_number:
                    break
            else:
                return port

        return None


def main():
    connector = GNS3Connector("http://localhost:3080", "gns3", "gns3")
    # connector.create_switch("centralA")

    a = connector.get_free_port_for_node(connector.project_id, "A-Central")
    print("tet", a)
    # connector.create_vpcs("A1")
    # connector.create_vpcs("A2")
    # connector.create_vpcs("A3")
    # connector.create_vpcs("A4")

    # connector.create_link("A1", "A2")

    # Création d'un switch
    # connector.create_node(project_id, compute_id, "test", "ethernet_switch", ":/symbols/ethernet_switch.svg")
    # # Création d'un vpc
    # connector.create_node(project_id, compute_id, "test", "vpcs", ":/symbols/vpcs_guest.svg")
    # a = connector.get_nodes(project_id)
    # pprint(a)


if __name__ == "__main__":
    main()
