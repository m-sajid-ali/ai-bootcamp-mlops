
# Basic Housing Web App

## For 1-simple-housing-app-without-ml-model
#### 1. Build docker image for backend
```bash
docker build --network=host -t housing-backend-app-without-ml-model ./3-backend/.
```
#### 2. Run the application
```bash
docker compose up -d
```
#### 3. Access the application
```bash
http://localhost

or

http:<you-ip>
```

## For 2-simple-housing-app-with-ml-model

```bash
See details in readme.md file of the **2-simple-housing-app-with-ml-model**
```

## For 4-simple-housing-app-with-ml-model

```bash
# First execute the commands available in run-commands-to-build-images file

docker build -t housing-ai-model-service ./4-ai-model-service/
docker build -t housing-backend-app-with-ml-model ./3-backend/

docker compose up -d
```
