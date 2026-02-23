"""
Platform OAuth Module - OAuth 2.0 Authentication Flows

This module implements OAuth 2.0 authentication for all supported platforms:
- YouTube (Google OAuth)
- TikTok
- LinkedIn
- Instagram (Facebook/Meta)
- Twitter/X
- Facebook
- Pinterest
- Snapchat

Elite AI Implementation - Secure token management with auto-refresh
"""

import asyncio
import base64
import hashlib
import json
import logging
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import aiohttp
from cryptography.fernet import Fernet

from .config import settings, utc_now

logger = logging.getLogger(__name__)


# ============================================================================
# Token Models
# ============================================================================


@dataclass
class OAuthToken:
    """OAuth token with metadata"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)
    platform: str = ""
    user_id: Optional[str] = None

    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        # Consider token expired 5 minutes before actual expiry
        return utc_now() >= (self.expires_at - timedelta(minutes=5))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "created_at": self.created_at.isoformat(),
            "platform": self.platform,
            "user_id": self.user_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthToken":
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = utc_now()

        return cls(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope"),
            created_at=created_at,
            platform=data.get("platform", ""),
            user_id=data.get("user_id"),
        )


@dataclass
class OAuthState:
    """OAuth state for CSRF protection"""

    state: str
    platform: str
    redirect_uri: str
    created_at: datetime = field(default_factory=utc_now)
    code_verifier: Optional[str] = None  # For PKCE

    @property
    def is_expired(self) -> bool:
        return utc_now() > (self.created_at + timedelta(minutes=10))


# ============================================================================
# Token Storage
# ============================================================================


class TokenStorage(ABC):
    """Abstract base for token storage backends"""

    @abstractmethod
    async def save_token(self, user_id: str, platform: str, token: OAuthToken):
        pass

    @abstractmethod
    async def get_token(self, user_id: str, platform: str) -> Optional[OAuthToken]:
        pass

    @abstractmethod
    async def delete_token(self, user_id: str, platform: str):
        pass

    @abstractmethod
    async def list_tokens(self, user_id: str) -> List[Tuple[str, OAuthToken]]:
        pass


class InMemoryTokenStorage(TokenStorage):
    """In-memory token storage (for development)"""

    def __init__(self):
        self._tokens: Dict[str, Dict[str, OAuthToken]] = {}

    async def save_token(self, user_id: str, platform: str, token: OAuthToken):
        if user_id not in self._tokens:
            self._tokens[user_id] = {}
        self._tokens[user_id][platform] = token

    async def get_token(self, user_id: str, platform: str) -> Optional[OAuthToken]:
        return self._tokens.get(user_id, {}).get(platform)

    async def delete_token(self, user_id: str, platform: str):
        if user_id in self._tokens and platform in self._tokens[user_id]:
            del self._tokens[user_id][platform]

    async def list_tokens(self, user_id: str) -> List[Tuple[str, OAuthToken]]:
        return list(self._tokens.get(user_id, {}).items())


class EncryptedTokenStorage(TokenStorage):
    """Encrypted token storage with Redis or file backend"""

    def __init__(self, encryption_key: Optional[str] = None, backend: str = "memory"):
        key = encryption_key or getattr(settings, "TOKEN_ENCRYPTION_KEY", None)
        if key:
            # Ensure key is 32 bytes for Fernet
            key_bytes = hashlib.sha256(key.encode()).digest()
            self._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        else:
            self._fernet = None
            logger.warning("No encryption key provided, tokens stored unencrypted")

        self._backend = backend
        self._memory_storage: Dict[str, str] = {}

    def _encrypt(self, data: str) -> str:
        if self._fernet:
            return self._fernet.encrypt(data.encode()).decode()
        return data

    def _decrypt(self, data: str) -> str:
        if self._fernet:
            return self._fernet.decrypt(data.encode()).decode()
        return data

    async def save_token(self, user_id: str, platform: str, token: OAuthToken):
        key = f"oauth:{user_id}:{platform}"
        encrypted = self._encrypt(json.dumps(token.to_dict()))
        self._memory_storage[key] = encrypted

    async def get_token(self, user_id: str, platform: str) -> Optional[OAuthToken]:
        key = f"oauth:{user_id}:{platform}"
        encrypted = self._memory_storage.get(key)
        if encrypted:
            decrypted = self._decrypt(encrypted)
            return OAuthToken.from_dict(json.loads(decrypted))
        return None

    async def delete_token(self, user_id: str, platform: str):
        key = f"oauth:{user_id}:{platform}"
        self._memory_storage.pop(key, None)

    async def list_tokens(self, user_id: str) -> List[Tuple[str, OAuthToken]]:
        prefix = f"oauth:{user_id}:"
        tokens = []
        for key, encrypted in self._memory_storage.items():
            if key.startswith(prefix):
                platform = key.replace(prefix, "")
                decrypted = self._decrypt(encrypted)
                token = OAuthToken.from_dict(json.loads(decrypted))
                tokens.append((platform, token))
        return tokens


# ============================================================================
# Base OAuth Provider
# ============================================================================


class BaseOAuthProvider(ABC):
    """Abstract base class for OAuth providers"""

    def __init__(
        self, client_id: str, client_secret: str, redirect_uri: str, scopes: List[str]
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self._states: Dict[str, OAuthState] = {}

    @property
    @abstractmethod
    def platform_name(self) -> str:
        pass

    @property
    @abstractmethod
    def authorize_url(self) -> str:
        pass

    @property
    @abstractmethod
    def token_url(self) -> str:
        pass

    def generate_state(self) -> str:
        """Generate CSRF state token"""
        state = secrets.token_urlsafe(32)
        self._states[state] = OAuthState(
            state=state, platform=self.platform_name, redirect_uri=self.redirect_uri
        )
        return state

    def verify_state(self, state: str) -> bool:
        """Verify state token"""
        oauth_state = self._states.get(state)
        if not oauth_state:
            return False
        if oauth_state.is_expired:
            del self._states[state]
            return False
        del self._states[state]
        return True

    def get_authorization_url(
        self, extra_params: Optional[Dict[str, str]] = None
    ) -> str:
        """Get OAuth authorization URL"""
        state = self.generate_state()

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }

        if extra_params:
            params.update(extra_params)

        return f"{self.authorize_url}?{urlencode(params)}"

    async def exchange_code(self, code: str, state: str) -> OAuthToken:
        """Exchange authorization code for token"""
        if not self.verify_state(state):
            raise ValueError("Invalid state parameter")

        async with aiohttp.ClientSession() as session:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }

            async with session.post(
                self.token_url, data=data, headers={"Accept": "application/json"}
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Token exchange failed: {error}")

                token_data = await response.json()
                return self._parse_token_response(token_data)

    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            async with session.post(
                self.token_url, data=data, headers={"Accept": "application/json"}
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Token refresh failed: {error}")

                token_data = await response.json()
                return self._parse_token_response(token_data)

    def _parse_token_response(self, data: Dict[str, Any]) -> OAuthToken:
        """Parse token response"""
        return OAuthToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 3600),
            refresh_token=data.get("refresh_token"),
            scope=data.get("scope"),
            platform=self.platform_name,
        )

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token (if supported)"""
        return True  # Override in subclasses


