# import os
# import json
# from flask import Flask, render_template_string
# from azure.identity import DefaultAzureCredential
# from azure.storage.blob import BlobServiceClient

# app = Flask(__name__)

# # Use DefaultAzureCredential to leverage Managed Identity on Azure
# credential = DefaultAzureCredential()
# storage_account_url = "https://sdpocblobstorage.blob.core.windows.net"
# blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
# container_name = "poc-container"

# def list_client_blobs(client_name):
#     container_client = blob_service_client.get_container_client(container_name)
#     blobs = container_client.list_blobs(name_starts_with=f"{client_name}/")
#     return [blob.name for blob in blobs]

# def get_blob_content(blob_name):
#     container_client = blob_service_client.get_container_client(container_name)
#     blob_client = container_client.get_blob_client(blob_name)
#     content = blob_client.download_blob().readall()
#     return json.loads(content.decode("utf-8"))

# @app.route("/client/<client_name>")
# def client_data(client_name):
#     blobs = list_client_blobs(client_name)
#     data = {blob_name: get_blob_content(blob_name) for blob_name in blobs}
#     html_template = """
#     <h1>Client: {{ client_name }}</h1>
#     {% for blob, content in data.items() %}
#         <h3>{{ blob }}</h3>
#         <pre>{{ content | tojson(indent=2) }}</pre>
#     {% endfor %}
#     """
#     return render_template_string(html_template, client_name=client_name, data=data)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     app.run(host="0.0.0.0", port=port)

from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Azure Web App!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)