# NeuroUX - Phase 1: The Foundation

Self-Adapting Intelligent Web Interface for Real-time UI Personalization and Fraud Detection

## Project Overview

**NeuroUX** is an MVP that solves two critical problems:

1. **Real-time UI Personalization**: Adapts interface density (SIMPLE, STANDARD, EXPERT) based on detected user behavior
2. **Fraud Detection**: Identifies "Impossible Paths" in user flows using DAG validation and velocity checks

## Architecture

### Tech Stack

**Frontend:**
- React 18 with Vite
- Tailwind CSS for styling
- Framer Motion for animations
- Socket.io-client for real-time communication
- React Router DOM for navigation

**Backend:**
- FastAPI (Python)
- Python-socketio for WebSocket support
- Uvicorn ASGI server
- Pydantic for data validation

## Project Structure

```
NeuroUX/
├── backend/
│   ├── main.py              # FastAPI app + Socket.io server
│   ├── models.py            # Domain models (DAGValidator, UserSession, etc.)
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── AdaptiveUI.jsx       # Density-aware UI components
│   │   ├── context/
│   │   │   └── NeuroProvider.jsx    # Global state + Socket.io setup
│   │   ├── hooks/
│   │   │   └── useNeuroTracker.js   # Event tracking hook (1s buffer)
│   │   ├── App.jsx                  # Main app with Navbar, Hero, Grid
│   │   ├── main.jsx                 # React entry point
│   │   └── index.css                # Tailwind + custom styles
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
```

## Core Features - Phase 1

### 1. Backend Architecture (main.py)

**FastAPI Setup:**
- CORS enabled for frontend communication
- Health check endpoint: `GET /health`
- DAG endpoint: `GET /dag`
- Session endpoint: `GET /session/{session_id}`

**Socket.io Integration:**
- Asynchronous event handlers
- Real-time bidirectional communication
- Automatic reconnection with exponential backoff

### 2. Event Ingestor (user_action handler)

Receives JSON payload:
```json
{
  "userId": "user123",
  "sessionId": "sess_abc123",
  "actionType": "click|scroll|navigate",
  "currentPath": "/home",
  "targetPath": "/products",
  "timestamp": 1234567890000,
  "elementId": "btn-explore"
}
```

### 3. PS3 Foundation Logic

**Path Validation:**
- Validates transitions using DAG (Directed Acyclic Graph)
- Flags invalid paths with `is_invalid_path: true`
- Suspicion score += 0.3 for invalid paths

**Velocity Check:**
- Calculates time delta between consecutive actions
- Flags as bot if navigation happens in < 200ms
- Suspicion score += 0.5 for bot-like velocity

### 4. Frontend Nervous System (useNeuroTracker.js)

**Global Event Listeners:**
- Click tracking with element ID capture
- Scroll tracking for engagement metrics
- Automatic path tracking via React Router

**Micro-Batching:**
- 1-second buffer for action batching
- Reduces server load
- Sends via `batch_actions` Socket.io event

**Payload Structure:**
```json
{
  "type": "CLICK",
  "elementId": "btn-explore",
  "path": "/home",
  "time": 1234567890000
}
```

### 5. NeuroProvider Context API

**State Management:**
- `uiDensity`: SIMPLE | STANDARD | EXPERT
- `suspicionScore`: 0.0 - 1.0
- `isConnected`: WebSocket connection status
- `sessionId` & `userId`: Session tracking

**Socket.io Listeners:**
- `connection_response`: Connection confirmation
- `UI_COMMAND`: Adaptive UI instructions
- `action_ack`: Action acknowledgment
- `error`: Error handling

### 6. Adaptive UI Components

**DensityWrapper:**
```javascript
// SIMPLE: max-w-2xl, text-2xl, gap-12
// STANDARD: max-w-4xl, text-base, gap-6
// EXPERT: max-w-full, text-xs, grid-cols-6, gap-2
```

**AdaptiveGrid & AdaptiveText:**
- Conditional Tailwind classes
- Responsive to `uiDensity` context changes
- Smooth transitions via Framer Motion

## Running the Project

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run FastAPI server:**
   ```bash
   python main.py
   ```
   
   Server will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   
   App will open at `http://localhost:5173`

## Testing the System

### 1. Open Developer Console (Frontend)

Monitor Socket.io events:
- `✅ Connected to NeuroUX Backend` - Connection established
- `📍 Action buffered: CLICK on /home` - User interactions tracked
- `📦 Flushing X buffered actions` - Batch send to backend

### 2. Backend Logs

Monitor event processing:
- `🆕 New session created` - Session initialized
- `📍 Action received` - Action processed
- `🎭 UI Density Changed` - Adaptive UI triggered

### 3. Test Bot Detection

Rapidly click elements in < 200ms intervals to trigger bot detection:
- `is_potential_bot: true` flag set
- `suspicionScore` increases
- UI density adapts to SIMPLE

## Data Models

### UserAction
```python
{
  "action_id": "uuid",
  "user_id": "string",
  "session_id": "string",
  "action_type": "click|scroll|navigate",
  "current_path": "string",
  "target_path": "string",
  "timestamp": int,
  "is_invalid_path": bool,
  "is_potential_bot": bool,
  "suspicion_score": float
}
```

### UserSession
```python
{
  "session_id": "string",
  "user_id": "string",
  "created_at": datetime,
  "actions": [UserAction],
  "suspicion_score": float,
  "current_density": "SIMPLE|STANDARD|EXPERT"
}
```

### DAGValidator

Validates user flow transitions:
```python
VALID_DAG = {
  "Home": ["Products", "Profile", "Settings"],
  "Products": ["ProductDetail", "Cart", "Home"],
  "ProductDetail": ["Cart", "Products", "Home"],
  "Cart": ["Checkout", "Products", "Home"],
  "Checkout": ["OrderConfirmation", "Home"],
  "OrderConfirmation": ["Home", "Products"],
  "Profile": ["Home", "Settings"],
  "Settings": ["Home", "Profile"],
}
```

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/dag` | Get valid flow DAG |
| GET | `/session/{session_id}` | Get session details |
| WS | Socket.io `user_action` | Submit user action |
| WS | Socket.io `batch_actions` | Submit batched actions |
| WS | Socket.io `UI_COMMAND` | Receive UI instructions |

## Phase 2 Roadmap

- [ ] MongoDB integration with Motor driver
- [ ] Isolation Forest ML model for anomaly detection
- [ ] User behavior clustering
- [ ] Predictive UI adaptation
- [ ] Advanced analytics dashboard
- [ ] Rate limiting and security

## License

MIT

---

**Built for the Hackathon 2026**  
🧠 NeuroUX: Where AI Meets UX
