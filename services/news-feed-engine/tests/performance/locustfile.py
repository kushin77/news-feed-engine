"""
ElevatedIQ News Feed Engine - Performance Load Tests
Locust-based load testing suite for API endpoints

Usage:
    # Run locally
    locust -f testing/test_suite_2/performance/locustfile.py --host=http://127.0.0.1:8080

    # Run headless (CI/CD)
    locust -f testing/test_suite_2/performance/locustfile.py \
        --host=http://127.0.0.1:8080 \
        --headless \
        --users 100 \
        --spawn-rate 10 \
        --run-time 60s \
        --csv=reports/load-test

    # Docker
    docker compose -f docker-compose.test.yml run --rm load-tester
"""

import json
import random
import string
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


class NewsFeedEngineUser(HttpUser):
    """Simulates a typical News Feed Engine API user"""

    wait_time = between(0.5, 2.0)  # Wait 0.5-2s between tasks

    def on_start(self):
        """Initialize user session"""
        self.token = self._get_auth_token()
        self.content_ids = []
        self.trend_topics = [
            "AI",
            "technology",
            "automation",
            "machine learning",
            "data science",
        ]

    def _get_auth_token(self):
        """Simulate authentication (in real test, would use actual auth)"""
        return f"Bearer test-token-{self._random_string(16)}"

    def _random_string(self, length):
        """Generate random string"""
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def _headers(self):
        """Return common headers"""
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Tenant-ID": "elevatediq",
            "X-Request-ID": self._random_string(32),
        }

    # ========================================================================
    # Health and Readiness Endpoints
    # ========================================================================

    @task(10)
    def health_check(self):
        """Health check endpoint - high frequency"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(5)
    def readiness_check(self):
        """Readiness check endpoint"""
        self.client.get("/ready", headers=self._headers())

    @task(3)
    def metrics_endpoint(self):
        """Prometheus metrics endpoint"""
        self.client.get("/metrics", headers=self._headers())

    # ========================================================================
    # Content API Endpoints
    # ========================================================================

    @task(20)
    def get_content_feed(self):
        """Get content feed - main user action"""
        params = {
            "limit": random.choice([10, 20, 50]),
            "offset": random.randint(0, 100),
            "category": random.choice(
                ["all", "technology", "business", "entertainment"]
            ),
            "sort": random.choice(["trending", "recent", "popular"]),
        }
        with self.client.get(
            "/api/v1/content",
            params=params,
            headers=self._headers(),
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "items" in data and len(data["items"]) > 0:
                        # Store content IDs for later use
                        self.content_ids = [
                            item.get("id")
                            for item in data["items"][:5]
                            if item.get("id")
                        ]
                    response.success()
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(15)
    def get_content_by_id(self):
        """Get specific content item"""
        if not self.content_ids:
            content_id = self._random_string(24)
        else:
            content_id = random.choice(self.content_ids)

        self.client.get(f"/api/v1/content/{content_id}", headers=self._headers())

    @task(8)
    def search_content(self):
        """Search content endpoint"""
        query = random.choice(self.trend_topics)
        params = {"q": query, "limit": 20, "semantic": random.choice([True, False])}
        self.client.get(
            "/api/v1/content/search", params=params, headers=self._headers()
        )

    # ========================================================================
    # Trend API Endpoints
    # ========================================================================

    @task(12)
    def get_trending_topics(self):
        """Get trending topics"""
        params = {
            "limit": random.choice([10, 20, 50]),
            "timeframe": random.choice(["1h", "24h", "7d", "30d"]),
        }
        self.client.get("/api/v1/trends", params=params, headers=self._headers())

    @task(6)
    def get_trend_predictions(self):
        """Get trend predictions"""
        self.client.get("/api/v1/trends/predictions", headers=self._headers())

    @task(4)
    def get_trend_opportunities(self):
        """Get content opportunities based on trends"""
        self.client.get("/api/v1/trends/opportunities", headers=self._headers())

    # ========================================================================
    # Analytics API Endpoints
    # ========================================================================

    @task(5)
    def get_analytics_dashboard(self):
        """Get analytics dashboard data"""
        self.client.get("/api/v1/data/analytics/dashboard", headers=self._headers())

    @task(3)
    def get_content_performance(self):
        """Get content performance metrics"""
        if self.content_ids:
            content_id = random.choice(self.content_ids)
            self.client.get(
                f"/api/v1/data/analytics/content/{content_id}", headers=self._headers()
            )

    @task(2)
    def get_engagement_metrics(self):
        """Get engagement metrics"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "granularity": random.choice(["hour", "day", "week"]),
        }
        self.client.get(
            "/api/v1/data/analytics/engagement", params=params, headers=self._headers()
        )

    # ========================================================================
    # Video API Endpoints
    # ========================================================================

    @task(3)
    def get_video_queue(self):
        """Get video generation queue"""
        self.client.get("/api/v1/videos/queue", headers=self._headers())

    @task(1)
    def submit_video_job(self):
        """Submit a video generation job"""
        payload = {
            "content_id": random.choice(self.content_ids)
            if self.content_ids
            else self._random_string(24),
            "platform": random.choice(["youtube", "tiktok", "instagram"]),
            "style": random.choice(["news", "explainer", "shorts"]),
            "priority": random.choice(["low", "normal", "high"]),
        }
        self.client.post(
            "/api/v1/videos/generate", json=payload, headers=self._headers()
        )

    # ========================================================================
    # Publishing API Endpoints
    # ========================================================================

    @task(2)
    def get_scheduled_posts(self):
        """Get scheduled posts"""
        self.client.get("/api/v1/publishing/scheduled", headers=self._headers())

    @task(1)
    def get_publishing_queue(self):
        """Get publishing queue"""
        self.client.get("/api/v1/publishing/queue", headers=self._headers())


