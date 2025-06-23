const express = require('express');
const cors = require('cors');
const { DefaultAzureCredential } = require('@azure/identity');
const { ServiceBusClient } = require('@azure/service-bus');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/locacao', async (req, res) => {
    const { nome, email, modelo, ano, tempoAluguel } = req.body;
    const connectionString = process.env.AZURE_SERVICE_BUS_CONNECTION_STRING;

    const mensagem = {
        body: {
            nome,
            email,
            modelo,
            ano,
            tempoAluguel,
            data: new Date().toISOString(),
        },
        subject: "Locação de Veículo",
    };

    try {
        const credencial = new DefaultAzureCredential();
        const serviceBusConnection = connectionString;
        const queueName = process.env.AZURE_SERVICE_BUS_QUEUE_NAME;
        const sbClient = new ServiceBusClient(serviceBusConnection);
        const sender = sbClient.createSender(queueName);
        const message = {
            body: mensagem,
            contentType: "application/json",
            label: "locacao",
        };

        await sender.sendMessages(message);
        await sender.close();
        await sbClient.close();

        res.status(201).send("Mensagem enviada com sucesso");
    } catch (error) {
        console.error("Erro ao enviar mensagem:", error);
        res.status(500).send("Erro ao enviar mensagem");
    }
});

app.listen(3001, () => {
    console.log("Servidor rodando na porta 3001");
});