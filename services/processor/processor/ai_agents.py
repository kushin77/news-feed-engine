"""
AI Agents Module - Autonomous Content Pipeline Agents

This module implements autonomous AI agents that work together to:
- Curate trending content (ContentCuratorAgent)
- Produce video content (VideoProducerAgent)
- Distribute across platforms (DistributorAgent)
- Analyze performance (AnalystAgent)
- Optimize engagement (EngagementAgent)

Elite AI Implementation - Self-evolving, autonomous decision-making agents
"""

import asyncio
import hashlib
import json
import logging
import random
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import anthropic

from .config import settings, utc_now
from .predictive_engine import TrendOpportunity as TrendData
from .predictive_engine import TrendSurfingEngine as TrendForecastEngine
from .publishing_orchestrator import PublishingOrchestrator
from .video_factory import PlatformConfig as VideoConfig
from .video_factory import VideoFactory as VideoProductionPipeline

logger = logging.getLogger(__name__)


# ============================================================================
# Agent State and Message Types
# ============================================================================


class AgentState(str, Enum):
    """Agent operational states"""

    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    LEARNING = "learning"
    ERROR = "error"


class MessageType(str, Enum):
    """Inter-agent message types"""

    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    RESPONSE = "response"
    ALERT = "alert"
    HANDOFF = "handoff"
    FEEDBACK = "feedback"


@dataclass
class AgentMessage:
    """Message passed between agents"""

    id: str
    sender: str
    recipient: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=utc_now)
    priority: int = 5  # 1-10, higher = more urgent
    requires_response: bool = False
    correlation_id: Optional[str] = None


@dataclass
class AgentDecision:
    """Record of an agent's decision"""

    decision_id: str
    agent_name: str
    decision_type: str
    input_data: Dict[str, Any]
    reasoning: str
    action: str
    confidence: float
    timestamp: datetime = field(default_factory=utc_now)
    outcome: Optional[str] = None
    feedback_score: Optional[float] = None


@dataclass
class ContentItem:
    """Content item flowing through the pipeline"""

    id: str
    title: str
    description: str
    trend_score: float
    category: str
    keywords: List[str]
    source_urls: List[str]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Pipeline state
    curated: bool = False
    script_generated: bool = False
    video_produced: bool = False
    published: bool = False
    platforms_published: List[str] = field(default_factory=list)

    # Performance
    views: int = 0
    engagement_rate: float = 0.0
    conversion_rate: float = 0.0


# ============================================================================
# Base Agent Architecture
# ============================================================================


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Agents are autonomous entities that:
    1. Observe their environment
    2. Make decisions using AI reasoning
    3. Execute actions
    4. Learn from outcomes
    """

    def __init__(
        self,
        name: str,
        description: str,
        claude_client: Optional[anthropic.AsyncAnthropic] = None,
        message_bus: Optional["AgentMessageBus"] = None,
    ):
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self.claude = claude_client or anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key or "test-key"
        )
        self.message_bus = message_bus
        self.memory: List[AgentDecision] = []
        self.performance_metrics: Dict[str, float] = defaultdict(float)
        self.learning_rate = 0.1
        self._running = False
        self._task_queue: asyncio.Queue = asyncio.Queue()

        # Agent-specific prompts
        self.system_prompt = self._build_system_prompt()

        logger.info(f"Agent '{name}' initialized")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for this agent"""
        return f"""You are {self.name}, an autonomous AI agent in a content production pipeline.

Your role: {self.description}

You have the following capabilities:
1. Analyze data and make informed decisions
2. Communicate with other agents in the pipeline
3. Execute actions within your domain
4. Learn from outcomes to improve over time

When making decisions:
- Provide clear reasoning for your choices
- Consider historical performance data
- Optimize for engagement and quality
- Be decisive but explain uncertainty when relevant

Respond with structured JSON for actionable decisions."""

    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to reason about a situation and decide on action.
        Returns structured decision data.
        """
        self.state = AgentState.THINKING

        prompt = f"""Given the following context, analyze and provide your decision:

Context:
{json.dumps(context, indent=2, default=str)}

Recent performance metrics:
{json.dumps(dict(self.performance_metrics), indent=2)}

