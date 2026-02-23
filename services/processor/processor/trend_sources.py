"""
Trend Data Sources Module - Real-time Trend Detection

This module integrates with multiple trend data sources:
- Google Trends (via pytrends)
- Twitter/X Trending Topics
- Reddit Rising/Hot Posts
- YouTube Trending
- TikTok Discover
- News APIs (NewsAPI, Google News)

Elite AI Implementation - Comprehensive trend aggregation
"""

import asyncio
import hashlib
import json
import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

from .config import settings, utc_now

logger = logging.getLogger(__name__)


# ============================================================================
# Trend Data Models
# ============================================================================


@dataclass
class TrendItem:
    """Normalized trend data from any source"""

    id: str
    name: str
    source: str
    score: float  # Normalized 0-1
    volume: int  # Absolute volume/mentions
    growth_rate: float  # % growth
    category: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    source_url: Optional[str] = None
    region: str = "global"
    timestamp: datetime = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "score": self.score,
            "volume": self.volume,
            "growth_rate": self.growth_rate,
            "category": self.category,
            "description": self.description,
            "keywords": self.keywords,
            "related_topics": self.related_topics,
            "source_url": self.source_url,
            "region": self.region,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class TrendAggregation:
    """Aggregated trend data from multiple sources"""

    name: str
    normalized_name: str
    sources: List[str]
    combined_score: float
    total_volume: int
    avg_growth_rate: float
    category: Optional[str] = None
    items: List[TrendItem] = field(default_factory=list)
    first_seen: datetime = field(default_factory=utc_now)
    momentum: float = 0.0  # Trend acceleration


# ============================================================================
# Base Trend Source
# ============================================================================


class BaseTrendSource(ABC):
    """Abstract base class for trend data sources"""

    def __init__(self, name: str, rate_limit: int = 60):
        self.name = name
        self.rate_limit = rate_limit  # requests per minute
        self._last_request: Optional[datetime] = None
        self._request_count = 0
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = timedelta(minutes=5)

    async def _rate_limit_check(self):
        """Enforce rate limiting"""
        now = utc_now()
        if self._last_request:
            elapsed = (now - self._last_request).total_seconds()
            if elapsed < 60:
                if self._request_count >= self.rate_limit:
                    wait_time = 60 - elapsed
                    logger.info(
                        f"{self.name}: Rate limit reached, waiting {wait_time:.1f}s"
                    )
                    await asyncio.sleep(wait_time)
                    self._request_count = 0
            else:
                self._request_count = 0

        self._last_request = now
        self._request_count += 1

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cached data if not expired"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if utc_now() - timestamp < self._cache_ttl:
                return data
        return None

    def _set_cache(self, key: str, data: Any):
        """Cache data with timestamp"""
        self._cache[key] = (data, utc_now())

    @abstractmethod
    async def fetch_trends(self, **kwargs) -> List[TrendItem]:
        """Fetch trends from this source"""
        pass

    def normalize_score(self, value: float, max_value: float) -> float:
        """Normalize a value to 0-1 range"""
        if max_value <= 0:
            return 0.0
        return min(1.0, max(0.0, value / max_value))


# ============================================================================
# Google Trends Source
# ============================================================================


