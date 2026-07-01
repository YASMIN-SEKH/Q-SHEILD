# Q-Shield v2 Quick Reference

## 30-Second Overview

Q-Shield v2 is a quantum-resistant keystroke biometric authentication system:
- **Frontend**: Next.js 16 dark theme with glassmorphic design
- **Backend**: FastAPI with ML-powered authentication engine
- **Authentication**: Captures typing patterns (dwell time, flight time, etc.)
- **Analytics**: Real-time metrics, EER, ROC curves, anomaly detection

---

## Quick Start

### 1. Start Backend (Terminal 1)
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend (Terminal 2)
```bash
pnpm dev
```

### 3. Open Browser
```
http://localhost:3000
```

---

## Key URLs

| What | Where |
|------|-------|
| App | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## User Flow

1. **Home** → Click "Get Started"
2. **Register** → Fill in user ID, username, email
3. **Enroll** → Complete 3 keystroke samples (15+ keys each)
4. **Dashboard** → View analytics and authentication history

---

## Authentication Flow

1. User enters User ID
2. System captures 15+ keystrokes
3. Backend analyzes keystroke patterns
4. Returns decision: Accept/Reject
5. Shows confidence and anomaly level

---

## File Guide

| File | Purpose | Lines |
|------|---------|-------|
| `app/page.tsx` | Landing page | 234 |
| `app/register/page.tsx` | Registration | 186 |
| `app/enroll/page.tsx` | Enrollment | 264 |
| `app/login/page.tsx` | Authentication | 246 |
| `app/dashboard/page.tsx` | Analytics | 314 |
| `backend/main.py` | FastAPI server | 405 |
| `components/KeystrokeCapture.tsx` | Input component | 232 |
| `components/AuthDecision.tsx` | Result display | 224 |

---

## API Endpoints

### Enroll User
```bash
POST /auth/enroll
{
  "user_id": "john-doe",
  "username": "John Doe",
  "email": "john@example.com",
  "keystroke_samples": [...]  # 3 samples minimum
}
```

### Authenticate
```bash
POST /auth/authenticate
{
  "user_id": "john-doe",
  "keystrokes": [...],
  "session_id": "session-123"
}
```

### Get User Profile
```bash
GET /users/john-doe
```

### Get Analytics
```bash
GET /analytics/summary
GET /metrics/eer
GET /metrics/roc
GET /metrics/fusion
```

---

## Key Metrics

- **Fused Score**: 0-1 (higher = more confident)
- **LLR**: Log-likelihood ratio (numeric score)
- **Fidelity IP**: IP-based authentication confidence
- **Fidelity BC**: Behavioral/biometric confidence
- **Anomaly Zone**: LOW | MEDIUM | HIGH | CRITICAL

---

## Decision Logic

```
IF (fused_score > 0.65) AND (anomaly_zone != "CRITICAL")
  THEN authenticated = TRUE
  ELSE authenticated = FALSE
```

---

## Components

### KeystrokeCapture
Captures and displays keystroke metrics in real-time
- Shows: dwell time, flight time, latency, hold time
- Animated progress bar
- Validation feedback

### AuthDecision
Displays authentication results
- Accept/Reject icon
- Confidence score with gradient
- Detailed metric breakdown
- Anomaly zone indicator

### MetricCard
Reusable card for displaying metrics
- Icon support
- Trend indicators
- Gradient backgrounds

---

## Colors

| Name | Hex | Use |
|------|-----|-----|
| Background | #0a0e27 | Main background |
| Primary Cyan | #00d9ff | Buttons, primary accents |
| Secondary Purple | #b024d9 | Secondary accents, gradients |
| Card | #15192d | Card backgrounds |
| Text | #e8f0ff | Primary text |
| Muted | #8b94b8 | Secondary text |

---

## Environment Setup

### Frontend
```bash
pnpm install
NEXT_PUBLIC_API_URL=http://localhost:8000 pnpm dev
```

### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic numpy scipy scikit-learn pandas
uvicorn main:app --reload
```

---

## Troubleshooting

### Backend not responding
```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn main:app --port 8001
```

### Frontend build error
```bash
# Clear cache and reinstall
rm -rf .next node_modules pnpm-lock.yaml
pnpm install
```

### CORS errors
- Check backend CORS config in `main.py`
- Ensure frontend runs on :3000
- Check browser console for exact error

### Keystroke not capturing
- Ensure input field has focus
- Type more than 10 characters
- Check browser console

---

## Testing Workflow

### Enrollment
1. Register new user
2. Complete 3 keystroke samples
3. Verify user created: `GET /users/{user_id}`

### Authentication
1. Navigate to login
2. Enter user ID
3. Enter keystroke sample
4. Verify score returned
5. Check anomaly zone

### Analytics
1. Do multiple authentications
2. Check history: `GET /auth/history?user_id={id}`
3. View dashboard metrics

---

## Production Checklist

- [ ] Set up database
- [ ] Configure HTTPS/SSL
- [ ] Set environment variables
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test disaster recovery
- [ ] Security audit

---

## Key Concepts

**Keystroke Biometrics**: Authentication based on unique typing patterns
**Dwell Time**: How long a key is held down
**Flight Time**: Time between key release and next press
**Anomaly Detection**: Identifying unusual typing patterns
**Fused Score**: Combined metric from multiple sources
**Equal Error Rate**: Balance between false accepts and rejects

---

## Documentation Files

1. **README.md** - Full documentation
2. **SETUP.md** - Installation guide
3. **API_REFERENCE.md** - API details
4. **IMPLEMENTATION_SUMMARY.md** - Technical overview
5. **QUICK_REFERENCE.md** - This file

---

## Support

- FastAPI Docs: http://localhost:8000/docs
- Swagger UI available at /docs
- ReDoc available at /redoc
- See README.md for detailed troubleshooting

---

**Status**: ✅ Production Ready
**Version**: 2.0.0
**Last Updated**: June 2026