Provide your response as JSON with:
- "reasoning": Your step-by-step analysis
- "decision": The action you recommend
- "confidence": 0-1 confidence score
- "parameters": Any parameters for the action
- "risks": Potential risks to consider
"""

        try:
            response = await self.claude.messages.create(
                model=settings.claude_model,
                max_tokens=2000,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            content = response.content[0].text

            # Try to extract JSON from response
            try:
                # Handle code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                decision_data = json.loads(content)
            except json.JSONDecodeError:
                decision_data = {
                    "reasoning": content,
                    "decision": "analyze_further",
                    "confidence": 0.5,
                    "parameters": {},
                    "risks": ["Could not parse structured response"],
                }

            return decision_data

        except Exception as e:
            logger.error(f"Agent {self.name} thinking error: {e}")
            return {
                "reasoning": f"Error during reasoning: {str(e)}",
                "decision": "retry",
                "confidence": 0.0,
                "parameters": {},
                "risks": [str(e)],
            }
        finally:
            self.state = AgentState.IDLE

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action. Override in subclasses for specific actions."""
        self.state = AgentState.EXECUTING
        try:
            result = await self._execute_action(action, parameters)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Agent {self.name} execution error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            self.state = AgentState.IDLE

    @abstractmethod
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Implement specific action execution"""
        pass

    def record_decision(self, decision: AgentDecision):
        """Record a decision for learning purposes"""
        self.memory.append(decision)
        # Keep memory bounded
        if len(self.memory) > 1000:
            self.memory = self.memory[-1000:]

    def learn_from_outcome(self, decision_id: str, outcome: str, score: float):
        """Learn from the outcome of a decision"""
        for decision in self.memory:
            if decision.decision_id == decision_id:
                decision.outcome = outcome
                decision.feedback_score = score

                # Update performance metrics
                self.performance_metrics["total_decisions"] += 1
                self.performance_metrics["avg_score"] = (
                    self.performance_metrics["avg_score"] * 0.9 + score * 0.1
                )

                logger.info(
                    f"Agent {self.name} learned from decision {decision_id}: "
                    f"score={score:.2f}"
                )
                break

    async def send_message(
        self,
        recipient: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: int = 5,
    ):
        """Send a message to another agent"""
        if not self.message_bus:
            logger.warning(f"Agent {self.name} has no message bus configured")
            return

        message = AgentMessage(
            id=hashlib.md5(
                f"{self.name}{utc_now()}".encode(), usedforsecurity=False
            ).hexdigest()[:12],
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority,
        )

        await self.message_bus.publish(message)

    async def receive_message(self, message: AgentMessage):
        """Handle an incoming message"""
        await self._task_queue.put(message)

    async def run(self):
        """Main agent loop"""
        self._running = True
        logger.info(f"Agent {self.name} starting main loop")

        while self._running:
            try:
                # Check for messages
                try:
                    message = await asyncio.wait_for(
                        self._task_queue.get(), timeout=1.0
                    )
                    await self._handle_message(message)
                except asyncio.TimeoutError:
                    pass

                # Run periodic tasks
                await self._periodic_tasks()

            except Exception as e:
                logger.error(f"Agent {self.name} loop error: {e}")
                self.state = AgentState.ERROR
                await asyncio.sleep(5)

        logger.info(f"Agent {self.name} stopped")

    async def stop(self):
        """Stop the agent"""
        self._running = False

    async def _handle_message(self, message: AgentMessage):
        """Handle incoming message - override in subclasses"""
        logger.info(
            f"Agent {self.name} received {message.message_type} from {message.sender}"
        )

    async def _periodic_tasks(self):
        """Run periodic maintenance tasks - override in subclasses"""
        await asyncio.sleep(1)


# ============================================================================
# Agent Message Bus
# ============================================================================


class AgentMessageBus:
    """Central message bus for inter-agent communication"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        self._running = False

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the message bus"""
        self.agents[agent.name] = agent
        agent.message_bus = self
        logger.info(f"Registered agent: {agent.name}")

    async def publish(self, message: AgentMessage):
        """Publish a message to be routed"""
        await self.message_queue.put(message)
        self.message_history.append(message)

        # Bound history
        if len(self.message_history) > 10000:
            self.message_history = self.message_history[-10000:]

    async def broadcast(
        self,
        sender: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        exclude: Optional[List[str]] = None,
    ):
        """Broadcast a message to all agents except sender and excluded"""
        exclude = exclude or []
        exclude.append(sender)

        for agent_name in self.agents:
            if agent_name not in exclude:
                message = AgentMessage(
                    id=hashlib.md5(
                        f"{sender}{utc_now()}{agent_name}".encode(),
                        usedforsecurity=False,
                    ).hexdigest()[:12],
                    sender=sender,
                    recipient=agent_name,
                    message_type=message_type,
                    payload=payload,
                )
                await self.message_queue.put(message)

    async def run(self):
        """Main message routing loop"""
        self._running = True
        logger.info("Message bus started")

        while self._running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)

                if message.recipient in self.agents:
                    await self.agents[message.recipient].receive_message(message)
                else:
                    logger.warning(f"Unknown recipient: {message.recipient}")

            except asyncio.TimeoutError:
                pass
            except Exception as e:
                logger.error(f"Message bus error: {e}")

        logger.info("Message bus stopped")

    async def stop(self):
        """Stop the message bus"""
        self._running = False


# ============================================================================
# Content Curator Agent
# ============================================================================


class ContentCuratorAgent(BaseAgent):
    """
    Autonomous agent that curates trending content.

    Responsibilities:
    - Monitor trend data sources
    - Evaluate content potential
    - Filter and prioritize content
    - Hand off curated content to VideoProducerAgent
    """

    def __init__(self, trend_engine: TrendForecastEngine, **kwargs):
        super().__init__(
            name="ContentCurator",
            description="I curate and prioritize trending content for video production. "
            "I analyze trends, evaluate virality potential, and select the best "
            "topics for our content pipeline.",
            **kwargs,
        )
        self.trend_engine = trend_engine
        self.curated_queue: List[ContentItem] = []
        self.rejection_reasons: Dict[str, int] = defaultdict(int)
        self.curation_criteria = {
            "min_trend_score": 0.6,
            "min_growth_rate": 0.05,
            "preferred_categories": [
                "technology",
                "business",
                "lifestyle",
                "entertainment",
            ],
            "max_age_hours": 24,
        }

    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute curator-specific actions"""

        if action == "curate_trends":
            return await self._curate_trends(parameters.get("limit", 10))

        elif action == "evaluate_content":
            return await self._evaluate_content(parameters["content"])

        elif action == "update_criteria":
            self.curation_criteria.update(parameters.get("criteria", {}))
            return {"updated_criteria": self.curation_criteria}

        elif action == "get_queue":
            return {
                "queue_size": len(self.curated_queue),
                "items": self.curated_queue[:5],
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    async def _curate_trends(self, limit: int = 10) -> List[ContentItem]:
        """Fetch and curate trending topics"""
        try:
            # Get trends from forecast engine
            trends = await self.trend_engine.get_trending_topics(limit=limit * 2)

            curated = []
            for trend in trends:
                # Evaluate each trend
                evaluation = await self._evaluate_trend(trend)

                if evaluation["approved"]:
                    content_item = ContentItem(
                        id=hashlib.md5(
                            trend.name.encode(), usedforsecurity=False
                        ).hexdigest()[:12],
                        title=trend.name,
                        description=trend.description or "",
                        trend_score=trend.score,
                        category=trend.category or "general",
                        keywords=trend.keywords or [],
                        source_urls=trend.sources or [],
                        created_at=utc_now(),
                        metadata={
                            "growth_rate": trend.growth_rate,
                            "momentum": trend.momentum,
                            "evaluation": evaluation,
                        },
                    )
                    content_item.curated = True
                    curated.append(content_item)

                    if len(curated) >= limit:
                        break
                else:
                    self.rejection_reasons[evaluation["reason"]] += 1

            # Add to queue
            self.curated_queue.extend(curated)

            # Notify video producer
            if curated and self.message_bus:
                await self.send_message(
                    recipient="VideoProducer",
                    message_type=MessageType.HANDOFF,
                    payload={
                        "content_items": [item.__dict__ for item in curated],
                        "priority": "normal",
                    },
                    priority=7,
                )

            logger.info(f"Curated {len(curated)} trends from {len(trends)} candidates")
            return curated

        except Exception as e:
            logger.error(f"Curation error: {e}")
            return []

    async def _evaluate_trend(self, trend: TrendData) -> Dict[str, Any]:
        """Evaluate a single trend for curation"""
        # Basic criteria check
        if trend.score < self.curation_criteria["min_trend_score"]:
            return {"approved": False, "reason": "low_score"}

        if trend.growth_rate < self.curation_criteria["min_growth_rate"]:
            return {"approved": False, "reason": "low_growth"}

        # Use AI for deeper evaluation
        context = {
            "trend_name": trend.name,
            "score": trend.score,
            "category": trend.category,
            "growth_rate": trend.growth_rate,
            "description": trend.description,
            "curation_criteria": self.curation_criteria,
        }

        decision = await self.think(context)

        # Record decision
        self.record_decision(
            AgentDecision(
                decision_id=hashlib.md5(
                    f"{trend.name}{utc_now()}".encode(),
                    usedforsecurity=False,
                ).hexdigest()[:12],
                agent_name=self.name,
                decision_type="trend_evaluation",
                input_data=context,
                reasoning=decision.get("reasoning", ""),
                action=decision.get("decision", ""),
                confidence=decision.get("confidence", 0.5),
            )
        )

        approved = decision.get("decision", "").lower() in [
            "approve",
            "accept",
            "curate",
        ]
        return {
            "approved": approved,
            "reason": decision.get("decision", "unknown"),
            "confidence": decision.get("confidence", 0.5),
            "reasoning": decision.get("reasoning", ""),
        }

    async def _evaluate_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate specific content for quality"""
        context = {
            "content": content,
            "criteria": self.curation_criteria,
            "task": "Evaluate this content for production suitability",
        }

        return await self.think(context)

    async def _periodic_tasks(self):
        """Periodically check for new trends"""
        # Auto-curate every 5 minutes (simulated with counter)
        if not hasattr(self, "_periodic_counter"):
            self._periodic_counter = 0

        self._periodic_counter += 1
        if self._periodic_counter >= 300:  # ~5 minutes
            self._periodic_counter = 0
            await self._curate_trends(limit=5)

        await asyncio.sleep(1)


# ============================================================================
# Video Producer Agent
# ============================================================================


class VideoProducerAgent(BaseAgent):
    """
    Autonomous agent that produces video content.

    Responsibilities:
    - Receive curated content
    - Generate scripts using AI
    - Produce videos via ElevenLabs + D-ID
    - Queue for distribution
    """

    def __init__(self, video_pipeline: VideoProductionPipeline, **kwargs):
        super().__init__(
            name="VideoProducer",
            description="I produce high-quality video content from curated topics. "
            "I write engaging scripts, generate voiceovers, and create videos "
            "optimized for each platform.",
            **kwargs,
        )
        self.video_pipeline = video_pipeline
        self.production_queue: List[ContentItem] = []
        self.completed_videos: List[Dict[str, Any]] = []
        self.production_stats = {
            "total_produced": 0,
            "avg_production_time": 0,
            "success_rate": 1.0,
        }

    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute producer-specific actions"""

        if action == "produce_video":
            return await self._produce_video(parameters["content"])

        elif action == "generate_script":
            return await self._generate_script(parameters["content"])

        elif action == "queue_content":
            self.production_queue.append(parameters["content"])
            return {"queue_size": len(self.production_queue)}

        elif action == "get_stats":
            return self.production_stats

        else:
            raise ValueError(f"Unknown action: {action}")

    async def _generate_script(self, content: ContentItem) -> Dict[str, Any]:
        """Generate video script from content"""
        context = {
            "title": content.title,
            "description": content.description,
            "keywords": content.keywords,
            "trend_score": content.trend_score,
            "category": content.category,
            "task": "Write an engaging 60-90 second video script for this topic",
        }

        decision = await self.think(context)

        script = decision.get("parameters", {}).get("script", "")
        if not script:
            # Generate more explicitly
            response = await self.claude.messages.create(
                model=settings.claude_model,
                max_tokens=2000,
                system="You are an expert video script writer. Write engaging, concise scripts.",
                messages=[
                    {
                        "role": "user",
                        "content": f"""Write a 60-90 second video script about: {content.title}

Description: {content.description}
Keywords: {', '.join(content.keywords)}

The script should be:
- Hook viewers in the first 5 seconds
- Informative but entertaining
- End with a call to action

Format:
HOOK: [Opening hook]
BODY: [Main content]
CTA: [Call to action]
""",
                    }
                ],
            )
            script = response.content[0].text

        return {
            "script": script,
            "estimated_duration": 75,  # seconds
            "content_id": content.id,
        }

    async def _produce_video(self, content: ContentItem) -> Dict[str, Any]:
        """Produce a complete video from content"""
        start_time = utc_now()

        try:
            # Generate script
            script_result = await self._generate_script(content)
            content.script_generated = True

            # Determine video configuration based on content
            config = self._optimize_video_config(content)

            # Produce video
            video_result = await self.video_pipeline.produce_video(
                script=script_result["script"], title=content.title, config=config
            )

            content.video_produced = True
            content.metadata["video_url"] = video_result.get("video_url")
            content.metadata["production_time"] = (
                utc_now() - start_time
            ).total_seconds()

            # Update stats
            self.production_stats["total_produced"] += 1
            self.production_stats["avg_production_time"] = (
                self.production_stats["avg_production_time"] * 0.9
                + content.metadata["production_time"] * 0.1
            )

            self.completed_videos.append(
                {
                    "content": content.__dict__,
                    "video": video_result,
                    "produced_at": utc_now().isoformat(),
                }
            )

            # Notify distributor
            if self.message_bus:
                await self.send_message(
                    recipient="Distributor",
                    message_type=MessageType.HANDOFF,
                    payload={"content": content.__dict__, "video": video_result},
                    priority=8,
                )

            logger.info(f"Produced video for: {content.title}")
            return video_result

        except Exception as e:
            logger.error(f"Video production error: {e}")
            self.production_stats["success_rate"] *= 0.99
            return {"error": str(e), "content_id": content.id}

    def _optimize_video_config(self, content: ContentItem) -> VideoConfig:
        """Determine optimal video configuration based on content"""
        # Select voice based on category
        voice_map = {
            "technology": "onyx",
            "business": "adam",
            "lifestyle": "nova",
            "entertainment": "shimmer",
            "news": "echo",
        }

        voice = voice_map.get(content.category, "alloy")

        # Select avatar based on trend score
        avatar = "professional-1" if content.trend_score > 0.8 else "casual-1"

        return VideoConfig(
            voice_id=voice,
            avatar_id=avatar,
            resolution="1080p",
            aspect_ratio="16:9",
            background="gradient",
            subtitles_enabled=True,
        )

    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        if message.message_type == MessageType.HANDOFF:
            # Received content from curator
            items = message.payload.get("content_items", [])
            for item_data in items:
                content = ContentItem(**item_data)
                self.production_queue.append(content)

            logger.info(f"Received {len(items)} items for production")

    async def _periodic_tasks(self):
        """Process production queue"""
        if self.production_queue and self.state == AgentState.IDLE:
            content = self.production_queue.pop(0)
            await self._produce_video(content)

        await asyncio.sleep(1)


# ============================================================================
# Distributor Agent
# ============================================================================


class DistributorAgent(BaseAgent):
    """
    Autonomous agent that distributes content across platforms.

    Responsibilities:
    - Receive produced videos
    - Optimize for each platform
    - Schedule and publish content
    - Track distribution status
    """

    def __init__(self, publishing_orchestrator: PublishingOrchestrator, **kwargs):
        super().__init__(
            name="Distributor",
            description="I distribute video content across all social platforms. "
            "I optimize timing, format each post for maximum engagement, "
            "and track publishing status.",
            **kwargs,
        )
        self.publisher = publishing_orchestrator
        self.distribution_queue: List[Dict[str, Any]] = []
        self.published_content: List[Dict[str, Any]] = []
        self.platform_performance: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"posts": 0, "success_rate": 1.0, "avg_engagement": 0.0}
        )

    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute distributor-specific actions"""

        if action == "distribute":
            return await self._distribute(
                parameters["content"], parameters.get("platforms")
            )

        elif action == "schedule":
            return await self._schedule(
                parameters["content"], parameters["schedule_time"]
            )

        elif action == "optimize_timing":
            return await self._optimize_timing(parameters.get("platforms", []))

        elif action == "get_performance":
            return dict(self.platform_performance)

        else:
            raise ValueError(f"Unknown action: {action}")

    async def _distribute(
        self, content: Dict[str, Any], platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Distribute content to specified platforms"""
        platforms = platforms or [
            "youtube",
            "tiktok",
            "instagram",
            "linkedin",
            "twitter",
        ]

        results = {}

        for platform in platforms:
            try:
                # Optimize content for platform
                optimized = await self._optimize_for_platform(content, platform)

                # Publish
                result = await self.publisher.publish(
                    platform=platform, content=optimized
                )

                results[platform] = {
                    "success": result.get("success", False),
                    "post_id": result.get("post_id"),
                    "url": result.get("url"),
                }

                # Update metrics
                perf = self.platform_performance[platform]
                perf["posts"] += 1
                if result.get("success"):
                    perf["success_rate"] = perf["success_rate"] * 0.95 + 0.05
                else:
                    perf["success_rate"] *= 0.95

            except Exception as e:
                logger.error(f"Distribution to {platform} failed: {e}")
                results[platform] = {"success": False, "error": str(e)}

        # Record distribution
        self.published_content.append(
            {
                "content_id": content.get("id"),
                "platforms": results,
                "distributed_at": utc_now().isoformat(),
            }
        )

        # Notify analyst
        if self.message_bus:
            await self.send_message(
                recipient="Analyst",
                message_type=MessageType.HANDOFF,
                payload={
                    "content_id": content.get("id"),
                    "distribution_results": results,
                },
            )

        logger.info(f"Distributed to {len(platforms)} platforms")
        return results

    async def _optimize_for_platform(
        self, content: Dict[str, Any], platform: str
    ) -> Dict[str, Any]:
        """Optimize content for a specific platform"""
        # Platform-specific configurations
        platform_specs = {
            "youtube": {
                "max_title_length": 100,
                "max_description_length": 5000,
                "hashtags": 15,
                "aspect_ratio": "16:9",
            },
            "tiktok": {
                "max_title_length": 150,
                "max_description_length": 2200,
                "hashtags": 5,
                "aspect_ratio": "9:16",
            },
            "instagram": {
                "max_title_length": 125,
                "max_description_length": 2200,
                "hashtags": 30,
                "aspect_ratio": "1:1",
            },
            "linkedin": {
                "max_title_length": 200,
                "max_description_length": 3000,
                "hashtags": 5,
                "aspect_ratio": "16:9",
            },
            "twitter": {
                "max_title_length": 280,
                "max_description_length": 280,
                "hashtags": 3,
                "aspect_ratio": "16:9",
            },
        }

        specs = platform_specs.get(platform, platform_specs["youtube"])

        # Use AI to optimize
        context = {
            "content": content,
            "platform": platform,
            "specs": specs,
            "task": f"Optimize this content for {platform}",
        }

        decision = await self.think(context)

        optimized = content.copy()
        if decision.get("parameters"):
            optimized.update(decision["parameters"])

        # Ensure within limits
        if "title" in optimized:
            optimized["title"] = optimized["title"][: specs["max_title_length"]]

        return optimized

    async def _schedule(
        self, content: Dict[str, Any], schedule_time: datetime
    ) -> Dict[str, Any]:
        """Schedule content for future distribution"""
        self.distribution_queue.append(
            {
                "content": content,
                "scheduled_for": schedule_time,
                "created_at": utc_now(),
            }
        )

        return {
            "scheduled": True,
            "schedule_time": schedule_time.isoformat(),
            "queue_position": len(self.distribution_queue),
        }

    async def _optimize_timing(self, platforms: List[str]) -> Dict[str, Dict[str, str]]:
        """Get optimal posting times for platforms"""
        # Best posting times based on general data
        optimal_times = {
            "youtube": {"best_day": "Thursday", "best_time": "15:00 UTC"},
            "tiktok": {"best_day": "Tuesday", "best_time": "19:00 UTC"},
            "instagram": {"best_day": "Wednesday", "best_time": "11:00 UTC"},
            "linkedin": {"best_day": "Tuesday", "best_time": "10:00 UTC"},
            "twitter": {"best_day": "Wednesday", "best_time": "09:00 UTC"},
        }

        return {
            p: optimal_times.get(p, {"best_day": "Monday", "best_time": "12:00 UTC"})
            for p in platforms
        }

    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        if message.message_type == MessageType.HANDOFF:
            # Received video from producer
            content = message.payload.get("content", {})
            video = message.payload.get("video", {})
            content["video"] = video

            await self._distribute(content)


