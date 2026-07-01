# Q-Shield v2 Setup Guide

## Quick Start (Development)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic numpy scipy scikit-learn pandas

# Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Backend is now available at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### 2. Frontend Setup

In a **new terminal**:

```bash
# Navigate to project root
cd /path/to/project

# Install dependencies
pnpm install

# Start Next.js dev server
pnpm dev

# Frontend is now available at http://localhost:3000
```

### 3. Test the Application

1. Open browser to `http://localhost:3000`
2. Click "Get Started" or "Start Enrollment"
3. Fill in registration form
4. Complete enrollment with 3 keystroke samples
5. Dashboard will show analytics

## API Integration

The frontend communicates with the backend at:
- **Development**: `http://localhost:8000`
- **Production**: Set via environment variables

### Environment Variables

Create `.env.local` in project root:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Endpoints

All endpoints return JSON:

```bash
# Health check
curl http://localhost:8000/health

# Enroll user
curl -X POST http://localhost:8000/auth/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "username": "Test User",
    "email": "test@example.com",
    "keystroke_samples": [[[...]], [[...]], [[...]]]
  }'

# Authenticate
curl -X POST http://localhost:8000/auth/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "keystrokes": [[...]],
    "session_id": "session-123"
  }'

# Get user profile
curl http://localhost:8000/users/test-user

# Get analytics
curl http://localhost:8000/analytics/summary
```

## Project Structure

```
project/
├── app/                          # Next.js pages
│   ├── page.tsx                  # Landing page
│   ├── register/page.tsx         # Registration
│   ├── enroll/page.tsx           # Enrollment wizard
│   ├── login/page.tsx            # Authentication
│   ├── dashboard/page.tsx        # Analytics dashboard
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Design system
├── components/
│   ├── KeystrokeCapture.tsx      # Keystroke input
│   └── AuthDecision.tsx          # Auth result display
├── backend/
│   ├── main.py                   # FastAPI server
│   └── crypto/
│       └── v2_crypto_layer.py    # Authentication engine
├── public/                       # Static files
├── package.json                  # Frontend deps
├── tsconfig.json                 # TypeScript config
└── README.md                     # Full documentation
```

## Common Issues & Fixes

### Backend not starting
```bash
# Check if port 8000 is in use
lsof -i :8000

# Or try different port
uvicorn main:app --port 8001
```

### CORS errors in frontend
- Backend CORS is configured for `localhost:3000`
- Make sure frontend is actually running on :3000
- Check browser console for exact error message

### Keystroke not capturing
- Ensure input field has focus
- Try typing more than 10 characters
- Check browser console for errors

### Module not found errors
```bash
# Frontend: missing deps
pnpm install

# Backend: missing deps
pip install -r requirements.txt  # If using requirements.txt
# OR
pip install fastapi uvicorn pydantic numpy scipy scikit-learn pandas
```

## Production Deployment

### Frontend (Vercel)
```bash
# Build
pnpm build

# Deploy to Vercel
vercel deploy

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL https://api.your-domain.com
```

### Backend (Any Cloud Provider)
```bash
# Create requirements.txt
pip freeze > requirements.txt

# Deploy with gunicorn
gunicorn main:app --workers 4 --bind 0.0.0.0:8000

# Or use Docker
docker build -t qshield-backend .
docker run -p 8000:8000 qshield-backend
```

### Environment Setup
```bash
# .env.production.local
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_ENV=production
```

## Performance Optimization

### Frontend
- Images are lazy-loaded
- Code splitting with dynamic imports
- CSS is optimized with Tailwind
- Next.js handles caching automatically

### Backend
- Async request handling
- In-memory user storage (for demo)
- Connection pooling ready for DB

## Monitoring & Debugging

### Frontend
- Open DevTools (F12)
- Check Network tab for API calls
- Look at Console for errors

### Backend
- API docs at `http://localhost:8000/docs`
- ReDoc at `http://localhost:8000/redoc`
- Use logging for debugging

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

## Testing Workflows

### Enrollment Flow
1. Register new user → enroll → get 3 keystroke samples
2. Verify user in backend: `GET /users/{user_id}`
3. Check enrollment data stored

### Authentication Flow
1. Submit keystroke sample
2. Verify score calculation
3. Check anomaly detection
4. Verify decision logic

### Analytics
1. Multiple authentications
2. Check history: `GET /auth/history?user_id={id}`
3. Verify metrics: `GET /metrics/fusion`

## Advanced Configuration

### Custom Keystroke Thresholds
In `components/KeystrokeCapture.tsx`:
```tsx
<KeystrokeCapture
  minKeystrokes={20}  // Require more keystrokes
  // ...
/>
```

### Custom Authentication Threshold
In `backend/main.py`:
```python
authenticated = (
    fused_score > 0.70 and  # Change threshold
    anomaly_zone != "CRITICAL"
)
```

### Database Integration
Replace in-memory storage in `main.py`:
```python
# Instead of:
users_db: Dict[str, Any] = {}

# Use:
from sqlalchemy import create_engine
engine = create_engine('postgresql://...')
```

## Support & Troubleshooting

For detailed troubleshooting:
1. See README.md
2. Check API docs: http://localhost:8000/docs
3. Review browser console
4. Check backend logs

---

Happy authenticating! 🔐
