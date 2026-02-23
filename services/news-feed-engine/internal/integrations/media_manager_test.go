package integrations

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestMediaManagerClient tests the Media Manager client implementation
func TestMediaManagerClient(t *testing.T) {
	t.Run("NewMediaManagerClient", func(t *testing.T) {
		client := NewMediaManagerClient(
			"https://api.example.com",
			"test-api-key",
		)

		assert.NotNil(t, client)
		assert.Equal(t, "https://api.example.com", client.baseURL)
	})

	t.Run("GetAsset", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/api/v1/assets/asset-123", r.URL.Path)
			assert.Equal(t, "GET", r.Method)
			assert.Equal(t, "Bearer test-api-key", r.Header.Get("Authorization"))

			response := MediaAsset{
				ID:        "asset-123",
				Name:      "test-image.jpg",
				Type:      "image",
				URL:       "https://cdn.example.com/test-image.jpg",
				MimeType:  "image/jpeg",
				SizeBytes: 1024000,
				Width:     1920,
				Height:    1080,
				AITags:    []string{"technology", "AI"},
				CreatedAt: time.Now(),
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		asset, err := client.GetAsset(ctx, "asset-123")

		require.NoError(t, err)
		assert.Equal(t, "asset-123", asset.ID)
		assert.Equal(t, "test-image.jpg", asset.Name)
		assert.Equal(t, "image", asset.Type)
	})

	t.Run("SearchAssets", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/api/v1/assets/search", r.URL.Path)
			assert.Equal(t, "GET", r.Method)
			assert.Equal(t, "AI technology", r.URL.Query().Get("query"))

			response := struct {
				Assets []MediaAsset `json:"assets"`
				Total  int          `json:"total"`
			}{
				Assets: []MediaAsset{
					{ID: "1", Name: "ai-image.jpg", Type: "image"},
					{ID: "2", Name: "tech-video.mp4", Type: "video"},
				},
				Total: 2,
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		assets, err := client.SearchAssets(ctx, AssetSearchRequest{
			Query:  "AI technology",
			Type:   "",
			Tags:   nil,
			Limit:  10,
			Offset: 0,
		})

		require.NoError(t, err)
		assert.Len(t, assets, 2)
	})

	t.Run("GetRecommendedAssets", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/api/v1/assets/recommendations", r.URL.Path)
			assert.Equal(t, "POST", r.Method)

			var request struct {
				ContentID string `json:"content_id"`
				Limit     int    `json:"limit"`
			}
			json.NewDecoder(r.Body).Decode(&request)
			assert.Equal(t, "content-123", request.ContentID)

			response := []RecommendedAsset{
				{
					Asset:           MediaAsset{ID: "1", Name: "recommended.jpg"},
					RelevanceScore:  0.95,
					RecommendReason: "High topic match",
				},
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		recommendations, err := client.GetRecommendedAssets(ctx, "content-123", 10)

		require.NoError(t, err)
		assert.Len(t, recommendations, 1)
		assert.Equal(t, 0.95, recommendations[0].RelevanceScore)
	})

	t.Run("UploadAsset", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/api/v1/assets/upload", r.URL.Path)
			assert.Equal(t, "POST", r.Method)

			response := MediaAsset{
				ID:        "new-asset-123",
				Name:      "uploaded-image.jpg",
				Type:      "image",
				URL:       "https://cdn.example.com/uploaded-image.jpg",
				SizeBytes: 2048000,
			}

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(response)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		asset, err := client.UploadAsset(ctx, UploadAssetRequest{
			FileName:    "uploaded-image.jpg",
			ContentType: "image/jpeg",
			Data:        []byte("fake-image-data"),
			Tags:        []string{"test", "upload"},
		})

		require.NoError(t, err)
		assert.Equal(t, "new-asset-123", asset.ID)
	})

	t.Run("AnalyzeAsset", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/api/v1/assets/asset-123/analyze", r.URL.Path)
			assert.Equal(t, "POST", r.Method)

			response := AIAssetAnalysis{
				AssetID:         "asset-123",
				Tags:            []string{"technology", "AI", "futuristic"},
				Description:     "An image depicting AI technology concepts",
				ObjectsDetected: []string{"computer", "robot", "circuit"},
				Colors:          []string{"#0066CC", "#1A1A1A", "#FFFFFF"},
				Sentiment:       "positive",
				Confidence:      0.92,
			}

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		analysis, err := client.AnalyzeAsset(ctx, "asset-123")

		require.NoError(t, err)
		assert.Equal(t, "asset-123", analysis.AssetID)
		assert.Contains(t, analysis.Tags, "AI")
		assert.Equal(t, 0.92, analysis.Confidence)
	})

	t.Run("DeleteAsset", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/api/v1/assets/asset-123", r.URL.Path)
			assert.Equal(t, "DELETE", r.Method)

			w.WriteHeader(http.StatusNoContent)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		err := client.DeleteAsset(ctx, "asset-123")

		require.NoError(t, err)
	})

	t.Run("ErrorHandling_NotFound", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
			json.NewEncoder(w).Encode(map[string]string{
				"error": "Asset not found",
			})
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx := context.Background()

		_, err := client.GetAsset(ctx, "nonexistent")

		require.Error(t, err)
		assert.Contains(t, err.Error(), "not found")
	})

	t.Run("ErrorHandling_Unauthorized", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusUnauthorized)
			json.NewEncoder(w).Encode(map[string]string{
				"error": "Invalid API key",
			})
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "invalid-key")
		ctx := context.Background()

		_, err := client.GetAsset(ctx, "asset-123")

		require.Error(t, err)
		assert.Contains(t, err.Error(), "unauthorized")
	})

	t.Run("ContextCancellation", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			time.Sleep(5 * time.Second) // Simulate slow response
			w.WriteHeader(http.StatusOK)
		}))
		defer server.Close()

		client := NewMediaManagerClient(server.URL, "test-api-key")
		ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
		defer cancel()

		_, err := client.GetAsset(ctx, "asset-123")

		require.Error(t, err)
		assert.Contains(t, err.Error(), "context")
	})
}