# ============================================================================
# YouTube OAuth (Google)
# ============================================================================


class YouTubeOAuthProvider(BaseOAuthProvider):
    """YouTube/Google OAuth 2.0 provider"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "GOOGLE_CLIENT_ID", ""),
            client_secret=client_secret
            or getattr(settings, "GOOGLE_CLIENT_SECRET", ""),
            redirect_uri=redirect_uri or getattr(settings, "GOOGLE_REDIRECT_URI", ""),
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.readonly",
            ],
        )

    @property
    def platform_name(self) -> str:
        return "youtube"

    @property
    def authorize_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    def get_authorization_url(
        self, extra_params: Optional[Dict[str, str]] = None
    ) -> str:
        params = {"access_type": "offline", "prompt": "consent"}  # Force refresh token
        if extra_params:
            params.update(extra_params)
        return super().get_authorization_url(params)

    async def revoke_token(self, token: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://oauth2.googleapis.com/revoke", data={"token": token}
            ) as response:
                return response.status == 200


# ============================================================================
# TikTok OAuth
# ============================================================================


class TikTokOAuthProvider(BaseOAuthProvider):
    """TikTok OAuth 2.0 provider"""

    def __init__(
        self,
        client_key: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_key or getattr(settings, "TIKTOK_CLIENT_KEY", ""),
            client_secret=client_secret
            or getattr(settings, "TIKTOK_CLIENT_SECRET", ""),
            redirect_uri=redirect_uri or getattr(settings, "TIKTOK_REDIRECT_URI", ""),
            scopes=["user.info.basic", "video.upload", "video.list"],
        )

    @property
    def platform_name(self) -> str:
        return "tiktok"

    @property
    def authorize_url(self) -> str:
        return "https://www.tiktok.com/v2/auth/authorize/"

    @property
    def token_url(self) -> str:
        return "https://open.tiktokapis.com/v2/oauth/token/"

    def get_authorization_url(
        self, extra_params: Optional[Dict[str, str]] = None
    ) -> str:
        state = self.generate_state()

        # TikTok uses different parameter names
        params = {
            "client_key": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": ",".join(self.scopes),
            "state": state,
        }

        if extra_params:
            params.update(extra_params)

        return f"{self.authorize_url}?{urlencode(params)}"

    async def exchange_code(self, code: str, state: str) -> OAuthToken:
        if not self.verify_state(state):
            raise ValueError("Invalid state parameter")

        async with aiohttp.ClientSession() as session:
            data = {
                "client_key": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }

            async with session.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Token exchange failed: {error}")

                result = await response.json()
                token_data = result.get("data", result)

                return OAuthToken(
                    access_token=token_data["access_token"],
                    token_type="Bearer",
                    expires_in=token_data.get("expires_in", 86400),
                    refresh_token=token_data.get("refresh_token"),
                    scope=",".join(self.scopes),
                    platform=self.platform_name,
                    user_id=token_data.get("open_id"),
                )


# ============================================================================
# LinkedIn OAuth
# ============================================================================


class LinkedInOAuthProvider(BaseOAuthProvider):
    """LinkedIn OAuth 2.0 provider"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "LINKEDIN_CLIENT_ID", ""),
            client_secret=client_secret
            or getattr(settings, "LINKEDIN_CLIENT_SECRET", ""),
            redirect_uri=redirect_uri or getattr(settings, "LINKEDIN_REDIRECT_URI", ""),
            scopes=["r_liteprofile", "r_emailaddress", "w_member_social"],
        )

    @property
    def platform_name(self) -> str:
        return "linkedin"

    @property
    def authorize_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/authorization"

    @property
    def token_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/accessToken"

    async def get_user_profile(self, token: OAuthToken) -> Dict[str, Any]:
        """Get LinkedIn user profile"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.linkedin.com/v2/me",
                headers={"Authorization": f"Bearer {token.access_token}"},
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}


# ============================================================================
# Instagram OAuth (Meta/Facebook)
# ============================================================================


class InstagramOAuthProvider(BaseOAuthProvider):
    """Instagram OAuth 2.0 provider (via Facebook/Meta)"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "FACEBOOK_APP_ID", ""),
            client_secret=client_secret or getattr(settings, "FACEBOOK_APP_SECRET", ""),
            redirect_uri=redirect_uri
            or getattr(settings, "INSTAGRAM_REDIRECT_URI", ""),
            scopes=[
                "instagram_basic",
                "instagram_content_publish",
                "instagram_manage_comments",
                "instagram_manage_insights",
                "pages_show_list",
                "pages_read_engagement",
            ],
        )

    @property
    def platform_name(self) -> str:
        return "instagram"

    @property
    def authorize_url(self) -> str:
        return "https://www.facebook.com/v18.0/dialog/oauth"

    @property
    def token_url(self) -> str:
        return "https://graph.facebook.com/v18.0/oauth/access_token"

    async def get_long_lived_token(self, short_token: str) -> OAuthToken:
        """Exchange short-lived token for long-lived token"""
        async with aiohttp.ClientSession() as session:
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "fb_exchange_token": short_token,
            }

            async with session.get(self.token_url, params=params) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Long-lived token exchange failed: {error}")

                data = await response.json()
                return OAuthToken(
                    access_token=data["access_token"],
                    expires_in=data.get("expires_in", 5184000),  # 60 days
                    platform=self.platform_name,
                )


