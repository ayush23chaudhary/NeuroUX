import { useEffect, useRef, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { useNeuro } from "../context/NeuroProvider";

/**
 * useNeuroTracker Hook - Phase 2 Enhanced
 * Tracks user interactions including rage click detection
 * Implements micro-batching with 1-second buffer
 */
export function useNeuroTracker() {
  const { sendUserAction, sendBatchActions } = useNeuro();
  const location = useLocation();
  const actionBufferRef = useRef([]);
  const flushTimerRef = useRef(null);
  const lastPathRef = useRef(location.pathname);
  const clickHistoryRef = useRef({}); // Track clicks per elementId
  const hoverHistoryRef = useRef({}); // Track hover events per elementId

  // Rage Click Detection Parameters
  const RAGE_CLICK_TIMEOUT = 500; // ms window
  const RAGE_CLICKS_THRESHOLD = 3; // 3+ clicks = rage
  const HOVER_CHAOS_TIMEOUT = 1000; // ms window
  const HOVER_CHAOS_THRESHOLD = 8; // many rapid hovers = chaos

  // ========== BUFFER FLUSHING ==========
  const flushBuffer = useCallback(() => {
    if (actionBufferRef.current.length > 0) {
      console.log(`📦 Flushing ${actionBufferRef.current.length} buffered actions`);
      sendBatchActions(actionBufferRef.current);
      actionBufferRef.current = [];
    }
  }, [sendBatchActions]);

  const scheduleFlush = useCallback(() => {
    if (flushTimerRef.current) {
      clearTimeout(flushTimerRef.current);
    }
    flushTimerRef.current = setTimeout(() => {
      flushBuffer();
    }, 1000); // 1-second buffer
  }, [flushBuffer]);

  // ========== TRACK ACTIONS ==========
  const trackAction = useCallback(
    (type, elementId = null, targetPath = null) => {
      const action = {
        type,
        elementId,
        path: location.pathname,
        targetPath: targetPath || location.pathname,
        time: Date.now(),
      };

      // Add to buffer
      actionBufferRef.current.push(action);

      // Schedule flush
      scheduleFlush();

      console.log(`📍 Action buffered: ${type} on ${location.pathname}`);
    },
    [location.pathname, scheduleFlush]
  );

  const trackClick = useCallback(
    (event) => {
      const target = event.target;
      const elementId = target.id || target.className || target.tagName;
      const now = Date.now();
      
      // Skip internal UI elements
      if (!elementId || elementId.startsWith("neuro-")) {
        return;
      }

      // ========== RAGE CLICK DETECTION (Phase 2) ==========
      // Initialize or filter old clicks for this element
      if (!clickHistoryRef.current[elementId]) {
        clickHistoryRef.current[elementId] = [];
      }

      // Remove clicks outside the rage window
      clickHistoryRef.current[elementId] = clickHistoryRef.current[elementId]
        .filter(t => now - t < RAGE_CLICK_TIMEOUT);

      // Add current click
      clickHistoryRef.current[elementId].push(now);

      // Check if rage click detected
      if (clickHistoryRef.current[elementId].length >= RAGE_CLICKS_THRESHOLD) {
        console.warn(`😠 RAGE CLICK DETECTED on ${elementId}! Clicks: ${clickHistoryRef.current[elementId].length}`);
        
        // Send frustration event immediately
        sendUserAction({
          actionType: "EVENT_FRUSTRATION",
          elementId: elementId,
          currentPath: location.pathname,
          rageClickCount: clickHistoryRef.current[elementId].length,
        });

        // Reset for this element
        clickHistoryRef.current[elementId] = [];
      }

      // Regular click tracking
      trackAction("CLICK", elementId);
    },
    [trackAction, sendUserAction, location.pathname]
  );

  const trackScroll = useCallback(() => {
    trackAction("SCROLL", "window");
  }, [trackAction]);

  const trackHover = useCallback((event) => {
    const target = event.target;
    const elementId = target.id || target.className || target.tagName;
    const now = Date.now();

    if (!elementId || elementId.startsWith("neuro-")) return;

    if (!hoverHistoryRef.current[elementId]) hoverHistoryRef.current[elementId] = [];
    hoverHistoryRef.current[elementId] = hoverHistoryRef.current[elementId].filter(t => now - t < HOVER_CHAOS_TIMEOUT);
    hoverHistoryRef.current[elementId].push(now);

    if (hoverHistoryRef.current[elementId].length >= HOVER_CHAOS_THRESHOLD) {
      console.warn(`🌀 HOVER CHAOS detected on ${elementId}`);
      sendUserAction({
        actionType: "EVENT_FRUSTRATION",
        elementId,
        currentPath: location.pathname,
        reason: "hover_chaos",
        count: hoverHistoryRef.current[elementId].length,
      });
      // reset
      hoverHistoryRef.current[elementId] = [];
    }
    // also track as non-batched action for analytics
    trackAction("HOVER", elementId);
  }, [location.pathname, sendUserAction, trackAction]);

  // ========== PATH CHANGE TRACKING ==========
  useEffect(() => {
    if (location.pathname !== lastPathRef.current) {
      console.log(
        `🔀 Navigation detected: ${lastPathRef.current} -> ${location.pathname}`
      );

      // Send navigate action immediately
      sendUserAction({
        actionType: "navigate",
        currentPath: lastPathRef.current,
        targetPath: location.pathname,
      });

      lastPathRef.current = location.pathname;
    }
  }, [location.pathname, sendUserAction]);

  // ========== EVENT LISTENER SETUP ==========
  useEffect(() => {
    window.addEventListener("click", trackClick);
    window.addEventListener("scroll", trackScroll);
    window.addEventListener("mouseover", trackHover);

    return () => {
      window.removeEventListener("click", trackClick);
      window.removeEventListener("scroll", trackScroll);
      window.removeEventListener("mouseover", trackHover);
      if (flushTimerRef.current) {
        clearTimeout(flushTimerRef.current);
      }
      // Flush remaining actions on unmount
      flushBuffer();
    };
  }, [trackClick, trackScroll, flushBuffer]);

  return {
    trackAction,
    trackClick,
    trackScroll,
    flushBuffer,
  };
}
