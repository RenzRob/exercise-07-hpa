import random
import string
from locust import HttpUser, task, between


class NodeRegistryUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.node_names = []

    @task(4)
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def list_nodes(self):
        self.client.get("/api/nodes")

    @task(2)
    def register_node(self):
        name = "node-" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )
        with self.client.post(
            "/api/nodes",
            json={"name": name, "host": "192.168.1.100", "port": 8080},
            catch_response=True,
        ) as resp:
            if resp.status_code in (201, 409):
                resp.success()
                if resp.status_code == 201:
                    self.node_names.append(name)

    @task(1)
    def get_node(self):
        if self.node_names:
            name = random.choice(self.node_names)
            with self.client.get(
                f"/api/nodes/{name}", catch_response=True
            ) as resp:
                if resp.status_code in (200, 404):
                    resp.success()