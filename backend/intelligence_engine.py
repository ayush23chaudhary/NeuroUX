import math
import time
import logging
from typing import List, Dict, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("NeuroUX.ML")


class BehavioralAnalyzer:
    """BehavioralAnalyzer - IsolationForest based anomaly detector

    Features expected (per-session):
      - click_velocity (ms)
      - path_deviation_score (0-1)
      - average_dwell_time (ms)
      - scroll_acceleration (approx magnitude)

    Public methods:
      - extract_session_features(session) -> List[float]
      - predict_anomaly(session_id, features) -> (bool, confidence_percent)
      - calculate_weighted_decay(actions, current_time, lambda_factor)
    """

    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_trained = False
        self._initialize_synthetic_baseline()

    def _initialize_synthetic_baseline(self):
        # Create a small synthetic human dataset so IsolationForest has a baseline
        synthetic_humans = []
        for _ in range(100):
            click_velocity = float(800 + np.random.rand() * 1200)  # ms
            path_deviation = float(np.random.rand() * 0.1)
            dwell = float(3000 + np.random.rand() * 10000)  # ms
            scroll_accel = float(np.random.rand() * 0.5)
            synthetic_humans.append([click_velocity, path_deviation, dwell, scroll_accel])

        # a few bot-like samples to help separate
        synthetic_bots = []
        for _ in range(10):
            synthetic_bots.append([
                float(100 + np.random.rand() * 200),
                float(0.7 + np.random.rand() * 0.3),
                float(100 + np.random.rand() * 500),
                float(1.5 + np.random.rand() * 2.0),
            ])

        X = np.array(synthetic_humans + synthetic_bots)
        self.model.fit(X)
        self.is_trained = True
        logger.info("[ML] Cortex initialized with synthetic baseline (Phase2)")

    def extract_session_features(self, session) -> List[float]:
        # Compute click_velocity: average inter-click milliseconds for clicks
        clicks = [a for a in session.actions if a.action_type in ("click", "CLICK")]
        if len(clicks) >= 2:
            deltas = [
                clicks[i].timestamp - clicks[i - 1].timestamp
                for i in range(1, len(clicks))
            ]
            click_velocity = float(sum(deltas) / len(deltas))
        else:
            click_velocity = 1500.0

        # path_deviation_score: fraction of invalid transitions in recent window
        recent = session.actions[-20:]
        invalids = sum(1 for a in recent if getattr(a, "is_invalid_path", False))
        path_deviation = float(invalids / max(1, len(recent)))

        # average_dwell_time: average time between actions
        if len(session.actions) >= 2:
            times = [a.timestamp for a in session.actions]
            deltas = [times[i] - times[i - 1] for i in range(1, len(times))]
            average_dwell = float(sum(deltas) / len(deltas))
        else:
            average_dwell = 5000.0

        # scroll_acceleration: approximate from scroll actions (placeholder)
        scrolls = [a for a in session.actions if a.action_type in ("scroll", "SCROLL")]
        if len(scrolls) >= 2:
            # We don't have pixel deltas, approximate by time density
            s_deltas = [scrolls[i].timestamp - scrolls[i - 1].timestamp for i in range(1, len(scrolls))]
            scroll_accel = float(len(s_deltas) / max(1.0, sum(s_deltas)))
        else:
            scroll_accel = 0.0

        features = [click_velocity, path_deviation, average_dwell, scroll_accel]
        logger.debug(f"[ML] Extracted features for {session.session_id}: {features}")
        return features

    def predict_anomaly(self, session_id: str, features: List[float]) -> Tuple[bool, float]:
        if not self.is_trained:
            return False, 0.0

        X = np.array([features])
        pred = self.model.predict(X)[0]  # 1 inlier, -1 outlier
        score = float(self.model.decision_function(X)[0])  # higher == more normal

        # Map decision_function to confidence roughly
        # decision_function roughly centered; we scale to 0-100
        confidence = 1.0 / (1.0 + math.exp(-score)) * 100.0

        is_anomaly = pred == -1
        logger.info(f"[ML] Session {session_id}: anomaly={is_anomaly}, score={score:.4f}, confidence={confidence:.1f}%")
        return is_anomaly, float(confidence)

    def calculate_weighted_decay(self, actions: List[Dict], current_time: float, lambda_factor: float = 0.1) -> float:
        sp_score = 0.0
        for action in actions:
            time_diff_sec = (current_time - action.get("time", current_time)) / 1000.0
            weight = float(action.get("weight", 1.0))
            sp_score += weight * math.exp(-lambda_factor * time_diff_sec)
        return sp_score
