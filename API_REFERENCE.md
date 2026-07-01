# Q-Shield v2 API Reference

Complete API documentation for the FastAPI backend.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.your-domain.com` (configure via env vars)

## Authentication

Currently uses session-based authentication. Future versions will support JWT tokens.

## Endpoints

### System & Health

#### GET /

Returns API information and status.

**Response:**
```json
{
  "name": "Q-Shield v2 Authentication Engine",
  "version": "2.0.0",
  "status": "operational",
  "docs_url": "/docs",
  "endpoints": {
    "health": "/health",
    "auth": "/auth/enroll, /auth/authenticate",
    "users": "/users/{user_id}",
    "analytics": "/auth/history, /analytics/summary",
    "metrics": "/metrics/eer, /metrics/roc, /metrics/fusion"
  }
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "operational",
  "version": "2.0.0",
  "timestamp": "2026-06-27T12:34:56.789Z"
}
```

---

### Authentication Endpoints

#### POST /auth/enroll

Enroll a new user with keystroke biometric samples.

**Request:**
```json
{
  "user_id": "john-doe-123",
  "username": "John Doe",
  "email": "john@example.com",
  "keystroke_samples": [
    [
      {
        "key": "S",
        "timestamp": 0,
        "duration": 45
      },
      {
        "key": "e",
        "timestamp": 52,
        "duration": 38
      }
    ],
    [],
    []
  ]
}
```

**Fields:**
- `user_id` (string, required): Unique identifier (3+ chars)
- `username` (string, required): Display name
- `email` (string, required): Valid email address
- `keystroke_samples` (array, required): 3+ keystroke sample arrays
  - Each sample is an array of keystroke events
  - Each event: `{ key: string, timestamp: number, duration?: number }`

**Response:**
```json
{
  "success": true,
  "user_id": "john-doe-123",
  "message": "User john-doe enrolled successfully",
  "samples_processed": 3
}
```

**Status Codes:**
- `200`: Enrollment successful
- `400`: Invalid input or insufficient samples
- `409`: User already enrolled
- `500`: Server error

---

#### POST /auth/authenticate

Authenticate a user via keystroke biometrics.

**Request:**
```json
{
  "user_id": "john-doe-123",
  "keystrokes": [
    {
      "key": "S",
      "timestamp": 0,
      "duration": 45
    },
    {
      "key": "e",
      "timestamp": 52,
      "duration": 38
    }
  ],
  "session_id": "session-1234567890"
}
```

**Fields:**
- `user_id` (string, required): User to authenticate
- `keystrokes` (array, required): Single keystroke sample
- `session_id` (string, required): Unique session identifier

**Response:**
```json
{
  "authenticated": true,
  "fused_score": 0.82,
  "llr": 4.123,
  "fidelity_ip": 0.75,
  "fidelity_bc": 0.88,
  "anomaly_zone": "LOW",
  "confidence": 0.64,
  "session_id": "session-1234567890",
  "timestamp": "2026-06-27T12:34:56.789Z",
  "message": "Access granted"
}
```

**Response Fields:**
- `authenticated` (boolean): Final authentication decision
- `fused_score` (number): Fused likelihood ratio (0-1)
- `llr` (number): Log-likelihood ratio
- `fidelity_ip` (number): IP-based fidelity metric (0-1)
- `fidelity_bc` (number): Behavioral/biometric fidelity (0-1)
- `anomaly_zone` (string): Anomaly level (LOW, MEDIUM, HIGH, CRITICAL)
- `confidence` (number): Confidence in decision (0-1)
- `session_id` (string): Session identifier
- `timestamp` (string): ISO 8601 timestamp
- `message` (string): Human-readable result

**Status Codes:**
- `200`: Authentication processed
- `404`: User not found
- `400`: User not enrolled
- `500`: Server error

---

### User Endpoints

#### GET /users/{user_id}

Get user profile and statistics.

**Parameters:**
- `user_id` (string, path): User identifier

**Response:**
```json
{
  "user_id": "john-doe-123",
  "username": "John Doe",
  "email": "john@example.com",
  "enrolled": true,
  "enrollment_date": "2026-06-27T10:15:00.000Z",
  "last_authentication": "2026-06-27T12:30:00.000Z",
  "total_authentications": 15,
  "failed_attempts": 2
}
```

**Status Codes:**
- `200`: Profile retrieved
- `404`: User not found

---

### Analytics Endpoints

#### GET /auth/history

Get authentication history with optional filtering.

**Query Parameters:**
- `user_id` (string, optional): Filter by user
- `limit` (integer, optional, default: 100): Maximum records to return

**Response:**
```json
[
  {
    "timestamp": "2026-06-27T12:30:00.000Z",
    "user_id": "john-doe-123",
    "authenticated": true,
    "fused_score": 0.82,
    "anomaly_zone": "LOW",
    "session_id": "session-1234567890"
  },
  {
    "timestamp": "2026-06-27T12:25:00.000Z",
    "user_id": "john-doe-123",
    "authenticated": false,
    "fused_score": 0.45,
    "anomaly_zone": "HIGH",
    "session_id": "session-1234567891"
  }
]
```

---

#### GET /analytics/summary

Get system-wide analytics summary.

**Response:**
```json
{
  "total_users": 42,
  "enrolled_users": 38,
  "total_authentications": 1250,
  "failed_authentications": 45,
  "success_rate": 96.4,
  "anomaly_distribution": {
    "LOW": 1100,
    "MEDIUM": 120,
    "HIGH": 25,
    "CRITICAL": 5
  },
  "system_timestamp": "2026-06-27T12:34:56.789Z"
}
```

---

### Metrics Endpoints

#### GET /metrics/eer

Get Equal Error Rate (EER) metrics.

**Response:**
```json
{
  "eer": 0.032,
  "far": 0.025,
  "frr": 0.040,
  "threshold": 0.65,
  "data_points": 1250
}
```

**Fields:**
- `eer` (number): Equal Error Rate (target is FAR = FRR)
- `far` (number): False Acceptance Rate
- `frr` (number): False Rejection Rate
- `threshold` (number): Current authentication threshold
- `data_points` (number): Number of authentications analyzed

---

#### GET /metrics/roc

Get ROC curve points.

**Response:**
```json
{
  "points": [
    {
      "threshold": 0.0,
      "tpr": 1.0,
      "fpr": 1.0
    },
    {
      "threshold": 0.1,
      "tpr": 0.98,
      "fpr": 0.95
    },
    ...
    {
      "threshold": 1.0,
      "tpr": 0.0,
      "fpr": 0.0
    }
  ],
  "auc": 0.978
}
```

**Fields:**
- `points` (array): ROC curve data points
  - `threshold` (number): Score threshold
  - `tpr` (number): True Positive Rate
  - `fpr` (number): False Positive Rate
- `auc` (number): Area Under Curve (0-1, higher is better)

---

#### GET /metrics/fusion

Get score fusion distribution metrics.

**Response:**
```json
{
  "distribution": {
    "0-10": 5,
    "10-20": 8,
    "20-30": 12,
    "30-40": 15,
    "40-50": 35,
    "50-60": 120,
    "60-70": 480,
    "70-80": 420,
    "80-90": 140,
    "90-100": 15
  },
  "mean": 0.67,
  "std": 0.15,
  "min": 0.12,
  "max": 0.98,
  "data_points": 1250
}
```

**Fields:**
- `distribution` (object): Score histogram (10% buckets)
- `mean` (number): Mean fused score (0-1)
- `std` (number): Standard deviation
- `min` (number): Minimum score observed
- `max` (number): Maximum score observed
- `data_points` (number): Total samples

---

## Error Responses

All errors return JSON with `detail` field:

```json
{
  "detail": "User not found"
}
```

### Common Error Codes

| Code | Error | Solution |
|------|-------|----------|
| 400 | Bad Request | Check JSON format and required fields |
| 404 | Not Found | User doesn't exist, verify user_id |
| 409 | Conflict | User already enrolled, use different ID |
| 500 | Server Error | Backend issue, check logs |

---

## Rate Limiting

Not currently implemented. Recommended for production:
- 10 enrollments per minute per IP
- 100 authentications per minute per user
- 1000 requests per minute per IP

---

## CORS

Frontend CORS origins configured for:
- `http://localhost:3000`
- `http://localhost:3001`
- `*` (development)

