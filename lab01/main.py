import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pyodbc
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

blobConnectionString = os.getenv("BLOB_CONNECTION_STRING")
blobCountainerName = os.getenv("BLOB_CONTAINER_NAME")
blobAccountName = os.getenv("BLOB_ACCOUNT_NAME")
sqlServer = os.getenv("SQL_SERVER")
sqlDatabase = os.getenv("SQL_DATABASE")
sqlUsername = os.getenv("SQL_USERNAME")
sqlPassword = os.getenv("SQL_PASSWORD")

st.title("Cadastro de Produtos")

product_name = st.text_input("Nome do Produto")
product_description = st.text_area("Descrição do Produto") 
product_price = st.number_input("Preço do Produto", min_value=0.0, format="%.2f")
product_image = st.file_uploader("Imagem do Produto", type=["jpg", "jpeg", "png"])

# Save image on blob storage
def save_image_to_blob(image_file):
    blob_service_client = BlobServiceClient.from_connection_string(blobConnectionString)
    container_client = blob_service_client.get_container_client(blobCountainerName)
    blob_client = container_client.get_blob_client(f"{uuid.uuid4()}/{image_file.name}")
    blob_client.upload_blob(image_file.getvalue(), overwrite=True)
    return f"https://{blobAccountName}.blob.core.windows.net/{blobCountainerName}/{image_file.name}"

if st.button("Cadastrar Produto"):
    if product_image is not None:
        image_url = save_image_to_blob(product_image)
        return_message = "Produto cadastrado com sucesso!"
    else:
        return_message = "Por favor, envie uma imagem do produto."

st.header("Produtos Cadastrados")

if st.button("Carregar Produtos"):
    with pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={sqlServer};DATABASE={sqlDatabase};UID={sqlUsername};PWD={sqlPassword}") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()
        for produto in produtos:
            st.image(produto.imagem_url, caption=produto.nome)
    return_message = "Produtos carregados com sucesso!"