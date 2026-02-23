// Package database provides content repository implementation
package database

import (
	"context"
	"database/sql"
	"fmt"
	"strings"

	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/models"
)

// ContentRepository handles content database operations
type ContentRepository struct {
	db *DB
}

// NewContentRepository creates a new content repository
func NewContentRepository(db *DB) *ContentRepository {
	return &ContentRepository{db: db}
}

// List returns paginated content list with filters
func (r *ContentRepository) List(ctx context.Context, tenantID string, opts ListOptions) ([]*models.Content, int, error) {
	// Build WHERE clause
	whereClauses := []string{"c.tenant_id = $1"}
	args := []interface{}{tenantID}
	argCount := 1

	if opts.Category != "" {
		argCount++
		whereClauses = append(whereClauses, fmt.Sprintf("c.category = $%d", argCount))
		args = append(args, opts.Category)
	}

	if opts.Platform != "" {
		argCount++
		whereClauses = append(whereClauses, fmt.Sprintf("c.platform = $%d", argCount))
		args = append(args, opts.Platform)
	}

	if opts.GeoClassification != "" {
		argCount++
		whereClauses = append(whereClauses, fmt.Sprintf("c.geo_classification = $%d", argCount))
		args = append(args, opts.GeoClassification)
	}

	if opts.ProcessingStatus != "" {
		argCount++
		whereClauses = append(whereClauses, fmt.Sprintf("c.processing_status = $%d", argCount))
		args = append(args, opts.ProcessingStatus)
	}

	whereClause := strings.Join(whereClauses, " AND ")

	// Count total items
	var total int
	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM content c WHERE %s", whereClause)
	if err := r.db.GetContext(ctx, &total, countQuery, args...); err != nil {
		return nil, 0, fmt.Errorf("failed to count content: %w", err)
	}

	// Build ORDER BY clause
	orderBy := "c.published_at DESC"
	if opts.SortBy != "" {
		switch opts.SortBy {
		case "engagement_score":
			orderBy = "c.engagement_score DESC"
		case "quality_score":
			orderBy = "c.quality_score DESC"
		case "view_count":
			orderBy = "c.view_count DESC"
		case "published_at":
			if opts.Order == "asc" {
				orderBy = "c.published_at ASC"
			}
		}
	}

	// Calculate offset
	offset := (opts.Page - 1) * opts.Limit

	// Query with pagination
	query := fmt.Sprintf(`
		SELECT c.*, cr.name as creator_name, cr.avatar_url as creator_avatar_url
		FROM content c
		LEFT JOIN creators cr ON c.creator_id = cr.id
		WHERE %s
		ORDER BY %s
		LIMIT $%d OFFSET $%d
	`, whereClause, orderBy, argCount+1, argCount+2)

	args = append(args, opts.Limit, offset)

	rows, err := r.db.QueryxContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query content: %w", err)
	}
	defer rows.Close()

	var contents []*models.Content
	for rows.Next() {
		var content models.Content
		var creatorName sql.NullString
		var creatorAvatarURL sql.NullString

		// Create a map for scanning
		scanMap := make(map[string]interface{})
		if err := rows.MapScan(scanMap); err != nil {
			return nil, 0, fmt.Errorf("failed to scan content: %w", err)
		}

		// Manually map to struct (simplified, use struct tags in production)
		content.ID = uuid.MustParse(scanMap["id"].(string))
		content.TenantID = scanMap["tenant_id"].(string)
		content.Title = scanMap["title"].(string)
		content.Platform = models.Platform(scanMap["platform"].(string))
		content.ContentType = models.ContentType(scanMap["content_type"].(string))
		content.OriginalURL = scanMap["original_url"].(string)

		if creatorName.Valid {
			content.Creator = &models.Creator{
				Name:      creatorName.String,
				AvatarURL: creatorAvatarURL.String,
			}
		}

		contents = append(contents, &content)
	}

	if err := rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("error iterating rows: %w", err)
	}

	return contents, total, nil
}

// GetByID retrieves a single content item by ID
func (r *ContentRepository) GetByID(ctx context.Context, tenantID string, contentID uuid.UUID) (*models.Content, error) {
	query := `
		SELECT c.*,
			   cr.id as "creator.id", cr.name as "creator.name", cr.platform as "creator.platform",
			   cr.avatar_url as "creator.avatar_url", cr.tier as "creator.tier"
		FROM content c
		LEFT JOIN creators cr ON c.creator_id = cr.id
		WHERE c.tenant_id = $1 AND c.id = $2
	`

	var content models.Content
	content.Creator = &models.Creator{}

	err := r.db.GetContext(ctx, &content, query, tenantID, contentID)
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("content not found")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get content: %w", err)
	}

	return &content, nil
}

