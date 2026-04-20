"""
NeuroUX Backend - FastAPI with Socket.io Integration
Phase 2: Intelligence Cortex - ML-Powered Anomaly Detection
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from socketio import AsyncServer

from models import DAGValidator, UserSession, UserAction, UIDensity
from intelligence_engine import BehavioralAnalyzer

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NeuroUX")

# ============================================================================
# ML CORTEX INITIALIZATION
# ============================================================================
analyzer = BehavioralAnalyzer()
logger.info("✨ Phase 2: Intelligence Cortex loaded and ready")


async def _periodic_ml_check():
    """Background task: run ML prediction every 5 seconds for active sessions."""
    while True:
        try:
            await asyncio.sleep(5)
            for session_id, session in list(active_sessions.items()):
                try:
                    features = analyzer.extract_session_features(session)
                    is_anom, conf = analyzer.predict_anomaly(session_id, features)
                    if is_anom:
                        # Increase suspicion and notify client
                        session.suspicion_score = min(1.0, session.suspicion_score + 0.4)
                        logger.warning(f"[ML-PERIODIC] Session {session_id} anomalous ({conf:.1f}%), suspicion -> {session.suspicion_score:.2f}")
                        # emit reorder event to client's socket
                        try:
                            await sio.emit("REORDER_COMPONENTS", {"reason": "ml_anomaly", "confidence": conf}, to=session.socket_id)
                        except Exception:
                            logger.exception("Failed to emit REORDER_COMPONENTS")
                except Exception:
                    logger.exception("Error during ML prediction for session %s", session_id)
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Error in periodic ML check loop")

# ============================================================================
# SOCKET.IO SERVER SETUP
# ============================================================================
sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # In production, specify exact origins
    ping_timeout=60,
    ping_interval=25,
)

# ============================================================================
# IN-MEMORY STORAGE (Phase 1 - Will migrate to MongoDB in Phase 2)
# ============================================================================
active_sessions: Dict[str, UserSession] = {}
action_buffer: Dict[str, list] = {}  # sessionId -> [actions]

# ============================================================================
# DAG INITIALIZATION (Valid User Flow Graph)
# ============================================================================
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

dag_validator = DAGValidator(graph=VALID_DAG)

# ============================================================================
# FASTAPI LIFESPAN CONTEXT
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI app lifecycle"""
    logger.info("🚀 NeuroUX Backend Starting...")
    # start periodic ML background task
    ml_task = asyncio.create_task(_periodic_ml_check())
    try:
        yield
    finally:
        ml_task.cancel()
        try:
            await ml_task
        except asyncio.CancelledError:
            pass
        logger.info("🛑 NeuroUX Backend Shutting Down...")


# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================
app = FastAPI(title="NeuroUX Backend", version="1.0.0", lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.io
sio_app = AsyncServer.ASGIApp(sio, app) if hasattr(AsyncServer, 'ASGIApp') else None

# Alternatively, use the ASGI wrapper from socketio
from socketio import ASGIApp
sio_app = ASGIApp(sio, app)

# ============================================================================
# REST API ENDPOINTS
# ============================================================================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(active_sessions),
    }


@app.get("/dag")
async def get_dag():
    """Return the valid DAG for frontend validation"""
    return {"dag": VALID_DAG}


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return {
        "sessionId": session.session_id,
        "userId": session.user_id,
        "createdAt": session.created_at,
        "actionCount": len(session.actions),
        "suspicionScore": session.suspicion_score,
        "currentDensity": session.current_density,
    }


@app.get("/api/admin/debug")
async def honey_pot_debug(sessionId: Optional[str] = None):
    """Hidden honey-pot endpoint: if visited with a sessionId, mark it as fully suspicious."""
    if not sessionId:
        return JSONResponse({"detail": "sessionId required"}, status_code=400)

    if sessionId not in active_sessions:
        return JSONResponse({"detail": "session not found"}, status_code=404)

    session = active_sessions[sessionId]
    session.suspicion_score = 1.0
    logger.warning(f"[HONEY-POT] Session {sessionId} hit honey-pot. suspicion -> 1.0")
    try:
        await sio.emit(
            "UI_COMMAND",
            {
                "command": "SET_DENSITY",
                "value": UIDensity.SIMPLE.value,
                "reason": "Honey-pot triggered - immediate lockdown",
            },
            to=session.socket_id,
        )
    except Exception:
        logger.exception("Failed to notify client of honey-pot")

    return {"ok": True, "sessionId": sessionId, "suspicionScore": session.suspicion_score}