class GoogleTrendsSource(BaseTrendSource):
    """
    Google Trends data source using unofficial API endpoints.
    Falls back to pytrends library if available.
    """

    def __init__(self):
        super().__init__("google_trends", rate_limit=30)
        self.base_url = "https://trends.google.com/trends/api"
        self.daily_trends_url = f"{self.base_url}/dailytrends"
        self.realtime_url = f"{self.base_url}/realtimetrends"

        # Try to import pytrends for backup
        try:
            from pytrends.request import TrendReq

            self.pytrends = TrendReq(hl="en-US", tz=360)
            self._use_pytrends = True
        except ImportError:
            self.pytrends = None
            self._use_pytrends = False

    async def fetch_trends(
        self, region: str = "US", category: Optional[str] = None, limit: int = 20
    ) -> List[TrendItem]:
        """Fetch trending searches from Google Trends"""
        cache_key = f"google_{region}_{category}_{limit}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        await self._rate_limit_check()

        trends = []

        try:
            if self._use_pytrends:
                trends = await self._fetch_with_pytrends(region, category, limit)
            else:
                trends = await self._fetch_with_api(region, category, limit)
        except Exception as e:
            logger.error(f"Google Trends fetch error: {e}")

        self._set_cache(cache_key, trends)
        return trends

    async def _fetch_with_pytrends(
        self, region: str, category: Optional[str], limit: int
    ) -> List[TrendItem]:
        """Fetch using pytrends library"""
        trends = []

        try:
            # Get daily trending searches
            daily = self.pytrends.trending_searches(pn=region.lower())

            for idx, row in enumerate(daily.head(limit).itertuples()):
                query = row[1] if hasattr(row, "_1") else str(row)

                # Get interest over time for context
                self.pytrends.build_payload([query], timeframe="now 1-d")
                interest = self.pytrends.interest_over_time()

                avg_interest = 50
                if not interest.empty and query in interest.columns:
                    avg_interest = interest[query].mean()

                trend = TrendItem(
                    id=hashlib.md5(
                        f"google_{query}".encode(), usedforsecurity=False
                    ).hexdigest()[:12],
                    name=query,
                    source="google_trends",
                    score=self.normalize_score(avg_interest, 100),
                    volume=int(avg_interest * 1000),
                    growth_rate=0.1,  # Would need historical data
                    category=category,
                    region=region,
                    metadata={"rank": idx + 1},
                )
                trends.append(trend)

        except Exception as e:
            logger.error(f"Pytrends error: {e}")

        return trends

    async def _fetch_with_api(
        self, region: str, category: Optional[str], limit: int
    ) -> List[TrendItem]:
        """Fetch using direct API (may be rate-limited)"""
        trends = []

        params = {"hl": "en-US", "geo": region, "ns": 15}  # Number of stories

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.daily_trends_url,
                    params=params,
                    headers={"Accept": "application/json"},
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Google prepends )]}'
                        if text.startswith(")]}'"):
                            text = text[5:]

                        data = json.loads(text)

                        for day_data in data.get("default", {}).get(
                            "trendingSearchesDays", []
                        ):
                            for search in day_data.get("trendingSearches", [])[:limit]:
                                title = search.get("title", {}).get("query", "")
                                traffic = search.get("formattedTraffic", "0")

                                # Parse traffic (e.g., "100K+", "1M+")
                                volume = self._parse_traffic(traffic)

                                trend = TrendItem(
                                    id=hashlib.md5(
                                        f"google_{title}".encode(),
                                        usedforsecurity=False,
                                    ).hexdigest()[:12],
                                    name=title,
                                    source="google_trends",
                                    score=self.normalize_score(volume, 1000000),
                                    volume=volume,
                                    growth_rate=0.15,
                                    category=category,
                                    description=search.get("title", {}).get(
                                        "exploreLink", ""
                                    ),
                                    region=region,
                                )
                                trends.append(trend)

            except Exception as e:
                logger.error(f"Google Trends API error: {e}")

        return trends[:limit]

    def _parse_traffic(self, traffic: str) -> int:
        """Parse Google Trends traffic string (e.g., '100K+', '1M+')"""
        traffic = traffic.replace("+", "").replace(",", "").upper()

        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}

        for suffix, mult in multipliers.items():
            if suffix in traffic:
                try:
                    return int(float(traffic.replace(suffix, "")) * mult)
                except ValueError:
                    pass

        try:
            return int(traffic)
        except ValueError:
            return 0


# ============================================================================
# Twitter/X Trends Source
# ============================================================================


