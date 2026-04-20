"""
Unit tests for backend models and logic
Run with: pytest tests/test_models.py -v
"""

import pytest
from backend.models import (
    DAGValidator,
    UserAction,
    UserSession,
    UIDensity,
    BotDetectionMetrics,
    ActionType,
)


class TestDAGValidator:
    """Test DAG validation logic"""

    @pytest.fixture
    def dag(self):
        return {
            "Home": ["Products", "Profile"],
            "Products": ["Cart", "Home"],
            "Cart": ["Checkout", "Home"],
            "Checkout": ["Home"],
            "Profile": ["Home"],
        }

    @pytest.fixture
    def validator(self, dag):
        return DAGValidator(graph=dag)

    def test_valid_transition(self, validator):
        """Test valid path transitions"""
        assert validator.validate_transition("Home", "Products") is True
        assert validator.validate_transition("Products", "Cart") is True
        assert validator.validate_transition("Cart", "Checkout") is True

    def test_invalid_transition(self, validator):
        """Test invalid path transitions"""
        assert validator.validate_transition("Home", "Checkout") is False
        assert validator.validate_transition("Cart", "Profile") is False
        assert validator.validate_transition("Checkout", "Products") is False

    def test_same_path_allowed(self, validator):
        """Test that same path is always valid (refresh)"""
        assert validator.validate_transition("Home", "Home") is True
        assert validator.validate_transition("Cart", "Cart") is True

    def test_nonexistent_source_path(self, validator):
        """Test transition from nonexistent source"""
        assert validator.validate_transition("InvalidPath", "Home") is False

    def test_get_neighbors(self, validator):
        """Test getting valid neighbors"""
        assert validator.get_neighbors("Home") == ["Products", "Profile"]
        assert validator.get_neighbors("Cart") == ["Checkout", "Home"]
        assert validator.get_neighbors("InvalidPath") == []

    def test_is_reachable(self, validator):
        """Test BFS reachability check"""
        assert validator.is_reachable("Home", "Checkout") is True
        assert validator.is_reachable("Cart", "Profile") is False
        assert validator.is_reachable("Home", "Home") is True

    def test_get_all_paths(self, validator):
        """Test getting all valid paths"""
        paths = validator.get_all_paths()
        assert "Home" in paths
        assert "Products" in paths
        assert len(paths) == 5


class TestUserAction:
    """Test UserAction model"""

    def test_action_creation(self):
        """Test creating a user action"""
        action = UserAction(
            user_id="user123",
            session_id="sess_456",
            action_type=ActionType.CLICK,
            current_path="/home",
            target_path="/home",
            element_id="btn-1",
            timestamp=1234567890,
        )

        assert action.user_id == "user123"
        assert action.session_id == "sess_456"
        assert action.action_type == ActionType.CLICK
        assert action.is_potential_bot is False
        assert action.suspicion_score == 0.0

    def test_action_with_flags(self):
        """Test action with fraud detection flags"""
        action = UserAction(
            user_id="user123",
            session_id="sess_456",
            action_type=ActionType.NAVIGATE,
            current_path="/home",
            target_path="/invalid",
            timestamp=1234567890,
            is_invalid_path=True,
            is_potential_bot=True,
            suspicion_score=0.8,
        )

        assert action.is_invalid_path is True
        assert action.is_potential_bot is True
        assert action.suspicion_score == 0.8


class TestUserSession:
    """Test UserSession model"""

    def test_session_creation(self):
        """Test creating a user session"""
        session = UserSession(
            session_id="sess_123",
            user_id="user456",
        )

        assert session.session_id == "sess_123"
        assert session.user_id == "user456"
        assert len(session.actions) == 0
        assert session.suspicion_score == 0.0
        assert session.current_density == UIDensity.STANDARD

    def test_session_with_actions(self):
        """Test session with multiple actions"""
        session = UserSession(
            session_id="sess_123",
            user_id="user456",
        )

        action1 = UserAction(
            user_id="user456",
            session_id="sess_123",
            action_type=ActionType.CLICK,
            current_path="/home",
            target_path="/home",
            timestamp=1000,
        )

        action2 = UserAction(
            user_id="user456",
            session_id="sess_123",
            action_type=ActionType.NAVIGATE,
            current_path="/home",
            target_path="/products",
            timestamp=1100,
        )

        session.actions.append(action1)
        session.actions.append(action2)

        assert len(session.actions) == 2
        assert session.actions[0].action_type == ActionType.CLICK
        assert session.actions[1].action_type == ActionType.NAVIGATE


class TestBotDetectionMetrics:
    """Test bot detection metrics calculation"""

    def test_metrics_from_empty_session(self):
        """Test metrics from session with no actions"""
        session = UserSession(session_id="sess_123", user_id="user456")
        metrics = BotDetectionMetrics.from_session(session)

        assert metrics.total_actions == 0
        assert metrics.average_time_between_actions_ms == 0
        assert metrics.suspicious_count == 0

    def test_metrics_from_session_with_actions(self):
        """Test metrics calculation from session"""
        session = UserSession(session_id="sess_123", user_id="user456")

        # Add actions with 50ms intervals (would trigger bot detection)
        for i in range(5):
            action = UserAction(
                user_id="user456",
                session_id="sess_123",
                action_type=ActionType.NAVIGATE if i > 0 else ActionType.CLICK,
                current_path="/home",
                target_path="/products",
                timestamp=1000 + (i * 50),
                is_potential_bot=(i > 0),
            )
            session.actions.append(action)

        metrics = BotDetectionMetrics.from_session(session)

        assert metrics.total_actions == 5
        assert metrics.potential_bot_actions == 4
        assert metrics.average_time_between_actions_ms == 50.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
