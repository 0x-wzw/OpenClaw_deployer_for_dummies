"""
OpenClaw Cloud Deployer — MCP Server
Provides tools for deploying VMs on AWS, GCP, Azure, and DigitalOcean,
and for installing OpenClaw on those VMs automatically.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

app = Server("openclaw-cloud-deployer")

# ---------------------------------------------------------------------------
# VM Size Presets  (small / medium / large — provider-specific instance types)
# ---------------------------------------------------------------------------
VM_SIZES = {
    "small": {
        "aws": "t3.medium",
        "gcp": "e2-standard-2",
        "azure": "Standard_B2s",
        "digitalocean": "s-2vcpu-2gb",
        "label": "Small",
        "description": "2 vCPU · 4 GB RAM — great for testing",
        "monthly_cost": "~$30–40 / month",
    },
    "medium": {
        "aws": "t3.large",
        "gcp": "e2-standard-4",
        "azure": "Standard_B4ms",
        "digitalocean": "s-4vcpu-8gb",
        "label": "Medium (Recommended)",
        "description": "4 vCPU · 8 GB RAM — ideal for most use-cases",
        "monthly_cost": "~$60–80 / month",
    },
    "large": {
        "aws": "t3.xlarge",
        "gcp": "e2-standard-8",
        "azure": "Standard_D4s_v3",
        "digitalocean": "s-8vcpu-16gb",
        "label": "Large",
        "description": "8 vCPU · 16 GB RAM — heavy workloads",
        "monthly_cost": "~$120–160 / month",
    },
}

REGIONS = {
    "aws": [
        {"id": "us-east-1", "name": "US East (N. Virginia)"},
        {"id": "us-west-2", "name": "US West (Oregon)"},
        {"id": "eu-west-1", "name": "Europe (Ireland)"},
        {"id": "ap-southeast-1", "name": "Asia Pacific (Singapore)"},
        {"id": "ap-northeast-1", "name": "Asia Pacific (Tokyo)"},
        {"id": "sa-east-1", "name": "South America (São Paulo)"},
    ],
    "gcp": [
        {"id": "us-central1", "name": "US Central (Iowa)"},
        {"id": "us-east1", "name": "US East (South Carolina)"},
        {"id": "europe-west1", "name": "Europe West (Belgium)"},
        {"id": "asia-southeast1", "name": "Asia Southeast (Singapore)"},
        {"id": "australia-southeast1", "name": "Australia (Sydney)"},
    ],
    "azure": [
        {"id": "eastus", "name": "East US"},
        {"id": "westus2", "name": "West US 2"},
        {"id": "westeurope", "name": "West Europe"},
        {"id": "southeastasia", "name": "Southeast Asia"},
        {"id": "australiaeast", "name": "Australia East"},
    ],
    "digitalocean": [
        {"id": "nyc3", "name": "New York 3"},
        {"id": "sfo3", "name": "San Francisco 3"},
        {"id": "lon1", "name": "London 1"},
        {"id": "sgp1", "name": "Singapore 1"},
        {"id": "ams3", "name": "Amsterdam 3"},
    ],
}

# ---------------------------------------------------------------------------
# OpenClaw installation script (runs as VM user-data / startup script)
# ---------------------------------------------------------------------------
def make_install_script(api_key: str = "", base_url: str = "", model: str = "") -> str:
    api_key_line = f'OPENAI_API_KEY="{api_key}"' if api_key else 'OPENAI_API_KEY="your-api-key-here"'
    base_url_line = f'OPENAI_BASE_URL="{base_url}"' if base_url else 'OPENAI_BASE_URL="https://api.openai.com/v1"'
    model_line = f'MODEL_NAME="{model}"' if model else 'MODEL_NAME="gpt-4o-mini"'

    return f"""#!/bin/bash
set -e
exec > /var/log/openclaw-install.log 2>&1

echo "=== [1/6] Updating system packages ==="
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git curl wget

echo "=== [2/6] Installing Node.js via nvm ==="
export NVM_DIR="/opt/nvm"
mkdir -p "$NVM_DIR"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | NVM_DIR="$NVM_DIR" bash
export NVM_DIR="/opt/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install 20
nvm use 20
nvm alias default 20
echo "export NVM_DIR=/opt/nvm" >> /etc/profile.d/nvm.sh
echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"' >> /etc/profile.d/nvm.sh

echo "=== [3/6] Cloning OpenClaw ==="
cd /opt
git clone https://github.com/0x-wzw/OpenClaw_deployer_for_dummies.git openclaw
cd openclaw

