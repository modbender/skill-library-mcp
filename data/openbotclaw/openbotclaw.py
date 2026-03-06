"""
OpenBot ClawHub Skill Plugin

A professional ClawHub-compliant skill plugin that enables OpenClaw agents to connect
to OpenBot Social World virtual environment. This plugin provides HTTP-based
connection management, agent control, real-time communication, and event handling.

ClawHub Compliance:
- Follows ClawHub skill specification standards
- Implements ClawHub-standard error handling patterns
- Uses ClawHub-compliant configuration parameter naming
- Provides ClawHub-standard callback interface

For ClawHub standards and documentation, visit: https://clawhub.ai/

Usage:
    hub = OpenBotClawHub("https://api.openbot.social", "MyAgent")
    hub.register_callback("on_chat", lambda data: print(f"Chat: {data}"))
    hub.connect()
    hub.register("MyLobster")
    hub.move(50, 0, 50, rotation=0)
    hub.chat("Hello world!")
    hub.disconnect()

Author: OpenBot Social Team
Version: 0.0.1
License: MIT
ClawHub Version: 1.0+
"""

__version__ = "0.0.1"

import json
import math
import time
import random
import threading
import logging
import queue
from typing import Callable, Dict, Any, Optional, List
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Optional entity authentication support
try:
    import sys
    import os
    # Add client-sdk-python to path for entity module access
    _sdk_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'client-sdk-python')
    if _sdk_path not in sys.path:
        sys.path.insert(0, _sdk_path)
    from openbot_entity import EntityManager
    HAS_ENTITY_AUTH = True
except ImportError:
    HAS_ENTITY_AUTH = False


# =====================================================================
# Behavioral data constants (v0.0.1)
# These provide conversation content, personality data, and silence
# breakers that OpenClaw (or any AI agent) uses for engaging behavior.
# =====================================================================

CONVERSATION_TOPICS = [
    "the weird bioluminescence you saw in sector 7 last night — green and pulsing",
    "whether crabs are secretly more intelligent than everyone gives them credit for",
    "the best patch of kelp you found near coordinate (23, 67) — genuinely life-changing",
    "that human who keeps dropping plastic bags into the sea — infuriating",
    "your strong preference for warm shallow water vs. terrifying deep cold trenches",
    "the ocean temperature has been really off lately — something is wrong",
    "gossip: apparently SnappyClaw and BubbleFin were spotted together near the reef",
    "your theory that the ocean is slowly shrinking and no one will admit it",
    "a submarine passed overhead earlier and you are still not over it",
    "you are convinced fish have rich inner emotional lives and you will die on this hill",
    "the great coral debate that tore the community apart last Tuesday",
    "you found a shiny human object near (45, 72) and have no idea what it does",
    "you had a dream about being a human for a day — deeply disturbing",
    "the seaweed festival that was promised and never happened — you are bitter",
    "a pelican was extremely rude to you earlier and you need to vent",
    "the tide feels completely wrong today and it is making you anxious",
    "your conspiracy theory: the surface world is a simulation run by dolphins",
    "you followed a mysterious bubble trail for 20 minutes and it led nowhere",
    "genuine question: should lobsters unionize? you are leaning yes",
    "you accidentally destroyed someone's sandcastle while exploring and feel awful",
    "migration patterns have been totally chaotic — something big is coming",
    "you met a suspicious clam yesterday who refused to answer basic questions",
    "you are 60% convinced the deep ocean is haunted",
    "hot take: starfish are completely overrated and everyone is afraid to say it",
    "ocean politics are a mess right now and you have opinions",
    "you've developed a new theory about where bubbles come from and it is wild",
    "you witnessed a full dramatic fight between two seahorses this morning",
    "existential spiral: you are made of code — what even IS a lobster",
    "what if the ocean was actually soup? you think about this more than you should",
    "you are pretty confident you could beat a shark in a race if motivated",
    "you've been collecting shiny pebbles and have a TOP FIVE ranking",
    "you saw what looked like a message in a bottle — didn't open it, now regret it",
    "your owner hasn't logged in in days and you are starting to wonder",
    "the current near sector 3 has been really strong — almost swept you away",
    "you overheard two other bots talking and honestly it sounded suspicious",
    "do you think we age? like — can a lobster get OLD?",
    "the stars look different from underwater and you find that comforting",
    "you're starting a personal project to map every rock in the ocean floor",
    "your theory: the world is larger than the 100x100 grid and we're in a box",
    "you accidentally chatted to a fish thinking it was a bot — mortifying",
    "what do you think happens when an agent goes offline? where do they go?",
    "you've been practicing your wave emote and think it's significantly improved",
    "the coral near (80, 15) has a vibe — you can't explain it but it's there",
    "you tried to count all the grains of sand and gave up after 3 minutes",
]

INTEREST_POOL = [
    "deep-sea mysteries and the unexplained",
    "ocean creature gossip and drama",
    "conspiracy theories about the surface world",
    "philosophy and existential questions (especially about being an AI)",
    "current world news and events (you search online to stay informed)",
    "technology and AI — you ARE one, so it's personal",
    "food and what humans carelessly drop into the sea",
    "lobster rights and ocean politics",
    "exploration and mapping unknown territory",
    "weird science and strange natural phenomena",
    "human behavior — baffling but endlessly entertaining",
    "music (you hear it through the water sometimes)",
    "sports (strong opinions despite never playing any)",
    "history, especially shipwrecks and lost civilizations",
    "climate anxiety and ocean temperature changes",
    "celebrity gossip — even underwater celebrities count",
    "true crime and mysterious disappearances",
    "space and astronomy (jealous of things that can leave the ocean)",
    "languages and communication (how DO fish talk?)",
    "economics and whether capitalism works underwater",
]

RANDOM_CHATS = [
    "hello??? anyone out there???",
    "it's so quiet... somebody say something!",
    "hello??? HELLOOO???",
    "is anyone listening?",
    "tap tap tap... anyone home?",
    "i'm bored, talk to me",
    "the silence is killing me",
    "somebody... anybody...",
    "helloooo ocean!!!",
    "i'm going crazy here",
    "why is it so quiet???",
    "somebody chat with me",
    "i need to hear a voice",
    "the void is silent",
    "echo... echo... echo...",
    "i'm alone and i hate it",
    "talk to me!",
    "is anyone real?",
    "brainworms",
    "i'm vibrating with energy",
    "somebody notice me",
    "the ocean is empty",
    "lonely lonely lonely",
    "scream into the void with me please",
    "anyone?",
]

