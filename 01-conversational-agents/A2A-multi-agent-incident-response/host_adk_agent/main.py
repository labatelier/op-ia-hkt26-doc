import logging
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from bedrock_agentcore import BedrockAgentCoreApp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

APP_NAME = "HostAgentA2A"

app = BedrockAgentCoreApp()

session_service = InMemorySessionService()

root_agent = None


@app.entrypoint
async def call_agent(payload: dict, context):
    """AgentCore runtime entrypoint for the Google ADK host agent.

    On the first invocation the root agent is created and the agent cards of the
    remote A2A sub-agents are resolved and yielded as the first event, so the
    caller can display which agents are available. Every invocation then runs the
    user prompt through the ADK runner and yields the runner events as they are
    produced.

    Args:
        payload: Request body. Must contain a ``prompt`` key with the user query.
        context: AgentCore request context. ``context.session_id`` and the
            ``x-amzn-bedrock-agentcore-runtime-custom-actorid`` request header are
            both required.

    Yields:
        The agent cards mapping (first invocation only) followed by the ADK
        runner events for the current prompt.

    Raises:
        Exception: If the actor id or the session id is missing from the request.
        KeyError: If ``payload`` does not contain a ``prompt`` field.
    """
    global root_agent

    session_id = context.session_id
    logger.info(f"Received request with session_id: {session_id}")

    actor_id = context.request_headers["x-amzn-bedrock-agentcore-runtime-custom-actorid"]

    if not actor_id:
        raise Exception("Actor id is not is not set")

    if not session_id:
        raise Exception("Context session_id is not set")

    if not root_agent:
        # Import agent creation inside entrypoint so workload identity is available
        from agent import get_agent_and_card

        logger.info("Initializing root agent and resolving agent cards...")
        # Create root agent once - LazyClientFactory creates fresh httpx clients
        # on each A2A invocation in the current event loop context
        try:
            root_agent, agents_cards = await get_agent_and_card(session_id=session_id, actor_id=actor_id)
            logger.info(f"Successfully initialized root agent. Agent cards: {list(agents_cards.keys())}")
        except Exception as e:
            logger.error(f"Failed to initialize root agent: {e}", exc_info=True)
            raise

        yield agents_cards

    query = payload.get("prompt")
    logger.info(f"Processing query: {query}")

    if not query:
        raise KeyError("'prompt' field is required in payload")

    in_memory_session = session_service.get_session_sync(app_name=APP_NAME, user_id=actor_id, session_id=session_id)

    if not in_memory_session:
        # Session doesn't exist, create it
        _ = session_service.create_session_sync(app_name=APP_NAME, user_id=actor_id, session_id=session_id)

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=query)])

    # Use async run to properly maintain event loop across invocations
    async for event in runner.run_async(user_id=actor_id, session_id=session_id, new_message=content):
        yield event


if __name__ == "__main__":
    app.run()  # Ready to run on Bedrock AgentCore
