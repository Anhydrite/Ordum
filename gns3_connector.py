from sqlite3 import connect
from numpy import full
import requests

from data_structure.computes import ComputeInput, ComputeOutput, ComputesResponse
from data_structure.nodes import Node, NodesResponse
from data_structure.projects import LoadProjectResponse, Project, ProjectsResponse
from data_structure.templates import Template, TemplatesResponse


class GNS3Connector:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        print(response.content)
        response.raise_for_status()
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
    def get_links(self, project_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/links")

    def get_link(self, project_id, link_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/links/{link_id}")

    def get_node(self, project_id, node_id):
        return self._make_request("GET", f"/v2/projects/{project_id}/nodes/{node_id}")

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

    def create_node(self, project_id: str, compute_id, node_name: str, node_type: str) -> Node:
        data = self._make_request(
            "POST",
            f"/v2/projects/{project_id}/nodes",
            json={"name": node_name, "node_type": node_type, "compute_id": compute_id},
        )
        return Node(**data)

    def get_nodes(self, project_id: str) -> NodesResponse:
        data = self._make_request("GET", f"/v2/projects/{project_id}/nodes")
        return NodesResponse(nodes=[Node(**node) for node in data])

    def register_compute(self, compute_data: ComputeInput) -> ComputeOutput:
        data = self._make_request("POST", "/v2/computes", json=compute_data.dict())
        return ComputeOutput(**data)

    def get_computes(self) -> ComputesResponse:
        data = self._make_request("GET", "/v2/computes")
        return ComputesResponse(computes=[ComputeOutput(**compute) for compute in data])


def main():
    connector = GNS3Connector("http://localhost:3080", "gns3", "gns3")
    project_id = connector.load_project("untitled").project_id
    compute_id = connector.get_computes().computes[0].compute_id
    connector.create_node(project_id, compute_id, "test", "vpcs")


if __name__ == "__main__":
    main()
