// Package middleware provides HTTP middleware for the News Feed Engine
package middleware

import (
	"fmt"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

// TenantContextKey is the context key for tenant ID
const TenantContextKey = "tenant_id"

// DefaultTenantID is used when no tenant is specified
const DefaultTenantID = "elevatediq"

// TenantMiddleware extracts tenant ID from request headers or uses default
func TenantMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tenantID := c.GetHeader("X-Tenant-ID")
		if tenantID == "" {
			// Check subdomain for white-label
			host := c.Request.Host
			parts := strings.Split(host, ".")
			if len(parts) >= 3 {
				tenantID = parts[0]
			} else {
				tenantID = DefaultTenantID
			}
		}

		c.Set(TenantContextKey, tenantID)
		c.Next()
	}
}

// GetTenantID retrieves the tenant ID from the context
func GetTenantID(c *gin.Context) string {
	if tenantID, exists := c.Get(TenantContextKey); exists {
		return tenantID.(string)
	}
	return DefaultTenantID
}

// AuthMiddleware validates JWT tokens for protected routes
func AuthMiddleware(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error":   "🔑 Authorization required",
				"help":    "Please include Bearer token in Authorization header",
				"example": "Authorization: Bearer eyJhbGciOiJIUzI1NiIs...",
				"docs":    "https://docs.elevatediq.ai/news-feed-api#authentication",
			})
			return
		}

		// Extract token from "Bearer <token>"
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error":   "🔑 Invalid authorization format",
				"help":    "Use format: Authorization: Bearer <token>",
				"example": "Authorization: Bearer eyJhbGciOiJIUzI1NiIs...",
				"docs":    "https://docs.elevatediq.ai/news-feed-api#authentication",
			})
			return
		}

		tokenString := parts[1]

		// Parse and validate token
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, jwt.ErrSignatureInvalid
			}
			return []byte(jwtSecret), nil
		})

		if err != nil || !token.Valid {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"error":  "🔑 Token invalid or expired",
				"help":   "Please generate a new authentication token",
				"action": "Request new token from /auth/login endpoint",
				"docs":   "https://docs.elevatediq.ai/news-feed-api#authentication",
			})
			return
		}

		// Extract claims
		if claims, ok := token.Claims.(jwt.MapClaims); ok {
			c.Set("user_id", claims["sub"])
			c.Set("user_email", claims["email"])
			c.Set("user_roles", claims["roles"])
		}

		c.Next()
	}
}

// RateLimiter implements a simple token bucket rate limiter
func RateLimiter(maxRequests int, window time.Duration) gin.HandlerFunc {
	type client struct {
		count    int
		lastSeen time.Time
	}

	var (
		clients = make(map[string]*client)
		mu      sync.Mutex
	)

	// Cleanup old entries periodically
	go func() {
		for {
			time.Sleep(window)
			mu.Lock()
			for ip, c := range clients {
				if time.Since(c.lastSeen) > window {
					delete(clients, ip)
				}
			}
			mu.Unlock()
		}
	}()

	return func(c *gin.Context) {
		ip := c.ClientIP()
		tenantID := GetTenantID(c)
		key := tenantID + ":" + ip

		mu.Lock()
		defer mu.Unlock()

		if clients[key] == nil {
			clients[key] = &client{}
		}

		cl := clients[key]

		// Reset count if window has passed
		if time.Since(cl.lastSeen) > window {
			cl.count = 0
		}

		cl.count++
		cl.lastSeen = time.Now()

		if cl.count > maxRequests {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"error":       "⏱️ Rate limit exceeded",
				"message":     fmt.Sprintf("Maximum %d requests per %.0f seconds allowed", maxRequests, window.Seconds()),
				"retry_after": int(window.Seconds()),
				"reset_in":    fmt.Sprintf("%d seconds", int((time.Until(cl.lastSeen.Add(window))).Seconds())),
				"help":        "Please wait before retrying. Contact support to request higher limits",
			})
			return
		}

		// Set rate limit headers
		c.Header("X-RateLimit-Limit", string(rune(maxRequests)))
		c.Header("X-RateLimit-Remaining", string(rune(maxRequests-cl.count)))

		c.Next()
	}
}

// CacheMiddleware adds caching headers for GET requests
func CacheMiddleware(maxAge time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		if c.Request.Method == "GET" {
			c.Header("Cache-Control", "public, max-age="+string(rune(int(maxAge.Seconds()))))
		}
		c.Next()
	}
}

// RequestIDMiddleware adds a unique request ID to each request
func RequestIDMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = generateRequestID()
		}
		c.Set("request_id", requestID)
		c.Header("X-Request-ID", requestID)
		c.Next()
	}
}

func generateRequestID() string {
	// Simple implementation - in production use UUID
	return time.Now().Format("20060102150405") + "-" + randomString(8)
}

func randomString(n int) string {
	const letters = "abcdefghijklmnopqrstuvwxyz0123456789"
	b := make([]byte, n)
	for i := range b {
		b[i] = letters[time.Now().UnixNano()%int64(len(letters))]
	}
	return string(b)
}