# ============================================================================
# SOCKET.IO EVENT HANDLERS
# ============================================================================
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"✅ Client connected: {sid}")
    await sio.emit("connection_response", {"data": "Connected to NeuroUX"}, to=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"❌ Client disconnected: {sid}")
    # Clean up session if exists
    if sid in active_sessions:
        del active_sessions[sid]
    if sid in action_buffer:
        del action_buffer[sid]


@sio.event
async def user_action(sid: str, data: Dict[str, Any]):
    """
    Main event handler for user actions
    
    Expected payload:
    {
        "userId": "user123",
        "sessionId": "sess_abc123",
        "actionType": "click|scroll|navigate",
        "currentPath": "/home",
        "targetPath": "/products",
        "timestamp": 1234567890000,
        "elementId": "btn-explore" (optional)
    }
    """
    try:
        # ========== PAYLOAD VALIDATION ==========
        required_fields = ["userId", "sessionId", "actionType", "currentPath", "timestamp"]
        if not all(field in data for field in required_fields):
            logger.warning(f"Invalid payload from {sid}: missing required fields")
            await sio.emit("error", {"message": "Invalid payload"}, to=sid)
            return

        # ========== SESSION INITIALIZATION ==========
        session_id = data.get("sessionId")
        user_id = data.get("userId")

        if session_id not in active_sessions:
            active_sessions[session_id] = UserSession(
                session_id=session_id,
                user_id=user_id,
                socket_id=sid,
            )
            action_buffer[session_id] = []
            logger.info(f"🆕 New session created: {session_id}")

        session = active_sessions[session_id]

        # ========== CREATE USER ACTION OBJECT ==========
        action = UserAction(
            user_id=user_id,
            session_id=session_id,
            action_type=data.get("actionType"),
            current_path=data.get("currentPath"),
            target_path=data.get("targetPath", data.get("currentPath")),
            element_id=data.get("elementId"),
            timestamp=data.get("timestamp"),
        )

        # ========== PATH VALIDATION (PS3 Foundation - Part 1) ==========
        is_valid_path = True
        path_validation_error = None

        if action.action_type == "navigate":
            is_valid = dag_validator.validate_transition(
                from_path=action.current_path,
                to_path=action.target_path,
            )
            if not is_valid:
                is_valid_path = False
                path_validation_error = (
                    f"Invalid path: {action.current_path} -> {action.target_path}"
                )
                action.is_invalid_path = True
                action.suspicion_score += 0.3  # Penalize invalid paths

        # ========== VELOCITY CHECK (PS3 Foundation - Part 2) ==========
        is_potential_bot = False
        time_delta_ms = 0

        if session.actions:
            last_action = session.actions[-1]
            time_delta_ms = action.timestamp - last_action.timestamp
            
            # Flag as potential bot if navigation happens in < 200ms
            if action.action_type == "navigate" and time_delta_ms < 200:
                is_potential_bot = True
                action.is_potential_bot = True
                action.suspicion_score += 0.5  # High suspicion for inhuman velocity

        # Add action to session and buffer
        session.actions.append(action)
        action_buffer[session_id].append(action)

        # ========== ML CORTEX ANALYSIS (Phase 2) ==========
        ml_features = analyzer.extract_session_features(session)
        is_anomalous, ml_confidence = analyzer.predict_anomaly(session_id, ml_features)
        
        if is_anomalous:
            # ML Model detected anomalous behavior
            action.suspicion_score += 0.4
            logger.warning(f"[ML] 🚨 Session {session_id}: Anomaly detected! Confidence: {ml_confidence:.1f}%")
        
        # Apply weighted decay for personalization
        weighted_score = analyzer.calculate_weighted_decay(
            [{"time": a.timestamp, "weight": 1.0} for a in session.actions[-10:]],
            action.timestamp,
            lambda_factor=0.1
        )

        # Update session metrics
        session.suspicion_score = max(session.suspicion_score, action.suspicion_score)
        session.last_action_time = action.timestamp

        # ========== ADAPTIVE UI DECISION (Chameleon Logic) ==========
        new_density = session.current_density
        ui_reason = "No change"
        
        if session.suspicion_score > 0.75:
            new_density = UIDensity.SIMPLE  # Restrict UI for suspicious users
            ui_reason = "High suspicion: Activated SIMPLE mode (Guided Tour)"
        elif session.suspicion_score > 0.4:
            new_density = UIDensity.STANDARD
            ui_reason = "Medium suspicion: STANDARD mode active"
        else:
            new_density = UIDensity.EXPERT  # Trust human users
            ui_reason = "Low suspicion: EXPERT mode unlocked (Advanced controls)"
        
        if new_density != session.current_density:
            session.current_density = new_density
            logger.info(f"🎭 UI Density Changed: {session_id} -> {new_density} ({ui_reason})")
            
            # Emit adaptive UI command to client
            await sio.emit(
                "UI_COMMAND",
                {
                    "command": "SET_DENSITY",
                    "value": new_density,
                    "reason": ui_reason,
                    "weighted_decay_score": weighted_score,
                    "ml_confidence": ml_confidence,
                },
                to=sid,
            )

        # ========== LOG AND EMIT FEEDBACK ==========
        logger.info(
            f"📍 Action received - Session: {session_id}, Type: {action.action_type}, "
            f"Path: {action.current_path} -> {action.target_path}, "
            f"ΔT: {time_delta_ms}ms, Valid: {is_valid_path}, Bot: {is_potential_bot}, "
            f"ML_Anomaly: {is_anomalous}"
        )

        # Send acknowledgment to client
        await sio.emit(
            "action_ack",
            {
                "received": True,
                "actionId": action.action_id,
                "pathValid": is_valid_path,
                "isPotentialBot": is_potential_bot,
                "suspicionScore": session.suspicion_score,
                "mlConfidence": ml_confidence,
                "currentDensity": new_density,
            },
            to=sid,
        )


        # ========== ADAPTIVE UI COMMAND (Based on suspicion score) ==========
        # Phase 1: Simple density adaptation
        new_density = UIDensity.STANDARD
        if session.suspicion_score > 0.7:
            new_density = UIDensity.SIMPLE
        elif session.suspicion_score < 0.2:
            new_density = UIDensity.EXPERT

        if new_density != session.current_density:
            session.current_density = new_density
            logger.info(f"🎭 UI Density Changed: {session_id} -> {new_density.value}")
            
            # Emit UI_COMMAND to client
            await sio.emit(
                "UI_COMMAND",
                {
                    "command": "SET_DENSITY",
                    "value": new_density.value,
                    "reason": "Adaptive UI based on behavior analysis",
                },
                to=sid,
            )

    except Exception as e:
        logger.error(f"❌ Error processing user_action: {str(e)}")
        await sio.emit("error", {"message": f"Server error: {str(e)}"}, to=sid)