class ContentCreatorUser(HttpUser):
    """Simulates a content creator user with write-heavy operations"""

    wait_time = between(1.0, 3.0)
    weight = 1  # Less common than regular users

    def on_start(self):
        self.token = f"Bearer creator-token-{''.join(random.choices(string.ascii_letters, k=16))}"

    def _headers(self):
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Tenant-ID": "elevatediq",
        }

    @task(5)
    def create_content_brief(self):
        """Create a content brief"""
        payload = {
            "topic": random.choice(["AI trends", "Tech news", "Startup updates"]),
            "target_platforms": random.sample(
                ["youtube", "tiktok", "instagram", "linkedin"], k=2
            ),
            "tone": random.choice(["professional", "casual", "educational"]),
            "length": random.choice(["short", "medium", "long"]),
        }
        self.client.post(
            "/api/v1/content/briefs", json=payload, headers=self._headers()
        )

    @task(3)
    def submit_for_review(self):
        """Submit content for review"""
        content_id = "".join(random.choices(string.ascii_letters + string.digits, k=24))
        payload = {"action": "submit", "notes": "Ready for publication"}
        self.client.post(
            f"/api/v1/content/{content_id}/review",
            json=payload,
            headers=self._headers(),
        )

    @task(2)
    def schedule_publication(self):
        """Schedule content for publication"""
        content_id = "".join(random.choices(string.ascii_letters + string.digits, k=24))
        payload = {
            "platforms": random.sample(
                ["youtube", "tiktok", "instagram"], k=random.randint(1, 3)
            ),
            "scheduled_time": "2024-12-01T10:00:00Z",
            "timezone": "America/New_York",
        }
        self.client.post(
            f"/api/v1/content/{content_id}/schedule",
            json=payload,
            headers=self._headers(),
        )


class AdminUser(HttpUser):
    """Simulates admin operations - low frequency, high impact"""

    wait_time = between(3.0, 10.0)
    weight = 1  # Rare

    def on_start(self):
        self.token = (
            f"Bearer admin-token-{''.join(random.choices(string.ascii_letters, k=16))}"
        )

    def _headers(self):
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Tenant-ID": "elevatediq",
            "X-Admin": "true",
        }

    @task(3)
    def get_system_status(self):
        """Get system status"""
        self.client.get("/api/v1/admin/status", headers=self._headers())

    @task(2)
    def get_user_list(self):
        """Get user list"""
        params = {"limit": 50, "offset": 0}
        self.client.get("/api/v1/admin/users", params=params, headers=self._headers())

    @task(1)
    def get_audit_log(self):
        """Get audit log"""
        params = {"limit": 100, "days": 7}
        self.client.get("/api/v1/admin/audit", params=params, headers=self._headers())


# ============================================================================
# Custom Event Handlers for Metrics
# ============================================================================


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialize custom metrics on startup"""
    if isinstance(environment.runner, MasterRunner):
        print("Running as master - coordinating workers")
    elif isinstance(environment.runner, WorkerRunner):
        print("Running as worker")
    else:
        print("Running in standalone mode")


@events.request.add_listener
def on_request(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    **kwargs,
):
    """Track custom metrics for each request"""
    if response_time > 1000:
        print(f"⚠️ Slow request: {name} took {response_time}ms")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary when test stops"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST COMPLETE")
    print("=" * 60)
    if environment.stats.total.num_requests > 0:
        print(f"Total Requests: {environment.stats.total.num_requests}")
        print(f"Failures: {environment.stats.total.num_failures}")
        print(f"Avg Response Time: {environment.stats.total.avg_response_time:.2f}ms")
        print(f"RPS: {environment.stats.total.current_rps:.2f}")
    print("=" * 60)
