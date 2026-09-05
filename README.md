
# 🔍 TENDERAPP

### Intelligent Tender Monitoring Platform for Tunisia

---

TenderApp is a web platform that automates the monitoring of tenders published in Tunisia. It uses an AI agent (RAG) with LangChain for semantic search, automated scraping, and personalized notifications.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributors](#-contributors)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Automated Scraping** | Daily collection from TUNEPS, HAICOP, and custom sources |
| **AI Agent** | Semantic search, IT classification, automatic translation (EN ↔ FR) with LangChain |
| **RAG System** | Contextual search with OpenRAG + Milvus |
| **Personalized Notifications** | Daily emails with filters (region, buyer, source) |
| **Automated Scheduler** | Scraping (07:00 AM), expired deletion (07:30 AM), email sending (08:00 AM) |
| **Secure Authentication** | Google OIDC |
| **Administration** | Scraping source management, expired tender monitoring |

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | React.js, Vite |
| **Backend** | Flask (Python) |
| **Database** | PostgreSQL |
| **Vector Database** | Milvus |
| **RAG** | OpenRAG |
| **AI** | OpenAI GPT-4o-mini, LangChain |
| **Authentication** | Google OIDC |
| **Containerization** | Docker, Docker Compose |
| **Version Control** | Git, GitHub |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [PostgreSQL 14+](https://www.postgresql.org/download/)
- [Docker & Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ahmed-fatnassi2/tenderapp.git
cd tenderapp
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required environment variables:**

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here

# PostgreSQL Connection
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/tender_db

# OpenRAG Connection
OPENRAG_URL=http://localhost:8080
OPENRAG_TOKEN=or-openrag-1234

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com
FROM_NAME=TenderApp
DAILY_DIGEST_EMAIL=your_digest_email@gmail.com

# Google OIDC
OIDC_PROVIDER=google
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### 4. Database Setup

```bash
# Start PostgreSQL (if not already running)
sudo service postgresql start  # Linux
# or
brew services start postgresql  # macOS

# Create database
createdb tenderapp

# Run migrations
flask db upgrade
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your backend URL
# REACT_APP_API_URL=http://localhost:5000/api
```

### 6. Start OpenRAG with Milvus

```bash
# Navigate to OpenRAG directory
cd ../openrag/infra/compose

# Start the system
docker compose --profile cpu up -d

# Wait for services to be ready (about 30 seconds)

# Check if OpenRAG is running
curl http://localhost:8080/health_check

# Check if Milvus is running
docker ps | grep milvus

# If Milvus is not running, start it
docker start compose-milvus-1

# View logs (optional)
docker compose logs -f openrag-cpu

# Stop the system (when done)
docker compose --profile cpu down
```

---

## 🚀 Running the Application

### Start All Services

**1. OpenRAG:**
```bash
cd openrag/infra/compose
docker compose --profile cpu up -d
```

**2. Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**3. Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:5000/api |
| **OpenRAG API** | http://localhost:8080 |
| **Milvus** | http://localhost:19530 |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/tenders` | List tenders |
| `GET` | `/api/tenders/count` | Count tenders |
| `GET` | `/api/preferences/` | User preferences |
| `PUT` | `/api/preferences/` | Update preferences |
| `POST` | `/api/scrapers/scrape-all-and-index` | Full scraping and indexing |
| `POST` | `/api/scrapers/check-expired-deadlines` | Check expired tenders |
| `POST` | `/api/scrapers/delete-expired` | Delete expired tenders |
| `POST` | `/api/it-notifications/send-test` | Test notification |
| `GET` | `/api/openrag/search` | Semantic search |
| `GET` | `/api/admin/check` | Admin system check |

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🤖 AI Agent & LangChain

### Pipeline

1. **Query Understanding**: EN ↔ FR translation with LangChain
2. **Semantic Search**: OpenRAG + Milvus
3. **Classification**: OpenAI GPT-4o-mini (relevance, category)
4. **Custom Filtering**: Region / Buyer / Source
5. **Results Generation**: Email digest / API

### IT Categories Detected

- Software Development
- Hardware
- Networking
- Cybersecurity
- Cloud Computing
- AI
- IT Services
- Telecommunications

---

## 🔐 Authentication

- OpenID Connect (OIDC)
- Google OAuth 2.0
- Secure Sessions

---

## 📝 Roadmap

| Status | Feature |
|--------|---------|
| ✅ | Multi-source scraping |
| ✅ | Personalized email notifications |
| ✅ | RAG semantic search |
| ✅ | Google OIDC authentication |
| ✅ | Automated scheduler |
| ✅ | AI agent with LangChain |
| ⏳ | WhatsApp / Telegram integration |
| ⏳ | Advanced analytics dashboard |
| ⏳ | Public API |
| ⏳ | Conversational agent |
| ⏳ | Automatic responses |

---

## 👥 Contributors

**Ahmed Fatnassi** - Lead Developer

---

## 📄 License

This project is developed as part of an end-of-study internship.

---

## 🔗 Links

- **GitHub**: [https://github.com/Ahmed-fatnassi2/tenderapp](https://github.com/Ahmed-fatnassi2/tenderapp)

---

## 🙏 Acknowledgments

- **Linagora** for the internship, supervision, and providing the OpenRAG platform
- The teaching team for their support
- The supervisor for guidance and valuable advice

---

*Developed with ❤️ by Ahmed Fatnassi*