@sio.event
async def batch_actions(sid: str, data: Dict[str, Any]):
    """
    Handle batched actions from frontend
    
    Expected payload:
    {
        "sessionId": "sess_abc123",
        "userId": "user123",
        "actions": [
            { "type": "CLICK", "elementId": "btn-1", "path": "/home", "time": 123456 },
            { "type": "SCROLL", "elementId": "main", "path": "/home", "time": 123457 },
        ]
    }
    """
    try:
        actions_list = data.get("actions", [])
        for action_data in actions_list:
            # Convert batch format to user_action format
            converted = {
                "userId": data.get("userId"),
                "sessionId": data.get("sessionId"),
                "actionType": action_data.get("type", "click").lower(),
                "currentPath": action_data.get("path", "/"),
                "targetPath": action_data.get("targetPath", action_data.get("path", "/")),
                "elementId": action_data.get("elementId"),
                "timestamp": action_data.get("time", int(datetime.utcnow().timestamp() * 1000)),
            }
            await user_action(sid, converted)

        logger.info(f"📦 Batch processed: {len(actions_list)} actions from {sid}")

    except Exception as e:
        logger.error(f"❌ Error processing batch_actions: {str(e)}")
        await sio.emit("error", {"message": f"Batch processing error: {str(e)}"}, to=sid)


@sio.event
async def ping(sid):
    """Handle keepalive ping from client"""
    await sio.emit("pong", to=sid)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:sio_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
