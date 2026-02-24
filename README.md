# 🎓 SmartEduMine

> **AI-Powered Student Dropout Prediction & Performance Analytics Platform**

SmartEduMine is a full-stack educational analytics system that leverages Machine Learning and Deep Learning to predict student dropout risk, analyze academic performance, and provide actionable insights for educators and administrators.

---

## 🚀 Features

- **🔮 Dropout Prediction** — Deep learning model (DMSW) trained on real academic data to predict student dropout risk with high accuracy
- **📊 Performance Analytics** — Visualize student performance trends across subjects and semesters
- **🧠 ML-Powered Insights** — Supports Random Forest, XGBoost, and LSTM-based DMSW models
- **🔑 JWT Authentication** — Secure login and registration for admin/faculty roles
- **📈 Interactive Dashboard** — Modern React-based dashboard with charts, stat cards, and activity feeds
- **📱 Responsive UI** — Dark-themed glassmorphism design with smooth animations

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React.js, CSS3 (Glassmorphism), Chart.js, Recharts |
| **Backend** | Node.js, Express.js, JWT Authentication |
| **Database** | MongoDB Atlas (Mongoose ODM) |
| **ML Service** | Python, Flask/FastAPI, TensorFlow/Keras, Scikit-learn, XGBoost |
| **Models** | DMSW (Deep Multi-Stage Weighting), Random Forest, XGBoost |

---

## 📁 Project Structure

```
SmartEduMine/
├── frontend/          # React.js frontend application
│   └── src/
│       ├── components/    # UI components (Dashboard, Auth, Charts)
│       └── index.css      # Global styles & design system
├── backend/           # Node.js + Express REST API
│   ├── routes/            # API route handlers
│   ├── models/            # Mongoose schemas (User, Student)
│   ├── middleware/        # JWT auth middleware
│   └── server.js          # Entry point
└── ml_service/        # Python ML API server
    ├── api_server.py      # Flask/FastAPI ML model endpoints
    ├── train_dmsw_real.py # DMSW model training script
    ├── generate_dmsw_dataset.py  # Dataset generation utilities
    └── requirements.txt   # Python dependencies
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Node.js >= 16
- Python >= 3.8
- MongoDB Atlas account (or local MongoDB)

### 1. Clone the Repository
```bash
git clone https://github.com/siddhanth3/SmartEduMine.git
cd SmartEduMine
```

### 2. Backend Setup
```bash
cd backend
npm install
```
Create a `.env` file in `backend/`:
```env
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret_key
PORT=5002
NODE_ENV=development
```
Start the server:
```bash
npm run dev
```

### 3. ML Service Setup
```bash
cd ml_service
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Linux/Mac
pip install -r requirements.txt
python api_server.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm start
```

The app will be available at **http://localhost:3000**

---

## 🤖 ML Models

| Model | Description | Use Case |
|---|---|---|
| **DMSW** | Deep Multi-Stage Weighting Neural Network (LSTM-based) | Primary dropout prediction |
| **Random Forest** | Ensemble decision tree classifier | Feature importance & baseline |
| **XGBoost** | Gradient boosted trees | High-accuracy classification |

### Training the DMSW Model
```bash
cd ml_service
python train_dmsw_real.py
```

### Generating Synthetic Dataset
```bash
cd ml_service
python generate_dmsw_dataset.py
```

---

## 🔌 API Endpoints

### Backend (Node.js — Port 5002)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add a new student |

### ML Service (Python — Port 5001)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/predict` | Predict dropout risk for a student |
| GET | `/model/info` | Get model metadata and accuracy |

---

## 🌐 Environment Variables

> ⚠️ **Never commit `.env` files.** The `.gitignore` already excludes them.

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `JWT_SECRET` | Secret key for signing JWT tokens |
| `PORT` | Backend server port (default: 5002) |
| `NODE_ENV` | `development` or `production` |

---

## 👥 Team

**Group G15**

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgements

- [UCI Student Performance Dataset](https://archive.ics.uci.edu/ml/datasets/student+performance)
- [TensorFlow / Keras](https://www.tensorflow.org/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [React.js](https://reactjs.org/)
