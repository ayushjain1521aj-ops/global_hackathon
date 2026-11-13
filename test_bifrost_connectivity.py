"""
Connectivity & Functionality Test for Bifrost Client
Verifies health check, fallback labeling, and completion mechanics.
"""

from bifrost.client import get_bifrost_client

def test_gateway():
    print("Testing Bifrost LLM Gateway Client...")
    client = get_bifrost_client()

    print(f"Base URL: {client.config.base_url}")
    print(f"Model: {client.config.model}")
    print(f"Demo Mode: {client.config.demo_mode}")

    # Health check
    health = client.check_gateway_health()
    print("\n--- Bifrost Gateway Health Check ---")
    print(f"Online: {health['online']}")
    print(f"Status: {health['status']}")
    print(f"Message: {health['message']}")
    print(f"Is Simulated: {health.get('is_simulated', False)}")

    # Test Completion Request
    messages = [
        {"role": "system", "content": "You are a concise code assistant."},
        {"role": "user", "content": "Write a Python calculator"}
    ]
    content, meta = client.chat_completion(messages)
    print("\n--- Completion Response Metadata ---")
    print(f"Request ID: {meta['request_id']}")
    print(f"Model: {meta['model']}")
    print(f"Prompt Tokens: {meta['prompt_tokens']}")
    print(f"Completion Tokens: {meta['completion_tokens']}")
    print(f"Total Tokens: {meta['total_tokens']}")
    print(f"Is Simulated: {meta['is_simulated']}")
    print(f"Latency: {meta['latency_ms']} ms")

    print("\n--- First 150 chars of Generated Code ---")
    print(content[:150].strip())
    print("...\nBifrost client verification complete!")

if __name__ == "__main__":
    test_gateway()
