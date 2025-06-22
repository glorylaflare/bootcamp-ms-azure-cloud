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
    blob_name = f"{uuid.uuid4()}/{image_file.name}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(image_file.read(), overwrite=True)
    return f"https://{blobAccountName}.blob.core.windows.net/{blobCountainerName}/{blob_name}"

def insert_product_to_db(name, description, price, image_url):
    try:
        with pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={sqlServer};DATABASE={sqlDatabase};UID={sqlUsername};PWD={sqlPassword}") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Produtos (nome, descricao, preco, imagem_url) VALUES (?, ?, ?, ?)",
                name, description, price, image_url
            )
            conn.commit()
    except Exception as e:
        st.error(f"Erro ao inserir produto no banco de dados: {e}")

def list_products_from_db():
    try:
        with pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={sqlServer};DATABASE={sqlDatabase};UID={sqlUsername};PWD={sqlPassword}") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Produtos")
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []

def list_products_on_screen():
    produtos = list_products_from_db()
    if produtos:
        for produto in produtos:
            st.write(f"Nome: {produto[1]}")
            st.write(f"Descrição: {produto[2]}")
            st.write(f"Preço: R$ {produto[3]:.2f}")
            st.image(produto[4], caption=produto[1])
    else:
        st.write("Nenhum produto cadastrado.")

if st.button("Cadastrar Produto"):
    if product_name and product_description and product_price and product_image:
        image_url = save_image_to_blob(product_image)
        insert_product_to_db(product_name, product_description, product_price, image_url)
        st.success("Produto cadastrado com sucesso!")
    else:
        st.error("Por favor, preencha todos os campos obrigatórios.")

st.header("Produtos Cadastrados")

if st.button("Carregar Produtos"):
    list_products_on_screen()