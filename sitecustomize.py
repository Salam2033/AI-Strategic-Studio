"""Runtime compatibility shim for Render environment-variable naming.

The current Render service has an accidentally concatenated OpenAI key variable
name (OPENAI_API_KEYOPENAI_API_KEY). Normalize it before the application loads,
without exposing or logging the secret value. The normal OPENAI_API_KEY remains
preferred when it is already configured.
"""
import os

if not os.environ.get("OPENAI_API_KEY", "").strip():
    for legacy_name in ("OPENAI_API_KEYOPENAI_API_KEY",):
        value = os.environ.get(legacy_name, "").strip()
        if value:
            os.environ["OPENAI_API_KEY"] = value
            break
