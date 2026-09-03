
# 🔍 TenderApp

**Plateforme de veille intelligente des appels d'offres en Tunisie**

TenderApp est une plateforme web qui automatise la veille des appels d'offres publiés en Tunisie. Elle utilise un agent IA (RAG) avec LangChain pour la recherche sémantique, le scraping automatisé et des notifications personnalisées.

---

## 🚀 Fonctionnalités

- **Scraping automatisé** : Collecte quotidienne depuis TUNEPS, HAICOP et sources personnalisées
- **Agent IA** : Recherche sémantique, classification IT, traduction automatique (EN ↔ FR) avec LangChain
- **Système RAG** : Recherche contextuelle avec OpenRAG + Milvus
- **Notifications personnalisées** : Emails quotidiens avec filtres (région, acheteur, source)
- **Scheduler automatisé** : Scraping (07h00), suppression expirés (07h30), envoi emails (08h00)
- **Authentification sécurisée** : Google OIDC
- **Administration** : Gestion des sources de scraping, monitoring des expirés

---

## 🛠️ Stack Technique

| Catégorie | Technologies |
|-----------|--------------|
| **Frontend** | React.js, Vite |
| **Backend** | Flask (Python) |
| **Base de données** | PostgreSQL |
| **Vector Database** | Milvus |
| **RAG** | OpenRAG |
| **IA** | OpenAI GPT-4o-mini, LangChain |
| **Authentification** | Google OIDC |
| **Containerisation** | Docker, Docker Compose |
| **Versionnage** | Git, GitHub |

---

## 🤖 Agent IA & LangChain

### Pipeline

1. **Compréhension de la requête** : Traduction EN ↔ FR avec LangChain
2. **Recherche sémantique** : OpenRAG + Milvus
3. **Classification** : OpenAI GPT-4o-mini (pertinence, catégorie)
4. **Filtrage personnalisé** : Région / Acheteur / Source
5. **Génération des résultats** : Digest email / API

### LangChain dans TenderApp

- **Orchestration des appels LLM** : Gestion des prompts et des réponses
- **Chaînage** : Enchaînement des étapes de traitement (traduction → recherche → classification)
- **Agents** : Agent IA autonome pour la recherche et l'analyse des tenders

### Catégories IT détectées

- Software Development
- Hardware
- Networking
- Cybersecurity
- Cloud Computing
- AI
- IT Services
- Telecommunications

---

## 🔐 Authentification

- OpenID Connect (OIDC)
- Google OAuth 2.0
- Sessions sécurisées

---

## 📊 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Vérification de l'état |
| GET | `/api/tenders` | Liste des appels d'offres |
| GET | `/api/preferences/` | Préférences utilisateur |
| PUT | `/api/preferences/` | Mise à jour préférences |
| POST | `/api/scrapers/scrape-all-and-index` | Scraping complet |
| POST | `/api/scrapers/delete-expired` | Suppression expirés |
| POST | `/api/it-notifications/send-test` | Test notification |
| GET | `/api/openrag/search` | Recherche sémantique |

---

## 🧪 Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

---

## 📝 Roadmap

- [x] Scraping multi-sources
- [x] Notifications email personnalisées
- [x] Recherche sémantique RAG
- [x] Authentification Google OIDC
- [x] Scheduler automatisé
- [x] Agent IA avec LangChain
- [ ] Intégration WhatsApp / Telegram
- [ ] Dashboard analytique avancé
- [ ] API publique
- [ ] Agent conversationnel
- [ ] Réponse automatique

---

## 👥 Contributeurs

- **Ahmed Fatnassi** - Développeur principal

---

## 📄 Licence

Ce projet est développé dans le cadre d'un stage de fin d'études.

---

## 🔗 Liens

- **GitHub** : https://github.com/Ahmed-fatnassi2/tenderapp

---

## 🙏 Remerciements

- **Linagora** pour le stage, l'encadrement et la mise à disposition de la plateforme OpenRAG
- **L'équipe pédagogique** pour leur accompagnement
- **Le tuteur** pour le suivi et les précieux conseils

---

Développé avec ❤️ par Ahmed Fatnassi
