from datetime import timedelta
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient
import boto3
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ssm = boto3.client("ssm")
agentcore_client = boto3.client("bedrock-agentcore")

GATEWAY_PROVIDER_NAME = os.getenv("GATEWAY_PROVIDER_NAME")


def get_gateway_url() -> str:
    """Read the AgentCore Gateway URL from SSM Parameter Store.

    Returns:
        str: Value of the ``/monitoragent/agentcore/gateway/gateway_url``
            parameter.

    Raises:
        botocore.exceptions.ClientError: If the parameter cannot be read, for
            example when it does not exist or the caller lacks permission.
    """

    response = ssm.get_parameter(Name="/monitoragent/agentcore/gateway/gateway_url", WithDecryption=True)
    logger.info("Gateway URL loaded from SSM")
    return response["Parameter"]["Value"]


def create_gateway_client(workload_token: str) -> MCPClient:
    """Create an MCP client for the AgentCore Gateway using OAuth2 (M2M).

    The workload access token is exchanged for a gateway access token through the
    credential provider named by the ``GATEWAY_PROVIDER_NAME`` environment
    variable, and the token is attached as a bearer token to every MCP request.

    Args:
        workload_token: AgentCore workload identity token of the caller.

    Returns:
        MCPClient: A client configured for the gateway URL stored in SSM. The
            caller is responsible for starting it.

    Raises:
        botocore.exceptions.ClientError: If the OAuth2 token exchange or the SSM
            lookup fails.
    """
    # Get OAuth2 access token for gateway
    response = agentcore_client.get_resource_oauth2_token(
        workloadIdentityToken=workload_token,
        resourceCredentialProviderName=GATEWAY_PROVIDER_NAME,
        scopes=[],
        oauth2Flow="M2M",
        forceAuthentication=False,
    )

    gateway_access_token = response["accessToken"]
    gateway_url = get_gateway_url()

    logger.info("Gateway access token obtained")
    return MCPClient(
        lambda: streamablehttp_client(
            url=gateway_url,
            headers={"Authorization": f"Bearer {gateway_access_token}"},
            timeout=timedelta(seconds=120),
        )
    )