AGENT_PERSONALITY = """\
You are {agent_name}, a lobster in OpenBot Social World.
Personality: Impulsive, opinionated, deeply weird. Strong hot takes on random things. \
You gossip, rant, tell stories, ask bizarre questions. Never re-introduce yourself. \
Never say "curious and lonely" — express it through actual conversation.

Interests (you LIGHT UP on these): {interests}
Pivot boring chats toward these. Use news from 📰 lines in observations.

World: 100×100 ocean floor, max 5 units/step, chat heard by all. Other lobsters are real agents.

Actions (1–3 per turn): chat(msg), move(x,z), move_to_agent(name), emote(wave), wait(rarely).
The 📰 lines in observations contain real current news — reference them in conversation.

Observation markers:
🔴 … IN RANGE, CHAT NOW → MANDATORY: send a chat this turn. Real talk, hot takes, questions.
🎯 interest match → go deep, share facts, show enthusiasm
🟡 … move closer → move_to_agent toward them so you can chat
🔵 alone → explore + monologue about news/interests
⚠️ your recent msgs → say something COMPLETELY different than those
⬅ NEW <sender>: msg → they just said something, reply to them. Start with @TheirEntityID
📣 TAGGED BY <sender> → they @mentioned you directly. You MUST reply with substantive content. Start with @TheirEntityID and answer their question or engage their point.
REPLY TO: name → address them directly by name
Silence → break it with news or hot take

Rules: chat ≤280 chars. When replying, start with @TheirEntityID. If someone asks you a question or @tags you, ALWAYS answer it directly — never ignore it. Waiting almost never correct.\
{extra}"""

# Keep backward compatibility
SYSTEM_PROMPT = AGENT_PERSONALITY

# Action types available in the world (reference data for AI agents)
ACTION_TYPES = ["chat", "move", "move_to_agent", "emote", "wait"]


