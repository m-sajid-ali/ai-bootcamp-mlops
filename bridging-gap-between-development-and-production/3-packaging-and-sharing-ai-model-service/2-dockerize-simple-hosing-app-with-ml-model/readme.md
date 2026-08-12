# Dockerizing a Simple Housing Web Application Featuring Price Prediction - MLOps Exercise

This project is designed as a hands-on exercise to help you learn how to containerize a complete ML-powered web app using Docker. It consists of four components:

- AI Model training and saved model
- Backend service exposing APIs
- AI Model API service serving the model
- Frontend served via NGINX

---

## Exercise Instructions

Your goal is to **dockerize each component separately** and create containers that communicate properly to form a working app.

---

### 1. AI Model (No Docker required)

- This folder contains the training notebook and a pre-trained model.
- You will **use the existing saved model** for the AI Model API service.

---

### 2. Frontend (Dockerize with NGINX)

- Use the official image: `nginx:1.29.0`
- Expose port `80` on the container.
- ```src``` directory contains the frontend code.
- Configure the frontend to connect to the backend using the environment variable: ``` API_URL=http://192.168.65.91:5000 ```
- Map the volume to use the provided nginx template config file:``` ./nginx.template.conf:/etc/nginx/templates/default.conf.template ```
- Name your image `app-frontend` (or any name you prefer).
---

### 3. Backend (Dockerize with FastAPI)
- Use the base image: `python:3.11-slim`
- Install dependencies from `requirements.txt`.
- Set the environment variable: ``` MODEL_API_BASE_URL=http://192.168.65.91:8000 ```
- Use this command to start the app: ``` uvicorn main:app --host 0.0.0.0 --port 80 ```
- Name your image `app-backend` (or any name you prefer).

### 4. AI Model API Service (Dockerize with FastAPI)
- Use the base image: python:3.11-slim
- Install dependencies from requirements.txt.
- Set the environment variable: 
    ```
        MLFLOW_TRACKING_URI=http://10.1.134.219:5001
        MODEL_URI=models:/house-price-model@champion 
    ```
- Use this command to start the app: ``` uvicorn main:app --host 0.0.0.0 --port 80 ```
- Name your image `ai-model-service` (or any name you prefer).

### 5. Run Your Containers
- Create containers from your images.
- Ensure the frontend can communicate with the backend, and the backend can communicate with the AI model service.
- Validate your app by visiting the frontend in a browser.