// TestAssetSearchRequest tests search request validation
func TestAssetSearchRequest(t *testing.T) {
	t.Run("ValidRequest", func(t *testing.T) {
		req := AssetSearchRequest{
			Query:  "AI technology",
			Type:   "image",
			Tags:   []string{"tech", "AI"},
			Limit:  10,
			Offset: 0,
		}

		assert.NotEmpty(t, req.Query)
		assert.Equal(t, "image", req.Type)
	})

	t.Run("EmptyQuery", func(t *testing.T) {
		req := AssetSearchRequest{
			Query: "",
			Type:  "image",
		}

		assert.Empty(t, req.Query)
	})
}

// TestMediaAsset tests media asset structure
func TestMediaAsset(t *testing.T) {
	t.Run("ImageAsset", func(t *testing.T) {
		asset := MediaAsset{
			ID:        "img-123",
			Name:      "test.jpg",
			Type:      "image",
			MimeType:  "image/jpeg",
			Width:     1920,
			Height:    1080,
			SizeBytes: 1024000,
		}

		assert.True(t, asset.IsImage())
		assert.False(t, asset.IsVideo())
	})

	t.Run("VideoAsset", func(t *testing.T) {
		asset := MediaAsset{
			ID:              "vid-123",
			Name:            "test.mp4",
			Type:            "video",
			MimeType:        "video/mp4",
			Width:           1920,
			Height:          1080,
			DurationSeconds: 120,
		}

		assert.False(t, asset.IsImage())
		assert.True(t, asset.IsVideo())
		assert.Equal(t, 120, asset.DurationSeconds)
	})
}

// TestRecommendedAsset tests recommendation structure
func TestRecommendedAsset(t *testing.T) {
	t.Run("HighRelevance", func(t *testing.T) {
		rec := RecommendedAsset{
			Asset: MediaAsset{
				ID:   "asset-1",
				Name: "recommended.jpg",
			},
			RelevanceScore:  0.95,
			RecommendReason: "Exact topic match with content",
		}

		assert.True(t, rec.IsHighlyRelevant())
	})

	t.Run("LowRelevance", func(t *testing.T) {
		rec := RecommendedAsset{
			Asset: MediaAsset{
				ID:   "asset-2",
				Name: "low-match.jpg",
			},
			RelevanceScore:  0.3,
			RecommendReason: "Partial category match",
		}

		assert.False(t, rec.IsHighlyRelevant())
	})
}

// TestCDNURLGeneration tests CDN URL generation
func TestCDNURLGeneration(t *testing.T) {
	t.Run("GenerateWithTransform", func(t *testing.T) {
		asset := MediaAsset{
			ID:     "asset-123",
			URL:    "https://storage.example.com/asset-123.jpg",
			CDNURL: "https://cdn.example.com/asset-123.jpg",
		}

		cdnURL := asset.GetCDNURL(CDNTransformOptions{
			Width:   800,
			Height:  600,
			Quality: 85,
			Format:  "webp",
		})

		assert.Contains(t, cdnURL, "cdn.example.com")
	})

	t.Run("FallbackToOriginal", func(t *testing.T) {
		asset := MediaAsset{
			ID:     "asset-123",
			URL:    "https://storage.example.com/asset-123.jpg",
			CDNURL: "",
		}

		cdnURL := asset.GetCDNURL(CDNTransformOptions{})

		assert.Equal(t, asset.URL, cdnURL)
	})
}

// Benchmark tests
func BenchmarkSearchAssets(b *testing.B) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		response := struct {
			Assets []MediaAsset `json:"assets"`
		}{
			Assets: make([]MediaAsset, 100),
		}
		json.NewEncoder(w).Encode(response)
	}))
	defer server.Close()

	client := NewMediaManagerClient(server.URL, "test-key")
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		client.SearchAssets(ctx, AssetSearchRequest{
			Query: "test",
			Limit: 100,
		})
	}
}

func BenchmarkGetAsset(b *testing.B) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(MediaAsset{ID: "test"})
	}))
	defer server.Close()

	client := NewMediaManagerClient(server.URL, "test-key")
	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		client.GetAsset(ctx, "test-id")
	}
}
