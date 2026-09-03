# TenderApp - Quick Start Guide

## Project Overview

TenderApp is a full-stack government tender management system with:
- **Backend**: Flask REST API with PostgreSQL database
- **Frontend**: Modern React dashboard with red & white theme

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js v16+
- PostgreSQL running locally
- npm or yarn

---

## Backend Setup & Run

### 1. Navigate to backend folder
```powershell
cd backend
```

### 2. Create virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Setup database
Ensure PostgreSQL is running and create the database:
```powershell
# Update DATABASE_URL in .env if needed
# Default: postgresql://postgres:Postgrespwd12345.@localhost:5432/tender_db

# Run migrations
flask db upgrade
```

### 5. Run backend
```powershell
flask --app app run --debug
```

Backend will be available at: **http://localhost:5000**

---

## Frontend Setup & Run

### 1. Navigate to frontend folder
```powershell
cd frontend
```

### 2. Install dependencies
```powershell
npm install
```

### 3. Start development server
```powershell
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## Using the Application

### 1. Sign In
- Open http://localhost:5173
- Use any email and password (demo mode)
- Example: `user@example.com` / `password123`

### 2. Dashboard
- Overview of system statistics
- Backend health status
- Total tender count
- Quick action buttons

### 3. Tenders Page
- View all scraped tenders from TUNEPS
- Search by title, reference, or buyer
- Click expand (▶) to see detailed information
- Delete tenders if needed
- Refresh button to sync data

### 4. Scrape Data
- Manually trigger new scraping from TUNEPS
- Shows new tenders added, duplicates skipped
- Real-time progress feedback
- Success/error messages

### 5. Navigation
- Use sidebar to switch between pages
- Click user menu (⋮) in navbar to sign out
- Responsive design works on mobile/tablet

---

## API Endpoints

### Health Check
```
GET http://localhost:5000/api/health
```

### Get All Tenders
```
GET http://localhost:5000/api/tenders
```

### Get Tender Count
```
GET http://localhost:5000/api/tenders/count
```

### Trigger Scrape
```
POST http://localhost:5000/api/tenders/scrape
```

### Get Tender by Reference
```
GET http://localhost:5000/api/tenders/<reference>
```

### Delete Tender
```
DELETE http://localhost:5000/api/tenders/<id>
```

---

## Frontend Features

✅ **Authentication** - Sign in with email/password
✅ **Dashboard** - System overview and statistics
✅ **Tender Management** - View, search, filter tenders
✅ **Data Scraping** - Trigger TUNEPS data collection
✅ **Responsive Design** - Works on all devices
✅ **Red & White Theme** - Professional color scheme
✅ **Sidebar Navigation** - Easy page switching
✅ **User Profile** - Account menu and logout

---

## Frontend Color Scheme

```
Primary Red:    #dc2626
Dark Red:       #991b1b
Light Red:      #fee2e2
White:          #ffffff
Light Gray:     #f9fafb
Dark Text:      #1f2937
```

---

## Development Notes

### Backend Structure
```
backend/
├── app.py              # Flask app with routes
├── database.py         # SQLAlchemy setup
├── models/             # Tender, User models
├── services/           # Scraper service
├── migrations/         # Database migrations
└── requirements.txt    # Python dependencies
```

### Frontend Structure
```
frontend/
├── src/
│   ├── pages/          # Dashboard, Tenders, Scrape, SignIn
│   ├── components/     # Layout, Navbar, Sidebar
│   ├── services/       # API integration
│   ├── styles/         # CSS with red & white theme
│   └── App.jsx         # Main component
├── package.json
└── vite.config.js
```

---

## Troubleshooting

### Frontend can't connect to backend
- Ensure backend is running on http://localhost:5000
- Check CORS is enabled (it is in app.py)
- Check frontend .env has correct API_BASE_URL

### Database connection error
- Verify PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Ensure database `tender_db` exists

### Port already in use
- Backend: Change port in `flask run --port=5001`
- Frontend: Vite will auto-use next available port

---

## Production Build

### Frontend
```powershell
cd frontend
npm run build
```
Output will be in `frontend/dist/`

### Linting
```powershell
npm run lint
```

---

## Next Steps

Consider adding:
- Real authentication with JWT tokens
- User preferences and saved filters
- Email notifications for new tenders
- Advanced analytics and reporting
- Export functionality (PDF, CSV)
- Multi-language support

---

## Support

For issues or questions, check:
- Frontend: [frontend/README.md](frontend/README.md)
- Backend: [backend/README.md](backend/README.md)
- Vite docs: https://vite.dev/
- React docs: https://react.dev/

---

**Happy coding! 🚀**
