# 📈 AI Demand Forecasting System

An end-to-end **AI-powered demand forecasting system** that predicts future product demand using historical data and machine learning models.  

This system helps businesses:

- 📦 Optimize inventory  
- 💰 Reduce overstock & stockouts  
- 📊 Make data-driven decisions  
- 📈 Improve supply chain efficiency  

---

## 🚀 Project Overview

This project consists of:

- 🧠 Machine Learning model for demand prediction  
- ⚙️ Backend API for model training & inference  
- 🌐 Frontend dashboard for visualization  
- 📊 Data creation & preprocessing notebook  

The system takes historical sales data as input and predicts future demand using advanced forecasting techniques.

---

## 📁 Repository Structure

AI-Demand-Forecasting-system/
│
├── backend/ # API, model training & inference logic
├── frontend/ # Dashboard / User Interface
├── data_creation.ipynb # Data generation & preprocessing notebook
├── .gitignore
└── README.md## 🧠 Core Features

✔️ Data preprocessing and feature engineering  
✔️ Machine Learning model training  
✔️ REST API for real-time predictions  
✔️ Interactive dashboard for visualization  
✔️ Modular project structure  
✔️ Scalable backend architecture  

---

## 🛠️ Tech Stack

### 🔹 Backend
- Python
- Machine Learning (Scikit-learn / Pandas / NumPy)
- FastAPI / Flask (depending on your implementation)

### 🔹 Frontend
- React.js (or your frontend framework)
- Axios / Fetch API
- Chart libraries (e.g., Chart.js / Recharts)

### 🔹 Data Processing
- Pandas
- NumPy
- Jupyter Notebook

---

## ⚙️ Installation Guide

### 📌 Prerequisites

Make sure you have installed:

- Python 3.8+
- Node.js 14+
- npm or yarn
- Git

---

# 🔹 Backend Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Avverma250106/AI-Demand-Forecasting-system.git
cd AI-Demand-Forecasting-system/backend

2️⃣ Create Virtual Environment
python -m venv venv


Activate environment:

Windows:

venv\Scripts\activate


macOS/Linux:

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Backend Server

If using FastAPI:

uvicorn main:app --reload


If using Flask:

python app.py


Backend will run on:

http://127.0.0.1:8000

🔹 Frontend Setup
1️⃣ Navigate to Frontend Folder
cd ../frontend

2️⃣ Install Dependencies
npm install


or

yarn install

3️⃣ Start Frontend
npm start


Frontend runs on:

http://localhost:3000
