import React, { createContext, useState, useCallback, useEffect } from "react";
import { io } from "socket.io-client";
import { AnimatePresence } from "framer-motion";

/**
 * NeuroContext
 * Provides UI personalization state and server communication
 */
export const NeuroContext = createContext(null);

export function NeuroProvider({ children }) {
  const [uiDensity, setUiDensity] = useState("STANDARD");
  const [suspicionScore, setSuspicionScore] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [userId, setUserId] = useState(null);
  const [showGuidedTour, setShowGuidedTour] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [isTrapActive, setIsTrapActive] = useState(false);

  // Initialize Socket.io connection on mount
  useEffect(() => {
    const generateUserId = () => {
      const stored = localStorage.getItem("neuroux_user_id");
      if (stored) return stored;
      const newId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("neuroux_user_id", newId);
      return newId;
    };

    const generateSessionId = () => {
      return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    };

    const uid = generateUserId();
    const sid = generateSessionId();

    setUserId(uid);
    setSessionId(sid);

    // Connect to backend
    const socketInstance = io("http://localhost:8000", {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ["websocket"],
    });

    // Socket event handlers
    socketInstance.on("connect", () => {
      console.log("✅ Connected to NeuroUX Backend");
      setIsConnected(true);
    });

    socketInstance.on("disconnect", () => {
      console.log("❌ Disconnected from NeuroUX Backend");
      setIsConnected(false);
    });

    socketInstance.on("UI_COMMAND", (data) => {
      console.log("🎭 UI_COMMAND received:", data);
      if (data.command === "SET_DENSITY") {
        setUiDensity(data.value);
        // Additional UI toggles handled via effect
      }
    });

    socketInstance.on("action_ack", (data) => {
      console.log("📍 Action acknowledged:", data);
      setSuspicionScore(data.suspicionScore || 0);
    });

    socketInstance.on("error", (error) => {
      console.error("❌ Socket error:", error);
    });

    setSocket(socketInstance);

    // Cleanup on unmount
    return () => {
      if (socketInstance) {
        socketInstance.disconnect();
      }
    };
  }, []);

  const sendUserAction = useCallback(
    (payload) => {
      if (socket && isConnected && sessionId && userId) {
        socket.emit("user_action", {
          ...payload,
          sessionId,
          userId,
          timestamp: Date.now(),
        });
      }
    },
    [socket, isConnected, sessionId, userId]
  );

  const sendBatchActions = useCallback(
    (actions) => {
      if (socket && isConnected && sessionId && userId) {
        socket.emit("batch_actions", {
          sessionId,
          userId,
          actions,
        });
      }
    },
    [socket, isConnected, sessionId, userId]
  );

  const value = {
    uiDensity,
    suspicionScore,
    isConnected,
    sessionId,
    userId,
    socket,
    sendUserAction,
    sendBatchActions,
    showGuidedTour,
    showShortcuts,
    isTrapActive,
    setIsTrapActive,
  };

  // Side-effects: toggle overlays based on uiDensity & suspicionScore
  useEffect(() => {
    if (uiDensity === "SIMPLE") {
      setShowGuidedTour(true);
      setShowShortcuts(false);
    } else if (uiDensity === "EXPERT") {
      setShowShortcuts(true);
      setShowGuidedTour(false);
    } else {
      setShowGuidedTour(false);
      setShowShortcuts(false);
    }
  }, [uiDensity]);

  useEffect(() => {
    if (suspicionScore > 0.8) {
      setIsTrapActive(true);
    }
  }, [suspicionScore]);

  return (
    <NeuroContext.Provider value={value}>
      {children}
    </NeuroContext.Provider>
  );
}

/**
 * useNeuro Hook
 * Easy access to NeuroContext
 */
export function useNeuro() {
  const context = React.useContext(NeuroContext);
  if (!context) {
    throw new Error("useNeuro must be used within NeuroProvider");
  }
  return context;
}