**Production**: Update `app.add_middleware()` in `main.py`

---

## Examples

### cURL Examples

#### Enroll User
```bash
curl -X POST http://localhost:8000/auth/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john-doe",
    "username": "John Doe",
    "email": "john@example.com",
    "keystroke_samples": [
      [{"key":"h","timestamp":0,"duration":50}],
      [{"key":"h","timestamp":0,"duration":48}],
      [{"key":"h","timestamp":0,"duration":52}]
    ]
  }'
```

#### Authenticate
```bash
curl -X POST http://localhost:8000/auth/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john-doe",
    "keystrokes": [{"key":"h","timestamp":0,"duration":49}],
    "session_id": "session-123"
  }'
```

#### Get Analytics
```bash
curl http://localhost:8000/analytics/summary | python -m json.tool
```

### JavaScript/TypeScript Example

```typescript
const API_URL = 'http://localhost:8000'

// Enroll user
async function enrollUser(userId: string, keystrokes: any[]) {
  const response = await fetch(`${API_URL}/auth/enroll`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      username: 'User Name',
      email: 'user@example.com',
      keystroke_samples: [keystrokes, keystrokes, keystrokes],
    }),
  })
  return response.json()
}

// Authenticate user
async function authenticateUser(userId: string, keystrokes: any[]) {
  const response = await fetch(`${API_URL}/auth/authenticate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      keystrokes,
      session_id: `session-${Date.now()}`,
    }),
  })
  return response.json()
}
```

---

## WebSocket Support

Not currently implemented. Recommended for real-time updates:
- Live authentication results
- Real-time dashboard updates
- Anomaly alerts

---

## Versioning

Current version: **2.0.0**

API is backward compatible. Breaking changes will increment major version.

---

## Support

- Interactive Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`
- See SETUP.md for troubleshooting