// SearchSemantic performs semantic search using pgvector
func (r *ContentRepository) SearchSemantic(ctx context.Context, tenantID string, embedding []float32, opts ListOptions) ([]*models.Content, int, error) {
	// Convert embedding to PostgreSQL vector format
	embeddingStr := fmt.Sprintf("[%s]", strings.Trim(strings.Join(strings.Fields(fmt.Sprint(embedding)), ","), "[]"))

	// Build WHERE clause
	whereClauses := []string{"c.tenant_id = $1", "c.embedding IS NOT NULL"}
	args := []interface{}{tenantID}
	argCount := 1

	if opts.Category != "" {
		argCount++
		whereClauses = append(whereClauses, fmt.Sprintf("c.category = $%d", argCount))
		args = append(args, opts.Category)
	}

	whereClause := strings.Join(whereClauses, " AND ")

	// Count total items (approximate for performance)
	var total int
	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM content c WHERE %s", whereClause)
	if err := r.db.GetContext(ctx, &total, countQuery, args...); err != nil {
		total = 1000 // Fallback estimate
	}

	// Calculate offset
	offset := (opts.Page - 1) * opts.Limit

	// Semantic search query with cosine similarity
	query := fmt.Sprintf(`
		SELECT c.*,
			   cr.name as creator_name,
			   cr.avatar_url as creator_avatar_url,
			   1 - (c.embedding <=> $%d::vector) as similarity
		FROM content c
		LEFT JOIN creators cr ON c.creator_id = cr.id
		WHERE %s
		ORDER BY c.embedding <=> $%d::vector
		LIMIT $%d OFFSET $%d
	`, argCount+1, whereClause, argCount+1, argCount+2, argCount+3)

	args = append(args, embeddingStr, opts.Limit, offset)

	rows, err := r.db.QueryxContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to search content: %w", err)
	}
	defer rows.Close()

	var contents []*models.Content
	for rows.Next() {
		var content models.Content
		var creatorName sql.NullString
		var creatorAvatarURL sql.NullString
		var similarity float64

		scanMap := make(map[string]interface{})
		if err := rows.MapScan(scanMap); err != nil {
			return nil, 0, fmt.Errorf("failed to scan content: %w", err)
		}

		// Map to struct (simplified)
		content.ID = uuid.MustParse(scanMap["id"].(string))
		content.TenantID = scanMap["tenant_id"].(string)
		content.Title = scanMap["title"].(string)
		similarity = scanMap["similarity"].(float64)

		// Store similarity in metadata
		if content.Metadata == nil {
			content.Metadata = make(models.JSONB)
		}
		content.Metadata["search_similarity"] = similarity

		if creatorName.Valid {
			content.Creator = &models.Creator{
				Name:      creatorName.String,
				AvatarURL: creatorAvatarURL.String,
			}
		}

		contents = append(contents, &content)
	}

	return contents, total, nil
}

// GetTrending returns trending content based on engagement score
func (r *ContentRepository) GetTrending(ctx context.Context, tenantID string, timeRange string, limit int) ([]*models.Content, error) {
	// Calculate time threshold
	var timeThreshold string
	switch timeRange {
	case "1h":
		timeThreshold = "NOW() - INTERVAL '1 hour'"
	case "6h":
		timeThreshold = "NOW() - INTERVAL '6 hours'"
	case "24h":
		timeThreshold = "NOW() - INTERVAL '24 hours'"
	case "7d":
		timeThreshold = "NOW() - INTERVAL '7 days'"
	default:
		timeThreshold = "NOW() - INTERVAL '24 hours'"
	}

	query := fmt.Sprintf(`
		SELECT c.*,
			   cr.name as creator_name,
			   cr.avatar_url as creator_avatar_url,
			   (c.view_count * 0.3 + c.like_count * 0.4 + c.comment_count * 0.2 + c.share_count * 0.1) as trending_score
		FROM content c
		LEFT JOIN creators cr ON c.creator_id = cr.id
		WHERE c.tenant_id = $1
		  AND c.published_at >= %s
		  AND c.processing_status = 'completed'
		ORDER BY trending_score DESC, c.published_at DESC
		LIMIT $2
	`, timeThreshold)

	rows, err := r.db.QueryxContext(ctx, query, tenantID, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to get trending content: %w", err)
	}
	defer rows.Close()

	var contents []*models.Content
	for rows.Next() {
		var content models.Content
		scanMap := make(map[string]interface{})
		if err := rows.MapScan(scanMap); err != nil {
			continue
		}

		content.ID = uuid.MustParse(scanMap["id"].(string))
		content.TenantID = scanMap["tenant_id"].(string)
		content.Title = scanMap["title"].(string)
		contents = append(contents, &content)
	}

	return contents, nil
}

