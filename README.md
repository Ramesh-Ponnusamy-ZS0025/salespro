# TaRaZ - AI-Powered Sales Platform

A comprehensive full-stack sales platform with 9 powerful modules to streamline your entire sales operation, from campaign creation to document generation and performance analytics.

![Platform](https://img.shields.io/badge/Platform-Full%20Stack-blue)
![Tech Stack](https://img.shields.io/badge/Tech-FastAPI%20%2B%20React%20%2B%20MongoDB-green)
![AI Powered](https://img.shields.io/badge/AI-OpenAI%20GPT--4o-orange)

## 🚀 Features

### Complete Sales Operations Suite

1. **Agent Builder** - Create and manage AI-powered sales agents
2. **Campaign Builder** - Design multi-touch outbound campaigns
3. **Personalization Assistant** - Generate 1:1 personalized messages
4. **Thread Intelligence** - Analyze email threads and generate follow-ups
5. **Document Generator** - Create professional legal documents (NDA/MSA/SOW)
6. **GTM Generator** - Generate prospect-specific microsite prompts
7. **Learning & Feedback Hub** - Performance insights and continuous improvement
8. **Saved Items** - Centralized management for all assets
9. **Dashboard** - Real-time analytics and quick actions

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.110.1
- **Database**: MongoDB (Motor async driver)
- **AI Integration**: OpenAI GPT-4o via Emergent LLM Key
- **Authentication**: JWT with bcrypt
- **Document Generation**: python-docx

### Frontend
- **Framework**: React 19.0.0
- **UI Library**: Shadcn UI + Radix UI + Tailwind CSS
- **Routing**: React Router DOM
- **Charts**: Recharts
- **Notifications**: Sonner

## 📋 Prerequisites

- Node.js 16.x or higher
- Python 3.11 or higher
- MongoDB 4.0 or higher
- Yarn 1.22.x or higher

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sales-agent-platform
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your MongoDB URL and JWT secret

# Run server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend: `http://localhost:8001`  
API Docs: `http://localhost:8001/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
yarn install
npm install docx-preview --legacy-peer-deps

#yarn add @dnd-kit/utilities
#yarn add @dnd-kit/core@5.0.3 @dnd-kit/sortable@6.0.3 @dnd-kit/utilities@3.0.0


# Configure .env
cp .env.example .env
# Set REACT_APP_BACKEND_URL=http://localhost:8001

# Start development server
yarn start
```

Frontend: `http://localhost:3000`

### 4. MongoDB Setup

**Local MongoDB:**
```bash
mongod --dbpath=/path/to/data
```

**MongoDB Atlas (Cloud):**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Get connection string
4. Update MONGO_URL in backend/.env

## 🔐 Environment Variables

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=sales_agent_platform
JWT_SECRET=your_secure_jwt_secret_key
EMERGENT_LLM_KEY=sk-emergent-4E1117e66D3282e790
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 📱 Using the Application

### Getting Started

1. **Register Account**
   - Navigate to http://localhost:3000
   - Click "Register" and create account

2. **Create Agent**
   - Go to "Agent Builder"
   - Define services, value props, pain points
   - Set tone and methodologies

3. **Launch Campaign**
   - Navigate to "Campaign Builder"
   - Select agent and configure settings
   - Generate AI-powered copy

4. **Personalize Outreach**
   - Use "Personalization Assistant"
   - Create sender profiles
   - Generate 1:1 messages

## 🎯 Key Modules

### Agent Builder
Create reusable AI sales agent templates with:
- Service definitions
- Value propositions
- Pain points
- Target personas
- Tone settings

### Campaign Builder
Multi-touch campaigns with:
- Funnel stage mapping (TOFU/MOFU/BOFU)
- AI-generated copy
- Methodology selection
- Resource linking

### Personalization Assistant
1:1 message generation with:
- LinkedIn/company context
- Sender profiles
- Keyword customization
- 500-character messaging

### Thread Intelligence
Email analysis featuring:
- Sentiment analysis
- Stage detection
- AI-powered follow-ups
- Next-best-action suggestions

### Document Generator
Professional documents:
- NDA (Non-Disclosure Agreement)
- MSA (Master Service Agreement)
- SOW (Statement of Work)
- Mail merge support

### GTM Generator
Prospect-specific microsites:
- Tailored landing page prompts
- Lovable/Emergent integration
- Pain point addressing

### Learning Hub
Performance tracking:
- Campaign metrics
- User feedback
- AI insights
- Methodology analysis

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Core Features
- `/api/agents` - Agent management
- `/api/campaigns` - Campaign operations
- `/api/personalize/generate` - Message generation
- `/api/thread/analyze` - Thread analysis
- `/api/documents/generate` - Document creation
- `/api/gtm/generate-prompt` - GTM prompts
- `/api/feedback` - Feedback system
- `/api/insights` - Performance insights

Full API docs: http://localhost:8001/docs

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check MongoDB
ps aux | grep mongod

# Check logs
tail -f /var/log/supervisor/backend.err.log

# Restart
uvicorn server:app --reload
```

### Frontend Issues
```bash
# Clear and reinstall
rm -rf node_modules
yarn install
yarn start
```

## 🚀 Production Deployment

### Backend
1. Set production environment variables
2. Use gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app`
3. Enable HTTPS
4. Configure CORS
5. Use managed MongoDB

### Frontend
1. Build: `yarn build`
2. Serve via nginx or CDN
3. Enable HTTPS
4. Set production env variables

## 📊 Database Collections

- **users** - User accounts
- **agents** - Sales agent templates
- **campaigns** - Campaign data
- **sender_profiles** - Sender information
- **personalizations** - Generated messages
- **thread_analyses** - Email thread analysis
- **documents** - Generated documents
- **gtm_assets** - GTM prompts
- **feedback** - User feedback
- **insights** - Performance insights

## 🔒 Security Features

- JWT authentication
- bcrypt password hashing
- CORS protection
- Input validation (Pydantic)
- Environment variable protection

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push and create Pull Request

## 📄 License

MIT License

---

**Built for sales teams to close more deals faster with AI assistance**
