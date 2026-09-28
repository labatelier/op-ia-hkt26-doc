"""Shared utilities for agent scripts"""

import json
import boto3
import requests
from boto3.session import Session
import sys
from typing import Any, Optional, Tuple
import urllib
from urllib.parse import quote
from bedrock_agentcore.identity.auth import requires_access_token


def get_ssm_parameter(name: str, with_decryption: bool = True) -> str:
    """Get parameter from AWS Systems Manager Parameter Store.

    Args:
        name: Full name of the parameter, for example
            ``/monitoragent/agentcore/runtime-id``.
        with_decryption: Whether SecureString values should be decrypted.

    Returns:
        str: The parameter value.

    Raises:
        botocore.exceptions.ClientError: If the parameter does not exist or the
            caller is not allowed to read it.
    """
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
    return response["Parameter"]["Value"]


def get_aws_info():
    """Get AWS account ID and region from boto3 session.

    Returns:
        tuple: An ``(account_id, region)`` pair of strings.

    Raises:
        SystemExit: If the region cannot be determined or the STS call fails. The
            error is printed and the process exits with status 1.
    """
    try:
        boto_session = Session()

        # Get region
        region = boto_session.region_name
        if not region:
            # Try to get from default session
            region = boto3.DEFAULT_SESSION.region_name if boto3.DEFAULT_SESSION else None
            if not region:
                raise ValueError("AWS region not configured. Please set AWS_DEFAULT_REGION or configure AWS CLI.")

        # Get account ID using STS
        sts = boto_session.client("sts")
        account_id = sts.get_caller_identity()["Account"]

        return account_id, region

    except Exception as e:
        print(f"❌ Error getting AWS info: {e}")
        print("Please ensure AWS credentials are configured (aws configure or environment variables)")
        sys.exit(1)


def invoke_endpoint(
    agent_arn: str,
    payload,
    session_id: str,
    bearer_token: Optional[str],
    endpoint_name: str = "DEFAULT",
    stream: bool = True,
) -> Any:
    """Invoke AgentCore runtime endpoint

    The response is printed to stdout as it arrives: in streaming mode the text
    deltas of ``contentBlockDelta`` events are printed incrementally, otherwise
    the whole body is printed at once. Nothing is returned.

    Args:
        agent_arn: ARN of the AgentCore runtime to invoke.
        payload: Request body. A JSON string is parsed, any other value is sent as
            is, and a non-JSON string is wrapped as ``{"payload": <string>}``.
        session_id: Value of the
            ``X-Amzn-Bedrock-AgentCore-Runtime-Session-Id`` header.
        bearer_token: OAuth2 access token used in the ``Authorization`` header.
        endpoint_name: Runtime endpoint qualifier to call.
        stream: Whether to consume the response as a stream of events.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
        SystemExit: Propagated from :func:`get_aws_info` when AWS configuration is
            missing.
    """
    escaped_arn = urllib.parse.quote(agent_arn, safe="")

    _, region = get_aws_info()

    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{escaped_arn}/invocations"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
    }

    try:
        body = json.loads(payload) if isinstance(payload, str) else payload
    except json.JSONDecodeError:
        body = {"payload": payload}

    response = requests.post(
        url,
        params={"qualifier": endpoint_name},
        headers=headers,
        json=body,
        timeout=100,
        stream=stream,
    )

    if not stream:
        print(
            response.content.decode("utf-8").replace("\\n", "\n").replace('"', ""),
            flush=True,
        )
    else:
        last_data = False

        for line in response.iter_lines(chunk_size=1):
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    last_data = True
                    data_content = line[6:]
                    parsed = json.loads(data_content)

                    # Check for event structure with contentBlockDelta
                    if isinstance(parsed, dict) and "event" in parsed:
                        event = parsed["event"]
                        if isinstance(event, dict) and "contentBlockDelta" in event:
                            delta = event["contentBlockDelta"].get("delta", {})
                            if "text" in delta:
                                text = delta["text"]
                                # Replace literal \n with actual newlines
                                text = text.replace("\\n", "\n")
                                print(text, end="", flush=True)
                elif line:
                    if last_data:
                        parsed = json.loads(line)
                        # Check for event structure with contentBlockDelta
                        if isinstance(parsed, dict) and "event" in parsed:
                            event = parsed["event"]
                            if isinstance(event, dict) and "contentBlockDelta" in event:
                                delta = event["contentBlockDelta"].get("delta", {})
                                if "text" in delta:
                                    text = delta["text"]
                                    # Replace literal \n with actual newlines
                                    text = text.replace("\\n", "\n")
                                    print(text, end="", flush=True)
                    last_data = False


def get_m2m_token_for_agent(ssm_prefix: str) -> Tuple[str, str]:
    """
    Get M2M bearer token for an agent using bedrock_agentcore.identity.auth.

    Args:
        ssm_prefix: SSM parameter prefix (e.g., '/websearchagent' or '/monitoragent')

    Returns:
        Tuple[str, str]: (access_token, agent_card_url)

    Raises:
        SystemExit: If the SSM lookups or the token request fail. The error is
            printed to stderr and the process exits with status 1.
    """
    try:
        # Get provider name from SSM
        provider_name = get_ssm_parameter(f"{ssm_prefix}/agentcore/provider-name")

        # Get agent runtime ID from SSM
        agent_id = get_ssm_parameter(f"{ssm_prefix}/agentcore/runtime-id")

        # Get AWS info
        account_id, region = get_aws_info()

        # Construct agent ARN
        agent_arn = f"arn:aws:bedrock-agentcore:{region}:{account_id}:runtime/{agent_id}"

        # Construct agent card URL
        escaped_agent_arn = quote(agent_arn, safe="")
        agent_card_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{escaped_agent_arn}/invocations/.well-known/agent-card.json"

        # Get token using decorator pattern
        @requires_access_token(
            provider_name=provider_name,
            scopes=[],
            auth_flow="M2M",
            into="bearer_token",
            force_authentication=True,
        )
        def _get_token_with_auth(bearer_token: str = str()) -> str:
            return bearer_token

        access_token = _get_token_with_auth()
        return access_token, agent_card_url

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