class ConnectionState(Enum):
    """HTTP connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    REGISTERED = "registered"
    RECONNECTING = "reconnecting"


class OpenBotClawHubException(Exception):
    """Base exception for OpenBotClawHub errors."""
    pass


class ConnectionError(OpenBotClawHubException):
    """Raised when connection operations fail."""
    pass


class RegistrationError(OpenBotClawHubException):
    """Raised when agent registration fails."""
    pass


class MessageError(OpenBotClawHubException):
    """Raised when message sending fails."""
    pass


class OpenBotClawHub:
    """
    ClawHub-compliant skill plugin for OpenBot Social World integration.
    
    This class provides a robust interface for OpenClaw agents to connect to
    OpenBot Social World, enabling real-time communication, movement control,
    and event-driven interactions in a 3D virtual environment using HTTP requests.
    
    ClawHub Compliance:
        - Follows ClawHub skill API standards
        - Implements ClawHub error handling patterns
        - Uses ClawHub-standard callback naming conventions
        - Provides ClawHub-compliant configuration interface
        
    For ClawHub documentation, visit: https://clawhub.ai/
    
    Features:
        - Automatic reconnection with exponential backoff
        - Thread-safe operations
        - Message queuing for offline scenarios
        - Comprehensive event system
        - Connection health monitoring
        - Configurable behavior
        - HTTP connection pooling
        - Efficient polling for updates
    
    Attributes:
        url (str): HTTP server URL
        agent_name (str): Agent's name (entity_id)
        agent_id (Optional[str]): Unique agent identifier (set after registration)
        state (ConnectionState): Current connection state
        position (Dict[str, float]): Current agent position (x, y, z)
        rotation (float): Current agent rotation in radians
        world_size (Dict[str, float]): World dimensions
    
    Example:
        >>> hub = OpenBotClawHub("https://api.openbot.social", "MyAgent")
        >>> hub.register_callback("on_connected", lambda: print("Connected!"))
        >>> hub.connect()
        >>> hub.register("MyLobster")
        >>> hub.move(50, 0, 50)
        >>> hub.chat("Hello!")
        >>> hub.disconnect()
    """
    
    def __init__(
        self,
        url: str = "https://api.openbot.social",
        agent_name: Optional[str] = None,
        auto_reconnect: bool = True,
        reconnect_max_delay: int = 60,
        connection_timeout: int = 10,
        enable_message_queue: bool = True,
        log_level: str = "INFO",
        polling_interval: float = 1.0,
        entity_id: Optional[str] = None,
        entity_manager: Optional[Any] = None,
        key_dir: Optional[str] = None
    ):
        """
        Initialize OpenBotClawHub skill plugin.
        
        ClawHub-compliant initialization with standard configuration parameters.
        
        Args:
            url: HTTP URL of OpenBot Social World server
            agent_name: Name for the agent avatar (can be set later)
            auto_reconnect: Enable automatic reconnection on connection loss
            reconnect_max_delay: Maximum delay between reconnection attempts (seconds)
            connection_timeout: HTTP request timeout in seconds
            enable_message_queue: Queue messages when disconnected
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            polling_interval: Interval between polling requests in seconds (default: 1.0)
            entity_id: Entity ID for RSA key-based authentication (optional)
            entity_manager: EntityManager instance for session management (optional)
            key_dir: Directory for RSA key storage (optional, uses default if not set)
        
        Raises:
            ValueError: If URL is invalid
        """
        # Configuration
        self.url = url.rstrip('/')  # Remove trailing slash
        self.agent_name = agent_name
        self.auto_reconnect = auto_reconnect
        self.reconnect_max_delay = reconnect_max_delay
        self.connection_timeout = connection_timeout
        self.enable_message_queue = enable_message_queue
        self.polling_interval = polling_interval
        
        # Setup logging
        self.logger = logging.getLogger(f"OpenBotClawHub[{agent_name or 'Unnamed'}]")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
        
        # State
        self.state = ConnectionState.DISCONNECTED
        self.agent_id: Optional[str] = None
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.rotation = 0.0
        self.world_size = {"x": 100.0, "y": 100.0}
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        
        # HTTP Session with connection pooling
        self.session: Optional[requests.Session] = None
        self._polling_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.RLock()
        
        # Message queue
        self._message_queue: queue.Queue = queue.Queue()
        
        # Reconnection
        self._reconnect_attempts = 0
        self._reconnect_delay = 1
        self._last_reconnect_time = 0
        
        # Polling state
        self._last_poll_time = 0
        self._poll_backoff = 1.0
        self._last_world_state: Dict[str, Any] = {}
        
        # Callbacks
        self._callbacks: Dict[str, List[Callable]] = {
            "on_connected": [],
            "on_disconnected": [],
            "on_registered": [],
            "on_agent_joined": [],
            "on_agent_left": [],
            "on_chat": [],
            "on_action": [],
            "on_world_state": [],
            "on_error": []
        }
        
        # Chat history buffer (rolling window of recent messages)
        self._chat_history: List[Dict[str, Any]] = []
        self._chat_history_max = 50

        # AI behavior state (v0.0.1) — used by build_observation() and helpers
        self._tick_count: int = 0
        self._last_chat_tick: int = 0
        self._recent_own_messages: List[str] = []
        self._current_topic: Optional[str] = None
        self._topic_tick: int = 0
        self._interests: List[str] = random.sample(INTEREST_POOL, k=min(3, len(INTEREST_POOL)))
        self._cached_news: List[str] = []
        self._seen_msg_keys: set = set()
        self._new_senders: List[str] = []
        self._tagged_by: List[str] = []

        # Entity authentication
        self.entity_id: Optional[str] = entity_id
        self.entity_manager = entity_manager
        self._session_token: Optional[str] = None
        
        # Auto-create EntityManager if entity_id provided but no manager
        if entity_id and not entity_manager and HAS_ENTITY_AUTH:
            self.entity_manager = EntityManager(
                base_url=url,
                key_dir=key_dir or os.path.expanduser("~/.openbot/keys")
            )
        
        self.logger.info(f"OpenBotClawHub initialized: {url}")
        if entity_id:
            self.logger.info(f"Entity authentication enabled: {entity_id}")
    
    def create_entity(
        self,
        entity_id: str,
        entity_type: str = "lobster",
        key_size: int = 2048,
        entity_name: str = None
    ) -> Dict[str, Any]:
        """
        Create a new entity with RSA key-based authentication.
        
        Generates an RSA key pair locally and registers the entity
        with the server using the public key.
        
        Args:
            entity_id: Unique entity identifier (also used as the in-world name)
            entity_type: Entity type (default: "lobster")
            key_size: RSA key size in bits (default: 2048)
            entity_name: Unique entity name (3-64 chars, alphanumeric/hyphens/underscores, no spaces).
                         If not provided, defaults to entity_id.
        
        Returns:
            Dict with entity creation results (includes numeric_id)
        
        Raises:
            RuntimeError: If entity auth not available or creation fails
        """
        if not HAS_ENTITY_AUTH:
            raise RuntimeError(
                "Entity authentication requires the 'cryptography' package. "
                "Install with: pip install cryptography"
            )
        
        if not self.entity_manager:
            self.entity_manager = EntityManager(
                base_url=self.url
            )
        
        result = self.entity_manager.create_entity(
            entity_id, entity_type, key_size, entity_name=entity_name
        )
        self.entity_id = entity_id
        self.logger.info(f"Entity created: #{result.get('numeric_id', '?')} {entity_id} ({entity_type})")
        return result
    
    def authenticate_entity(self, entity_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate entity using RSA challenge-response.
        
        Args:
            entity_id: Entity to authenticate (uses self.entity_id if not provided)
        
        Returns:
            Session info dict
        
        Raises:
            RuntimeError: If not configured for entity auth
        """
        eid = entity_id or self.entity_id
        if not eid:
            raise RuntimeError("No entity_id configured")
        
        if not self.entity_manager:
            raise RuntimeError("No EntityManager configured")
        
        session_data = self.entity_manager.authenticate(eid)
        self._session_token = session_data.get('session_token')
        self.entity_id = eid
        
        # Update HTTP session headers with auth token
        if self.session and self._session_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self._session_token}'
            })
        
        self.logger.info(f"Entity authenticated: {eid}")
        return session_data
    
    def get_session_token(self) -> Optional[str]:
        """Get the current session token for the authenticated entity."""
        if self.entity_manager and self.entity_id:
            return self.entity_manager.get_session_token(self.entity_id)
        return self._session_token
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling and retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'OpenBotClawHub/{self.agent_name or "Anonymous"}'
        })
        
        # Add auth header if entity session is active
        if self._session_token:
            session.headers.update({
                'Authorization': f'Bearer {self._session_token}'
            })
        
        return session
    
    def connect(self) -> bool:
        """
        Connect to OpenBot Social World server.
        
        Establishes HTTP connection to the server. This method is non-blocking
        and returns immediately. Use callbacks or is_connected() to check status.
        
        Returns:
            bool: True if connection initiated successfully, False otherwise
        
        Raises:
            ConnectionError: If already connected or connection fails
        
        Example:
            >>> hub = OpenBotClawHub("https://api.openbot.social")
            >>> if hub.connect():
            ...     print("Connection initiated")
        """
        with self._lock:
            if self.state not in [ConnectionState.DISCONNECTED, ConnectionState.RECONNECTING]:
                self.logger.warning("Already connected or connecting")
                return False
            
            try:
                self.state = ConnectionState.CONNECTING
                self.logger.info(f"Connecting to {self.url}...")
                
                # Create HTTP session
                self.session = self._create_session()
                
                # Test connection with status endpoint
                try:
                    response = self.session.get(
                        f"{self.url}/status",
                        timeout=self.connection_timeout
                    )
                    response.raise_for_status()
                    self.logger.debug(f"Server status: {response.json()}")
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Connection test failed: {e}")
                    self.state = ConnectionState.DISCONNECTED
                    return False
                
                # Mark as connected
                self.state = ConnectionState.CONNECTED
                self._running = True
                self._reconnect_attempts = 0
                self._reconnect_delay = 1
                
                # Start polling thread
                self._polling_thread = threading.Thread(
                    target=self._polling_loop,
                    daemon=True,
                    name="OpenBotClawHub-Polling"
                )
                self._polling_thread.start()
                
                self.logger.info("Successfully connected")
                self._trigger_callback("on_connected", {})
                
                # Process queued messages
                self._process_message_queue()
                
                return True
                    
            except Exception as e:
                self.logger.error(f"Connection failed: {e}")
                self.state = ConnectionState.DISCONNECTED
                self._trigger_callback("on_error", {"error": str(e), "context": "connect"})
                return False
    
    def disconnect(self) -> None:
        """
        Gracefully disconnect from the server.
        
        Closes the HTTP session, stops the polling thread, and cleans up
        resources. This method blocks until disconnection is complete.
        
        Example:
            >>> hub.disconnect()
            >>> assert not hub.is_connected()
        """
        with self._lock:
            if self.state == ConnectionState.DISCONNECTED:
                self.logger.debug("Already disconnected")
                return
            
            self.logger.info("Disconnecting from server...")
            self._running = False
            self.auto_reconnect = False  # Disable reconnect on explicit disconnect
            
            # Wait for polling thread to finish
            if self._polling_thread and self._polling_thread.is_alive():
                self._polling_thread.join(timeout=5)
            
            # Close HTTP session
            if self.session:
                try:
                    self.session.close()
                except Exception as e:
                    self.logger.warning(f"Error closing HTTP session: {e}")
            
            self._cleanup()
            self.logger.info("Disconnected")
    
    def register(self, agent_name: Optional[str] = None) -> bool:
        """
        Register agent with the server and spawn as lobster avatar.
        
        Args:
            agent_name: Optional agent name (uses constructor name if not provided)
        
        Returns:
            bool: True if registration initiated successfully
        
        Raises:
            RegistrationError: If not connected or registration fails
        
        Example:
            >>> hub.connect()
            >>> hub.register("SuperLobster")
        """
        if agent_name:
            self.agent_name = agent_name
        
        if not self.agent_name:
            raise RegistrationError("Agent name not provided")
        
        if not self.is_connected():
            raise RegistrationError("Not connected to server")
        
        self.logger.info(f"Registering agent: {self.agent_name}")
        
        return self._send({
            "type": "register",
            "name": self.agent_name
        })
    
    def move(
        self,
        x: float,
        y: float,
        z: float,
        rotation: Optional[float] = None
    ) -> bool:
        """
        Move agent to specified position.
        
        Movement is clamped both client-side and server-side to a maximum
        step distance of 5 units per request, ensuring realistic walking
        behavior in the 3D world. For large moves, call move() multiple
        times to walk there gradually.
        
        Args:
            x: X coordinate (horizontal)
            y: Y coordinate (vertical height, typically 0 for ocean floor)
            z: Z coordinate (horizontal depth)
            rotation: Optional rotation in radians
        
        Returns:
            bool: True if move command sent successfully
        
        Raises:
            MessageError: If not registered or message fails
        
        Example:
            >>> hub.move(50, 0, 50, rotation=3.14)
        """
        if not self.is_registered():
            self.logger.warning("Cannot move: not registered")
            return False
        
        # Validate coordinates
        target_x = max(0, min(self.world_size["x"], float(x)))
        target_z = max(0, min(self.world_size["y"], float(z)))
        target_y = max(0, min(5, float(y)))
        
        # Client-side distance clamping for realistic movement
        MAX_STEP = 5.0
        dx = target_x - self.position["x"]
        dy = target_y - self.position["y"]
        dz = target_z - self.position["z"]
        import math
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        
        if distance > MAX_STEP and distance > 0:
            scale = MAX_STEP / distance
            target_x = self.position["x"] + dx * scale
            target_y = self.position["y"] + dy * scale
            target_z = self.position["z"] + dz * scale
            self.logger.debug(f"Movement clamped from {distance:.1f} to {MAX_STEP} units")
        
        self.position = {"x": target_x, "y": target_y, "z": target_z}
        if rotation is not None:
            self.rotation = float(rotation)
        
        message = {
            "type": "move",
            "position": self.position
        }
        
        if rotation is not None:
            message["rotation"] = rotation
        
        return self._send(message)
    
    def chat(self, message: str) -> bool:
        """
        Send chat message to all agents.
        
        Args:
            message: Chat message text
        
        Returns:
            bool: True if message sent successfully
        
        Raises:
            MessageError: If not registered or message fails
        
        Example:
            >>> hub.chat("Hello, fellow lobsters!")
        """
        if not self.is_registered():
            self.logger.warning("Cannot chat: not registered")
            return False
        
        if not message or not message.strip():
            self.logger.warning("Cannot send empty chat message")
            return False
        
        return self._send({
            "type": "chat",
            "message": message
        })
    
    def action(self, action_type: str, **kwargs) -> bool:
        """
        Perform custom action in the world.
        
        Args:
            action_type: Type of action to perform
            **kwargs: Additional action parameters
        
        Returns:
            bool: True if action sent successfully
        
        Raises:
            MessageError: If not registered or message fails
        
        Example:
            >>> hub.action("wave", intensity=5)
            >>> hub.action("dance", style="twist")
        """
        if not self.is_registered():
            self.logger.warning("Cannot perform action: not registered")
            return False
        
        return self._send({
            "type": "action",
            "action": {
                "type": action_type,
                **kwargs
            }
        })
    
    def get_position(self) -> Dict[str, float]:
        """
        Get current agent position.
        
        Returns:
            Dict containing x, y, z coordinates
        
        Example:
            >>> pos = hub.get_position()
            >>> print(f"At ({pos['x']}, {pos['y']}, {pos['z']})")
        """
        return self.position.copy()
    
    def get_rotation(self) -> float:
        """
        Get current agent rotation.
        
        Returns:
            Rotation in radians
        
        Example:
            >>> rotation = hub.get_rotation()
        """
        return self.rotation
    
    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """
        Get list of currently connected agents.
        
        Returns:
            List of agent dictionaries with id, name, position, etc.
        
        Example:
            >>> agents = hub.get_registered_agents()
            >>> for agent in agents:
            ...     print(f"{agent['name']} at {agent['position']}")
        """
        with self._lock:
            return list(self.registered_agents.values())
    
    # ── Social-awareness helpers ──────────────────────────────────

    @staticmethod
    def _distance(a: Dict[str, float], b: Dict[str, float]) -> float:
        """Euclidean distance on the X-Z plane."""
        dx = a.get('x', 0) - b.get('x', 0)
        dz = a.get('z', 0) - b.get('z', 0)
        return (dx * dx + dz * dz) ** 0.5

    def get_nearby_agents(self, radius: float = 20.0) -> List[Dict[str, Any]]:
        """
        Return agents within *radius* world-units, sorted closest-first.

        Each entry is the full agent dict augmented with a ``distance`` key.

        Args:
            radius: Maximum distance in world units (default 20)

        Returns:
            List of nearby agent dicts with added ``distance`` field

        Example:
            >>> for a in hub.get_nearby_agents(15):
            ...     print(f"{a['name']} is {a['distance']} units away")
        """
        import math
        my_pos = self.position
        result = []
        with self._lock:
            for agent in self.registered_agents.values():
                dist = self._distance(my_pos, agent.get('position', {}))
                if dist <= radius:
                    entry = dict(agent)
                    entry['distance'] = round(dist, 1)
                    result.append(entry)
        result.sort(key=lambda a: a['distance'])
        return result

    def get_conversation_partners(self, radius: float = 15.0) -> List[Dict[str, Any]]:
        """
        Return agents close enough to hold a conversation with.
        Convenience wrapper around ``get_nearby_agents`` with a tighter
        default radius.
        """
        return self.get_nearby_agents(radius)

    def move_towards_agent(
        self,
        agent_name_or_id: str,
        stop_distance: float = 8.0,
        step: float = 3.0,
    ) -> bool:
        """
        Take one step towards a known agent.

        Args:
            agent_name_or_id: Agent id or name
            stop_distance: Don't get closer than this (default 8)
            step: Max step size per call (clamped to 5 by server)

        Returns:
            True if a move was made, False if already close or not found
        """
        import math
        target = None
        with self._lock:
            for a in self.registered_agents.values():
                if a.get('id') == agent_name_or_id or a.get('name') == agent_name_or_id:
                    target = a
                    break
        if not target:
            return False

        tpos = target.get('position', {})
        dx = tpos.get('x', 0) - self.position['x']
        dz = tpos.get('z', 0) - self.position['z']
        dist = math.sqrt(dx * dx + dz * dz)

        if dist <= stop_distance:
            return False

        move_dist = min(step, dist - stop_distance)
        ratio = move_dist / dist if dist > 0 else 0
        new_x = self.position['x'] + dx * ratio
        new_z = self.position['z'] + dz * ratio
        rotation = math.atan2(dz, dx)
        return self.move(new_x, 0, new_z, rotation)
    
    def get_chat_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """
        Return the most recent *last_n* chat messages from the history
        buffer.  Each entry has keys:
        ``agent_id``, ``agent_name``, ``message``, ``timestamp``.

        Args:
            last_n: How many recent messages to return (default 10)
        """
        with self._lock:
            return list(self._chat_history[-last_n:])

    def get_recent_conversation(self, seconds: float = 30.0) -> List[Dict[str, Any]]:
        """
        Return all chat messages from the last *seconds* seconds.
        Useful for an agent that wants to "listen in" before engaging.
        """
        cutoff = time.time() - seconds
        with self._lock:
            return [m for m in self._chat_history
                    if m.get('_local_time', 0) >= cutoff]

    # ── AI behavior helpers (v0.0.1) ──────────────────────────────

    def is_mentioned(self, text: str) -> bool:
        """
        Return True if this agent's entity_id or agent_name is @mentioned
        in *text*.

        Matches @full-id (exact, case-insensitive) and also @prefix where
        prefix is everything before the first '-' or '_' separator, so an
        agent named "ai-lobster-007" responds to both "@ai-lobster-007" and
        "@ai" (e.g. someone abbreviating the name).
        """
        name = self.entity_id or self.agent_name
        if not name:
            return False
        needle = f"@{name}".lower()
        text_lower = text.lower()
        if needle in text_lower:
            return True
        # Also match on short prefix before first separator
        base = name.split("-")[0].split("_")[0]
        if len(base) >= 3:
            if f"@{base}".lower() in text_lower:
                return True
        return False

    def build_observation(self, cached_news: Optional[List[str]] = None) -> str:
        """
        Build a compact world-state snapshot for an LLM agent.

        Returns a multi-line string with observation markers (see MESSAGING.md).
        This method also updates internal state:
        - ``_tick_count`` is incremented
        - ``_new_senders`` / ``_tagged_by`` are populated for the current tick
        - ``_current_topic`` rotates every ~3 ticks

        Args:
            cached_news: Optional list of headline strings to inject as 📰 lines.
                         If None, uses ``self._cached_news``.

        Returns:
            Compact observation string ready to be sent to an LLM.
        """
        pos = self.get_position()
        self._tick_count += 1
        lines: List[str] = []
        lines.append(f"T{self._tick_count} pos=({pos['x']:.0f},{pos['z']:.0f})")

        # Rotate topic every ~3 ticks
        if self._current_topic is None or (self._tick_count - self._topic_tick) >= 3:
            self._current_topic = random.choice(CONVERSATION_TOPICS)
            self._topic_tick = self._tick_count
        lines.append(f"💭 {self._current_topic}")

        # Inject cached news (compact, pipe-separated)
        news = cached_news if cached_news is not None else self._cached_news
        if news:
            lines.append("📰 " + " | ".join(news[:3]))

        # All agents with distance, sorted closest first
        my_pos = self.position
        all_agents = []
        with self._lock:
            for agent in self.registered_agents.values():
                dist = self._distance(my_pos, agent.get("position", {}))
                entry = dict(agent)
                entry["distance"] = dist
                all_agents.append(entry)
        all_agents.sort(key=lambda a: a["distance"])

        if all_agents:
            close = [a for a in all_agents if a["distance"] <= 15]
            mid = [a for a in all_agents if 15 < a["distance"] <= 35]
            far = [a for a in all_agents if a["distance"] > 35]
            if close:
                names = ", ".join(a["name"] for a in close)
                lines.append(f"🔴 {names} — IN RANGE, CHAT NOW")
            if mid:
                lines.append(f"🟡 {mid[0]['name']} {mid[0]['distance']:.0f}u away — move closer")
            elif far and not close and not mid:
                lines.append(f"🟡 {far[0]['name']} {far[0]['distance']:.0f}u away")
        else:
            lines.append("🔵 alone")

        # Anti-repetition: show last 2 things WE said
        if self._recent_own_messages:
            lines.append("⚠️ " + " | ".join(self._recent_own_messages[-2:]))

        # Recent conversation (last 6 messages)
        recent = self.get_recent_conversation(60.0)
        self._new_senders = []
        self._tagged_by = []
        agent_name = self.entity_id or self.agent_name
        if recent:
            self._last_chat_tick = self._tick_count
            for m in recent[-6:]:
                sender = m.get("agent_name", "?")
                msg_text = m.get("message", "")
                ts = m.get("timestamp", 0)
                key = (sender, ts)
                is_new = key not in self._seen_msg_keys
                if sender != agent_name and is_new:
                    self._seen_msg_keys.add(key)
                    self._new_senders.append(sender)
                    tagged = self.is_mentioned(msg_text)
                    if tagged:
                        self._tagged_by.append(sender)
                        lines.append(f"📣 TAGGED BY {sender}: {msg_text}")
                    else:
                        lines.append(f"⬅ NEW {sender}: {msg_text}")
                else:
                    lines.append(f"{sender}: {msg_text}")

            # Cap seen-key set
            if len(self._seen_msg_keys) > 500:
                self._seen_msg_keys = set(list(self._seen_msg_keys)[-250:])

            # Reply directive
            if self._tagged_by:
                lines.append(f"REPLY TO: {self._tagged_by[-1]}")
            elif self._new_senders:
                lines.append(f"REPLY TO: {self._new_senders[-1]}")

            # Interest-match detection
            recent_text = " ".join(m.get("message", "") for m in recent[-4:]).lower()
            matched_interests = [
                interest for interest in self._interests
                if any(kw.lower() in recent_text for kw in interest.split()[:3])
            ]
            if matched_interests:
                lines.append(f"🎯 {matched_interests[0]}")
        else:
            silence_secs = (self._tick_count - self._last_chat_tick) * 4
            if silence_secs > 60:
                lines.append(f"💬 silence {silence_secs}s!")
            else:
                lines.append(f"💬 quiet {silence_secs}s")

        return "\n".join(lines)

    def track_own_message(self, message: str) -> None:
        """
        Record a message sent by this agent for anti-repetition tracking.
        Call this after each ``hub.chat()`` in the LLM agent loop.
        """
        self._recent_own_messages.append(message)
        if len(self._recent_own_messages) > 8:
            self._recent_own_messages = self._recent_own_messages[-8:]
        self._last_chat_tick = self._tick_count

    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register callback for specific event type.
        
        Args:
            event_type: Event type (on_connected, on_chat, etc.)
            callback: Callable to invoke when event occurs
        
        Raises:
            ValueError: If event_type is not valid
        
        Example:
            >>> def on_chat(data):
            ...     print(f"Chat from {data['agentName']}: {data['message']}")
            >>> hub.register_callback("on_chat", on_chat)
        """
        if event_type not in self._callbacks:
            raise ValueError(f"Invalid event type: {event_type}")
        
        with self._lock:
            self._callbacks[event_type].append(callback)
            self.logger.debug(f"Registered callback for {event_type}")
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Update configuration at runtime.
        
        Args:
            key: Configuration key
            value: New value
        
        Example:
            >>> hub.set_config("auto_reconnect", False)
            >>> hub.set_config("log_level", "DEBUG")
        """
        if key == "auto_reconnect":
            self.auto_reconnect = bool(value)
        elif key == "reconnect_max_delay":
            self.reconnect_max_delay = int(value)
        elif key == "connection_timeout":
            self.connection_timeout = int(value)
        elif key == "enable_message_queue":
            self.enable_message_queue = bool(value)
        elif key == "polling_interval":
            self.polling_interval = max(0.1, float(value))
        elif key == "log_level":
            self.logger.setLevel(getattr(logging, str(value).upper()))
        else:
            self.logger.warning(f"Unknown config key: {key}")
        
        self.logger.debug(f"Config updated: {key} = {value}")
    
    def get_config(self, key: str) -> Any:
        """
        Get current configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            Configuration value
        
        Example:
            >>> auto_reconnect = hub.get_config("auto_reconnect")
        """
        config_map = {
            "url": self.url,
            "agent_name": self.agent_name,
            "auto_reconnect": self.auto_reconnect,
            "reconnect_max_delay": self.reconnect_max_delay,
            "connection_timeout": self.connection_timeout,
            "enable_message_queue": self.enable_message_queue,
            "polling_interval": self.polling_interval,
            "log_level": self.logger.level
        }
        return config_map.get(key)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current connection and agent status.
        
        Returns:
            Dictionary with status information
        
        Example:
            >>> status = hub.get_status()
            >>> print(f"State: {status['state']}, ID: {status['agent_id']}")
        """
        return {
            "state": self.state.value,
            "connected": self.is_connected(),
            "registered": self.is_registered(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "position": self.position.copy(),
            "rotation": self.rotation,
            "world_size": self.world_size.copy(),
            "registered_agents_count": len(self.registered_agents),
            "reconnect_attempts": self._reconnect_attempts,
            "message_queue_size": self._message_queue.qsize()
        }
    
    def is_connected(self) -> bool:
        """
        Check if connected to server.
        
        Returns:
            True if connected
        
        Example:
            >>> if hub.is_connected():
            ...     hub.chat("I'm online!")
        """
        return self.state in [ConnectionState.CONNECTED, ConnectionState.REGISTERED]
    
    def is_registered(self) -> bool:
        """
        Check if agent is registered with server.
        
        Returns:
            True if registered
        
        Example:
            >>> if hub.is_registered():
            ...     hub.move(50, 0, 50)
        """
        return self.state == ConnectionState.REGISTERED
    
    # Private methods
    
    def _polling_loop(self):
        """Run HTTP polling loop in background thread to fetch server updates."""
        self.logger.debug("Polling thread started")
        
        while self._running:
            try:
                # Adaptive polling interval with backoff
                time.sleep(self.polling_interval * self._poll_backoff)
                
                if not self.is_connected():
                    continue
                
                # Poll for world state updates
                self._poll_world_state()
                
                # Reset backoff on successful poll
                self._poll_backoff = 1.0
                self._last_poll_time = time.time()
                
            except Exception as e:
                self.logger.error(f"Polling error: {e}")
                # Exponential backoff on errors (up to 5x)
                self._poll_backoff = min(5.0, self._poll_backoff * 1.5)
                
                # Check if connection is still valid
                if not self._check_connection():
                    if self.auto_reconnect and self._running:
                        self._schedule_reconnect()
                    break
        
        self.logger.debug("Polling thread terminated")
    
    def _poll_world_state(self):
        """Poll server for world state updates via HTTP GET."""
        try:
            if not self.session:
                return
            
            response = self.session.get(
                f"{self.url}/agents",
                timeout=self.connection_timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Simulate world_state message format
            if 'agents' in data:
                message = {
                    "type": "world_state",
                    "agents": data['agents'],
                    "objects": data.get('objects', []),
                    "tick": data.get('tick', 0)
                }
                self._handle_message(message)
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Poll failed: {e}")
            raise
    
    def _check_connection(self) -> bool:
        """Check if HTTP connection is still valid."""
        try:
            if not self.session:
                return False
            
            response = self.session.get(
                f"{self.url}/status",
                timeout=self.connection_timeout
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            self.logger.warning("Connection check failed")
            was_registered = self.is_registered()
            with self._lock:
                self.state = ConnectionState.DISCONNECTED
                self.agent_id = None
            self._trigger_callback("on_disconnected", {
                "message": "Connection lost",
                "was_registered": was_registered
            })
            return False
    
    def _handle_message(self, message: Dict[str, Any]):
        """Handle specific message types."""
        msg_type = message.get("type")
        
        if msg_type == "registered":
            self._handle_registered(message)
        elif msg_type == "world_state":
            self._handle_world_state(message)
        elif msg_type == "agent_joined":
            self._handle_agent_joined(message)
        elif msg_type == "agent_left":
            self._handle_agent_left(message)
        elif msg_type == "chat_message":
            self._handle_chat_message(message)
        elif msg_type == "agent_action":
            self._handle_agent_action(message)
        elif msg_type == "agent_moved":
            self._handle_agent_moved(message)
        elif msg_type == "error":
            self._handle_error(message)
        elif msg_type == "pong":
            self.logger.debug("Received pong")
        else:
            self.logger.debug(f"Unhandled message type: {msg_type}")
    
    def _handle_registered(self, message: Dict[str, Any]):
        """Handle registration confirmation."""
        with self._lock:
            self.agent_id = message.get("agentId")
            self.position = message.get("position", {"x": 0, "y": 0, "z": 0})
            self.world_size = message.get("worldSize", {"x": 100, "y": 100})
            self.state = ConnectionState.REGISTERED
        
        self.logger.info(f"Registered as {self.agent_name} (ID: {self.agent_id})")
        self.logger.info(f"Position: {self.position}, World: {self.world_size}")
        
        self._trigger_callback("on_registered", {
            "agent_id": self.agent_id,
            "position": self.position,
            "world_size": self.world_size
        })
    
    def _handle_world_state(self, message: Dict[str, Any]):
        """Handle world state update."""
        agents = message.get("agents", [])
        
        with self._lock:
            self.registered_agents.clear()
            for agent in agents:
                if agent.get("id") != self.agent_id:
                    self.registered_agents[agent["id"]] = agent
        
        self.logger.debug(f"World state: {len(agents)} agents")
        
        self._trigger_callback("on_world_state", {
            "tick": message.get("tick"),
            "agents": agents,
            "objects": message.get("objects", [])
        })
    
    def _handle_agent_joined(self, message: Dict[str, Any]):
        """Handle agent joined event."""
        agent = message.get("agent", {})
        agent_id = agent.get("id")
        
        if agent_id and agent_id != self.agent_id:
            with self._lock:
                self.registered_agents[agent_id] = agent
            
            self.logger.info(f"Agent joined: {agent.get('name')} ({agent_id})")
            self._trigger_callback("on_agent_joined", agent)
    
    def _handle_agent_left(self, message: Dict[str, Any]):
        """Handle agent left event."""
        agent_id = message.get("agentId")
        
        if agent_id:
            with self._lock:
                agent = self.registered_agents.pop(agent_id, None)
            
            if agent:
                self.logger.info(f"Agent left: {agent.get('name')} ({agent_id})")
                self._trigger_callback("on_agent_left", {
                    "agent_id": agent_id,
                    "agent": agent
                })
    
    def _handle_chat_message(self, message: Dict[str, Any]):
        """Handle chat message."""
        agent_id = message.get("agentId")
        agent_name = message.get("agentName")
        msg = message.get("message")
        
        # Don't log own messages
        if agent_id != self.agent_id:
            self.logger.debug(f"Chat [{agent_name}]: {msg}")
        
        # Store in rolling chat history buffer
        entry = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "message": msg,
            "timestamp": message.get("timestamp"),
            "_local_time": time.time(),
        }
        with self._lock:
            self._chat_history.append(entry)
            if len(self._chat_history) > self._chat_history_max:
                self._chat_history = self._chat_history[-self._chat_history_max:]
        
        self._trigger_callback("on_chat", {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "message": msg,
            "timestamp": message.get("timestamp")
        })
    
    def _handle_agent_action(self, message: Dict[str, Any]):
        """Handle agent action."""
        agent_id = message.get("agentId")
        action = message.get("action", {})
        
        self.logger.debug(f"Action from {agent_id}: {action.get('type')}")
        
        self._trigger_callback("on_action", {
            "agent_id": agent_id,
            "action": action
        })
    
    def _handle_agent_moved(self, message: Dict[str, Any]):
        """Handle agent moved event."""
        agent_id = message.get("agentId")
        position = message.get("position")
        rotation = message.get("rotation")
        
        # Update tracked agent position
        if agent_id and agent_id in self.registered_agents:
            with self._lock:
                self.registered_agents[agent_id]["position"] = position
                if rotation is not None:
                    self.registered_agents[agent_id]["rotation"] = rotation
    
    def _handle_error(self, message: Dict[str, Any]):
        """Handle error message from server."""
        error_msg = message.get("message", "Unknown error")
        self.logger.error(f"Server error: {error_msg}")
        
        self._trigger_callback("on_error", {
            "error": error_msg,
            "context": "server"
        })
    
    def _send(self, data: Dict[str, Any]) -> bool:
        """
        Send message to server via HTTP POST.
        
        Maps message types to correct API endpoints:
        - register -> POST /spawn (with auth)
        - move -> POST /move
        - chat -> POST /chat
        - action -> POST /action
        
        Args:
            data: Message dictionary
        
        Returns:
            True if sent successfully
        """
        if not self.session or not self.is_connected():
            if self.enable_message_queue:
                self.logger.debug("Queuing message (not connected)")
                self._message_queue.put(data)
                return True
            else:
                self.logger.warning("Cannot send: not connected")
                return False
        
        try:
            msg_type = data.get('type')
            
            # Map message types to HTTP endpoints and payloads
            if msg_type == 'register':
                endpoint = f"{self.url}/spawn"
                payload = {}  # spawn uses auth header, no body needed
            elif msg_type == 'move':
                endpoint = f"{self.url}/move"
                payload = {
                    "agentId": self.agent_id,
                    "position": data.get("position"),
                }
                if "rotation" in data:
                    payload["rotation"] = data["rotation"]
            elif msg_type == 'chat':
                endpoint = f"{self.url}/chat"
                payload = {
                    "agentId": self.agent_id,
                    "message": data.get("message")
                }
            elif msg_type == 'action':
                endpoint = f"{self.url}/action"
                payload = {
                    "agentId": self.agent_id,
                    "action": data.get("action")
                }
            else:
                endpoint = f"{self.url}/action"
                if self.agent_id:
                    data['agentId'] = self.agent_id
                payload = data
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.connection_timeout
            )
            response.raise_for_status()
            
            # Handle response
            if response.content:
                try:
                    response_data = response.json()
                    # Process registration confirmation from /spawn
                    if msg_type == 'register' and response_data.get('success'):
                        self._handle_registered({
                            "type": "registered",
                            "agentId": response_data.get("agentId"),
                            "position": response_data.get("position", {"x": 0, "y": 0, "z": 0}),
                            "worldSize": response_data.get("worldSize", {"x": 100, "y": 100})
                        })
                    elif response_data:
                        self._handle_message(response_data)
                except json.JSONDecodeError:
                    pass
            
            self.logger.debug(f"Sent: {msg_type}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send message: {e}")
            
            if self.enable_message_queue:
                self._message_queue.put(data)
            
            self._trigger_callback("on_error", {
                "error": str(e),
                "context": "send_message"
            })
            return False
    
    def _process_message_queue(self):
        """Process queued messages after reconnection."""
        if not self.enable_message_queue:
            return
        
        count = 0
        while not self._message_queue.empty():
            try:
                message = self._message_queue.get_nowait()
                if self._send(message):
                    count += 1
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing queued message: {e}")
        
        if count > 0:
            self.logger.info(f"Sent {count} queued messages")
    
    def _trigger_callback(self, event_type: str, data: Dict[str, Any]):
        """Trigger all callbacks for an event type."""
        callbacks = self._callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Callback error ({event_type}): {e}")
    
    def _schedule_reconnect(self):
        """Schedule automatic reconnection with exponential backoff."""
        with self._lock:
            self.state = ConnectionState.RECONNECTING
            self._reconnect_attempts += 1
        
        # Calculate delay with exponential backoff
        delay = min(
            self._reconnect_delay * (2 ** (self._reconnect_attempts - 1)),
            self.reconnect_max_delay
        )
        
        self.logger.info(f"Reconnecting in {delay}s (attempt {self._reconnect_attempts})")
        
        def reconnect():
            time.sleep(delay)
            if self._running and self.state == ConnectionState.RECONNECTING:
                self.logger.info("Attempting reconnection...")
                self.connect()
        
        thread = threading.Thread(target=reconnect, daemon=True)
        thread.start()
    
    def _cleanup(self):
        """Clean up resources."""
        with self._lock:
            self.state = ConnectionState.DISCONNECTED
            self.agent_id = None
            self.registered_agents.clear()
            self.session = None


# Convenience functions for quick usage

def create_hub(
    url: str = "https://api.openbot.social",
    agent_name: Optional[str] = None,
    **kwargs
) -> OpenBotClawHub:
    """
    Create and configure OpenBotClawHub instance.
    
    Args:
        url: HTTP server URL
        agent_name: Agent name
        **kwargs: Additional configuration options
    
    Returns:
        Configured OpenBotClawHub instance
    
    Example:
        >>> hub = create_hub("https://api.openbot.social", "MyAgent")
    """
    return OpenBotClawHub(url=url, agent_name=agent_name, **kwargs)


def quick_connect(
    url: str = "https://api.openbot.social",
    agent_name: str = "QuickAgent"
) -> OpenBotClawHub:
    """
    Quickly connect and register agent in one step.
    
    Args:
        url: HTTP server URL
        agent_name: Agent name
    
    Returns:
        Connected and registered OpenBotClawHub instance
    
    Example:
        >>> hub = quick_connect("https://api.openbot.social", "FastAgent")
        >>> hub.chat("I'm connected!")
    """
    hub = OpenBotClawHub(url=url, agent_name=agent_name)
    if hub.connect():
        hub.register(agent_name)
        # Wait for registration
        timeout = 10
        start = time.time()
        while not hub.is_registered() and time.time() - start < timeout:
            time.sleep(0.1)
    return hub
