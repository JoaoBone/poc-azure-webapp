import os
import json
from flask import Flask, render_template_string
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# Use DefaultAzureCredential to leverage Managed Identity on Azure
credential = DefaultAzureCredential()
storage_account_url = "https://sdpocblobstorage.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
container_name = "poc-container"

def list_client_blobs(client_name):
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs(name_starts_with=f"{client_name}/")
    return [blob.name for blob in blobs]

def get_blob_content(blob_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    content = blob_client.download_blob().readall()
    return json.loads(content.decode("utf-8"))

@app.route("/")
def home():
    return "Hello from Azure Web App with Blob Access!"

@app.route("/client/<client_name>")
def client_data(client_name):
    try:
        blobs = list_client_blobs(client_name)
        data = {blob_name: get_blob_content(blob_name) for blob_name in blobs}
        html_template = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f7f9fc;
                    text-align: center;
                    margin: 0;
                    padding: 20px;
                }
                h1 {
                    color: #333;
                }
                .card {
                    background: #fff;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    margin: 20px auto;
                    padding: 20px;
                    max-width: 700px;
                    text-align: left;
                }
                .filename {
                    font-weight: bold;
                    font-size: 1.2em;
                    color: #0056b3;
                    margin-bottom: 5px;
                }
                .path {
                    font-size: 0.9em;
                    color: #666;
                    margin-bottom: 15px;
                }
                pre {
                    background: #f4f4f4;
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <h1>Client: {{ client_name }}</h1>
            {% for blob, content in data.items() %}
                <div class="card">
                    <div class="filename">{{ blob.split('/')[-1] }}</div>
                    <div class="path">{{ blob }}</div>
                    <pre>{{ content | tojson(indent=2) }}</pre>
                </div>
            {% endfor %}
        </body>
        </html>
        """
        return render_template_string(html_template, client_name=client_name, data=data)
    except Exception as e:
        return f"❌ Error rendering client data: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)