# ============================================================================
# Analyst Agent
# ============================================================================


class AnalystAgent(BaseAgent):
    """
    Autonomous agent that analyzes content performance.

    Responsibilities:
    - Track content metrics
    - Analyze performance patterns
    - Generate insights and recommendations
    - Feed learnings back to other agents
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Analyst",
            description="I analyze content performance across all platforms. "
            "I identify patterns, generate insights, and provide "
            "recommendations to improve future content.",
            **kwargs,
        )
        self.content_metrics: Dict[str, Dict[str, Any]] = {}
        self.insights: List[Dict[str, Any]] = []
        self.recommendations: List[Dict[str, Any]] = []

    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute analyst-specific actions"""

        if action == "analyze_content":
            return await self._analyze_content(parameters["content_id"])

        elif action == "generate_insights":
            return await self._generate_insights()

        elif action == "get_recommendations":
            return await self._get_recommendations(parameters.get("category"))

        elif action == "benchmark":
            return await self._benchmark(parameters.get("timeframe", "week"))

        else:
            raise ValueError(f"Unknown action: {action}")

    async def _analyze_content(self, content_id: str) -> Dict[str, Any]:
        """Analyze specific content performance"""
        metrics = self.content_metrics.get(content_id, {})

        if not metrics:
            return {"error": "No metrics found for content"}

        context = {
            "content_id": content_id,
            "metrics": metrics,
            "task": "Analyze this content's performance and provide insights",
        }

        analysis = await self.think(context)

        return {
            "content_id": content_id,
            "metrics": metrics,
            "analysis": analysis.get("reasoning", ""),
            "recommendations": analysis.get("parameters", {}).get(
                "recommendations", []
            ),
        }

    async def _generate_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from all content performance"""
        if not self.content_metrics:
            return []

        context = {
            "all_metrics": self.content_metrics,
            "previous_insights": self.insights[-10:] if self.insights else [],
            "task": "Generate actionable insights from content performance data",
        }

        analysis = await self.think(context)

        new_insights = analysis.get("parameters", {}).get("insights", [])
        if isinstance(new_insights, list):
            self.insights.extend(
                [
                    {"insight": i, "generated_at": utc_now().isoformat()}
                    for i in new_insights
                ]
            )

        # Share insights with other agents
        if self.message_bus and new_insights:
            await self.message_bus.broadcast(
                sender=self.name,
                message_type=MessageType.FEEDBACK,
                payload={"insights": new_insights},
            )

        return self.insights[-10:]

    async def _get_recommendations(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recommendations for content improvement"""
        context = {
            "content_metrics": self.content_metrics,
            "category_filter": category,
            "task": "Provide specific recommendations to improve content performance",
        }

        analysis = await self.think(context)

        recommendations = analysis.get("parameters", {}).get("recommendations", [])

        return recommendations

    async def _benchmark(self, timeframe: str = "week") -> Dict[str, Any]:
        """Generate performance benchmarks"""
        # Calculate aggregate metrics
        total_views = sum(m.get("views", 0) for m in self.content_metrics.values())
        total_engagement = sum(
            m.get("engagement", 0) for m in self.content_metrics.values()
        )
        content_count = len(self.content_metrics)

        benchmarks = {
            "timeframe": timeframe,
            "content_count": content_count,
            "total_views": total_views,
            "total_engagement": total_engagement,
            "avg_views": total_views / max(content_count, 1),
            "avg_engagement": total_engagement / max(content_count, 1),
            "top_performers": sorted(
                self.content_metrics.items(),
                key=lambda x: x[1].get("views", 0),
                reverse=True,
            )[:5],
        }

        return benchmarks

    def record_metrics(self, content_id: str, metrics: Dict[str, Any]):
        """Record metrics for content"""
        if content_id not in self.content_metrics:
            self.content_metrics[content_id] = {}

        self.content_metrics[content_id].update(metrics)
        self.content_metrics[content_id]["updated_at"] = utc_now().isoformat()

    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        if message.message_type == MessageType.HANDOFF:
            # Received distribution results
            content_id = message.payload.get("content_id")
            results = message.payload.get("distribution_results", {})

            self.record_metrics(
                content_id,
                {
                    "platforms": list(results.keys()),
                    "distribution_success": sum(
                        1 for r in results.values() if r.get("success")
                    ),
                    "distributed_at": utc_now().isoformat(),
                },
            )