# ============================================================================
# Twitter/X OAuth 2.0
# ============================================================================


class TwitterOAuthProvider(BaseOAuthProvider):
    """Twitter/X OAuth 2.0 provider with PKCE"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "TWITTER_CLIENT_ID", ""),
            client_secret=client_secret
            or getattr(settings, "TWITTER_CLIENT_SECRET", ""),
            redirect_uri=redirect_uri or getattr(settings, "TWITTER_REDIRECT_URI", ""),
            scopes=["tweet.read", "tweet.write", "users.read", "offline.access"],
        )

    @property
    def platform_name(self) -> str:
        return "twitter"

    @property
    def authorize_url(self) -> str:
        return "https://twitter.com/i/oauth2/authorize"

    @property
    def token_url(self) -> str:
        return "https://api.twitter.com/2/oauth2/token"

    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        return secrets.token_urlsafe(64)

    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge"""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

    def get_authorization_url(
        self, extra_params: Optional[Dict[str, str]] = None
    ) -> str:
        state = self.generate_state()
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)

        # Store verifier with state
        self._states[state].code_verifier = code_verifier

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        if extra_params:
            params.update(extra_params)

        return f"{self.authorize_url}?{urlencode(params)}"

    async def exchange_code(self, code: str, state: str) -> OAuthToken:
        oauth_state = self._states.get(state)
        if not oauth_state or oauth_state.is_expired:
            raise ValueError("Invalid state parameter")

        code_verifier = oauth_state.code_verifier
        del self._states[state]

        async with aiohttp.ClientSession() as session:
            # Twitter requires Basic auth for confidential clients
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)

            data = {
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
                "code_verifier": code_verifier,
            }

            async with session.post(
                self.token_url,
                data=data,
                auth=auth,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Token exchange failed: {error}")

                token_data = await response.json()
                return self._parse_token_response(token_data)


# ============================================================================
# Facebook OAuth
# ============================================================================


class FacebookOAuthProvider(BaseOAuthProvider):
    """Facebook OAuth 2.0 provider"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "FACEBOOK_APP_ID", ""),
            client_secret=client_secret or getattr(settings, "FACEBOOK_APP_SECRET", ""),
            redirect_uri=redirect_uri or getattr(settings, "FACEBOOK_REDIRECT_URI", ""),
            scopes=[
                "pages_manage_posts",
                "pages_read_engagement",
                "pages_show_list",
                "publish_video",
            ],
        )

    @property
    def platform_name(self) -> str:
        return "facebook"

    @property
    def authorize_url(self) -> str:
        return "https://www.facebook.com/v18.0/dialog/oauth"

    @property
    def token_url(self) -> str:
        return "https://graph.facebook.com/v18.0/oauth/access_token"

    async def get_page_tokens(self, user_token: str) -> List[Dict[str, Any]]:
        """Get page access tokens for all pages the user manages"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://graph.facebook.com/v18.0/me/accounts",
                params={"access_token": user_token},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                return []


# ============================================================================
# Pinterest OAuth
# ============================================================================


class PinterestOAuthProvider(BaseOAuthProvider):
    """Pinterest OAuth 2.0 provider"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "PINTEREST_APP_ID", ""),
            client_secret=client_secret
            or getattr(settings, "PINTEREST_APP_SECRET", ""),
            redirect_uri=redirect_uri
            or getattr(settings, "PINTEREST_REDIRECT_URI", ""),
            scopes=[
                "boards:read",
                "boards:write",
                "pins:read",
                "pins:write",
                "user_accounts:read",
            ],
        )

    @property
    def platform_name(self) -> str:
        return "pinterest"

    @property
    def authorize_url(self) -> str:
        return "https://www.pinterest.com/oauth/"

    @property
    def token_url(self) -> str:
        return "https://api.pinterest.com/v5/oauth/token"

    async def exchange_code(self, code: str, state: str) -> OAuthToken:
        if not self.verify_state(state):
            raise ValueError("Invalid state parameter")

        async with aiohttp.ClientSession() as session:
            # Pinterest requires Basic auth
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)

            data = {
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            }

            async with session.post(
                self.token_url,
                data=data,
                auth=auth,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Token exchange failed: {error}")

                token_data = await response.json()
                return self._parse_token_response(token_data)


# ============================================================================
# Snapchat OAuth
# ============================================================================


class SnapchatOAuthProvider(BaseOAuthProvider):
    """Snapchat OAuth 2.0 provider"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        super().__init__(
            client_id=client_id or getattr(settings, "SNAPCHAT_CLIENT_ID", ""),
            client_secret=client_secret
            or getattr(settings, "SNAPCHAT_CLIENT_SECRET", ""),
            redirect_uri=redirect_uri or getattr(settings, "SNAPCHAT_REDIRECT_URI", ""),
            scopes=["snapchat-marketing-api"],
        )

    @property
    def platform_name(self) -> str:
        return "snapchat"

    @property
    def authorize_url(self) -> str:
        return "https://accounts.snapchat.com/login/oauth2/authorize"

    @property
    def token_url(self) -> str:
        return "https://accounts.snapchat.com/login/oauth2/access_token"