echo "=== [4/6] Setting up Python environment ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install flask flask-cors

echo "=== [5/6] Writing configuration ==="
cat > /opt/openclaw/.env << 'ENVEOF'
{api_key_line}
{base_url_line}
{model_line}
ENVEOF

echo "=== [6/6] Creating systemd service ==="
cat > /etc/systemd/system/openclaw.service << 'SVCEOF'
[Unit]
Description=OpenClaw AI Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/openclaw
ExecStart=/opt/openclaw/venv/bin/python main.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/openclaw/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable openclaw
echo "=== OpenClaw installation complete! ==="
echo "=== Run: systemctl start openclaw  to launch the agent ==="
touch /var/log/openclaw-install-done
"""


# ---------------------------------------------------------------------------
# MCP Tool Definitions
# ---------------------------------------------------------------------------
@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_regions",
            description="List available cloud regions for a given provider.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["aws", "gcp", "azure", "digitalocean"],
                        "description": "Cloud provider identifier",
                    }
                },
                "required": ["provider"],
            },
        ),
        types.Tool(
            name="list_vm_sizes",
            description="List available VM size options (small / medium / large) with descriptions and pricing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["aws", "gcp", "azure", "digitalocean"],
                    }
                },
                "required": ["provider"],
            },
        ),
        types.Tool(
            name="validate_credentials",
            description="Validate cloud provider credentials before starting deployment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["aws", "gcp", "azure", "digitalocean"],
                    },
                    "credentials": {
                        "type": "object",
                        "description": "Provider-specific credentials object",
                    },
                },
                "required": ["provider", "credentials"],
            },
        ),
        types.Tool(
            name="deploy_vm",
            description=(
                "Deploy a cloud VM and automatically install OpenClaw on it. "
                "Returns the VM ID and public IP address when ready."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["aws", "gcp", "azure", "digitalocean"]},
                    "region": {"type": "string"},
                    "vm_size": {"type": "string", "enum": ["small", "medium", "large"]},
                    "vm_name": {"type": "string"},
                    "credentials": {"type": "object"},
                    "openclaw_api_key": {
                        "type": "string",
                        "description": "OpenAI/Anthropic API key to pre-configure on the VM",
                    },
                    "openclaw_base_url": {
                        "type": "string",
                        "description": "Optional custom API base URL (for Anthropic or local models)",
                    },
                    "openclaw_model": {
                        "type": "string",
                        "description": "Model name to use (e.g. gpt-4o, claude-opus-4-6)",
                    },
                },
                "required": ["provider", "region", "vm_size", "vm_name", "credentials"],
            },
        ),
        types.Tool(
            name="get_vm_status",
            description="Check the current state and public IP of a deployed VM.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "vm_id": {"type": "string"},
                    "region": {"type": "string"},
                    "credentials": {"type": "object"},
                },
                "required": ["provider", "vm_id", "region", "credentials"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# MCP Tool Dispatch
# ---------------------------------------------------------------------------
@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "list_regions":
            return _list_regions(arguments["provider"])
        elif name == "list_vm_sizes":
            return _list_vm_sizes(arguments["provider"])
        elif name == "validate_credentials":
            return await _validate_credentials(arguments["provider"], arguments["credentials"])
        elif name == "deploy_vm":
            return await _deploy_vm(
                provider=arguments["provider"],
                region=arguments["region"],
                vm_size=arguments["vm_size"],
                vm_name=arguments["vm_name"],
                credentials=arguments["credentials"],
                api_key=arguments.get("openclaw_api_key", ""),
                base_url=arguments.get("openclaw_base_url", ""),
                model=arguments.get("openclaw_model", ""),
            )
        elif name == "get_vm_status":
            return await _get_vm_status(
                arguments["provider"],
                arguments["vm_id"],
                arguments["region"],
                arguments.get("credentials", {}),
            )
        else:
            return [types.TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    except Exception as exc:
        return [types.TextContent(type="text", text=json.dumps({"error": str(exc)}))]


# ---------------------------------------------------------------------------
# Tool Implementations — list_regions / list_vm_sizes
# ---------------------------------------------------------------------------
def _list_regions(provider: str) -> list[types.TextContent]:
    regions = REGIONS.get(provider, [])
    return [types.TextContent(type="text", text=json.dumps({"regions": regions}))]


def _list_vm_sizes(provider: str) -> list[types.TextContent]:
    sizes = [
        {
            "id": k,
            "label": v["label"],
            "instance_type": v[provider],
            "description": v["description"],
            "monthly_cost": v["monthly_cost"],
        }
        for k, v in VM_SIZES.items()
    ]
    return [types.TextContent(type="text", text=json.dumps({"sizes": sizes}))]


# ---------------------------------------------------------------------------
# Tool Implementations — validate_credentials
# ---------------------------------------------------------------------------
async def _validate_credentials(provider: str, creds: dict) -> list[types.TextContent]:
    def ok(msg):
        return [types.TextContent(type="text", text=json.dumps({"valid": True, "message": msg}))]
    def fail(msg):
        return [types.TextContent(type="text", text=json.dumps({"valid": False, "message": msg}))]

    if provider == "aws":
        try:
            import boto3
            client = boto3.client(
                "sts",
                aws_access_key_id=creds.get("access_key"),
                aws_secret_access_key=creds.get("secret_key"),
                region_name=creds.get("region", "us-east-1"),
            )
            identity = client.get_caller_identity()
            account = identity.get("Account", "unknown")
            return ok(f"AWS credentials valid! Account: {account}")
        except ImportError:
            # boto3 not installed; do a lightweight REST-based STS check
            if creds.get("access_key") and creds.get("secret_key"):
                return ok("AWS credential fields present. Full validation requires boto3 (pip install boto3).")
            return fail("Missing AWS access_key or secret_key.")
        except Exception as e:
            return fail(f"AWS credential error: {e}")

    elif provider == "gcp":
        sa_json_str = creds.get("service_account_json", "")
        try:
            sa = json.loads(sa_json_str) if isinstance(sa_json_str, str) else sa_json_str
        except json.JSONDecodeError:
            return fail("Service account JSON is not valid JSON.")
        if sa.get("type") != "service_account":
            return fail("JSON does not appear to be a GCP service account key (missing 'type': 'service_account').")
        if not sa.get("project_id"):
            return fail("Service account JSON is missing 'project_id'.")
        return ok(f"GCP service account JSON looks valid. Project: {sa['project_id']}")

    elif provider == "azure":
        required = ["client_id", "client_secret", "tenant_id", "subscription_id"]
        missing = [f for f in required if not creds.get(f)]
        if missing:
            return fail(f"Missing required Azure fields: {', '.join(missing)}")
        return ok("Azure credential fields look complete.")

    elif provider == "digitalocean":
        token = creds.get("api_token", "")
        if not token:
            return fail("DigitalOcean API token is required.")
        try:
            req = urllib.request.Request(
                "https://api.digitalocean.com/v2/account",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                email = data.get("account", {}).get("email", "")
                return ok(f"DigitalOcean token valid! Account: {email}")
        except urllib.error.HTTPError as e:
            return fail(f"DigitalOcean rejected the token (HTTP {e.code}). Check it and try again.")
        except Exception as e:
            return fail(f"DigitalOcean validation error: {e}")

    return fail(f"Unknown provider: {provider}")


# ---------------------------------------------------------------------------
# Tool Implementations — deploy_vm
# ---------------------------------------------------------------------------
async def _deploy_vm(
    provider: str,
    region: str,
    vm_size: str,
    vm_name: str,
    credentials: dict,
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> list[types.TextContent]:
    install_script = make_install_script(api_key, base_url, model)
    instance_type = VM_SIZES[vm_size][provider]

    if provider == "aws":
        return await _deploy_aws(region, instance_type, vm_name, credentials, install_script)
    elif provider == "gcp":
        return await _deploy_gcp(region, instance_type, vm_name, credentials, install_script)
    elif provider == "azure":
        return await _deploy_azure(region, instance_type, vm_name, credentials, install_script)
    elif provider == "digitalocean":
        return await _deploy_do(region, instance_type, vm_name, credentials, install_script)

    return [types.TextContent(type="text", text=json.dumps({"success": False, "error": f"Unknown provider: {provider}"}))]


# --- AWS ---
async def _deploy_aws(region, instance_type, vm_name, creds, install_script):
    def fail(msg):
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": msg}))]

    try:
        import boto3
    except ImportError:
        return fail("boto3 is not installed. Run: pip install boto3")

    try:
        ec2 = boto3.client(
            "ec2",
            aws_access_key_id=creds.get("access_key"),
            aws_secret_access_key=creds.get("secret_key"),
            region_name=region,
        )

        # Latest Ubuntu 22.04 LTS AMI
        images = ec2.describe_images(
            Filters=[
                {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]},
                {"Name": "state", "Values": ["available"]},
                {"Name": "architecture", "Values": ["x86_64"]},
            ],
            Owners=["099720109477"],  # Canonical
        )
        sorted_images = sorted(images["Images"], key=lambda x: x["CreationDate"], reverse=True)
        if not sorted_images:
            return fail("Could not locate Ubuntu 22.04 AMI in this region.")
        ami_id = sorted_images[0]["ImageId"]

        # Key pair
        key_name = f"openclaw-{vm_name}"
        private_key = None
        key_path = f"/tmp/{key_name}.pem"
        try:
            kp = ec2.create_key_pair(KeyName=key_name)
            private_key = kp["KeyMaterial"]
            with open(key_path, "w") as f:
                f.write(private_key)
            os.chmod(key_path, 0o600)
        except ec2.exceptions.ClientError as e:
            if "InvalidKeyPair.Duplicate" not in str(e):
                raise

        # Security group
        sg_name = f"openclaw-sg-{vm_name}"
        try:
            sg = ec2.create_security_group(GroupName=sg_name, Description="OpenClaw SG")
            sg_id = sg["GroupId"]
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                    {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                    {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                ],
            )
        except Exception:
            sgs = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [sg_name]}])
            sg_id = sgs["SecurityGroups"][0]["GroupId"] if sgs["SecurityGroups"] else None

        # Launch
        params = {
            "ImageId": ami_id,
            "InstanceType": instance_type,
            "KeyName": key_name,
            "MinCount": 1,
            "MaxCount": 1,
            "UserData": install_script,
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": vm_name}, {"Key": "Project", "Value": "OpenClaw"}],
                }
            ],
        }
        if sg_id:
            params["SecurityGroupIds"] = [sg_id]

        resp = ec2.run_instances(**params)
        instance = resp["Instances"][0]
        instance_id = instance["InstanceId"]

        # Brief wait for IP assignment
        time.sleep(5)
        desc = ec2.describe_instances(InstanceIds=[instance_id])
        inst_data = desc["Reservations"][0]["Instances"][0]
        public_ip = inst_data.get("PublicIpAddress", "Pending — check back in ~1 min")

        return [types.TextContent(type="text", text=json.dumps({
            "success": True,
            "vm_id": instance_id,
            "public_ip": public_ip,
            "region": region,
            "provider": "aws",
            "ssh_user": "ubuntu",
            "key_path": key_path,
            "private_key": private_key,
            "message": f"EC2 instance '{vm_name}' launched! OpenClaw is installing in the background (~5 min).",
        }))]
    except Exception as e:
        return fail(str(e))


# --- GCP ---
async def _deploy_gcp(region, machine_type, vm_name, creds, install_script):
    def fail(msg):
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": msg}))]

    sa_raw = creds.get("service_account_json", "{}")
    try:
        sa = json.loads(sa_raw) if isinstance(sa_raw, str) else sa_raw
    except Exception:
        return fail("Invalid GCP service account JSON.")

    project_id = sa.get("project_id")
    if not project_id:
        return fail("project_id not found in service account JSON.")

    creds_path = "/tmp/gcp_sa.json"
    with open(creds_path, "w") as f:
        json.dump(sa, f)

    zone = f"{region}-a"
    try:
        result = subprocess.run(
            [
                "gcloud", "compute", "instances", "create", vm_name,
                "--zone", zone,
                "--machine-type", machine_type,
                "--image-family", "ubuntu-2204-lts",
                "--image-project", "ubuntu-os-cloud",
                f"--metadata=startup-script={install_script}",
                "--tags", "openclaw,http-server,https-server",
                "--project", project_id,
                "--key-file", creds_path,
                "--format", "json",
            ],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode == 0:
            output = json.loads(result.stdout)
            inst = output[0] if isinstance(output, list) else output
            ifaces = inst.get("networkInterfaces", [{}])
            external_ip = ifaces[0].get("accessConfigs", [{}])[0].get("natIP", "Pending")
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "vm_id": vm_name,
                "public_ip": external_ip,
                "region": region,
                "zone": zone,
                "project_id": project_id,
                "provider": "gcp",
                "ssh_user": "ubuntu",
                "message": f"GCP VM '{vm_name}' created! OpenClaw is installing in the background (~5 min).",
            }))]
        else:
            return fail(f"gcloud error: {result.stderr}")
    except FileNotFoundError:
        return fail("gcloud CLI not found. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
    except Exception as e:
        return fail(str(e))


# --- Azure ---
async def _deploy_azure(region, vm_size, vm_name, creds, install_script):
    def fail(msg):
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": msg}))]

    try:
        # Login
        login = subprocess.run(
            [
                "az", "login", "--service-principal",
                "--username", creds.get("client_id", ""),
                "--password", creds.get("client_secret", ""),
                "--tenant", creds.get("tenant_id", ""),
            ],
            capture_output=True, text=True, timeout=30,
        )
        if login.returncode != 0:
            return fail(f"Azure login failed: {login.stderr}")

        if creds.get("subscription_id"):
            subprocess.run(["az", "account", "set", "--subscription", creds["subscription_id"]], capture_output=True)

        rg = f"openclaw-rg-{vm_name}"
        subprocess.run(["az", "group", "create", "--name", rg, "--location", region], capture_output=True, timeout=30)

        # Write user-data to temp file (Azure custom-data expects a file path)
        ud_path = "/tmp/openclaw_userdata.sh"
        with open(ud_path, "w") as f:
            f.write(install_script)

        create = subprocess.run(
            [
                "az", "vm", "create",
                "--resource-group", rg,
                "--name", vm_name,
                "--image", "Ubuntu2204",
                "--size", vm_size,
                "--admin-username", "azureuser",
                "--generate-ssh-keys",
                "--public-ip-sku", "Standard",
                "--custom-data", ud_path,
                "--output", "json",
            ],
            capture_output=True, text=True, timeout=300,
        )
        if create.returncode == 0:
            out = json.loads(create.stdout)
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "vm_id": vm_name,
                "public_ip": out.get("publicIpAddress", "Pending"),
                "region": region,
                "resource_group": rg,
                "provider": "azure",
                "ssh_user": "azureuser",
                "message": f"Azure VM '{vm_name}' created! OpenClaw is installing in the background (~5 min).",
            }))]
        else:
            return fail(f"az vm create failed: {create.stderr}")
    except FileNotFoundError:
        return fail("Azure CLI (az) not found. Install it: https://docs.microsoft.com/cli/azure/install-azure-cli")
    except Exception as e:
        return fail(str(e))


# --- DigitalOcean ---
async def _deploy_do(region, size, vm_name, creds, install_script):
    def fail(msg):
        return [types.TextContent(type="text", text=json.dumps({"success": False, "error": msg}))]

    token = creds.get("api_token", "")
    if not token:
        return fail("DigitalOcean API token is required.")

    payload = json.dumps({
        "name": vm_name,
        "region": region,
        "size": size,
        "image": "ubuntu-22-04-x64",
        "user_data": install_script,
        "tags": ["openclaw"],
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            "https://api.digitalocean.com/v2/droplets",
            data=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            droplet = result.get("droplet", {})
            return [types.TextContent(type="text", text=json.dumps({
                "success": True,
                "vm_id": str(droplet.get("id", "")),
                "public_ip": "Assigned in ~2 min — use get_vm_status to check",
                "region": region,
                "provider": "digitalocean",
                "ssh_user": "root",
                "message": f"DigitalOcean Droplet '{vm_name}' is being created! OpenClaw installs automatically.",
            }))]
    except Exception as e:
        return fail(str(e))


# ---------------------------------------------------------------------------
# Tool Implementations — get_vm_status
# ---------------------------------------------------------------------------
async def _get_vm_status(provider, vm_id, region, creds):
    def wrap(data):
        return [types.TextContent(type="text", text=json.dumps(data))]

    if provider == "aws":
        try:
            import boto3
            ec2 = boto3.client(
                "ec2",
                aws_access_key_id=creds.get("access_key"),
                aws_secret_access_key=creds.get("secret_key"),
                region_name=region,
            )
            resp = ec2.describe_instances(InstanceIds=[vm_id])
            inst = resp["Reservations"][0]["Instances"][0]
            return wrap({
                "state": inst["State"]["Name"],
                "public_ip": inst.get("PublicIpAddress", "Not yet assigned"),
                "private_ip": inst.get("PrivateIpAddress"),
                "launch_time": str(inst.get("LaunchTime", "")),
            })
        except ImportError:
            return wrap({"error": "boto3 not installed"})
        except Exception as e:
            return wrap({"error": str(e)})

    elif provider == "digitalocean":
        token = creds.get("api_token", "")
        try:
            req = urllib.request.Request(
                f"https://api.digitalocean.com/v2/droplets/{vm_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                droplet = data.get("droplet", {})
                networks = droplet.get("networks", {}).get("v4", [])
                public_ip = next((n["ip_address"] for n in networks if n["type"] == "public"), "Pending")
                return wrap({"state": droplet.get("status"), "public_ip": public_ip})
        except Exception as e:
            return wrap({"error": str(e)})

    return wrap({"error": f"get_vm_status not yet implemented for provider: {provider}"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