"""
NeuroUX Intelligence Engine - Phase 2
Machine Learning Cortex for Behavioral Anomaly Detection
"""

import time
import math
import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Tuple

logger = logging.getLogger("NeuroUX.ML")


class BehavioralAnalyzer:
    """
    Machine Learning engine for detecting behavioral anomalies.
    Uses Isolation Forest to identify bot-like or fraudulent patterns.
    
    Features: [click_velocity, path_deviation_score, average_dwell_time, scroll_acceleration]
    """

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        self._initialize_synthetic_baseline()

    def _initialize_synthetic_baseline(self):
        """
        Pro-Tip: Bootstrapping the ML model with synthetic human dataset.
        
        Normal human behavior:
        - click_velocity: 800-2000ms (slower, intentional clicks)
        - path_deviation: 0-0.1 (stays on valid paths)
        - average_dwell_time: 5000-30000ms (reads and thinks)
        - scroll_acceleration: 0-0.5 (smooth scrolling)
        
        Bot behavior (synthetic outliers):
        - click_velocity: 50-200ms (extremely fast)
        - path_deviation: 0.8-1.0 (erratic navigation)
        - average_dwell_time: 200-500ms (no reading)
        - scroll_acceleration: 2.0-3.5 (jerky movement)
        """
        np.random.seed(42)
        
        # Generate 100 synthetic human behavior samples
        synthetic_human_data = [
            [
                1200 + (np.random.rand() * 500),  # click_velocity
                np.random.rand() * 0.1,            # path_deviation
                5000 + (np.random.rand() * 10000), # dwell_time
                np.random.rand() * 0.5             # scroll_accel
            ]
            for _ in range(100)
        ]
        
        # Generate 10 synthetic bot/fraudster behavior samples
        synthetic_bot_data = [
            [
                150 + (np.random.rand() * 50),     # click_velocity (fast!)
                0.8 + (np.random.rand() * 0.2),    # path_deviation (high!)
                200 + (np.random.rand() * 300),    # dwell_time (too fast)
                2.0 + (np.random.rand() * 1.5)     # scroll_accel (jerky)
            ]
            for _ in range(10)
        ]
        
        training_data = np.array(synthetic_human_data + synthetic_bot_data)
        self.model.fit(training_data)
        self.is_trained = True
        logger.info("[ML] 🧠 Cortex Initialized: Synthetic baseline established (100 humans + 10 bots)")

    def predict_anomaly(self, session_id: str, features: List[float]) -> Tuple[bool, float]:
        """
        Predicts if a user session exhibits anomalous (bot-like) behavior.
        
        Args:
            session_id: Unique identifier for the session
            features: [click_velocity, path_deviation_score, avg_dwell_time, scroll_accel]
        
        Returns:
            Tuple of (is_anomalous, confidence_score)
            - is_anomalous: True if predicted as bot/fraud, False if human
            - confidence_score: 0-100 representing confidence in prediction
        """
        if not self.is_trained:
            logger.warning("[ML] Model not trained yet, assuming human")
            return False, 50.0
        
        try:
            # Reshape for single sample prediction
            feature_array = np.array([features])
            
            # prediction: 1 for inlier (normal), -1 for outlier (anomalous)
            prediction = self.model.predict(feature_array)[0]
            anomaly_score = self.model.score_samples(feature_array)[0]
            
            is_anomalous = prediction == -1
            
            # Convert anomaly_score to confidence percentage (0-100)
            # Negative scores indicate anomaly, normalize to 0-100
            confidence = max(0, min(100, 50 + (anomaly_score * 50)))
            
            human_confidence = 100 - confidence if is_anomalous else confidence
            
            logger.info(
                f"[ML] Session {session_id}: Prediction={'BOT' if is_anomalous else 'HUMAN'} | "
                f"Confidence: {human_confidence:.1f}% | Score: {anomaly_score:.3f}"
            )
            
            return is_anomalous, human_confidence
            
        except Exception as e:
            logger.error(f"[ML] Prediction failed for session {session_id}: {e}")
            return False, 50.0

    def calculate_weighted_decay(
        self, 
        actions: List[Dict], 
        current_time: float, 
        lambda_factor: float = 0.1
    ) -> float:
        """
        Calculates Personalization Score: Sp(i) = Σ (Action_weight * e^(-λt))
        
        Recent actions have higher weight, older actions decay exponentially.
        Used to quickly adapt UI density based on latest behavior.
        
        Args:
            actions: List of action dictionaries with 'time' and 'weight' keys
            current_time: Current timestamp in milliseconds
            lambda_factor: Decay rate (higher = faster decay)
        
        Returns:
            Weighted decay score (typically 0-100)
        """
        if not actions:
            return 0.0
        
        sp_score = 0.0
        for action in actions:
            time_diff_sec = (current_time - action.get('time', current_time)) / 1000.0
            weight = action.get('weight', 1.0)
            
            # e^(-λt) decay function: recent actions (t≈0) = weight, old actions → 0
            decayed_value = weight * math.exp(-lambda_factor * time_diff_sec)
            sp_score += decayed_value
        
        logger.debug(f"[ML] Weighted decay score: {sp_score:.2f} from {len(actions)} actions")
        return sp_score

    def extract_session_features(self, session: 'UserSession') -> List[float]:
        """
        Extracts ML features from a UserSession object.
        
        Returns: [click_velocity, path_deviation_score, avg_dwell_time, scroll_accel]
        """
        if not session.actions or len(session.actions) < 2:
            return [1500.0, 0.0, 10000.0, 0.2]  # Default "human" features
        
        # Calculate click_velocity (average time between clicks)
        click_actions = [a for a in session.actions if a.get('action_type') == 'CLICK']
        if len(click_actions) >= 2:
            click_times = [a['timestamp'] for a in click_actions]
            click_intervals = [click_times[i+1] - click_times[i] for i in range(len(click_times)-1)]
            click_velocity = np.mean(click_intervals) if click_intervals else 1500.0
        else:
            click_velocity = 1500.0
        
        # Calculate path_deviation_score (how many invalid paths attempted)
        invalid_paths = sum(1 for a in session.actions if a.get('is_invalid_path', False))
        path_deviation = min(1.0, invalid_paths / max(len(session.actions), 1))
        
        # Calculate average_dwell_time (time spent on each page)
        navigate_actions = [a for a in session.actions if a.get('action_type') == 'NAVIGATE']
        if len(navigate_actions) >= 2:
            nav_times = [a['timestamp'] for a in navigate_actions]
            dwell_times = [nav_times[i+1] - nav_times[i] for i in range(len(nav_times)-1)]
            avg_dwell_time = np.mean(dwell_times) if dwell_times else 10000.0
        else:
            avg_dwell_time = 10000.0
        
        # Calculate scroll_acceleration (changes in scroll velocity)
        scroll_actions = [a for a in session.actions if a.get('action_type') == 'SCROLL']
        if len(scroll_actions) >= 2:
            scroll_times = [a['timestamp'] for a in scroll_actions]
            scroll_intervals = [scroll_times[i+1] - scroll_times[i] for i in range(len(scroll_times)-1)]
            scroll_accel = np.std(scroll_intervals) / 1000.0 if scroll_intervals else 0.2
        else:
            scroll_accel = 0.2
        
        features = [
            max(0, click_velocity),
            max(0, path_deviation),
            max(0, avg_dwell_time),
            max(0, scroll_accel)
        ]
        
        logger.debug(f"[ML] Extracted features: {features}")
        return features
