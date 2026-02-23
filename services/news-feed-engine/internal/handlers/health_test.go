package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func init() {
	gin.SetMode(gin.TestMode)
}

func setupRouter() *gin.Engine {
	router := gin.New()
	router.GET("/health", HealthHandler)
	router.GET("/ready", ReadinessHandler)
	return router
}

func TestHealthHandler(t *testing.T) {
	router := setupRouter()

	t.Run("returns healthy status", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/health", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response ServiceStatus
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "healthy", response.Status)
		assert.Equal(t, "news-feed-engine", response.Service)
		assert.Equal(t, "1.0.0", response.Version)
	})
}

func TestReadinessHandler(t *testing.T) {
	router := setupRouter()

	t.Run("returns ready status when all checks pass", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/ready", nil)
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response ServiceStatus
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "ready", response.Status)
		assert.NotEmpty(t, response.Checks)
	})
}
