package integrations

import (
	"context"
	"encoding/xml"
	"fmt"
	"html"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"

	"go.uber.org/zap"
)

// RSSIntegration handles RSS/Atom feed parsing
type RSSIntegration struct {
	httpClient *http.Client
	logger     *zap.Logger
}

// FeedItem represents a single item from an RSS/Atom feed
type FeedItem struct {
	ID          string    `json:"id"`
	Title       string    `json:"title"`
	Link        string    `json:"link"`
	Description string    `json:"description"`
	Content     string    `json:"content"`
	Author      string    `json:"author"`
	Categories  []string  `json:"categories"`
	PublishedAt time.Time `json:"published_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	ImageURL    string    `json:"image_url"`
}

// Feed represents an RSS/Atom feed
type Feed struct {
	Title       string     `json:"title"`
	Link        string     `json:"link"`
	Description string     `json:"description"`
	Language    string     `json:"language"`
	Items       []FeedItem `json:"items"`
	LastUpdated time.Time  `json:"last_updated"`
}

// RSS 2.0 structs
type rssFeed struct {
	XMLName xml.Name   `xml:"rss"`
	Channel rssChannel `xml:"channel"`
}

type rssChannel struct {
	Title       string    `xml:"title"`
	Link        string    `xml:"link"`
	Description string    `xml:"description"`
	Language    string    `xml:"language"`
	Items       []rssItem `xml:"item"`
}

type rssItem struct {
	Title        string        `xml:"title"`
	Link         string        `xml:"link"`
	Description  string        `xml:"description"`
	Content      string        `xml:"http://purl.org/rss/1.0/modules/content/ encoded"`
	Author       string        `xml:"author"`
	Creator      string        `xml:"http://purl.org/dc/elements/1.1/ creator"`
	Categories   []string      `xml:"category"`
	PubDate      string        `xml:"pubDate"`
	GUID         string        `xml:"guid"`
	Enclosure    *rssEnclosure `xml:"enclosure"`
	MediaContent *mediaContent `xml:"http://search.yahoo.com/mrss/ content"`
}

type rssEnclosure struct {
	URL  string `xml:"url,attr"`
	Type string `xml:"type,attr"`
}

type mediaContent struct {
	URL    string `xml:"url,attr"`
	Medium string `xml:"medium,attr"`
}

// Atom structs
type atomFeed struct {
	XMLName  xml.Name    `xml:"http://www.w3.org/2005/Atom feed"`
	Title    string      `xml:"title"`
	Link     []atomLink  `xml:"link"`
	Subtitle string      `xml:"subtitle"`
	Updated  string      `xml:"updated"`
	Entries  []atomEntry `xml:"entry"`
}

type atomLink struct {
	Href string `xml:"href,attr"`
	Rel  string `xml:"rel,attr"`
}

type atomEntry struct {
	ID         string         `xml:"id"`
	Title      string         `xml:"title"`
	Link       []atomLink     `xml:"link"`
	Content    atomContent    `xml:"content"`
	Summary    string         `xml:"summary"`
	Author     atomAuthor     `xml:"author"`
	Categories []atomCategory `xml:"category"`
	Published  string         `xml:"published"`
	Updated    string         `xml:"updated"`
}

type atomContent struct {
	Content string `xml:",chardata"`
	Type    string `xml:"type,attr"`
}

type atomAuthor struct {
	Name  string `xml:"name"`
	Email string `xml:"email"`
}

type atomCategory struct {
	Term  string `xml:"term,attr"`
	Label string `xml:"label,attr"`
}

// NewRSSIntegration creates a new RSS integration
func NewRSSIntegration(logger *zap.Logger) *RSSIntegration {
	return &RSSIntegration{
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: logger,
	}
}

// FetchFeed fetches and parses an RSS or Atom feed
func (r *RSSIntegration) FetchFeed(ctx context.Context, feedURL string) (*Feed, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, feedURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("User-Agent", "ElevatedIQ News Feed Engine/1.0")
	req.Header.Set("Accept", "application/rss+xml, application/atom+xml, application/xml, text/xml")

	resp, err := r.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch feed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("feed returned status: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read feed body: %w", err)
	}

	// Try to detect and parse feed type
	feed, err := r.parseRSS(body)
	if err == nil {
		return feed, nil
	}

	feed, err = r.parseAtom(body)
	if err == nil {
		return feed, nil
	}

	return nil, fmt.Errorf("failed to parse feed as RSS or Atom")
}

// parseRSS parses RSS 2.0 feed
func (r *RSSIntegration) parseRSS(data []byte) (*Feed, error) {
	var rss rssFeed
	if err := xml.Unmarshal(data, &rss); err != nil {
		return nil, err
	}

	if rss.Channel.Title == "" {
		return nil, fmt.Errorf("not a valid RSS feed")
	}

	feed := &Feed{
		Title:       rss.Channel.Title,
		Link:        rss.Channel.Link,
		Description: rss.Channel.Description,
		Language:    rss.Channel.Language,
		Items:       make([]FeedItem, 0, len(rss.Channel.Items)),
	}

	for _, item := range rss.Channel.Items {
		feedItem := FeedItem{
			ID:          item.GUID,
			Title:       cleanText(item.Title),
			Link:        item.Link,
			Description: cleanHTML(item.Description),
			Categories:  item.Categories,
		}

		// Use content:encoded if available, otherwise description
		if item.Content != "" {
			feedItem.Content = cleanHTML(item.Content)
		} else {
			feedItem.Content = feedItem.Description
		}

		// Author
		if item.Author != "" {
			feedItem.Author = item.Author
		} else if item.Creator != "" {
			feedItem.Author = item.Creator
		}

		// Parse published date
		if item.PubDate != "" {
			pubDate, err := parseRSSDate(item.PubDate)
			if err == nil {
				feedItem.PublishedAt = pubDate
			}
		}

		// Image URL from enclosure or media:content
		if item.Enclosure != nil && strings.HasPrefix(item.Enclosure.Type, "image/") {
			feedItem.ImageURL = item.Enclosure.URL
		} else if item.MediaContent != nil && (item.MediaContent.Medium == "image" || strings.HasPrefix(item.MediaContent.URL, "http")) {
			feedItem.ImageURL = item.MediaContent.URL
		} else {
			// Try to extract image from content
			feedItem.ImageURL = extractImageFromHTML(item.Content)
			if feedItem.ImageURL == "" {
				feedItem.ImageURL = extractImageFromHTML(item.Description)
			}
		}

		// Use link as ID if no GUID
		if feedItem.ID == "" {
			feedItem.ID = feedItem.Link
		}

		feed.Items = append(feed.Items, feedItem)
	}

	return feed, nil
}

// parseAtom parses Atom feed
func (r *RSSIntegration) parseAtom(data []byte) (*Feed, error) {
	var atom atomFeed
	if err := xml.Unmarshal(data, &atom); err != nil {
		return nil, err
	}

	if atom.Title == "" {
		return nil, fmt.Errorf("not a valid Atom feed")
	}

	feed := &Feed{
		Title:       atom.Title,
		Description: atom.Subtitle,
		Items:       make([]FeedItem, 0, len(atom.Entries)),
	}

	// Find feed link
	for _, link := range atom.Link {
		if link.Rel == "" || link.Rel == "alternate" {
			feed.Link = link.Href
			break
		}
	}

	// Parse updated time
	if atom.Updated != "" {
		updated, err := time.Parse(time.RFC3339, atom.Updated)
		if err == nil {
			feed.LastUpdated = updated
		}
	}

	for _, entry := range atom.Entries {
		feedItem := FeedItem{
			ID:    entry.ID,
			Title: cleanText(entry.Title),
		}

		// Find entry link
		for _, link := range entry.Link {
			if link.Rel == "" || link.Rel == "alternate" {
				feedItem.Link = link.Href
				break
			}
		}

		// Content
		if entry.Content.Content != "" {
			if entry.Content.Type == "html" || entry.Content.Type == "xhtml" {
				feedItem.Content = cleanHTML(entry.Content.Content)
			} else {
				feedItem.Content = cleanText(entry.Content.Content)
			}
		}

		// Summary/Description
		feedItem.Description = cleanHTML(entry.Summary)
		if feedItem.Content == "" {
			feedItem.Content = feedItem.Description
		}

		// Author
		if entry.Author.Name != "" {
			feedItem.Author = entry.Author.Name
		}

		// Categories
		for _, cat := range entry.Categories {
			if cat.Label != "" {
				feedItem.Categories = append(feedItem.Categories, cat.Label)
			} else if cat.Term != "" {
				feedItem.Categories = append(feedItem.Categories, cat.Term)
			}
		}

		// Parse dates
		if entry.Published != "" {
			published, err := time.Parse(time.RFC3339, entry.Published)
			if err == nil {
				feedItem.PublishedAt = published
			}
		}
		if entry.Updated != "" {
			updated, err := time.Parse(time.RFC3339, entry.Updated)
			if err == nil {
				feedItem.UpdatedAt = updated
			}
		}

		// Extract image from content
		feedItem.ImageURL = extractImageFromHTML(entry.Content.Content)

		feed.Items = append(feed.Items, feedItem)
	}

	return feed, nil
}

// ValidateFeedURL checks if a URL is a valid RSS/Atom feed
func (r *RSSIntegration) ValidateFeedURL(ctx context.Context, feedURL string) (bool, error) {
	feed, err := r.FetchFeed(ctx, feedURL)
	if err != nil {
		return false, err
	}
	return feed != nil && len(feed.Items) > 0, nil
}

// parseRSSDate parses various RSS date formats
func parseRSSDate(dateStr string) (time.Time, error) {
	formats := []string{
		time.RFC1123Z,
		time.RFC1123,
		time.RFC822Z,
		time.RFC822,
		"Mon, 2 Jan 2006 15:04:05 -0700",
		"Mon, 2 Jan 2006 15:04:05 MST",
		"2006-01-02T15:04:05-07:00",
		"2006-01-02T15:04:05Z",
		"2006-01-02 15:04:05",
		"2006-01-02",
	}

	dateStr = strings.TrimSpace(dateStr)

	for _, format := range formats {
		if t, err := time.Parse(format, dateStr); err == nil {
			return t, nil
		}
	}

	return time.Time{}, fmt.Errorf("unable to parse date: %s", dateStr)
}

// cleanText removes HTML and cleans up text
func cleanText(s string) string {
	s = html.UnescapeString(s)
	s = regexp.MustCompile(`<[^>]*>`).ReplaceAllString(s, "")
	s = regexp.MustCompile(`\s+`).ReplaceAllString(s, " ")
	return strings.TrimSpace(s)
}

// cleanHTML removes HTML tags but preserves some structure
func cleanHTML(s string) string {
	s = html.UnescapeString(s)

	// Replace common block elements with newlines
	s = regexp.MustCompile(`(?i)<br\s*/?\s*>`).ReplaceAllString(s, "\n")
	s = regexp.MustCompile(`(?i)</p>`).ReplaceAllString(s, "\n\n")
	s = regexp.MustCompile(`(?i)</div>`).ReplaceAllString(s, "\n")
	s = regexp.MustCompile(`(?i)</li>`).ReplaceAllString(s, "\n")

	// Remove all remaining tags
	s = regexp.MustCompile(`<[^>]*>`).ReplaceAllString(s, "")

	// Clean up whitespace
	s = regexp.MustCompile(`[ \t]+`).ReplaceAllString(s, " ")
	s = regexp.MustCompile(`\n\s*\n`).ReplaceAllString(s, "\n\n")

	return strings.TrimSpace(s)
}

// extractImageFromHTML extracts the first image URL from HTML content
func extractImageFromHTML(htmlContent string) string {
	if htmlContent == "" {
		return ""
	}

	// Try to find img src
	imgRegex := regexp.MustCompile(`<img[^>]+src=["']([^"']+)["']`)
	matches := imgRegex.FindStringSubmatch(htmlContent)
	if len(matches) > 1 {
		return matches[1]
	}

	// Try to find og:image or similar meta tags (less common in feed content)
	metaRegex := regexp.MustCompile(`<meta[^>]+content=["']([^"']+\.(jpg|jpeg|png|gif|webp)[^"']*)["']`)
	matches = metaRegex.FindStringSubmatch(htmlContent)
	if len(matches) > 1 {
		return matches[1]
	}

	return ""
}