class TwitterTrendsSource(BaseTrendSource):
    """
    Twitter/X trending topics using API v2.
    Requires Twitter API Bearer Token.
    """

    def __init__(self):
        super().__init__("twitter", rate_limit=15)
        self.base_url = "https://api.twitter.com/2"
        self.bearer_token = getattr(settings, "TWITTER_BEARER_TOKEN", "")

    async def fetch_trends(
        self, woeid: int = 1, limit: int = 20  # 1 = Worldwide
    ) -> List[TrendItem]:
        """Fetch trending topics from Twitter"""
        if not self.bearer_token:
            logger.warning("Twitter Bearer Token not configured")
            return await self._fetch_mock_trends(limit)

        cache_key = f"twitter_{woeid}_{limit}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        await self._rate_limit_check()

        trends = []

        async with aiohttp.ClientSession() as session:
            try:
                # Get trends for location
                url = f"{self.base_url}/trends/place"
                headers = {"Authorization": f"Bearer {self.bearer_token}"}

                async with session.get(
                    url, params={"id": woeid}, headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for location in data:
                            for trend in location.get("trends", [])[:limit]:
                                tweet_volume = trend.get("tweet_volume") or 0

                                trend_item = TrendItem(
                                    id=hashlib.md5(
                                        f"twitter_{trend['name']}".encode(),
                                        usedforsecurity=False,
                                    ).hexdigest()[:12],
                                    name=trend["name"],
                                    source="twitter",
                                    score=self.normalize_score(tweet_volume, 1000000),
                                    volume=tweet_volume,
                                    growth_rate=0.0,  # Would need historical data
                                    source_url=trend.get("url"),
                                    keywords=[trend["name"].replace("#", "")],
                                    metadata={
                                        "promoted": trend.get("promoted_content")
                                        is not None
                                    },
                                )
                                trends.append(trend_item)
                    elif response.status == 429:
                        logger.warning("Twitter rate limit exceeded")
                    else:
                        logger.error(f"Twitter API error: {response.status}")

            except Exception as e:
                logger.error(f"Twitter fetch error: {e}")

        self._set_cache(cache_key, trends)
        return trends

    async def _fetch_mock_trends(self, limit: int) -> List[TrendItem]:
        """Return mock trends when API not available"""
        mock_trends = [
            ("AI Technology", 500000, 0.25, "technology"),
            ("Cryptocurrency", 350000, 0.15, "finance"),
            ("Climate Change", 280000, 0.10, "environment"),
            ("Space Exploration", 200000, 0.20, "science"),
            ("Remote Work", 180000, 0.12, "business"),
        ]

        trends = []
        for name, volume, growth, category in mock_trends[:limit]:
            trend = TrendItem(
                id=hashlib.md5(
                    f"twitter_mock_{name}".encode(), usedforsecurity=False
                ).hexdigest()[:12],
                name=name,
                source="twitter_mock",
                score=self.normalize_score(volume, 1000000),
                volume=volume,
                growth_rate=growth,
                category=category,
            )
            trends.append(trend)

        return trends


# ============================================================================
# Reddit Trends Source
# ============================================================================


class RedditTrendsSource(BaseTrendSource):
    """
    Reddit trending topics from popular subreddits.
    Uses Reddit API (requires client ID/secret) or public JSON endpoints.
    """

    def __init__(self):
        super().__init__("reddit", rate_limit=60)
        self.base_url = "https://www.reddit.com"
        self.oauth_url = "https://oauth.reddit.com"
        self.client_id = getattr(settings, "REDDIT_CLIENT_ID", "")
        self.client_secret = getattr(settings, "REDDIT_CLIENT_SECRET", "")
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

        # Popular subreddits for trend detection
        self.tracked_subreddits = [
            "technology",
            "worldnews",
            "science",
            "business",
            "futurology",
            "stocks",
            "cryptocurrency",
            "programming",
        ]

    async def _get_access_token(self) -> Optional[str]:
        """Get OAuth access token for Reddit API"""
        if not self.client_id or not self.client_secret:
            return None

        if (
            self._access_token
            and self._token_expires
            and utc_now() < self._token_expires
        ):
            return self._access_token

        async with aiohttp.ClientSession() as session:
            try:
                auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
                data = {"grant_type": "client_credentials"}
                headers = {"User-Agent": "EliteAI/1.0"}

                async with session.post(
                    "https://www.reddit.com/api/v1/access_token",
                    auth=auth,
                    data=data,
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self._access_token = token_data["access_token"]
                        self._token_expires = utc_now() + timedelta(
                            seconds=token_data.get("expires_in", 3600) - 60
                        )
                        return self._access_token
            except Exception as e:
                logger.error(f"Reddit auth error: {e}")

        return None

    async def fetch_trends(
        self,
        subreddits: Optional[List[str]] = None,
        time_filter: str = "day",
        limit: int = 20,
    ) -> List[TrendItem]:
        """Fetch trending posts from Reddit"""
        cache_key = f"reddit_{time_filter}_{limit}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        await self._rate_limit_check()

        subreddits = subreddits or self.tracked_subreddits
        trends = []

        # Try OAuth first, fallback to public API
        token = await self._get_access_token()

        async with aiohttp.ClientSession() as session:
            for subreddit in subreddits:
                try:
                    if token:
                        url = f"{self.oauth_url}/r/{subreddit}/hot"
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "User-Agent": "EliteAI/1.0",
                        }
                    else:
                        url = f"{self.base_url}/r/{subreddit}/hot.json"
                        headers = {"User-Agent": "EliteAI/1.0"}

                    params = {"limit": 10, "t": time_filter}

                    async with session.get(
                        url, params=params, headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()

                            for post in data.get("data", {}).get("children", []):
                                post_data = post.get("data", {})

                                # Calculate engagement score
                                ups = post_data.get("ups", 0)
                                comments = post_data.get("num_comments", 0)
                                engagement = ups + (comments * 2)

                                trend = TrendItem(
                                    id=post_data.get(
                                        "id",
                                        hashlib.md5(
                                            post_data.get("title", "").encode(),
                                            usedforsecurity=False,
                                        ).hexdigest()[:12],
                                    ),
                                    name=post_data.get("title", "")[:200],
                                    source="reddit",
                                    score=self.normalize_score(engagement, 100000),
                                    volume=engagement,
                                    growth_rate=post_data.get("upvote_ratio", 0.5)
                                    - 0.5,
                                    category=subreddit,
                                    description=post_data.get("selftext", "")[:500],
                                    source_url=f"https://reddit.com{post_data.get('permalink', '')}",
                                    keywords=self._extract_keywords(
                                        post_data.get("title", "")
                                    ),
                                    metadata={
                                        "subreddit": subreddit,
                                        "upvotes": ups,
                                        "comments": comments,
                                        "awards": post_data.get(
                                            "total_awards_received", 0
                                        ),
                                    },
                                )
                                trends.append(trend)

                except Exception as e:
                    logger.error(f"Reddit fetch error for r/{subreddit}: {e}")

        # Sort by score and limit
        trends.sort(key=lambda x: x.score, reverse=True)
        trends = trends[:limit]

        self._set_cache(cache_key, trends)
        return trends

    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from title"""
        # Remove common words
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "and",
            "but",
            "or",
            "nor",
            "so",
            "yet",
            "both",
            "either",
            "neither",
            "not",
            "only",
            "own",
            "same",
            "than",
            "too",
            "very",
            "just",
        }

        words = re.findall(r"\b[a-zA-Z]{3,}\b", title.lower())
        keywords = [w for w in words if w not in stopwords][:10]
        return keywords


# ============================================================================
# YouTube Trends Source
# ============================================================================


class YouTubeTrendsSource(BaseTrendSource):
    """
    YouTube trending videos using Data API v3.
    Requires YouTube API key.
    """

    def __init__(self):
        super().__init__("youtube", rate_limit=100)
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = getattr(settings, "YOUTUBE_API_KEY", "")

    async def fetch_trends(
        self, region: str = "US", category_id: Optional[str] = None, limit: int = 20
    ) -> List[TrendItem]:
        """Fetch trending videos from YouTube"""
        if not self.api_key:
            logger.warning("YouTube API key not configured")
            return []

        cache_key = f"youtube_{region}_{category_id}_{limit}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        await self._rate_limit_check()

        trends = []

        async with aiohttp.ClientSession() as session:
            try:
                params = {
                    "part": "snippet,statistics",
                    "chart": "mostPopular",
                    "regionCode": region,
                    "maxResults": limit,
                    "key": self.api_key,
                }

                if category_id:
                    params["videoCategoryId"] = category_id

                async with session.get(
                    f"{self.base_url}/videos", params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for video in data.get("items", []):
                            snippet = video.get("snippet", {})
                            stats = video.get("statistics", {})

                            views = int(stats.get("viewCount", 0))
                            likes = int(stats.get("likeCount", 0))
                            comments = int(stats.get("commentCount", 0))

                            engagement = likes + (comments * 5)

                            trend = TrendItem(
                                id=video.get("id"),
                                name=snippet.get("title", ""),
                                source="youtube",
                                score=self.normalize_score(views, 10000000),
                                volume=views,
                                growth_rate=0.0,  # Would need historical
                                category=snippet.get("categoryId"),
                                description=snippet.get("description", "")[:500],
                                source_url=f"https://youtube.com/watch?v={video.get('id')}",
                                keywords=snippet.get("tags", [])[:10],
                                region=region,
                                metadata={
                                    "channel": snippet.get("channelTitle"),
                                    "views": views,
                                    "likes": likes,
                                    "comments": comments,
                                    "engagement_rate": engagement / max(views, 1),
                                },
                            )
                            trends.append(trend)
                    else:
                        logger.error(f"YouTube API error: {response.status}")

            except Exception as e:
                logger.error(f"YouTube fetch error: {e}")

        self._set_cache(cache_key, trends)
        return trends


# ============================================================================
# News API Source
# ============================================================================


class NewsAPISource(BaseTrendSource):
    """
    News trends from NewsAPI.org.
    Requires NewsAPI key.
    """

    def __init__(self):
        super().__init__("newsapi", rate_limit=100)
        self.base_url = "https://newsapi.org/v2"
        self.api_key = getattr(settings, "NEWSAPI_KEY", "")

    async def fetch_trends(
        self, category: Optional[str] = None, country: str = "us", limit: int = 20
    ) -> List[TrendItem]:
        """Fetch top headlines from NewsAPI"""
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        cache_key = f"newsapi_{country}_{category}_{limit}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        await self._rate_limit_check()

        trends = []

        async with aiohttp.ClientSession() as session:
            try:
                params = {"country": country, "pageSize": limit, "apiKey": self.api_key}

                if category:
                    params["category"] = category

                async with session.get(
                    f"{self.base_url}/top-headlines", params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for idx, article in enumerate(data.get("articles", [])):
                            # Score based on position (earlier = more trending)
                            position_score = (limit - idx) / limit

                            trend = TrendItem(
                                id=hashlib.md5(
                                    article.get("url", "").encode(),
                                    usedforsecurity=False,
                                ).hexdigest()[:12],
                                name=article.get("title", ""),
                                source="newsapi",
                                score=position_score,
                                volume=1000 - (idx * 50),  # Estimated
                                growth_rate=0.1,
                                category=category,
                                description=article.get("description", ""),
                                source_url=article.get("url"),
                                region=country.upper(),
                                metadata={
                                    "source": article.get("source", {}).get("name"),
                                    "author": article.get("author"),
                                    "published_at": article.get("publishedAt"),
                                    "image": article.get("urlToImage"),
                                },
                            )
                            trends.append(trend)
                    else:
                        logger.error(f"NewsAPI error: {response.status}")

            except Exception as e:
                logger.error(f"NewsAPI fetch error: {e}")

        self._set_cache(cache_key, trends)
        return trends


# ============================================================================
# TikTok Trends Source
# ============================================================================


class TikTokTrendsSource(BaseTrendSource):
    """
    TikTok trending topics and hashtags.
    Uses unofficial methods as TikTok API is limited.
    """

    def __init__(self):
        super().__init__("tiktok", rate_limit=30)
        # TikTok doesn't have a public trends API
        # We'll use trending hashtag tracking services or manual data
        self.trending_endpoint = getattr(settings, "TIKTOK_TRENDS_ENDPOINT", "")

    async def fetch_trends(
        self, region: str = "US", limit: int = 20
    ) -> List[TrendItem]:
        """Fetch trending hashtags from TikTok"""
        cache_key = f"tiktok_{region}_{limit}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        await self._rate_limit_check()

        trends = []

        if self.trending_endpoint:
            # Use custom endpoint if configured
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        self.trending_endpoint,
                        params={"region": region, "limit": limit},
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            for item in data.get("trends", []):
                                trend = TrendItem(
                                    id=item.get(
                                        "id",
                                        hashlib.md5(
                                            item.get("name", "").encode(),
                                            usedforsecurity=False,
                                        ).hexdigest()[:12],
                                    ),
                                    name=item.get("name"),
                                    source="tiktok",
                                    score=item.get("score", 0.5),
                                    volume=item.get("views", 0),
                                    growth_rate=item.get("growth", 0),
                                    category="entertainment",
                                    region=region,
                                )
                                trends.append(trend)
                except Exception as e:
                    logger.error(f"TikTok trends fetch error: {e}")

        if not trends:
            # Return sample trending topics
            trends = await self._get_sample_trends(limit)

        self._set_cache(cache_key, trends)
        return trends

    async def _get_sample_trends(self, limit: int) -> List[TrendItem]:
        """Get sample TikTok trends when API unavailable"""
        sample_hashtags = [
            ("#fyp", 1000000000, "For You Page"),
            ("#viral", 500000000, "Viral content"),
            ("#trending", 300000000, "Trending topics"),
            ("#tech", 200000000, "Technology"),
            ("#ai", 150000000, "Artificial Intelligence"),
            ("#business", 100000000, "Business tips"),
            ("#news", 80000000, "Current events"),
            ("#education", 60000000, "Educational content"),
        ]

        trends = []
        for hashtag, views, desc in sample_hashtags[:limit]:
            trend = TrendItem(
                id=hashlib.md5(hashtag.encode(), usedforsecurity=False).hexdigest()[
                    :12
                ],
                name=hashtag,
                source="tiktok_sample",
                score=self.normalize_score(views, 1000000000),
                volume=views,
                growth_rate=0.15,
                category="entertainment",
                description=desc,
            )
            trends.append(trend)

        return trends


# ============================================================================
# Trend Aggregator
# ============================================================================


class TrendAggregator:
    """
    Aggregates trends from multiple sources into unified rankings.

    Features:
    - Multi-source collection
    - Deduplication
    - Score normalization
    - Trend momentum calculation
    """

    def __init__(self):
        self.sources: Dict[str, BaseTrendSource] = {
            "google": GoogleTrendsSource(),
            "twitter": TwitterTrendsSource(),
            "reddit": RedditTrendsSource(),
            "youtube": YouTubeTrendsSource(),
            "newsapi": NewsAPISource(),
            "tiktok": TikTokTrendsSource(),
        }

        self.trend_history: Dict[str, List[TrendAggregation]] = defaultdict(list)
        self._source_weights = {
            "google": 1.0,
            "twitter": 0.9,
            "reddit": 0.8,
            "youtube": 0.85,
            "newsapi": 0.7,
            "tiktok": 0.75,
        }

    async def fetch_all_trends(
        self, sources: Optional[List[str]] = None, limit_per_source: int = 20
    ) -> List[TrendItem]:
        """Fetch trends from all sources concurrently"""
        sources = sources or list(self.sources.keys())

        tasks = []
        for source_name in sources:
            if source_name in self.sources:
                tasks.append(self._fetch_from_source(source_name, limit_per_source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_trends = []
        for result in results:
            if isinstance(result, list):
                all_trends.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Source fetch error: {result}")

        logger.info(f"Fetched {len(all_trends)} trends from {len(sources)} sources")
        return all_trends

    async def _fetch_from_source(self, source_name: str, limit: int) -> List[TrendItem]:
        """Fetch from a single source with error handling"""
        try:
            return await self.sources[source_name].fetch_trends(limit=limit)
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
            return []

    def aggregate_trends(
        self, trends: List[TrendItem], limit: int = 50
    ) -> List[TrendAggregation]:
        """
        Aggregate and deduplicate trends from multiple sources.

        Groups similar trends, combines scores, and ranks by combined score.
        """
        # Group by normalized name
        grouped: Dict[str, List[TrendItem]] = defaultdict(list)

        for trend in trends:
            normalized = self._normalize_name(trend.name)
            grouped[normalized].append(trend)

        # Create aggregations
        aggregations = []

        for normalized_name, items in grouped.items():
            if not items:
                continue

            # Calculate combined score with source weights
            weighted_scores = [
                item.score * self._source_weights.get(item.source, 0.5)
                for item in items
            ]
            combined_score = (
                sum(weighted_scores) / len(items) * len(set(i.source for i in items))
            )
            combined_score = min(1.0, combined_score)  # Cap at 1.0

            # Use most common category
            categories = [i.category for i in items if i.category]
            category = (
                max(set(categories), key=categories.count) if categories else None
            )

            aggregation = TrendAggregation(
                name=items[0].name,  # Use first occurrence
                normalized_name=normalized_name,
                sources=list(set(i.source for i in items)),
                combined_score=combined_score,
                total_volume=sum(i.volume for i in items),
                avg_growth_rate=sum(i.growth_rate for i in items) / len(items),
                category=category,
                items=items,
                first_seen=min(i.timestamp for i in items),
            )

            # Calculate momentum based on history
            aggregation.momentum = self._calculate_momentum(
                normalized_name, aggregation
            )

            aggregations.append(aggregation)

        # Sort by combined score
        aggregations.sort(key=lambda x: x.combined_score, reverse=True)

        # Update history
        for agg in aggregations[:limit]:
            self.trend_history[agg.normalized_name].append(agg)
            # Keep last 24 hours of history
            self.trend_history[agg.normalized_name] = [
                h
                for h in self.trend_history[agg.normalized_name]
                if utc_now() - h.first_seen < timedelta(hours=24)
            ][-100:]

        return aggregations[:limit]

    def _normalize_name(self, name: str) -> str:
        """Normalize trend name for grouping"""
        # Lowercase, remove special characters, collapse whitespace
        normalized = name.lower()
        normalized = re.sub(r"[^a-z0-9\s]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _calculate_momentum(
        self, normalized_name: str, current: TrendAggregation
    ) -> float:
        """Calculate trend momentum based on score changes over time"""
        history = self.trend_history.get(normalized_name, [])

        if len(history) < 2:
            return 0.0

        # Compare with average of previous scores
        recent_scores = [h.combined_score for h in history[-10:]]
        avg_recent = sum(recent_scores) / len(recent_scores)

        momentum = (current.combined_score - avg_recent) / max(avg_recent, 0.1)
        return momentum

    async def get_top_trends(
        self,
        sources: Optional[List[str]] = None,
        limit: int = 20,
        category: Optional[str] = None,
    ) -> List[TrendAggregation]:
        """
        Get top aggregated trends.

        Main entry point for trend detection.
        """
        # Fetch from all sources
        raw_trends = await self.fetch_all_trends(sources, limit_per_source=30)

        # Filter by category if specified
        if category:
            raw_trends = [t for t in raw_trends if t.category == category]

        # Aggregate and rank
        aggregated = self.aggregate_trends(raw_trends, limit=limit)

        return aggregated

    def get_trend_insights(self) -> Dict[str, Any]:
        """Get insights about current trends"""
        all_recent = []
        for name, history in self.trend_history.items():
            if history:
                all_recent.append(history[-1])

        if not all_recent:
            return {"status": "no_data"}

        # Top categories
        categories = [t.category for t in all_recent if t.category]
        top_categories = {}
        for cat in set(categories):
            top_categories[cat] = categories.count(cat)

        # Top sources
        all_sources = []
        for t in all_recent:
            all_sources.extend(t.sources)
        top_sources = {}
        for src in set(all_sources):
            top_sources[src] = all_sources.count(src)

        # Momentum leaders
        momentum_sorted = sorted(all_recent, key=lambda x: x.momentum, reverse=True)

        return {
            "total_trends_tracked": len(self.trend_history),
            "top_categories": dict(
                sorted(top_categories.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "source_distribution": top_sources,
            "momentum_leaders": [
                {"name": t.name, "momentum": t.momentum, "score": t.combined_score}
                for t in momentum_sorted[:5]
            ],
            "avg_multi_source_coverage": sum(len(t.sources) for t in all_recent)
            / len(all_recent),
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_trend_aggregator() -> TrendAggregator:
    """Factory function to create configured trend aggregator"""
    return TrendAggregator()


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """Example usage of trend aggregation"""
    aggregator = create_trend_aggregator()

    # Get top trends
    trends = await aggregator.get_top_trends(limit=10)

    print("Top Aggregated Trends:")
    for trend in trends:
        print(
            f"- {trend.name} (Score: {trend.combined_score:.2f}, Sources: {', '.join(trend.sources)})"
        )

    # Get insights
    insights = aggregator.get_trend_insights()
    print(f"\nInsights: {json.dumps(insights, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
