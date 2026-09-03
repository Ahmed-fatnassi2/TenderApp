# TenderApp Frontend

A modern React dashboard for government tender management built with **React 19**, **Vite**, and styled with **red and white** color scheme.

## Features

✅ **User Authentication** - Sign in page with local storage persistence
✅ **Responsive Dashboard** - Overview of system statistics and quick actions
✅ **Tender Management** - View, search, and filter tenders scraped from TUNEPS
✅ **Scraping Control** - Trigger manual scraping from the dashboard
✅ **Modern UI** - Red and white color scheme with sidebar navigation
✅ **Backend Integration** - Full REST API integration with Flask backend

## Project Structure

```
src/
├── pages/              # Page components
│   ├── SignIn.jsx      # Authentication page
│   ├── Dashboard.jsx   # Overview dashboard
│   ├── Tenders.jsx     # Tender listing with search
│   └── Scrape.jsx      # Scraping control page
├── components/         # Reusable components
│   ├── Layout.jsx      # Main layout wrapper
│   ├── Navbar.jsx      # Top navigation bar
│   └── Sidebar.jsx     # Left sidebar navigation
├── services/
│   └── api.js          # API service layer
├── styles/             # CSS modules
│   ├── globals.css
│   ├── SignIn.css
│   ├── Navbar.css
│   ├── Sidebar.css
│   ├── Layout.css
│   ├── Dashboard.css
│   ├── Tenders.css
│   └── Scrape.css
├── App.jsx             # Main app component
└── main.jsx            # Entry point
```

## Setup

### Prerequisites
- Node.js (v16+)
- npm or yarn
- Backend Flask server running on `http://localhost:5000`

### Installation

```powershell
# Install dependencies
npm install
```

### Environment Variables

Create a `.env` file in the frontend directory (already created):

```
VITE_API_BASE_URL=http://localhost:5000/api
```

## Development

Start the development server:

```powershell
npm run dev
```

The app will be available at `http://localhost:5173`

## Build

Build for production:

```powershell
npm run build
```

Preview production build:

```powershell
npm run preview
```

## Linting

```powershell
npm run lint
```

## Color Scheme

- **Primary Red**: `#dc2626`
- **Dark Red**: `#991b1b`
- **Light Red**: `#fee2e2`
- **White**: `#ffffff`
- **Light Gray**: `#f9fafb`
- **Dark Text**: `#1f2937`

## API Integration

The frontend communicates with the Flask backend via REST API endpoints:

- `GET /api/health` - Health check
- `GET /api/tenders` - List all tenders
- `GET /api/tenders/count` - Tender count
- `POST /api/tenders/scrape` - Trigger scraping
- `DELETE /api/tenders/<id>` - Delete tender

## Authentication

Currently uses local storage-based authentication for demo purposes. Users can sign in with any email and password.

User data is stored in `localStorage` and persists across browser sessions.

## Features Detail

### Sign In Page
- Email and password validation
- Professional gradient background (red gradient)
- Responsive card layout
- Demo credentials: any email & password

### Dashboard
- System health status
- Total tender count
- Quick action buttons
- Statistics cards with icons

### Tenders Page
- Complete tender listing with search
- Filter by title, reference, or buyer
- Expandable tender cards for detailed view
- Delete functionality
- Refresh data button
- Responsive grid layout

### Scrape Page
- Manual data scraping trigger
- Real-time progress feedback
- Success/error messages
- Detailed scraping results
- Information about the scraping process

### Sidebar Navigation
- Dashboard link
- Tenders link
- Scrape Data link
- Analytics link (coming soon)
- Active page highlighting

### Navbar
- Application branding
- System info
- User profile display
- Dropdown menu with settings and logout
- User email display

## Technology Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **CSS3** - Styling with CSS variables
- **Fetch API** - HTTP requests
- **Local Storage** - Client-side data persistence

## Responsive Design

The app is fully responsive and includes breakpoints for:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (< 768px)

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
