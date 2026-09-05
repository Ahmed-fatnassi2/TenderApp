

🔍 TenderApp
Intelligent Tender Monitoring Platform for Tunisia

TenderApp is a web platform that automates the monitoring of tenders published in Tunisia. It uses an AI agent (RAG) with LangChain for semantic search, automated scraping, and personalized notifications.

🚀 Features
- **Automated Scraping**: Daily collection from TUNEPS, HAICOP, and custom sources
- **AI Agent**: Semantic search, IT classification, automatic translation (EN ↔ FR) with LangChain
- **RAG System**: Contextual search with OpenRAG + Milvus
- **Personalized Notifications**: Daily emails with filters (region, buyer, source)
- **Automated Scheduler**: Scraping (07:00 AM), expired deletion (07:30 AM), email sending (08:00 AM)
- **Secure Authentication**: Google OIDC
- **Administration**: Scraping source management, expired tender monitoring

🛠️ Tech Stack
| Category | Technologies |
|----------|--------------|
| Frontend | React.js, Vite |
| Backend | Flask (Python) |
| Database | PostgreSQL |
| Vector Database | Milvus |
| RAG | OpenRAG |
| AI | OpenAI GPT-4o-mini, LangChain |
| Authentication | Google OIDC |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

🤖 AI Agent & LangChain

**Pipeline**
1. **Query Understanding**: EN ↔ FR translation with LangChain
2. **Semantic Search**: OpenRAG + Milvus
3. **Classification**: OpenAI GPT-4o-mini (relevance, category)
4. **Custom Filtering**: Region / Buyer / Source
5. **Results Generation**: Email digest / API

**LangChain in TenderApp**
- **LLM Call Orchestration**: Prompt and response management
- **Chaining**: Sequential processing steps (translation → search → classification)
- **Agents**: Autonomous AI agent for tender research and analysis

**IT Categories Detected**
- Software Development
- Hardware
- Networking
- Cybersecurity
- Cloud Computing
- AI
- IT Services
- Telecommunications

🔐 Authentication
- OpenID Connect (OIDC)
- Google OAuth 2.0
- Secure Sessions

📊 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/tenders` | List tenders |
| GET | `/api/preferences/` | User preferences |
| PUT | `/api/preferences/` | Update preferences |
| POST | `/api/scrapers/scrape-all-and-index` | Full scraping |
| POST | `/api/scrapers/delete-expired` | Delete expired tenders |
| POST | `/api/it-notifications/send-test` | Test notification |
| GET | `/api/openrag/search` | Semantic search |

🧪 Testing
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

📝 Roadmap
- ✅ Multi-source scraping
- ✅ Personalized email notifications
- ✅ RAG semantic search
- ✅ Google OIDC authentication
- ✅ Automated scheduler
- ✅ AI agent with LangChain
- ⏳ WhatsApp / Telegram integration
- ⏳ Advanced analytics dashboard
- ⏳ Public API
- ⏳ Conversational agent
- ⏳ Automatic responses

👥 Contributors
**Ahmed Fatnassi** - Lead Developer

📄 License
This project is developed as part of an end-of-study internship.

🔗 Links
- **GitHub**: https://github.com/Ahmed-fatnassi2/tenderapp

🙏 Acknowledgments
- **Linagora** for the internship, supervision, and providing the OpenRAG platform
- The teaching team for their support
- The supervisor for guidance and valuable advice

---

Developed with ❤️ by Ahmed Fatnassi
