// Package database provides database access for creators
package database

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/models"
)

// CreatorRepository handles creator database operations
type CreatorRepository struct {
	db *DB
}

// NewCreatorRepository creates a new creator repository
func NewCreatorRepository(db *DB) *CreatorRepository {
	return &CreatorRepository{db: db}
}

// CreatorListOptions contains options for filtering creators
type CreatorListOptions struct {
	Page         int
	Limit        int
	Platform     string // youtube, twitter, reddit
	Tier         string // platinum, gold, silver, bronze, unverified
	VerifiedOnly bool
	Active       *bool
	SortBy       string // follower_count, content_count, engagement_rate, created_at
	Order        string // asc, desc
}

// List retrieves a paginated list of creators with filters
func (r *CreatorRepository) List(ctx context.Context, tenantID string, opts CreatorListOptions) ([]models.Creator, int, error) {
	query := `
		SELECT c.id, c.tenant_id, c.name, c.platform, c.platform_id, c.avatar_url, c.bio,
		       c.tier, c.verified_at, c.follower_count, c.content_count, c.engagement_rate,
		       c.topics_expertise, c.social_links, c.metadata, c.active, c.created_at, c.updated_at
		FROM creators c
		WHERE c.tenant_id = $1
	`
	args := []interface{}{tenantID}
	argCount := 1

	// Add filters
	if opts.Platform != "" {
		argCount++
		query += fmt.Sprintf(" AND c.platform = $%d", argCount)
		args = append(args, opts.Platform)
	}

	if opts.Tier != "" {
		argCount++
		query += fmt.Sprintf(" AND c.tier = $%d", argCount)
		args = append(args, opts.Tier)
	}

	if opts.VerifiedOnly {
		query += " AND c.verified_at IS NOT NULL"
	}

	if opts.Active != nil {
		argCount++
		query += fmt.Sprintf(" AND c.active = $%d", argCount)
		args = append(args, *opts.Active)
	}

	// Count total matching records
	countQuery := "SELECT COUNT(*) FROM creators c WHERE c.tenant_id = $1"
	countArgs := []interface{}{tenantID}
	if opts.Platform != "" {
		countQuery += " AND c.platform = $2"
		countArgs = append(countArgs, opts.Platform)
	}
	if opts.Tier != "" {
		countQuery += fmt.Sprintf(" AND c.tier = $%d", len(countArgs)+1)
		countArgs = append(countArgs, opts.Tier)
	}
	if opts.VerifiedOnly {
		countQuery += " AND c.verified_at IS NOT NULL"
	}

	var total int
	err := r.db.QueryRowContext(ctx, countQuery, countArgs...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count creators: %w", err)
	}

	// Add sorting
	sortBy := "created_at"
	if opts.SortBy == "follower_count" || opts.SortBy == "content_count" || opts.SortBy == "engagement_rate" {
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

	// Execute query
	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query creators: %w", err)
	}
	defer rows.Close()

	var creators []models.Creator
	for rows.Next() {
		var c models.Creator
		err := rows.Scan(
			&c.ID, &c.TenantID, &c.Name, &c.Platform, &c.PlatformID, &c.AvatarURL, &c.Bio,
			&c.Tier, &c.VerifiedAt, &c.FollowerCount, &c.ContentCount, &c.EngagementRate,
			&c.TopicsExpertise, &c.SocialLinks, &c.Metadata, &c.Active, &c.CreatedAt, &c.UpdatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan creator: %w", err)
		}
		creators = append(creators, c)
	}

	return creators, total, nil
}

// GetByID retrieves a single creator by ID
func (r *CreatorRepository) GetByID(ctx context.Context, tenantID string, creatorID uuid.UUID) (*models.Creator, error) {
	query := `
		SELECT c.id, c.tenant_id, c.name, c.platform, c.platform_id, c.avatar_url, c.bio,
		       c.tier, c.verified_at, c.follower_count, c.content_count, c.engagement_rate,
		       c.topics_expertise, c.social_links, c.metadata, c.active, c.created_at, c.updated_at
		FROM creators c
		WHERE c.tenant_id = $1 AND c.id = $2
	`

	var c models.Creator
	err := r.db.QueryRowContext(ctx, query, tenantID, creatorID).Scan(
		&c.ID, &c.TenantID, &c.Name, &c.Platform, &c.PlatformID, &c.AvatarURL, &c.Bio,
		&c.Tier, &c.VerifiedAt, &c.FollowerCount, &c.ContentCount, &c.EngagementRate,
		&c.TopicsExpertise, &c.SocialLinks, &c.Metadata, &c.Active, &c.CreatedAt, &c.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("creator not found")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get creator: %w", err)
	}

	return &c, nil
}

// GetByPlatformID retrieves a creator by platform and platform_id
func (r *CreatorRepository) GetByPlatformID(ctx context.Context, tenantID string, platform, platformID string) (*models.Creator, error) {
	query := `
		SELECT c.id, c.tenant_id, c.name, c.platform, c.platform_id, c.avatar_url, c.bio,
		       c.tier, c.verified_at, c.follower_count, c.content_count, c.engagement_rate,
		       c.topics_expertise, c.social_links, c.metadata, c.active, c.created_at, c.updated_at
		FROM creators c
		WHERE c.tenant_id = $1 AND c.platform = $2 AND c.platform_id = $3
	`

	var c models.Creator
	err := r.db.QueryRowContext(ctx, query, tenantID, platform, platformID).Scan(
		&c.ID, &c.TenantID, &c.Name, &c.Platform, &c.PlatformID, &c.AvatarURL, &c.Bio,
		&c.Tier, &c.VerifiedAt, &c.FollowerCount, &c.ContentCount, &c.EngagementRate,
		&c.TopicsExpertise, &c.SocialLinks, &c.Metadata, &c.Active, &c.CreatedAt, &c.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("creator not found")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get creator: %w", err)
	}

	return &c, nil
}

