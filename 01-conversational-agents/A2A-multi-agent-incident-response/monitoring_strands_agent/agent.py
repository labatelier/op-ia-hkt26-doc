from bedrock_agentcore.memory import MemoryClient
from memory_hook import MonitoringMemoryHooks
from prompt import SYSTEM_PROMPT
from strands import Agent
from strands.models import BedrockModel
from utils import create_gateway_client


class MonitoringAgent:
    """Strands agent that answers CloudWatch logs, metrics and dashboard questions.

    The agent is backed by an Amazon Bedrock model, uses AgentCore Memory hooks
    for short- and long-term context, and loads its tools from an AgentCore
    Gateway (MCP) target.

    Attributes:
        SUPPORTED_CONTENT_TYPES: Content types the A2A executor may send to this
            agent.
        agent: The underlying ``strands.Agent`` instance.
    """

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(
        self,
        memory_id: str,
        model_id: str,
        region_name: str,
        actor_id: str,
        session_id: str,
        workload_token: str,
    ):
        """Build the Strands agent together with its model, memory and tools.

        Args:
            memory_id: Identifier of the AgentCore Memory resource used to store
                and retrieve conversation context.
            model_id: Amazon Bedrock model identifier used by the agent.
            region_name: AWS region of the Bedrock model and the Memory resource.
            actor_id: Identifier of the end user, used as the memory actor and to
                resolve the long-term memory namespaces.
            session_id: Identifier of the current conversation session.
            workload_token: AgentCore workload access token used to obtain an
                OAuth2 token for the gateway.
        """
        bedrock_model = BedrockModel(model_id=model_id, region_name=region_name)
        memory_client = MemoryClient(region_name=region_name)

        monitoring_hooks = MonitoringMemoryHooks(
            memory_id=memory_id,
            client=memory_client,
            actor_id=actor_id,
            session_id=session_id,
        )

        self._gateway_client = create_gateway_client(workload_token)
        self._gateway_client.start()
        gateway_tools = self._gateway_client.list_tools_sync()

        self.agent = Agent(
            name="Monitoring Agent",
            description="A monitoring agent that handles CloudWatch logs, metrics, dashboards, and AWS service monitoring",
            system_prompt=SYSTEM_PROMPT,
            model=bedrock_model,
            tools=gateway_tools,
            hooks=[monitoring_hooks],
        )

    async def stream(self, query: str, session_id: str):
        """Stream the agent answer for a query as incremental updates.

        Text chunks produced by the model are forwarded one by one, and a final
        update carrying the complete response is always emitted last. Errors are
        not raised to the caller: they are reported as an update that asks for
        user input instead.

        Args:
            query: The user question to send to the agent.
            session_id: Identifier of the current conversation session. It is
                accepted for interface symmetry with ``invoke`` and is not used
                to reconfigure the agent.

        Yields:
            dict: An update with the keys ``is_task_complete`` (bool),
                ``require_user_input`` (bool) and ``content`` (str). Intermediate
                updates contain a single text chunk, the final update contains
                the accumulated response.
        """
        response = str()
        try:
            async for event in self.agent.stream_async(query):
                if "data" in event:
                    # Only stream text chunks to the client
                    response += event["data"]
                    yield {
                        "is_task_complete": "complete" in event,
                        "require_user_input": False,
                        "content": event["data"],
                    }

        except Exception as e:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"We are unable to process your request at the moment. Error: {e}",
            }
        finally:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
            }

    def invoke(self, query: str, session_id: str):
        """Run the agent synchronously and return the complete answer.

        Args:
            query: The user question to send to the agent.
            session_id: Identifier of the current conversation session. It is
                accepted for interface symmetry with ``stream`` and is not used
                to reconfigure the agent.

        Returns:
            str: The agent response as plain text.

        Raises:
            TypeError: If the underlying agent call fails. The failure branch
                raises a formatted string instead of an exception instance,
                which Python rejects with a ``TypeError``.
        """
        try:
            response = str(self.agent(query))

        except Exception as e:
            raise f"Error invoking agent: {e}"
        return response
