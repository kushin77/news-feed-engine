// Package database provides database access for video summaries
package database

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/models"
)

// VideoRepository handles video database operations
type VideoRepository struct {
	db *DB
}

// NewVideoRepository creates a new video repository
func NewVideoRepository(db *DB) *VideoRepository {
	return &VideoRepository{db: db}
}

// VideoListOptions contains options for filtering videos
type VideoListOptions struct {
	Page      int
	Limit     int
	Status    string // pending, processing, completed, failed
	ContentID *uuid.UUID
	DateFrom  string
	DateTo    string
	SortBy    string // created_at, duration, view_count
	Order     string // asc, desc
}

// List retrieves a paginated list of videos with filters
func (r *VideoRepository) List(ctx context.Context, tenantID string, opts VideoListOptions) ([]models.VideoSummary, int, error) {
	query := `
		SELECT v.id, v.tenant_id, v.content_id, v.title, v.script, v.voice_id, v.avatar_id,
		       v.video_url, v.thumbnail_url, v.duration, v.file_size, v.resolution, v.format,
		       v.status, v.error_message, v.view_count, v.like_count, v.share_count,
		       v.generated_at, v.generation_time, v.metadata, v.created_at, v.updated_at
		FROM video_summaries v
		WHERE v.tenant_id = $1
	`
	args := []interface{}{tenantID}
	argCount := 1

	// Add filters
	if opts.Status != "" {
		argCount++
		query += fmt.Sprintf(" AND v.status = $%d", argCount)
		args = append(args, opts.Status)
	}

	if opts.ContentID != nil {
		argCount++
		query += fmt.Sprintf(" AND v.content_id = $%d", argCount)
		args = append(args, opts.ContentID)
	}

	if opts.DateFrom != "" {
		argCount++
		query += fmt.Sprintf(" AND v.created_at >= $%d", argCount)
		args = append(args, opts.DateFrom)
	}

	if opts.DateTo != "" {
		argCount++
		query += fmt.Sprintf(" AND v.created_at <= $%d", argCount)
		args = append(args, opts.DateTo)
	}

	// Count total matching records
	countQuery := "SELECT COUNT(*) FROM video_summaries v WHERE v.tenant_id = $1"
	if opts.Status != "" {
		countQuery += " AND v.status = $2"
	}
	if opts.ContentID != nil {
		countQuery += fmt.Sprintf(" AND v.content_id = $%d", argCount-1)
	}

	var total int
	err := r.db.QueryRowContext(ctx, countQuery, args[:argCount]...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count videos: %w", err)
	}

	// Add sorting
	sortBy := "created_at"
	if opts.SortBy == "duration" || opts.SortBy == "view_count" {
		sortBy = opts.SortBy
	}

	order := "DESC"
	if opts.Order == "asc" {
		order = "ASC"
	}

	query += fmt.Sprintf(" ORDER BY v.%s %s", sortBy, order)

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
		return nil, 0, fmt.Errorf("failed to query videos: %w", err)
	}
	defer rows.Close()

	var videos []models.VideoSummary
	for rows.Next() {
		var v models.VideoSummary
		err := rows.Scan(
			&v.ID, &v.TenantID, &v.ContentID, &v.Title, &v.Script, &v.VoiceID, &v.AvatarID,
			&v.VideoURL, &v.ThumbnailURL, &v.Duration, &v.FileSize, &v.Resolution, &v.Format,
			&v.Status, &v.ErrorMessage, &v.ViewCount, &v.LikeCount, &v.ShareCount,
			&v.GeneratedAt, &v.GenerationTime, &v.Metadata, &v.CreatedAt, &v.UpdatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan video: %w", err)
		}
		videos = append(videos, v)
	}

	return videos, total, nil
}

// GetByID retrieves a single video by ID
func (r *VideoRepository) GetByID(ctx context.Context, tenantID string, videoID uuid.UUID) (*models.VideoSummary, error) {
	query := `
		SELECT v.id, v.tenant_id, v.content_id, v.title, v.script, v.voice_id, v.avatar_id,
		       v.video_url, v.thumbnail_url, v.duration, v.file_size, v.resolution, v.format,
		       v.status, v.error_message, v.view_count, v.like_count, v.share_count,
		       v.generated_at, v.generation_time, v.metadata, v.created_at, v.updated_at
		FROM video_summaries v
		WHERE v.tenant_id = $1 AND v.id = $2
	`

	var v models.VideoSummary
	err := r.db.QueryRowContext(ctx, query, tenantID, videoID).Scan(
		&v.ID, &v.TenantID, &v.ContentID, &v.Title, &v.Script, &v.VoiceID, &v.AvatarID,
		&v.VideoURL, &v.ThumbnailURL, &v.Duration, &v.FileSize, &v.Resolution, &v.Format,
		&v.Status, &v.ErrorMessage, &v.ViewCount, &v.LikeCount, &v.ShareCount,
		&v.GeneratedAt, &v.GenerationTime, &v.Metadata, &v.CreatedAt, &v.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("video not found")
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get video: %w", err)
	}

	return &v, nil
}

// GetTranscript retrieves the transcript (script) for a video
func (r *VideoRepository) GetTranscript(ctx context.Context, tenantID string, videoID uuid.UUID) (string, error) {
	query := `
		SELECT v.script
		FROM video_summaries v
		WHERE v.tenant_id = $1 AND v.id = $2
	`

	var transcript string
	err := r.db.QueryRowContext(ctx, query, tenantID, videoID).Scan(&transcript)

	if err == sql.ErrNoRows {
		return "", fmt.Errorf("video not found")
	}
	if err != nil {
		return "", fmt.Errorf("failed to get transcript: %w", err)
	}

	return transcript, nil
}

// GetQueueStats retrieves video generation queue statistics
func (r *VideoRepository) GetQueueStats(ctx context.Context, tenantID string) (*models.VideoQueueStats, error) {
	query := `
		SELECT
			COUNT(CASE WHEN status = 'pending' THEN 1 END) as queued,
			COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing,
			COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
			COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
		FROM video_summaries
		WHERE tenant_id = $1
	`

	var stats models.VideoQueueStats
	err := r.db.QueryRowContext(ctx, query, tenantID).Scan(
		&stats.Queued,
		&stats.Processing,
		&stats.Completed,
		&stats.Failed,
	)

	if err != nil {
		return nil, fmt.Errorf("failed to get queue stats: %w", err)
	}

	stats.TenantID = tenantID
	return &stats, nil
}