// GetTopCreators retrieves top creators by follower count or engagement rate
func (r *CreatorRepository) GetTopCreators(ctx context.Context, tenantID string, metric string, limit int) ([]models.Creator, error) {
	// Validate metric
	sortBy := "follower_count"
	if metric == "engagement" {
		sortBy = "engagement_rate"
	}

	query := fmt.Sprintf(`
		SELECT c.id, c.tenant_id, c.name, c.platform, c.platform_id, c.avatar_url, c.bio,
		       c.tier, c.verified_at, c.follower_count, c.content_count, c.engagement_rate,
		       c.topics_expertise, c.social_links, c.metadata, c.active, c.created_at, c.updated_at
		FROM creators c
		WHERE c.tenant_id = $1 AND c.active = true
		ORDER BY c.%s DESC
		LIMIT $2
	`, sortBy)

	rows, err := r.db.QueryContext(ctx, query, tenantID, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to query top creators: %w", err)
	}
	defer rows.Close()

	var creators []models.Creator
	for rows.Next() {
		var c models.Creator
		err := rows.Scan(
			&c.ID, &c.TenantID, &c.Name, &c.Platform, &c.PlatformID, &c.AvatarURL, &c.Bio,
			&c.Tier, &c.VerifiedAt, &c.FollowerCount, &c.ContentCount, &c.EngagementRate,
			&c.TopicsExpertise, &c.SocialLinks, &c.Metadata, &c.Active, &c.CreatedAt, &c.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan creator: %w", err)
		}
		creators = append(creators, c)
	}

	return creators, nil
}

// Create inserts a new creator
func (r *CreatorRepository) Create(ctx context.Context, creator *models.Creator) error {
	query := `
		INSERT INTO creators (
			id, tenant_id, name, platform, platform_id, avatar_url, bio, tier,
			follower_count, content_count, engagement_rate, topics_expertise,
			social_links, metadata, active
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
		)
		RETURNING created_at, updated_at
	`

	// Generate UUID if not provided
	if creator.ID == uuid.Nil {
		creator.ID = uuid.New()
	}

	err := r.db.QueryRowContext(ctx, query,
		creator.ID, creator.TenantID, creator.Name, creator.Platform, creator.PlatformID,
		creator.AvatarURL, creator.Bio, creator.Tier, creator.FollowerCount,
		creator.ContentCount, creator.EngagementRate, creator.TopicsExpertise,
		creator.SocialLinks, creator.Metadata, creator.Active,
	).Scan(&creator.CreatedAt, &creator.UpdatedAt)

	if err != nil {
		return fmt.Errorf("failed to create creator: %w", err)
	}

	return nil
}

// Update updates an existing creator
func (r *CreatorRepository) Update(ctx context.Context, creatorID uuid.UUID, updates map[string]interface{}) error {
	if len(updates) == 0 {
		return nil
	}

	// Whitelist of allowed updatable fields
	allowedFields := map[string]bool{
		"name":            true,
		"bio":             true,
		"profile_url":     true,
		"follower_count":  true,
		"engagement_rate": true,
		"verified_at":     true,
		"tier":            true,
		"platform":        true,
		"active":          true,
		"metadata":        true,
	}

	// Build dynamic UPDATE query with field validation
	query := "UPDATE creators SET "
	args := []interface{}{}
	argCount := 0

	for field, value := range updates {
		// Validate field name is in whitelist
		if !allowedFields[field] {
			return fmt.Errorf("field %q is not allowed for update", field)
		}

		argCount++
		if argCount > 1 {
			query += ", "
		}
		query += fmt.Sprintf("%s = $%d", field, argCount)
		args = append(args, value)
	}

	argCount++
	query += fmt.Sprintf(", updated_at = NOW() WHERE id = $%d", argCount)
	args = append(args, creatorID)

	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return fmt.Errorf("failed to update creator: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("creator not found")
	}

	return nil
}

// SoftDelete marks a creator as inactive
func (r *CreatorRepository) SoftDelete(ctx context.Context, tenantID string, creatorID uuid.UUID) error {
	query := `
		UPDATE creators
		SET active = false, updated_at = NOW()
		WHERE tenant_id = $1 AND id = $2
	`

	result, err := r.db.ExecContext(ctx, query, tenantID, creatorID)
	if err != nil {
		return fmt.Errorf("failed to soft delete creator: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("creator not found")
	}

	return nil
}

// Verify marks a creator as verified and sets the tier
func (r *CreatorRepository) Verify(ctx context.Context, tenantID string, creatorID uuid.UUID, tier string) error {
	query := `
		UPDATE creators
		SET tier = $1, verified_at = NOW(), updated_at = NOW()
		WHERE tenant_id = $2 AND id = $3
	`

	result, err := r.db.ExecContext(ctx, query, tier, tenantID, creatorID)
	if err != nil {
		return fmt.Errorf("failed to verify creator: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rows == 0 {
		return fmt.Errorf("creator not found")
	}

	return nil
}
