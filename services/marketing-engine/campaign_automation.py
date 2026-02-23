#!/usr/bin/env python3
"""
Marketing Campaign Automation Engine
=====================================

TOP 0.01% marketing automation capabilities:
- Multi-channel campaign orchestration
- A/B testing with statistical significance
- Customer journey automation
- Personalization at scale
- Real-time campaign analytics
- Attribution modeling

Usage:
    python3 campaign_automation.py campaign create --name "Q4 Launch"
    python3 campaign_automation.py ab-test analyze --test-id "test_123"
    python3 campaign_automation.py journey trigger --journey-id "onboarding"
"""

import argparse
import hashlib
import json
import logging
import math
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CampaignType(Enum):
    """Types of marketing campaigns."""

    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    MULTI_CHANNEL = "multi_channel"


class CampaignStatus(Enum):
    """Campaign lifecycle status."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TriggerType(Enum):
    """Types of automation triggers."""

    EVENT = "event"  # User performed an action
    TIME = "time"  # Time-based trigger
    SEGMENT = "segment"  # User enters/exits segment
    DATE = "date"  # Specific date/time
    API = "api"  # External API call


class JourneyNodeType(Enum):
    """Types of journey nodes."""

    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    DELAY = "delay"
    SPLIT = "split"
    EXIT = "exit"


@dataclass
class ABTestVariant:
    """A/B test variant."""

    id: str
    name: str
    weight: float  # Traffic percentage (0-1)
    content: Dict[str, Any]
    metrics: Dict[str, float] = field(default_factory=dict)
    sample_size: int = 0
    conversions: int = 0

    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.sample_size if self.sample_size > 0 else 0


@dataclass
class ABTest:
    """A/B test configuration."""

    id: str
    name: str
    campaign_id: str
    variants: List[ABTestVariant]
    primary_metric: str
    secondary_metrics: List[str] = field(default_factory=list)
    minimum_sample_size: int = 1000
    confidence_level: float = 0.95
    status: str = "running"
    winner: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def get_statistical_significance(self) -> Tuple[bool, float, Optional[str]]:
        """Calculate if the test has reached statistical significance."""
        if len(self.variants) < 2:
            return False, 0.0, None

        # Get control and best performing variant
        control = self.variants[0]
        best_variant = max(self.variants[1:], key=lambda v: v.conversion_rate)

        # Not enough samples
        if control.sample_size < self.minimum_sample_size:
            return False, 0.0, None

        # Z-test for proportions
        p1 = control.conversion_rate
        p2 = best_variant.conversion_rate
        n1 = control.sample_size
        n2 = best_variant.sample_size

        if p1 == 0 and p2 == 0:
            return False, 0.0, None

        # Pooled proportion
        p_pooled = (control.conversions + best_variant.conversions) / (n1 + n2)
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / n1 + 1 / n2))

        if se == 0:
            return False, 0.0, None

        z_score = (p2 - p1) / se

        # Convert to confidence
        confidence = 1 - 2 * (1 - self._normal_cdf(abs(z_score)))

        is_significant = confidence >= self.confidence_level
        winner = best_variant.id if is_significant and p2 > p1 else None

        return is_significant, confidence, winner

    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


@dataclass
class JourneyNode:
    """A node in a customer journey."""

    id: str
    type: JourneyNodeType
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)
    condition: Optional[str] = None


@dataclass
class CustomerJourney:
    """Customer journey automation."""

    id: str
    name: str
    description: str
    trigger: Dict[str, Any]
    nodes: List[JourneyNode]
    status: CampaignStatus = CampaignStatus.DRAFT
    entry_count: int = 0
    completion_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CampaignMetrics:
    """Campaign performance metrics."""

    sent: int = 0
    delivered: int = 0
    opened: int = 0
    clicked: int = 0
    converted: int = 0
    bounced: int = 0
    unsubscribed: int = 0
    complained: int = 0

    @property
    def delivery_rate(self) -> float:
        return self.delivered / self.sent if self.sent > 0 else 0

    @property
    def open_rate(self) -> float:
        return self.opened / self.delivered if self.delivered > 0 else 0

    @property
    def click_rate(self) -> float:
        return self.clicked / self.delivered if self.delivered > 0 else 0

    @property
    def conversion_rate(self) -> float:
        return self.converted / self.delivered if self.delivered > 0 else 0


@dataclass
class Campaign:
    """Marketing campaign."""

    id: str
    name: str
    type: CampaignType
    status: CampaignStatus
    subject: Optional[str] = None
    content: Dict[str, Any] = field(default_factory=dict)
    segment_id: Optional[str] = None
    ab_test: Optional[ABTest] = None
    scheduled_at: Optional[datetime] = None
    metrics: CampaignMetrics = field(default_factory=CampaignMetrics)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SegmentEngine:
    """Dynamic audience segmentation."""

    def __init__(self):
        self.segments: Dict[str, Dict] = {}
        self._create_default_segments()

    def _create_default_segments(self):
        """Create default marketing segments."""
        self.segments = {
            "all_users": {
                "name": "All Users",
                "conditions": [],
                "size": 0,
            },
            "active_users": {
                "name": "Active Users (30 days)",
                "conditions": [
                    {"field": "last_active", "operator": "gte", "value": "30_days_ago"}
                ],
                "size": 0,
            },
            "high_value": {
                "name": "High Value Customers",
                "conditions": [
                    {"field": "lifetime_value", "operator": "gte", "value": 1000}
                ],
                "size": 0,
            },
            "churning": {
                "name": "At Risk of Churn",
                "conditions": [
                    {"field": "last_active", "operator": "lte", "value": "60_days_ago"},
                    {
                        "field": "subscription_status",
                        "operator": "eq",
                        "value": "active",
                    },
                ],
                "size": 0,
            },
            "trial_users": {
                "name": "Trial Users",
                "conditions": [
                    {"field": "subscription_status", "operator": "eq", "value": "trial"}
                ],
                "size": 0,
            },
        }


class PersonalizationEngine:
    """Content personalization engine."""

    def __init__(self):
        self.templates: Dict[str, str] = {}

    def personalize(self, template: str, context: Dict[str, Any]) -> str:
        """Personalize content with user context."""
        result = template
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            result = result.replace(placeholder, str(value))
        return result

    def get_recommended_content(self, user_id: str, content_type: str) -> List[Dict]:
        """Get personalized content recommendations."""
        # In production, this would use ML recommendations
        return [
            {"id": "content_1", "title": "Recommended Article 1", "score": 0.95},
            {"id": "content_2", "title": "Recommended Article 2", "score": 0.87},
        ]


class AttributionModel:
    """Multi-touch attribution modeling."""

    def __init__(self):
        self.models = [
            "first_touch",
            "last_touch",
            "linear",
            "time_decay",
            "position_based",
        ]

    def calculate_attribution(
        self, touchpoints: List[Dict], model: str = "linear"
    ) -> Dict[str, float]:
        """Calculate attribution for touchpoints."""
        if not touchpoints:
            return {}

        if model == "first_touch":
            return {touchpoints[0]["channel"]: 1.0}

        elif model == "last_touch":
            return {touchpoints[-1]["channel"]: 1.0}

        elif model == "linear":
            weight = 1.0 / len(touchpoints)
            attribution = {}
            for tp in touchpoints:
                channel = tp["channel"]
                attribution[channel] = attribution.get(channel, 0) + weight
            return attribution

        elif model == "time_decay":
            # More recent touchpoints get more credit
            attribution = {}
            total_weight = 0
            for i, tp in enumerate(touchpoints):
                weight = 2 ** (i - len(touchpoints) + 1)  # Exponential decay
                total_weight += weight
                channel = tp["channel"]
                attribution[channel] = attribution.get(channel, 0) + weight

            # Normalize
            return {k: v / total_weight for k, v in attribution.items()}

        elif model == "position_based":
            # 40% first, 40% last, 20% middle
            attribution = {}
            if len(touchpoints) == 1:
                return {touchpoints[0]["channel"]: 1.0}
            elif len(touchpoints) == 2:
                return {
                    touchpoints[0]["channel"]: 0.5,
                    touchpoints[1]["channel"]: 0.5,
                }
            else:
                first = touchpoints[0]["channel"]
                last = touchpoints[-1]["channel"]
                attribution[first] = attribution.get(first, 0) + 0.4
                attribution[last] = attribution.get(last, 0) + 0.4

                middle_weight = 0.2 / (len(touchpoints) - 2)
                for tp in touchpoints[1:-1]:
                    channel = tp["channel"]
                    attribution[channel] = attribution.get(channel, 0) + middle_weight

                return attribution

        return {}


class CampaignAutomation:
    """Main campaign automation engine."""

    def __init__(self, storage_path: str = "tmp/campaigns"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.campaigns: Dict[str, Campaign] = {}
        self.journeys: Dict[str, CustomerJourney] = {}
        self.segment_engine = SegmentEngine()
        self.personalization = PersonalizationEngine()
        self.attribution = AttributionModel()

    def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        subject: Optional[str] = None,
        content: Optional[Dict] = None,
        segment_id: Optional[str] = None,
    ) -> Campaign:
        """Create a new campaign."""
        campaign_id = hashlib.md5(
            f"{name}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        campaign = Campaign(
            id=campaign_id,
            name=name,
            type=campaign_type,
            status=CampaignStatus.DRAFT,
            subject=subject,
            content=content or {},
            segment_id=segment_id,
        )

        self.campaigns[campaign_id] = campaign
        logger.info(f"Created campaign: {name} ({campaign_id})")
        return campaign

    def create_ab_test(
        self,
        campaign_id: str,
        name: str,
        variants: List[Dict],
        primary_metric: str = "conversion_rate",
    ) -> Optional[ABTest]:
        """Create an A/B test for a campaign."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None

        test_id = hashlib.md5(
            f"{name}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        variant_objects = []
        for i, v in enumerate(variants):
            variant = ABTestVariant(
                id=f"variant_{i}",
                name=v.get("name", f"Variant {chr(65 + i)}"),
                weight=v.get("weight", 1.0 / len(variants)),
                content=v.get("content", {}),
            )
            variant_objects.append(variant)

        test = ABTest(
            id=test_id,
            name=name,
            campaign_id=campaign_id,
            variants=variant_objects,
            primary_metric=primary_metric,
        )

        campaign.ab_test = test
        return test

    def record_ab_event(self, test_id: str, variant_id: str, converted: bool):
        """Record an A/B test event."""
        for campaign in self.campaigns.values():
            if campaign.ab_test and campaign.ab_test.id == test_id:
                for variant in campaign.ab_test.variants:
                    if variant.id == variant_id:
                        variant.sample_size += 1
                        if converted:
                            variant.conversions += 1
                        return True
        return False

    def create_journey(
        self,
        name: str,
        description: str,
        trigger: Dict,
        nodes: List[Dict],
    ) -> CustomerJourney:
        """Create a customer journey."""
        journey_id = hashlib.md5(
            f"{name}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        node_objects = []
        for n in nodes:
            node = JourneyNode(
                id=n.get(
                    "id", hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
                ),
                type=JourneyNodeType(n.get("type", "action")),
                name=n.get("name", "Unnamed Node"),
                config=n.get("config", {}),
                next_nodes=n.get("next_nodes", []),
                condition=n.get("condition"),
            )
            node_objects.append(node)

        journey = CustomerJourney(
            id=journey_id,
            name=name,
            description=description,
            trigger=trigger,
            nodes=node_objects,
        )

        self.journeys[journey_id] = journey
        logger.info(f"Created journey: {name} ({journey_id})")
        return journey

    def get_campaign_report(self, campaign_id: str) -> Optional[Dict]:
        """Get campaign performance report."""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None

        m = campaign.metrics
        report = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "status": campaign.status.value,
            "metrics": {
                "sent": m.sent,
                "delivered": m.delivered,
                "delivery_rate": f"{m.delivery_rate:.1%}",
                "opened": m.opened,
                "open_rate": f"{m.open_rate:.1%}",
                "clicked": m.clicked,
                "click_rate": f"{m.click_rate:.1%}",
                "converted": m.converted,
                "conversion_rate": f"{m.conversion_rate:.1%}",
                "bounced": m.bounced,
                "unsubscribed": m.unsubscribed,
            },
        }

        # Add A/B test results if present
        if campaign.ab_test:
            test = campaign.ab_test
            is_sig, confidence, winner = test.get_statistical_significance()
            report["ab_test"] = {
                "name": test.name,
                "status": test.status,
                "variants": [
                    {
                        "id": v.id,
                        "name": v.name,
                        "sample_size": v.sample_size,
                        "conversions": v.conversions,
                        "conversion_rate": f"{v.conversion_rate:.2%}",
                    }
                    for v in test.variants
                ],
                "is_significant": is_sig,
                "confidence": f"{confidence:.1%}",
                "winner": winner,
            }

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Marketing Campaign Automation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # Campaign commands
    campaign_parser = subparsers.add_parser("campaign", help="Campaign management")
    campaign_sub = campaign_parser.add_subparsers(dest="action")

    create_parser = campaign_sub.add_parser("create", help="Create campaign")
    create_parser.add_argument("--name", required=True, help="Campaign name")
    create_parser.add_argument("--type", default="email", help="Campaign type")

    list_parser = campaign_sub.add_parser("list", help="List campaigns")

    # A/B test commands
    ab_parser = subparsers.add_parser("ab-test", help="A/B testing")
    ab_sub = ab_parser.add_subparsers(dest="action")

    analyze_parser = ab_sub.add_parser("analyze", help="Analyze test")
    analyze_parser.add_argument("--test-id", required=True, help="Test ID")

    demo_parser = ab_sub.add_parser("demo", help="Run demo")

    # Journey commands
    journey_parser = subparsers.add_parser("journey", help="Customer journeys")
    journey_sub = journey_parser.add_subparsers(dest="action")

    trigger_parser = journey_sub.add_parser("trigger", help="Trigger journey")
    trigger_parser.add_argument("--journey-id", required=True, help="Journey ID")

    # Attribution commands
    attr_parser = subparsers.add_parser("attribution", help="Attribution modeling")
    attr_parser.add_argument("--model", default="linear", help="Attribution model")
    attr_parser.add_argument("--demo", action="store_true", help="Run demo")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    engine = CampaignAutomation()

    if args.command == "campaign":
        if args.action == "create":
            campaign = engine.create_campaign(
                name=args.name,
                campaign_type=CampaignType(args.type),
            )
            print(f"\n✅ Campaign created: {campaign.name}")
            print(f"   ID: {campaign.id}")
            print(f"   Type: {campaign.type.value}")
            print(f"   Status: {campaign.status.value}")

        elif args.action == "list":
            print("\n📋 Campaigns\n")
            if not engine.campaigns:
                print("No campaigns found.")
            for c in engine.campaigns.values():
                print(f"  • {c.name} ({c.id})")
                print(f"    Type: {c.type.value}, Status: {c.status.value}")

    elif args.command == "ab-test":
        if args.action == "demo":
            print("\n🧪 A/B Test Demo\n")
            print("=" * 60)

            # Create a campaign with A/B test
            campaign = engine.create_campaign(
                name="Email Subject Line Test",
                campaign_type=CampaignType.EMAIL,
            )

            test = engine.create_ab_test(
                campaign_id=campaign.id,
                name="Subject Line Test",
                variants=[
                    {
                        "name": "Control",
                        "content": {"subject": "Check out our new features!"},
                    },
                    {
                        "name": "Variant A",
                        "content": {"subject": "🚀 You won't believe what's new!"},
                    },
                    {
                        "name": "Variant B",
                        "content": {"subject": "[EXCLUSIVE] New features just for you"},
                    },
                ],
            )

            # Simulate test data
            print("Simulating A/B test results...\n")
            for _ in range(1500):
                variant = random.choices(
                    test.variants, weights=[v.weight for v in test.variants]
                )[0]

                # Different conversion rates per variant
                conversion_probs = {
                    "variant_0": 0.05,
                    "variant_1": 0.08,
                    "variant_2": 0.06,
                }
                converted = random.random() < conversion_probs.get(variant.id, 0.05)
                engine.record_ab_event(test.id, variant.id, converted)

            # Get results
            is_sig, confidence, winner = test.get_statistical_significance()

            print("📊 A/B Test Results:\n")
            for v in test.variants:
                bar_length = int(v.conversion_rate * 100)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                winner_badge = " 👑" if v.id == winner else ""
                print(f"  {v.name}: [{bar}] {v.conversion_rate:.2%}{winner_badge}")
                print(f"    Samples: {v.sample_size}, Conversions: {v.conversions}\n")

            print(f"  Statistical Significance: {'✅ Yes' if is_sig else '❌ No'}")
            print(f"  Confidence Level: {confidence:.1%}")
            if winner:
                winner_name = next(v.name for v in test.variants if v.id == winner)
                print(f"  Winner: {winner_name}")

    elif args.command == "attribution":
        if args.demo:
            print("\n📈 Attribution Modeling Demo\n")
            print("=" * 60)

            # Sample customer journey
            touchpoints = [
                {"channel": "Organic Search", "timestamp": "2024-01-01"},
                {"channel": "Email", "timestamp": "2024-01-05"},
                {"channel": "Paid Social", "timestamp": "2024-01-10"},
                {"channel": "Direct", "timestamp": "2024-01-15"},
                {"channel": "Email", "timestamp": "2024-01-20"},
            ]

            print("Customer Journey Touchpoints:")
            for tp in touchpoints:
                print(f"  • {tp['timestamp']}: {tp['channel']}")
            print()

            attribution = engine.attribution
            for model in attribution.models:
                result = attribution.calculate_attribution(touchpoints, model)
                print(f"\n{model.replace('_', ' ').title()} Attribution:")
                for channel, credit in sorted(result.items(), key=lambda x: -x[1]):
                    bar = "█" * int(credit * 20)
                    print(f"  {channel:<15} [{bar:<20}] {credit:.1%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
