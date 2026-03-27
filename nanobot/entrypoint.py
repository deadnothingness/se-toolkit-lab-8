#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then launches `nanobot gateway`.
"""

import json
import os
import sys


def main():
    # Read the base config
    config_path = "/app/nanobot/config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    # Resolve LLM provider configuration from env vars
    llm_api_key = os.environ.get("LLM_API_KEY", "")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL", "")
    llm_api_model = os.environ.get("LLM_API_MODEL", "coder-model")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base_url:
        config["providers"]["custom"]["apiBase"] = llm_api_base_url
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model

    # Resolve gateway configuration
    gateway_address = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "0.0.0.0")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "18790")

    # Resolve webchat channel configuration
    webchat_address = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765")
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY", "")

    # Update webchat channel config
    if "channels" not in config:
        config["channels"] = {}
    config["channels"]["webchat"] = {
        "enabled": True,
        "allow_from": ["*"],
        "host": webchat_address,
        "port": int(webchat_port),
        "access_key": nanobot_access_key,
    }

    # Resolve MCP server configuration
    nanobot_lms_backend_url = os.environ.get(
        "NANOBOT_LMS_BACKEND_URL", "http://backend:8000"
    )
    nanobot_lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY", "")

    if "mcpServers" in config.get("tools", {}):
        if "lms" in config["tools"]["mcpServers"]:
            config["tools"]["mcpServers"]["lms"]["env"] = {
                "NANOBOT_LMS_BACKEND_URL": nanobot_lms_backend_url,
                "NANOBOT_LMS_API_KEY": nanobot_lms_api_key,
            }

    # Write the resolved config
    resolved_path = "/app/nanobot/config.resolved.json"
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Resolved config written to {resolved_path}", file=sys.stderr)

    # Launch nanobot gateway
    workspace = "/app/nanobot/workspace"
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            resolved_path,
            "--workspace",
            workspace,
        ],
    )


if __name__ == "__main__":
    main()