// SoftDelete marks content as deleted (soft delete)
func (r *ContentRepository) SoftDelete(ctx context.Context, tenantID string, contentID uuid.UUID) error {
	query := `
		UPDATE content
		SET processing_status = 'failed',
			metadata = jsonb_set(COALESCE(metadata, '{}'::jsonb), '{deleted}', 'true'::jsonb),
			updated_at = NOW()
		WHERE tenant_id = $1 AND id = $2
	`

	result, err := r.db.ExecContext(ctx, query, tenantID, contentID)
	if err != nil {
		return fmt.Errorf("failed to delete content: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("content not found")
	}

	return nil
}

// ListOptions contains filtering and pagination options
type ListOptions struct {
	Page              int
	Limit             int
	Category          string
	Platform          string
	GeoClassification string
	ProcessingStatus  string
	SortBy            string
	Order             string
	DateFrom          string
	DateTo            string
}

// ListByCreator retrieves content for a specific creator
func (r *ContentRepository) ListByCreator(ctx context.Context, tenantID string, creatorID uuid.UUID, opts ListOptions) ([]*models.Content, int, error) {
	// Build query
	query := `
		SELECT c.id, c.tenant_id, c.creator_id, c.platform, c.platform_content_id, c.content_type,
		       c.title, c.description, c.original_url, c.thumbnail_url, c.summary, c.category,
		       c.tags, c.geo_classification, c.source_location, c.sentiment, c.quality_score,
		       c.engagement_score, c.view_count, c.like_count, c.comment_count, c.share_count,
		       c.processing_status, c.processed_at, c.published_at, c.ai_analysis, c.metadata,
		       c.featured_until, c.created_at, c.updated_at
		FROM content c
		WHERE c.tenant_id = $1 AND c.creator_id = $2 AND c.processing_status = 'completed'
	`
	args := []interface{}{tenantID, creatorID}
	argCount := 2

	// Add category filter if provided
	if opts.Category != "" {
		argCount++
		query += fmt.Sprintf(" AND c.category = $%d", argCount)
		args = append(args, opts.Category)
	}

	// Count total
	countQuery := "SELECT COUNT(*) FROM content c WHERE c.tenant_id = $1 AND c.creator_id = $2 AND c.processing_status = 'completed'"
	if opts.Category != "" {
		countQuery += " AND c.category = $3"
	}

	var total int
	if opts.Category != "" {
		err := r.db.QueryRowContext(ctx, countQuery, tenantID, creatorID, opts.Category).Scan(&total)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to count content: %w", err)
		}
	} else {
		err := r.db.QueryRowContext(ctx, countQuery, tenantID, creatorID).Scan(&total)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to count content: %w", err)
		}
	}

	// Add sorting
	sortBy := "published_at"
	if opts.SortBy == "engagement_score" || opts.SortBy == "view_count" || opts.SortBy == "quality_score" {
		sortBy = opts.SortBy
	}
	order := "DESC"
	if opts.Order == "asc" {
		order = "ASC"
	}
	query += fmt.Sprintf(" ORDER BY c.%s %s", sortBy, order)

	// Add pagination
	argCount++
	query += fmt.Sprintf(" LIMIT $%d", argCount)
	args = append(args, opts.Limit)

	argCount++
	query += fmt.Sprintf(" OFFSET $%d", argCount)
	args = append(args, (opts.Page-1)*opts.Limit)

	rows, err := r.db.QueryxContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query creator content: %w", err)
	}
	defer rows.Close()

	var contents []*models.Content
	for rows.Next() {
		var content models.Content
		err := rows.StructScan(&content)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan content: %w", err)
		}
		contents = append(contents, &content)
	}

	return contents, total, nil
}