# ============================================================================
# Engagement Agent
# ============================================================================


class EngagementAgent(BaseAgent):
    """
    Autonomous agent that optimizes audience engagement.

    Responsibilities:
    - Monitor comments and interactions
    - Generate response suggestions
    - Identify engagement opportunities
    - Optimize posting strategies
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Engager",
            description="I optimize audience engagement and community interaction. "
            "I monitor comments, suggest responses, and identify opportunities "
            "to increase engagement.",
            **kwargs,
        )
        self.engagement_queue: List[Dict[str, Any]] = []
        self.response_templates: Dict[str, List[str]] = {
            "positive": [
                "Thank you for the kind words! 🙏",
                "Glad you enjoyed it! More content coming soon.",
                "Appreciate the support! 💪",
            ],
            "question": [
                "Great question! Let me explain...",
                "Thanks for asking! Here's what you need to know...",
                "Happy to help! The answer is...",
            ],
            "negative": [
                "Thanks for the feedback, we'll work on improving.",
                "Appreciate you sharing your thoughts.",
                "We hear you and are working to do better.",
            ],
        }
        self.engagement_strategies: List[Dict[str, Any]] = []

    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute engagement-specific actions"""

        if action == "analyze_comments":
            return await self._analyze_comments(parameters["comments"])

        elif action == "generate_response":
            return await self._generate_response(parameters["comment"])

        elif action == "optimize_strategy":
            return await self._optimize_strategy(parameters.get("platform"))

        elif action == "identify_opportunities":
            return await self._identify_opportunities()

        else:
            raise ValueError(f"Unknown action: {action}")

    async def _analyze_comments(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a batch of comments"""
        context = {
            "comments": comments,
            "task": "Analyze these comments for sentiment and engagement opportunities",
        }

        analysis = await self.think(context)

        return {
            "total_comments": len(comments),
            "sentiment_breakdown": analysis.get("parameters", {}).get("sentiment", {}),
            "priority_responses": analysis.get("parameters", {}).get("priorities", []),
            "opportunities": analysis.get("parameters", {}).get("opportunities", []),
        }

    async def _generate_response(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response for a specific comment"""
        context = {
            "comment": comment,
            "templates": self.response_templates,
            "task": "Generate an engaging, authentic response to this comment",
        }

        decision = await self.think(context)

        response = decision.get("parameters", {}).get("response", "")

        if not response:
            # Use template based on sentiment
            sentiment = decision.get("parameters", {}).get("sentiment", "positive")
            templates = self.response_templates.get(
                sentiment, self.response_templates["positive"]
            )
            response = random.choice(templates)

        return {
            "original_comment": comment,
            "suggested_response": response,
            "confidence": decision.get("confidence", 0.7),
            "auto_approve": decision.get("confidence", 0) > 0.85,
        }

    async def _optimize_strategy(
        self, platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize engagement strategy for platform(s)"""
        context = {
            "platform": platform,
            "current_strategies": self.engagement_strategies,
            "task": "Analyze and optimize engagement strategy",
        }

        decision = await self.think(context)

        new_strategy = {
            "platform": platform or "all",
            "recommendations": decision.get("parameters", {}).get("strategy", {}),
            "generated_at": utc_now().isoformat(),
        }

        self.engagement_strategies.append(new_strategy)

        return new_strategy

    async def _identify_opportunities(self) -> List[Dict[str, Any]]:
        """Identify engagement opportunities"""
        context = {
            "engagement_queue": self.engagement_queue[-20:],
            "strategies": self.engagement_strategies[-5:],
            "task": "Identify high-value engagement opportunities",
        }

        decision = await self.think(context)

        opportunities = decision.get("parameters", {}).get("opportunities", [])

        # Notify relevant agents
        if self.message_bus and opportunities:
            await self.send_message(
                recipient="ContentCurator",
                message_type=MessageType.FEEDBACK,
                payload={"engagement_opportunities": opportunities},
            )

        return opportunities

    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        if message.message_type == MessageType.FEEDBACK:
            # Received insights from analyst
            insights = message.payload.get("insights", [])
            for insight in insights:
                # Incorporate into strategy
                self.engagement_strategies.append(
                    {
                        "source": "analyst_insight",
                        "insight": insight,
                        "added_at": utc_now().isoformat(),
                    }
                )


# ============================================================================
# Agent Orchestrator
# ============================================================================


class AgentOrchestrator:
    """
    Orchestrates all AI agents in the content pipeline.

    Manages:
    - Agent lifecycle
    - Inter-agent communication
    - Pipeline coordination
    - Performance monitoring
    """

    def __init__(self):
        self.message_bus = AgentMessageBus()
        self.agents: Dict[str, BaseAgent] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []

        # Initialize components
        self.trend_engine = TrendForecastEngine()
        self.video_pipeline = VideoProductionPipeline()
        self.publisher = PublishingOrchestrator()

    async def initialize(self):
        """Initialize all agents"""
        # Create agents
        self.agents["curator"] = ContentCuratorAgent(trend_engine=self.trend_engine)
        self.agents["producer"] = VideoProducerAgent(video_pipeline=self.video_pipeline)
        self.agents["distributor"] = DistributorAgent(
            publishing_orchestrator=self.publisher
        )
        self.agents["analyst"] = AnalystAgent()
        self.agents["engager"] = EngagementAgent()

        # Register with message bus
        for agent in self.agents.values():
            self.message_bus.register_agent(agent)

        logger.info("Agent orchestrator initialized with all agents")

    async def start(self):
        """Start all agents and message bus"""
        if self._running:
            return

        self._running = True

        # Start message bus
        self._tasks.append(asyncio.create_task(self.message_bus.run()))

        # Start all agents
        for agent in self.agents.values():
            self._tasks.append(asyncio.create_task(agent.run()))

        logger.info("Agent orchestrator started")

    async def stop(self):
        """Stop all agents and message bus"""
        self._running = False

        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()

        # Stop message bus
        await self.message_bus.stop()

        # Cancel tasks
        for task in self._tasks:
            task.cancel()

        logger.info("Agent orchestrator stopped")

    async def run_pipeline(self, topic: str) -> Dict[str, Any]:
        """Run the full content pipeline for a topic"""
        start_time = utc_now()

        # Create content item
        content = ContentItem(
            id=hashlib.md5(
                f"{topic}{start_time}".encode(), usedforsecurity=False
            ).hexdigest()[:12],
            title=topic,
            description=f"Content about {topic}",
            trend_score=0.8,
            category="general",
            keywords=topic.split(),
            source_urls=[],
            created_at=start_time,
        )

        results = {"content_id": content.id, "topic": topic, "stages": {}}

        try:
            # 1. Curate
            curator = self.agents.get("curator")
            if curator:
                eval_result = await curator.execute(
                    "evaluate_content", {"content": content.__dict__}
                )
                results["stages"]["curation"] = eval_result

            # 2. Produce
            producer = self.agents.get("producer")
            if producer:
                prod_result = await producer.execute(
                    "produce_video", {"content": content}
                )
                results["stages"]["production"] = prod_result

            # 3. Distribute
            distributor = self.agents.get("distributor")
            if distributor:
                dist_result = await distributor.execute(
                    "distribute", {"content": content.__dict__}
                )
                results["stages"]["distribution"] = dist_result

            results["success"] = True
            results["duration_seconds"] = (utc_now() - start_time).total_seconds()

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "running": self._running,
            "agents": {
                name: {
                    "state": agent.state.value,
                    "metrics": dict(agent.performance_metrics),
                }
                for name, agent in self.agents.items()
            },
            "message_bus": {
                "registered_agents": list(self.message_bus.agents.keys()),
                "message_history_size": len(self.message_bus.message_history),
            },
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_agent_system() -> AgentOrchestrator:
    """Factory function to create the complete agent system"""
    return AgentOrchestrator()


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """Example usage of the agent system"""
    orchestrator = create_agent_system()

    try:
        await orchestrator.initialize()
        await orchestrator.start()

        # Run a sample pipeline
        result = await orchestrator.run_pipeline("AI Trends 2025")
        print(json.dumps(result, indent=2, default=str))

        # Get status
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))

        # Let agents run for a bit
        await asyncio.sleep(10)

    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
