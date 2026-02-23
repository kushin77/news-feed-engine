// Package database provides database access for admin configuration
package database

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/models"
)

// SourceListOptions configures source listing
type SourceListOptions struct {
	Platform string
	Active   *bool
}

// SourceUpdate represents a source update request
type SourceUpdate struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name,omitempty"`
	Platform      string                 `json:"platform,omitempty"`
	SourceType    string                 `json:"source_type,omitempty"`
	Identifier    string                 `json:"identifier,omitempty"`
	Category      string                 `json:"category,omitempty"`
	Priority      *int                   `json:"priority,omitempty"`
	IngestionCron string                 `json:"ingestion_cron,omitempty"`
	Active        *bool                  `json:"active,omitempty"`
	Config        map[string]interface{} `json:"config,omitempty"`
}

// TemplateListOptions configures template listing
type TemplateListOptions struct {
	Category string
	Active   *bool
}

// TemplateUpdate represents a template update request
type TemplateUpdate struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name,omitempty"`
	Description string                 `json:"description,omitempty"`
	Category    string                 `json:"category,omitempty"`
	VoiceID     string                 `json:"voice_id,omitempty"`
	AvatarID    string                 `json:"avatar_id,omitempty"`
	Resolution  string                 `json:"resolution,omitempty"`
	Duration    *int                   `json:"duration,omitempty"`
	IsDefault   *bool                  `json:"is_default,omitempty"`
	Active      *bool                  `json:"active,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
}

// ContentAnalyticsOptions configures content analytics query
type ContentAnalyticsOptions struct {
	Days     int
	Category string
	Platform string
}

// ConfigRepository handles tenant configuration database operations
type ConfigRepository struct {
	db *DB
}

// NewConfigRepository creates a new config repository
func NewConfigRepository(db *DB) *ConfigRepository {
	return &ConfigRepository{db: db}
}

// Get retrieves tenant configuration
func (r *ConfigRepository) Get(ctx context.Context, tenantID string) (*models.TenantConfig, error) {
	query := `
		SELECT id, tenant_id, display_name, logo_url, favicon_url, primary_color, secondary_color,
		       accent_color, font_family, custom_css, custom_domain, enabled_platforms,
		       enabled_categories, default_voice_id, video_watermark, analytics_id,
		       settings, active, created_at, updated_at
		FROM tenant_configs
		WHERE tenant_id = $1
	`

	var cfg models.TenantConfig
	err := r.db.QueryRowContext(ctx, query, tenantID).Scan(
		&cfg.ID, &cfg.TenantID, &cfg.DisplayName, &cfg.LogoURL, &cfg.FaviconURL,
		&cfg.PrimaryColor, &cfg.SecondaryColor, &cfg.AccentColor, &cfg.FontFamily,
		&cfg.CustomCSS, &cfg.CustomDomain, &cfg.EnabledPlatforms, &cfg.EnabledCategories,
		&cfg.DefaultVoiceID, &cfg.VideoWatermark, &cfg.AnalyticsID, &cfg.Settings,
		&cfg.Active, &cfg.CreatedAt, &cfg.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("tenant config not found")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get tenant config: %w", err)
	}

	return &cfg, nil
}

// Update updates tenant configuration
func (r *ConfigRepository) Update(ctx context.Context, tenantID string, updates map[string]interface{}) error {
	if len(updates) == 0 {
		return nil
	}

	query := "UPDATE tenant_configs SET "
	args := []interface{}{}
	argCount := 0

	for field, value := range updates {
		argCount++
		if argCount > 1 {
			query += ", "
		}
		query += fmt.Sprintf("%s = $%d", field, argCount)
		args = append(args, value)
	}

	argCount++
	query += fmt.Sprintf(", updated_at = NOW() WHERE tenant_id = $%d", argCount)
	args = append(args, tenantID)

	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return fmt.Errorf("failed to update tenant config: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("tenant config not found")
	}

	return nil
}

// SourceRepository handles content source database operations
type SourceRepository struct {
	db *DB
}

// NewSourceRepository creates a new source repository
func NewSourceRepository(db *DB) *SourceRepository {
	return &SourceRepository{db: db}
}

// List retrieves all content sources for a tenant
func (r *SourceRepository) List(ctx context.Context, tenantID string, opts SourceListOptions) ([]models.ContentSource, error) {
	query := `
		SELECT id, tenant_id, name, platform, source_type, identifier, category,
		       priority, ingestion_cron, last_ingested, item_count, error_count,
		       last_error, config, active, created_at, updated_at
		FROM content_sources
		WHERE tenant_id = $1
	`
	args := []interface{}{tenantID}
	argCount := 1

	if opts.Platform != "" {
		argCount++
		query += fmt.Sprintf(" AND platform = $%d", argCount)
		args = append(args, opts.Platform)
	}

	if opts.Active != nil {
		argCount++
		query += fmt.Sprintf(" AND active = $%d", argCount)
		args = append(args, *opts.Active)
	}

	query += " ORDER BY priority ASC, name ASC"

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to query sources: %w", err)
	}
	defer rows.Close()

	var sources []models.ContentSource
	for rows.Next() {
		var s models.ContentSource
		err := rows.Scan(
			&s.ID, &s.TenantID, &s.Name, &s.Platform, &s.SourceType, &s.Identifier,
			&s.Category, &s.Priority, &s.IngestionCron, &s.LastIngested, &s.ItemCount,
			&s.ErrorCount, &s.LastError, &s.Config, &s.Active, &s.CreatedAt, &s.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan source: %w", err)
		}
		sources = append(sources, s)
	}

	return sources, nil
}

// Update updates an existing content source
func (r *SourceRepository) Update(ctx context.Context, tenantID string, sourceID string, update SourceUpdate) error {
	id, err := uuid.Parse(sourceID)
	if err != nil {
		return fmt.Errorf("invalid source ID: %w", err)
	}

	updates := make(map[string]interface{})
	if update.Name != "" {
		updates["name"] = update.Name
	}
	if update.Platform != "" {
		updates["platform"] = update.Platform
	}
	if update.SourceType != "" {
		updates["source_type"] = update.SourceType
	}
	if update.Identifier != "" {
		updates["identifier"] = update.Identifier
	}
	if update.Category != "" {
		updates["category"] = update.Category
	}
	if update.Priority != nil {
		updates["priority"] = *update.Priority
	}
	if update.IngestionCron != "" {
		updates["ingestion_cron"] = update.IngestionCron
	}
	if update.Active != nil {
		updates["active"] = *update.Active
	}

	if len(updates) == 0 {
		return nil
	}

	query := "UPDATE content_sources SET "
	args := []interface{}{}
	argCount := 0

	for field, value := range updates {
		argCount++
		if argCount > 1 {
			query += ", "
		}
		query += fmt.Sprintf("%s = $%d", field, argCount)
		args = append(args, value)
	}

	argCount++
	query += fmt.Sprintf(", updated_at = NOW() WHERE id = $%d", argCount)
	args = append(args, id)

	argCount++
	query += fmt.Sprintf(" AND tenant_id = $%d", argCount)
	args = append(args, tenantID)

	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return fmt.Errorf("failed to update source: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("source not found")
	}

	return nil
}

// Create creates a new content source
func (r *SourceRepository) Create(ctx context.Context, source *models.ContentSource) error {
	query := `
		INSERT INTO content_sources (
			id, tenant_id, name, platform, source_type, identifier, category,
			priority, ingestion_cron, config, active
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
		RETURNING created_at, updated_at
	`

	if source.ID == uuid.Nil {
		source.ID = uuid.New()
	}

	err := r.db.QueryRowContext(ctx, query,
		source.ID, source.TenantID, source.Name, source.Platform, source.SourceType,
		source.Identifier, source.Category, source.Priority, source.IngestionCron,
		source.Config, source.Active,
	).Scan(&source.CreatedAt, &source.UpdatedAt)

	if err != nil {
		return fmt.Errorf("failed to create source: %w", err)
	}

	return nil
}

// Delete deletes a content source
func (r *SourceRepository) Delete(ctx context.Context, tenantID string, sourceID string) error {
	id, err := uuid.Parse(sourceID)
	if err != nil {
		return fmt.Errorf("invalid source ID: %w", err)
	}

	query := "DELETE FROM content_sources WHERE id = $1 AND tenant_id = $2"

	result, err := r.db.ExecContext(ctx, query, id, tenantID)
	if err != nil {
		return fmt.Errorf("failed to delete source: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("source not found")
	}

	return nil
}

// TemplateRepository handles video template database operations
type TemplateRepository struct {
	db *DB
}

// NewTemplateRepository creates a new template repository
func NewTemplateRepository(db *DB) *TemplateRepository {
	return &TemplateRepository{db: db}
}

// List retrieves all video templates for a tenant
func (r *TemplateRepository) List(ctx context.Context, tenantID string, opts TemplateListOptions) ([]models.VideoTemplate, error) {
	query := `
		SELECT id, tenant_id, name, description, category, voice_id, avatar_id,
		       resolution, duration, intro_script, outro_script, music_track,
		       watermark_url, config, is_default, active, created_at, updated_at
		FROM video_templates
		WHERE tenant_id = $1
	`
	args := []interface{}{tenantID}
	argCount := 1

	if opts.Category != "" {
		argCount++
		query += fmt.Sprintf(" AND category = $%d", argCount)
		args = append(args, opts.Category)
	}

	if opts.Active != nil {
		argCount++
		query += fmt.Sprintf(" AND active = $%d", argCount)
		args = append(args, *opts.Active)
	}

	query += " ORDER BY is_default DESC, name ASC"

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to query templates: %w", err)
	}
	defer rows.Close()

	var templates []models.VideoTemplate
	for rows.Next() {
		var t models.VideoTemplate
		err := rows.Scan(
			&t.ID, &t.TenantID, &t.Name, &t.Description, &t.Category, &t.VoiceID, &t.AvatarID,
			&t.Resolution, &t.Duration, &t.IntroScript, &t.OutroScript, &t.MusicTrack,
			&t.WatermarkURL, &t.Config, &t.IsDefault, &t.Active, &t.CreatedAt, &t.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan template: %w", err)
		}
		templates = append(templates, t)
	}

	return templates, nil
}

// Update updates an existing video template
func (r *TemplateRepository) Update(ctx context.Context, tenantID string, templateID string, update TemplateUpdate) error {
	id, err := uuid.Parse(templateID)
	if err != nil {
		return fmt.Errorf("invalid template ID: %w", err)
	}

	updates := make(map[string]interface{})
	if update.Name != "" {
		updates["name"] = update.Name
	}
	if update.Description != "" {
		updates["description"] = update.Description
	}
	if update.Category != "" {
		updates["category"] = update.Category
	}
	if update.VoiceID != "" {
		updates["voice_id"] = update.VoiceID
	}
	if update.AvatarID != "" {
		updates["avatar_id"] = update.AvatarID
	}
	if update.Resolution != "" {
		updates["resolution"] = update.Resolution
	}
	if update.Duration != nil {
		updates["duration"] = *update.Duration
	}
	if update.IsDefault != nil {
		updates["is_default"] = *update.IsDefault
	}
	if update.Active != nil {
		updates["active"] = *update.Active
	}

	if len(updates) == 0 {
		return nil
	}

	query := "UPDATE video_templates SET "
	args := []interface{}{}
	argCount := 0

	for field, value := range updates {
		argCount++
		if argCount > 1 {
			query += ", "
		}
		query += fmt.Sprintf("%s = $%d", field, argCount)
		args = append(args, value)
	}

	argCount++
	query += fmt.Sprintf(", updated_at = NOW() WHERE id = $%d", argCount)
	args = append(args, id)

	argCount++
	query += fmt.Sprintf(" AND tenant_id = $%d", argCount)
	args = append(args, tenantID)

	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return fmt.Errorf("failed to update template: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("template not found")
	}

	return nil
}

// Create creates a new video template
func (r *TemplateRepository) Create(ctx context.Context, template *models.VideoTemplate) error {
	query := `
		INSERT INTO video_templates (
			id, tenant_id, name, description, category, voice_id, avatar_id,
			resolution, duration, intro_script, outro_script, music_track,
			watermark_url, config, is_default, active
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
		RETURNING created_at, updated_at
	`

	if template.ID == uuid.Nil {
		template.ID = uuid.New()
	}

	err := r.db.QueryRowContext(ctx, query,
		template.ID, template.TenantID, template.Name, template.Description, template.Category,
		template.VoiceID, template.AvatarID, template.Resolution, template.Duration,
		template.IntroScript, template.OutroScript, template.MusicTrack, template.WatermarkURL,
		template.Config, template.IsDefault, template.Active,
	).Scan(&template.CreatedAt, &template.UpdatedAt)

	if err != nil {
		return fmt.Errorf("failed to create template: %w", err)
	}

	return nil
}

// Delete deletes a video template
func (r *TemplateRepository) Delete(ctx context.Context, tenantID string, templateID string) error {
	id, err := uuid.Parse(templateID)
	if err != nil {
		return fmt.Errorf("invalid template ID: %w", err)
	}

	query := "DELETE FROM video_templates WHERE id = $1 AND tenant_id = $2"

	result, err := r.db.ExecContext(ctx, query, id, tenantID)
	if err != nil {
		return fmt.Errorf("failed to delete template: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("template not found")
	}

	return nil
}

// AnalyticsRepository handles analytics database operations
type AnalyticsRepository struct {
	db *DB
}

// NewAnalyticsRepository creates a new analytics repository
func NewAnalyticsRepository(db *DB) *AnalyticsRepository {
	return &AnalyticsRepository{db: db}
}

// GetOverview retrieves overview statistics for dashboard
func (r *AnalyticsRepository) GetOverview(ctx context.Context, tenantID string, days int) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// Total content
	var totalContent int
	err := r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM content WHERE tenant_id = $1", tenantID,
	).Scan(&totalContent)
	if err != nil {
		return nil, fmt.Errorf("failed to count content: %w", err)
	}
	stats["total_content"] = totalContent

	// Content in time period
	var periodContent int
	err = r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM content WHERE tenant_id = $1 AND created_at > NOW() - $2::interval",
		tenantID, fmt.Sprintf("%d days", days),
	).Scan(&periodContent)
	if err != nil {
		return nil, fmt.Errorf("failed to count period content: %w", err)
	}
	stats["content_this_period"] = periodContent

	// Calculate growth percentage
	if totalContent > 0 && periodContent > 0 {
		stats["content_growth"] = float64(periodContent) / float64(totalContent) * 100
	} else {
		stats["content_growth"] = 0.0
	}

	// Total creators
	var totalCreators int
	err = r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM creators WHERE tenant_id = $1 AND active = true", tenantID,
	).Scan(&totalCreators)
	if err != nil {
		return nil, fmt.Errorf("failed to count creators: %w", err)
	}
	stats["total_creators"] = totalCreators

	// Verified creators
	var verifiedCreators int
	err = r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM creators WHERE tenant_id = $1 AND verified_at IS NOT NULL", tenantID,
	).Scan(&verifiedCreators)
	if err != nil {
		return nil, fmt.Errorf("failed to count verified creators: %w", err)
	}
	stats["verified_creators"] = verifiedCreators

	// Total videos
	var totalVideos int
	err = r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM video_summaries WHERE tenant_id = $1", tenantID,
	).Scan(&totalVideos)
	if err != nil {
		return nil, fmt.Errorf("failed to count videos: %w", err)
	}
	stats["total_videos"] = totalVideos

	// Videos in time period
	var periodVideos int
	err = r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM video_summaries WHERE tenant_id = $1 AND created_at > NOW() - $2::interval",
		tenantID, fmt.Sprintf("%d days", days),
	).Scan(&periodVideos)
	if err != nil {
		return nil, fmt.Errorf("failed to count period videos: %w", err)
	}
	stats["videos_this_period"] = periodVideos

	// Total views
	var totalViews sql.NullInt64
	err = r.db.QueryRowContext(ctx,
		"SELECT SUM(view_count) FROM content WHERE tenant_id = $1", tenantID,
	).Scan(&totalViews)
	if err != nil {
		return nil, fmt.Errorf("failed to sum views: %w", err)
	}
	stats["total_views"] = totalViews.Int64

	// Views in time period
	var periodViews sql.NullInt64
	err = r.db.QueryRowContext(ctx,
		"SELECT SUM(view_count) FROM content WHERE tenant_id = $1 AND created_at > NOW() - $2::interval",
		tenantID, fmt.Sprintf("%d days", days),
	).Scan(&periodViews)
	if err != nil {
		return nil, fmt.Errorf("failed to sum period views: %w", err)
	}
	stats["views_this_period"] = periodViews.Int64

	// Get top categories
	categories, _ := r.getCategoryBreakdown(ctx, tenantID)
	stats["top_categories"] = categories

	// Get platform breakdown
	platforms, _ := r.getPlatformBreakdown(ctx, tenantID)
	stats["platform_breakdown"] = platforms

	return stats, nil
}

// getCategoryBreakdown retrieves content count by category
func (r *AnalyticsRepository) getCategoryBreakdown(ctx context.Context, tenantID string) ([]map[string]interface{}, error) {
	query := `
		SELECT category, COUNT(*) as count
		FROM content
		WHERE tenant_id = $1 AND category IS NOT NULL AND category != ''
		GROUP BY category
		ORDER BY count DESC
		LIMIT 10
	`

	rows, err := r.db.QueryContext(ctx, query, tenantID)
	if err != nil {
		return nil, fmt.Errorf("failed to query category breakdown: %w", err)
	}
	defer rows.Close()

	var breakdown []map[string]interface{}
	for rows.Next() {
		var category string
		var count int
		if err := rows.Scan(&category, &count); err != nil {
			continue
		}
		breakdown = append(breakdown, map[string]interface{}{
			"name":  category,
			"count": count,
		})
	}

	return breakdown, nil
}

// getPlatformBreakdown retrieves content count by platform
func (r *AnalyticsRepository) getPlatformBreakdown(ctx context.Context, tenantID string) ([]map[string]interface{}, error) {
	query := `
		SELECT platform, COUNT(*) as count
		FROM content
		WHERE tenant_id = $1
		GROUP BY platform
		ORDER BY count DESC
	`

	rows, err := r.db.QueryContext(ctx, query, tenantID)
	if err != nil {
		return nil, fmt.Errorf("failed to query platform breakdown: %w", err)
	}
	defer rows.Close()

	var breakdown []map[string]interface{}
	for rows.Next() {
		var platform string
		var count int
		if err := rows.Scan(&platform, &count); err != nil {
			continue
		}
		breakdown = append(breakdown, map[string]interface{}{
			"platform": platform,
			"count":    count,
		})
	}

	return breakdown, nil
}

// GetContentAnalytics retrieves content-specific analytics
func (r *AnalyticsRepository) GetContentAnalytics(ctx context.Context, tenantID string, opts ContentAnalyticsOptions) (map[string]interface{}, error) {
	analytics := make(map[string]interface{})

	// Build base query with filters
	whereClause := "tenant_id = $1"
	args := []interface{}{tenantID}
	argCount := 1

	if opts.Category != "" {
		argCount++
		whereClause += fmt.Sprintf(" AND category = $%d", argCount)
		args = append(args, opts.Category)
	}

	if opts.Platform != "" {
		argCount++
		whereClause += fmt.Sprintf(" AND platform = $%d", argCount)
		args = append(args, opts.Platform)
	}

	if opts.Days > 0 {
		argCount++
		whereClause += fmt.Sprintf(" AND created_at > NOW() - $%d::interval", argCount)
		args = append(args, fmt.Sprintf("%d days", opts.Days))
	}

	// Total items
	var totalItems int
	err := r.db.QueryRowContext(ctx,
		fmt.Sprintf("SELECT COUNT(*) FROM content WHERE %s", whereClause), args...,
	).Scan(&totalItems)
	if err != nil {
		return nil, fmt.Errorf("failed to count content: %w", err)
	}
	analytics["total_items"] = totalItems

	// Average quality score
	var avgQuality sql.NullFloat64
	err = r.db.QueryRowContext(ctx,
		fmt.Sprintf("SELECT AVG(quality_score) FROM content WHERE %s", whereClause), args...,
	).Scan(&avgQuality)
	if err != nil {
		return nil, fmt.Errorf("failed to avg quality: %w", err)
	}
	analytics["avg_quality_score"] = avgQuality.Float64

	// Average sentiment
	var avgSentiment sql.NullFloat64
	err = r.db.QueryRowContext(ctx,
		fmt.Sprintf("SELECT AVG(sentiment_score) FROM content WHERE %s", whereClause), args...,
	).Scan(&avgSentiment)
	if err != nil {
		return nil, fmt.Errorf("failed to avg sentiment: %w", err)
	}
	analytics["avg_sentiment"] = avgSentiment.Float64

	analytics["metrics"] = map[string]interface{}{
		"total_items":       totalItems,
		"avg_quality_score": avgQuality.Float64,
		"avg_sentiment":     avgSentiment.Float64,
	}

	return analytics, nil
}

// GetCreatorAnalytics retrieves creator-specific analytics
func (r *AnalyticsRepository) GetCreatorAnalytics(ctx context.Context, tenantID string, days int) (map[string]interface{}, error) {
	analytics := make(map[string]interface{})

	// Total creators
	var totalCreators int
	err := r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM creators WHERE tenant_id = $1 AND active = true", tenantID,
	).Scan(&totalCreators)
	if err != nil {
		return nil, fmt.Errorf("failed to count creators: %w", err)
	}
	analytics["total_creators"] = totalCreators

	// New creators in period
	var newCreators int
	err = r.db.QueryRowContext(ctx,
		"SELECT COUNT(*) FROM creators WHERE tenant_id = $1 AND created_at > NOW() - $2::interval",
		tenantID, fmt.Sprintf("%d days", days),
	).Scan(&newCreators)
	if err != nil {
		return nil, fmt.Errorf("failed to count new creators: %w", err)
	}
	analytics["new_creators"] = newCreators

	// Tier breakdown
	tierBreakdown, _ := r.getCreatorTierBreakdown(ctx, tenantID)
	analytics["tier_breakdown"] = tierBreakdown

	analytics["metrics"] = map[string]interface{}{
		"total_creators": totalCreators,
		"new_creators":   newCreators,
	}

	return analytics, nil
}

// getCreatorTierBreakdown retrieves creator count by tier
func (r *AnalyticsRepository) getCreatorTierBreakdown(ctx context.Context, tenantID string) ([]map[string]interface{}, error) {
	query := `
		SELECT tier, COUNT(*) as count
		FROM creators
		WHERE tenant_id = $1 AND active = true
		GROUP BY tier
		ORDER BY
			CASE tier
				WHEN 'platinum' THEN 1
				WHEN 'gold' THEN 2
				WHEN 'silver' THEN 3
				WHEN 'bronze' THEN 4
				ELSE 5
			END
	`

	rows, err := r.db.QueryContext(ctx, query, tenantID)
	if err != nil {
		return nil, fmt.Errorf("failed to query tier breakdown: %w", err)
	}
	defer rows.Close()

	var breakdown []map[string]interface{}
	for rows.Next() {
		var tier string
		var count int
		if err := rows.Scan(&tier, &count); err != nil {
			continue
		}
		breakdown = append(breakdown, map[string]interface{}{
			"tier":  tier,
			"count": count,
		})
	}

	return breakdown, nil
}
