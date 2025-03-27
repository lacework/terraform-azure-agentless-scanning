
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
from msgraph import GraphServiceClient


class AzureClientFactory:
    """Factory for Azure clients"""

    credential: DefaultAzureCredential
    principal_id: str
    _subscription_client: SubscriptionClient
    _graph_client: GraphServiceClient
    _network_clients: dict[str, NetworkManagementClient] = {}
    _compute_clients: dict[str, ComputeManagementClient] = {}
    _auth_clients: dict[str, AuthorizationManagementClient] = {}

    def __init__(self, credential: DefaultAzureCredential) -> None:
        self.credential = credential
        self._subscription_client = SubscriptionClient(credential)
        self._graph_client = GraphServiceClient(credential)

    def get_subscription_client(self) -> SubscriptionClient:
        return self._subscription_client

    def get_compute_client(self, subscription_id: str) -> ComputeManagementClient:
        if subscription_id not in self._compute_clients:
            self._compute_clients[subscription_id] = ComputeManagementClient(
                self.credential, subscription_id)
        return self._compute_clients[subscription_id]

    def get_network_client(self, subscription_id: str) -> NetworkManagementClient:
        if subscription_id not in self._network_clients:
            self._network_clients[subscription_id] = NetworkManagementClient(
                self.credential, subscription_id)
        return self._network_clients[subscription_id]

    def get_auth_client(self, subscription_id: str) -> AuthorizationManagementClient:
        if subscription_id not in self._auth_clients:
            self._auth_clients[subscription_id] = AuthorizationManagementClient(
                self.credential, subscription_id)
        return self._auth_clients[subscription_id]

    def get_graph_client(self) -> GraphServiceClient:
        return self._graph_client
