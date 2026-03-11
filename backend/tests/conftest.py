import os

# Force mock mode for all tests
os.environ["MOCK_MODE"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
