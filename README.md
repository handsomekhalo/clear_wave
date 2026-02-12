# clear_wave
# ClearWave

Practice management for small law firms. Simple, affordable, no bullshit.

## What It Does

- Case tracking
- Document management with audit trails
- Client portal (magic link login)
- Form templates (create once, reuse forever)
- Multi-tenant architecture

## For Who

Solo lawyers and small firms (1-10 people) who find Clio too expensive/complex.

## Tech Stack

**Backend:**
- Django 5.0 + Django REST Framework
- PostgreSQL 16 (multi-tenant)
- AWS S3 (document storage)
- Celery + Redis (background jobs)

**Frontend:**
- Next.js 14
- TailwindCSS

**Infrastructure:**
- Railway (backend)
- Vercel (frontend)
- SendGrid (email)

## Local Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

## Environment Variables
```bash
# backend/.env
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=clearwave-docs
SENDGRID_API_KEY=...
```

## Project Structure
```
clearwave/
├── backend/           # Django API
│   ├── firms/         # Firm & user management
│   ├── cases/         # Case CRUD
│   ├── documents/     # Document storage & tracking
│   ├── forms/         # Form templates
│   └── api/           # DRF endpoints
├── frontend/          # Next.js app
│   ├── app/           # App router
│   ├── components/    # Reusable UI
│   └── lib/           # API client, utils
└── docs/              # Product specs, design docs
```

## Development Roadmap

**Week 1-2:** Core models + auth  
**Week 3-4:** Case management + document upload  
**Week 5-6:** Client portal  
**Week 7-8:** Form templates  
**Week 9-10:** Polish + beta launch  

Current status: **Week 1** ✅

## Key Decisions

**Why multi-tenant from day 1?**  
Target is law firms with 3-10 people. Tenant isolation is core, not an add-on.

**Why no built-in calendar/tasks?**  
Integrates with existing tools (Google Cal, Zapier). Stay focused.

**Why graceful downgrade vs hard lockout?**  
SA market has cash flow volatility. Free tier keeps users, builds trust.

## Contributing

Not open source (yet). Private beta with select firms.

## License

Proprietary. © 2026 ClearWave.

## Contact

Founder: Titus  
Email: hello@clearwave.io  
First beta user: Karabo (UK legal professional)

---

**Built with:** Django, Next.js, determination, and too much coffee.