# ============================================================================
# OAuth Manager
# ============================================================================


class OAuthManager:
    """
    Central OAuth management for all platforms.

    Handles:
    - Provider registration
    - Token storage
    - Auto-refresh
    - Multi-platform coordination
    """

    def __init__(self, storage: Optional[TokenStorage] = None):
        self.storage = storage or EncryptedTokenStorage()
        self.providers: Dict[str, BaseOAuthProvider] = {}
        self._refresh_tasks: Dict[str, asyncio.Task] = {}

        # Register default providers
        self._register_default_providers()

    def _register_default_providers(self):
        """Register all default OAuth providers"""
        providers = [
            YouTubeOAuthProvider(),
            TikTokOAuthProvider(),
            LinkedInOAuthProvider(),
            InstagramOAuthProvider(),
            TwitterOAuthProvider(),
            FacebookOAuthProvider(),
            PinterestOAuthProvider(),
            SnapchatOAuthProvider(),
        ]

        for provider in providers:
            if provider.client_id:  # Only register if configured
                self.providers[provider.platform_name] = provider
                logger.info(f"Registered OAuth provider: {provider.platform_name}")

    def register_provider(self, provider: BaseOAuthProvider):
        """Register a custom OAuth provider"""
        self.providers[provider.platform_name] = provider

    def get_provider(self, platform: str) -> BaseOAuthProvider:
        """Get OAuth provider for platform"""
        if platform not in self.providers:
            raise ValueError(f"Unknown platform: {platform}")
        return self.providers[platform]

    def get_authorization_url(
        self, platform: str, extra_params: Optional[Dict[str, str]] = None
    ) -> str:
        """Get authorization URL for platform"""
        provider = self.get_provider(platform)
        return provider.get_authorization_url(extra_params)

    async def handle_callback(
        self, platform: str, code: str, state: str, user_id: str
    ) -> OAuthToken:
        """Handle OAuth callback and store token"""
        provider = self.get_provider(platform)
        token = await provider.exchange_code(code, state)
        token.user_id = user_id

        # Store token
        await self.storage.save_token(user_id, platform, token)

        # Start auto-refresh if refresh token available
        if token.refresh_token:
            self._schedule_refresh(user_id, platform, token)

        logger.info(f"OAuth token stored for {platform} user {user_id}")
        return token

    async def get_valid_token(
        self, user_id: str, platform: str
    ) -> Optional[OAuthToken]:
        """Get a valid (non-expired) token, refreshing if necessary"""
        token = await self.storage.get_token(user_id, platform)

        if not token:
            return None

        if token.is_expired and token.refresh_token:
            try:
                provider = self.get_provider(platform)
                new_token = await provider.refresh_token(token.refresh_token)
                new_token.user_id = user_id
                await self.storage.save_token(user_id, platform, new_token)
                token = new_token
                logger.info(f"Refreshed token for {platform} user {user_id}")
            except Exception as e:
                logger.error(f"Token refresh failed for {platform}: {e}")
                return None

        return token if not token.is_expired else None

    async def revoke_token(self, user_id: str, platform: str):
        """Revoke and delete a token"""
        token = await self.storage.get_token(user_id, platform)

        if token:
            provider = self.get_provider(platform)
            await provider.revoke_token(token.access_token)
            await self.storage.delete_token(user_id, platform)

            # Cancel refresh task
            task_key = f"{user_id}:{platform}"
            if task_key in self._refresh_tasks:
                self._refresh_tasks[task_key].cancel()
                del self._refresh_tasks[task_key]

        logger.info(f"Revoked token for {platform} user {user_id}")

    async def list_connected_platforms(self, user_id: str) -> List[Dict[str, Any]]:
        """List all connected platforms for a user"""
        tokens = await self.storage.list_tokens(user_id)

        return [
            {
                "platform": platform,
                "connected": True,
                "expires_at": token.expires_at.isoformat(),
                "scopes": token.scope,
            }
            for platform, token in tokens
        ]

    def _schedule_refresh(self, user_id: str, platform: str, token: OAuthToken):
        """Schedule automatic token refresh"""
        task_key = f"{user_id}:{platform}"

        if task_key in self._refresh_tasks:
            self._refresh_tasks[task_key].cancel()

        async def refresh_task():
            # Wait until 5 minutes before expiry
            wait_time = (
                token.expires_at - utc_now() - timedelta(minutes=5)
            ).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            await self.get_valid_token(user_id, platform)

        self._refresh_tasks[task_key] = asyncio.create_task(refresh_task())


# ============================================================================
# Factory Function
# ============================================================================


def create_oauth_manager(storage: Optional[TokenStorage] = None) -> OAuthManager:
    """Factory function to create OAuth manager"""
    return OAuthManager(storage)


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """Example usage of OAuth flows"""
    manager = create_oauth_manager()

    # Get authorization URLs
    for platform in ["youtube", "tiktok", "linkedin", "instagram", "twitter"]:
        if platform in manager.providers:
            url = manager.get_authorization_url(platform)
            print(f"{platform.title()}: {url[:80]}...")

    # List connected platforms (would be empty initially)
    user_id = "test_user"
    connected = await manager.list_connected_platforms(user_id)
    print(f"\nConnected platforms: {connected}")


if __name__ == "__main__":
    asyncio.run(main())
