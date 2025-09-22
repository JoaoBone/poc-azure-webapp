import os
import json
from datetime import datetime
from flask import Flask, render_template_string, request, abort
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import jwt

app = Flask(__name__)

# ------------------- Load Role Map -------------------
# role_map.json should contain something like:
# { "client1": "Client1Access", "client2": "Client2Access" }
with open("role_map.json", "r") as f:
    ROLE_MAP = json.load(f)

# ------------------- Azure Blob Storage Setup -------------------

credential = DefaultAzureCredential()
storage_account_url = "https://sdpocblobstorage.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
container_name = "poc-container"

# ------------------- HTML Template -------------------

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Client: {{ client_name }}</title>
<style>
body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
h1 { text-align: center; color: #333; }
.blob-card { background: white; border-radius: 8px; padding: 15px; margin: 10px auto; max-width: 800px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.blob-card h3 { margin-top: 0; color: #555; }
pre { background: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
</style>
</head>
<body>
<h1>Client: {{ client_name }}</h1>
{% for blob, content in data.items() %}
<div class="blob-card">
  <h3>{{ blob }}</h3>
  <pre>{{ content | tojson(indent=2) }}</pre>
</div>
{% endfor %}
</body>
</html>
"""

# ------------------- Azure Blob Helpers -------------------

def list_client_blobs(client_name):
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs(name_starts_with=f"{client_name}/")
    return [blob.name for blob in blobs]

def get_blob_content(blob_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    content = blob_client.download_blob().readall()
    return json.loads(content.decode("utf-8"))

# ------------------- Authentication Helpers -------------------

def get_user_roles():
    """
    Read the JWT token from Azure App Service Authentication header and extract roles.
    """
    token = request.headers.get("X-MS-TOKEN-AAD-ID-TOKEN")
    if not token:
        abort(401, description="Unauthorized: no token found")
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})  # POC: skip signature check
        return decoded.get("roles", [])
    except Exception as e:
        abort(401, description=f"Unauthorized: token decode failed ({str(e)})")

# ------------------- Routes -------------------

@app.route("/client/<client_name>")
def client_data(client_name):
    # Get required role for this client
    required_role = ROLE_MAP.get(client_name)
    if not required_role:
        abort(404, description="Client not found")

    # Check user roles
    user_roles = get_user_roles()
    if required_role not in user_roles:
        abort(403, description="Forbidden: you do not have access to this resource")

    # Fetch and render blobs
    blobs = list_client_blobs(client_name)
    data = {blob_name: get_blob_content(blob_name) for blob_name in blobs}
    return render_template_string(html_template, client_name=client_name, data=data)

# ------------------- App Entry -------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)