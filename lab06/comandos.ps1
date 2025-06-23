az acr login --name acrlab006glfeastus

docker tag bff-rent-a-car-local acrlab006glfeastus.azurecr.io/bff-rent-a-car-local:v1

docker push acrlab006glfeastus.azurecr.io/bff-rent-a-car-local:v1

az containerapp create --name bff-rent-a-car-local --resource-group lab006 --environment managedEnvironment-lab006-97d9 --image acrlab006glfeastus.azurecr.io/bff-rent-a-car-local:v1 --target-port 3001 --ingress 'external' --registry-server acrlab006glfeastus.azurecr.io 