"""
OpenClaw Deployment UI — Flask Web Server

Serves the wizard UI and orchestrates cloud VM deployment through the
cloud_deployer MCP server using the Model Context Protocol.
"""

import asyncio
import json
import os
import sys
import threading
import uuid
from contextlib import AsyncExitStack
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CLOUD_DEPLOYER = ROOT / "mcp_servers" / "cloud_deployer.py"

app = Flask(__name__)
CORS(app)

# In-memory job store: job_id -> status dict
jobs: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# MCP Client helper
# ---------------------------------------------------------------------------
class CloudMCPClient:
    """Thin async client that wraps the cloud_deployer MCP server."""

    def __init__(self):
        self._exit_stack = AsyncExitStack()
        self._session: ClientSession | None = None

    async def connect(self):
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(CLOUD_DEPLOYER)],
        )
        transport = await self._exit_stack.enter_async_context(stdio_client(params))
        read, write = transport
        self._session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()

    async def call(self, tool_name: str, arguments: dict) -> dict:
        if self._session is None:
            raise RuntimeError("Not connected to MCP server")
        result = await self._session.call_tool(tool_name, arguments=arguments)
        if result.isError:
            return {"error": str(result.content)}
        # MCP TextContent → parse JSON
        for item in result.content:
            if item.type == "text":
                try:
                    return json.loads(item.text)
                except json.JSONDecodeError:
                    return {"raw": item.text}
        return {}

    async def close(self):
        await self._exit_stack.aclose()


# ---------------------------------------------------------------------------
# Background deployment runner
# ---------------------------------------------------------------------------
def _run_deployment(job_id: str, config: dict):
    """Runs in a background thread; connects to the MCP server and deploys."""

    def log(msg: str):
        jobs[job_id]["logs"].append(msg)

    def set_phase(phase: str):
        jobs[job_id]["phase"] = phase

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = CloudMCPClient()

    async def deploy():
        try:
            log("Connecting to cloud deployment service…")
            await client.connect()
            log("Connected.")

            provider = config["provider"]
            creds = config["credentials"]
            region = config["region"]
            vm_size = config["vm_size"]
            vm_name = config["vm_name"]
            api_key = config.get("openclaw_api_key", "")
            base_url = config.get("openclaw_base_url", "")
            model = config.get("openclaw_model", "")

            # ── Step 1: Validate credentials ──────────────────────────────
            set_phase("Validating credentials")
            log(f"Validating your {provider.upper()} credentials…")
            val = await client.call("validate_credentials", {"provider": provider, "credentials": creds})
            if not val.get("valid", False):
                raise RuntimeError(f"Credential validation failed: {val.get('message', 'Unknown error')}")
            log(f"✓ {val.get('message', 'Credentials OK')}")

            # ── Step 2: Launch VM ──────────────────────────────────────────
            set_phase("Launching VM")
            log(f"Launching a '{vm_size}' VM in {region}…")
            deploy_result = await client.call("deploy_vm", {
                "provider": provider,
                "region": region,
                "vm_size": vm_size,
                "vm_name": vm_name,
                "credentials": creds,
                "openclaw_api_key": api_key,
                "openclaw_base_url": base_url,
                "openclaw_model": model,
            })

            if not deploy_result.get("success"):
                raise RuntimeError(f"VM deployment failed: {deploy_result.get('error', 'Unknown error')}")

            vm_id = deploy_result["vm_id"]
            public_ip = deploy_result.get("public_ip", "Pending")
            ssh_user = deploy_result.get("ssh_user", "ubuntu")
            private_key = deploy_result.get("private_key")
            log(f"✓ VM launched! ID: {vm_id}")
            log(f"  Public IP: {public_ip}")

            # ── Step 3: Wait for VM to be reachable ───────────────────────
            set_phase("Installing OpenClaw")
            log("OpenClaw is installing on your VM (this takes ~5 minutes)…")
            log("  The installation script will:")
            log("  • Install Python 3, Node.js, git")
            log("  • Clone the OpenClaw repository")
            log("  • Set up your API key")
            log("  • Register OpenClaw as a system service")

            # Poll for final IP (especially useful for DigitalOcean / AWS)
            if provider in ("aws", "digitalocean") and ("Pending" in public_ip or not public_ip):
                log("Waiting for public IP assignment…")
                for attempt in range(12):
                    await asyncio.sleep(10)
                    status = await client.call("get_vm_status", {
                        "provider": provider,
                        "vm_id": vm_id,
                        "region": region,
                        "credentials": creds,
                    })
                    public_ip = status.get("public_ip", "")
                    if public_ip and "Pending" not in public_ip and "Not yet" not in public_ip:
                        log(f"✓ Public IP assigned: {public_ip}")
                        break
                    log(f"  Still waiting… ({(attempt + 1) * 10}s elapsed)")

            # ── Step 4: Done ───────────────────────────────────────────────
            set_phase("complete")
            log("✓ Deployment complete!")

            jobs[job_id].update({
                "status": "complete",
                "vm_id": vm_id,
                "public_ip": public_ip,
                "ssh_user": ssh_user,
                "ssh_key": private_key,
                "provider": provider,
                "region": region,
                "vm_name": vm_name,
                "ssh_command": (
                    f"ssh {ssh_user}@{public_ip}" if "Pending" not in str(public_ip) else "Available once IP is assigned"
                ),
            })

        except Exception as exc:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(exc)
            log(f"✗ Error: {exc}")
        finally:
            await client.close()

    try:
        loop.run_until_complete(deploy())
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/regions")
def api_regions():
    provider = request.args.get("provider", "aws")

    async def _get():
        c = CloudMCPClient()
        try:
            await c.connect()
            return await c.call("list_regions", {"provider": provider})
        finally:
            await c.close()

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_get())
    finally:
        loop.close()
    return jsonify(result)


@app.route("/api/vm-sizes")
def api_vm_sizes():
    provider = request.args.get("provider", "aws")

    async def _get():
        c = CloudMCPClient()
        try:
            await c.connect()
            return await c.call("list_vm_sizes", {"provider": provider})
        finally:
            await c.close()

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_get())
    finally:
        loop.close()
    return jsonify(result)


@app.route("/api/validate-credentials", methods=["POST"])
def api_validate_credentials():
    body = request.get_json(force=True)
    provider = body.get("provider")
    credentials = body.get("credentials", {})

    async def _validate():
        c = CloudMCPClient()
        try:
            await c.connect()
            return await c.call("validate_credentials", {"provider": provider, "credentials": credentials})
        finally:
            await c.close()

    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_validate())
    finally:
        loop.close()
    return jsonify(result)


@app.route("/api/deploy", methods=["POST"])
def api_deploy():
    config = request.get_json(force=True)
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "running",
        "phase": "Starting",
        "logs": [],
        "error": None,
    }

    thread = threading.Thread(target=_run_deployment, args=(job_id, config), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/deploy-status/<job_id>")
def api_deploy_status(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  OpenClaw Deployment UI is running!")
    print(f"  Open your browser at: http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
