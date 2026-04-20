"""
NeuroUX Data Models
Phase 1: Core domain models for user sessions, actions, and DAG validation
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================
class ActionType(str, Enum):
    """Types of user actions"""
    CLICK = "click"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    HOVER = "hover"
    FOCUS = "focus"
    INPUT = "input"


class UIDensity(str, Enum):
    """UI complexity levels for adaptive interface"""
    SIMPLE = "SIMPLE"      # Minimal UI, large text, fewer options
    STANDARD = "STANDARD"  # Default UI
    EXPERT = "EXPERT"      # Full UI, tiny text, all options


class SessionStatus(str, Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class UserAction(BaseModel):
    """Represents a single user action"""
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    action_type: ActionType
    current_path: str
    target_path: str
    element_id: Optional[str] = None
    timestamp: int  # milliseconds since epoch
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Fraud detection flags
    is_invalid_path: bool = False
    is_potential_bot: bool = False
    
    # Metadata
    suspicion_score: float = 0.0  # 0.0 - 1.0


class UserSession(BaseModel):
    """Represents a user session"""
    session_id: str
    user_id: str
    socket_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_action_time: int = 0
    status: SessionStatus = SessionStatus.ACTIVE
    
    # Metrics
    actions: List[UserAction] = Field(default_factory=list)
    suspicion_score: float = 0.0
    
    # UI Personalization
    current_density: UIDensity = UIDensity.STANDARD
    
    class Config:
        use_enum_values = False


class DAGValidator:
    """
    Directed Acyclic Graph validator for user flow paths
    
    Validates if a transition from one path to another is valid according
    to the predefined application flow graph.
    """
    
    def __init__(self, graph: Dict[str, List[str]]):
        """
        Initialize DAG validator with a flow graph
        
        Args:
            graph: Dict where keys are paths and values are lists of valid next paths
                   Example: {"Home": ["Products", "Profile"], "Products": ["Cart", "Home"]}
        """
        self.graph = graph
        self._validate_graph()
    
    def _validate_graph(self):
        """Validate that the graph is well-formed"""
        if not isinstance(self.graph, dict):
            raise ValueError("Graph must be a dictionary")
        
        for node, neighbors in self.graph.items():
            if not isinstance(neighbors, list):
                raise ValueError(f"Graph node '{node}' must have a list of neighbors")
    
    def validate_transition(self, from_path: str, to_path: str) -> bool:
        """
        Validate if a transition from one path to another is allowed
        
        Args:
            from_path: Current user path
            to_path: Target user path
            
        Returns:
            True if transition is valid, False otherwise
        """
        # If same path, allow (user refreshing)
        if from_path == to_path:
            return True
        
        # Check if from_path exists in graph
        if from_path not in self.graph:
            return False
        
        # Check if to_path is in valid neighbors
        return to_path in self.graph[from_path]
    
    def get_neighbors(self, path: str) -> List[str]:
        """Get all valid next paths from a given path"""
        return self.graph.get(path, [])
    
    def get_all_paths(self) -> List[str]:
        """Get all valid paths in the graph"""
        return list(self.graph.keys())
    
    def is_reachable(self, from_path: str, to_path: str, max_depth: int = 10) -> bool:
        """
        Check if to_path is reachable from from_path using BFS
        
        Args:
            from_path: Starting path
            to_path: Target path
            max_depth: Maximum hops to prevent infinite loops
            
        Returns:
            True if reachable, False otherwise
        """
        if from_path == to_path:
            return True
        
        if from_path not in self.graph:
            return False
        
        visited = set()
        queue = [(from_path, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            
            if current in visited or depth > max_depth:
                continue
            
            visited.add(current)
            
            if current == to_path:
                return True
            
            for neighbor in self.graph.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return False


class BotDetectionMetrics(BaseModel):
    """Metrics for bot detection analysis"""
    session_id: str
    average_time_between_actions_ms: float = 0.0
    min_time_between_actions_ms: float = 0.0
    max_time_between_actions_ms: float = 0.0
    invalid_path_count: int = 0
    potential_bot_actions: int = 0
    total_actions: int = 0
    suspicion_score: float = 0.0
    
    @classmethod
    def from_session(cls, session: UserSession) -> "BotDetectionMetrics":
        """Generate metrics from a session"""
        if not session.actions:
            return cls(session_id=session.session_id)
        
        # Calculate time deltas
        time_deltas = []
        for i in range(1, len(session.actions)):
            delta = session.actions[i].timestamp - session.actions[i-1].timestamp
            time_deltas.append(delta)
        
        # Calculate statistics
        avg_time = sum(time_deltas) / len(time_deltas) if time_deltas else 0
        min_time = min(time_deltas) if time_deltas else 0
        max_time = max(time_deltas) if time_deltas else 0
        
        # Count flags
        invalid_paths = sum(1 for a in session.actions if a.is_invalid_path)
        bot_actions = sum(1 for a in session.actions if a.is_potential_bot)
        
        return cls(
            session_id=session.session_id,
            average_time_between_actions_ms=avg_time,
            min_time_between_actions_ms=min_time,
            max_time_between_actions_ms=max_time,
            invalid_path_count=invalid_paths,
            potential_bot_actions=bot_actions,
            total_actions=len(session.actions),
            suspicion_score=session.suspicion_score,
        )


class EventBatch(BaseModel):
    """Batch of events for efficient transmission"""
    session_id: str
    user_id: str
    actions: List[Dict]  # Flexible format for different action types
    timestamp: datetime = Field(default_factory=datetime.utcnow)
