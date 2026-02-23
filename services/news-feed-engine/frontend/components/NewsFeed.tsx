'use client';

import React, { useState, useEffect, useCallback } from 'react';

// Types
export interface Creator {
  id: string;
  name: string;
  platform: 'youtube' | 'twitter' | 'rss' | 'podcast';
  platform_id: string;
  avatar_url?: string;
  trust_score: number;
}

export interface ContentItem {
  id: string;
  creator_id: string;
  creator_name: string;
  creator_avatar?: string;
  title: string;
  summary?: string;
  content_type: 'video' | 'article' | 'tweet' | 'podcast';
  source_url: string;
  thumbnail_url?: string;
  published_at: string;
  category: string;
  tags: string[];
  relevance_score: number;
  sentiment: 'positive' | 'negative' | 'neutral';
  ai_analysis?: {
    key_points: string[];
    topics: string[];
    entities: string[];
  };
}

export interface VideoSummary {
  id: string;
  video_url: string;
  video_title: string;
  thumbnail_url?: string;
  duration_seconds: number;
  summary: string;
  key_points: string[];
  transcript?: string;
  creator_name: string;
}

export interface NewsFeedConfig {
  tenantId?: string;
  apiBaseUrl: string;
  authToken?: string;
  theme?: {
    primaryColor: string;
    secondaryColor: string;
    backgroundColor: string;
    textColor: string;
    cardBackground: string;
  };
  features?: {
    showVideoSummaries: boolean;
    showAIAnalysis: boolean;
    enableSemanticSearch: boolean;
  };
}

// Default theme
const defaultTheme = {
  primaryColor: '#6C5CE7',
  secondaryColor: '#00B894',
  backgroundColor: '#F8F9FA',
  textColor: '#2D3436',
  cardBackground: '#FFFFFF',
};

// Context for configuration
const NewsFeedContext = React.createContext<NewsFeedConfig>({
  apiBaseUrl: '/api/v1',
  theme: defaultTheme,
  features: {
    showVideoSummaries: true,
    showAIAnalysis: true,
    enableSemanticSearch: true,
  },
});

// API hook
function useNewsFeedAPI() {
  const config = React.useContext(NewsFeedContext);

  const fetchWithAuth = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(config.authToken && { Authorization: `Bearer ${config.authToken}` }),
      ...(config.tenantId && { 'X-Tenant-ID': config.tenantId }),
      ...options.headers,
    };

    const response = await fetch(`${config.apiBaseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }, [config.apiBaseUrl, config.authToken, config.tenantId]);

  return { fetchWithAuth };
}

// Provider Component
export function NewsFeedProvider({
  children,
  config,
}: {
  children: React.ReactNode;
  config: NewsFeedConfig;
}) {
  const mergedConfig = {
    ...config,
    theme: { ...defaultTheme, ...config.theme },
    features: {
      showVideoSummaries: true,
      showAIAnalysis: true,
      enableSemanticSearch: true,
      ...config.features,
    },
  };

  return (
    <NewsFeedContext.Provider value={mergedConfig}>
      <div
        style={{
          '--nf-primary': mergedConfig.theme?.primaryColor,
          '--nf-secondary': mergedConfig.theme?.secondaryColor,
          '--nf-bg': mergedConfig.theme?.backgroundColor,
          '--nf-text': mergedConfig.theme?.textColor,
          '--nf-card-bg': mergedConfig.theme?.cardBackground,
        } as React.CSSProperties}
      >
        {children}
      </div>
    </NewsFeedContext.Provider>
  );
}

// Content Card Component
export function ContentCard({
  content,
  onClick,
  compact = false,
}: {
  content: ContentItem;
  onClick?: (content: ContentItem) => void;
  compact?: boolean;
}) {
  const config = React.useContext(NewsFeedContext);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  const getPlatformIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎬';
      case 'article': return '📄';
      case 'tweet': return '🐦';
      case 'podcast': return '🎙️';
      default: return '📰';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '#00B894';
      case 'negative': return '#E74C3C';
      default: return '#95A5A6';
    }
  };

  return (
    <div
      className="nf-content-card"
      onClick={() => onClick?.(content)}
      style={{
        background: config.theme?.cardBackground || '#FFFFFF',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        padding: compact ? '12px' : '16px',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s, box-shadow 0.2s',
        display: 'flex',
        flexDirection: compact ? 'row' : 'column',
        gap: '12px',
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
      }}
    >
      {/* Thumbnail */}
      {content.thumbnail_url && !compact && (
        <div style={{ position: 'relative' }}>
          <img
            src={content.thumbnail_url}
            alt={content.title}
            style={{
              width: '100%',
              height: '180px',
              objectFit: 'cover',
              borderRadius: '8px',
            }}
          />
          <span
            style={{
              position: 'absolute',
              top: '8px',
              left: '8px',
              background: 'rgba(0,0,0,0.7)',
              color: 'white',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '12px',
            }}
          >
            {getPlatformIcon(content.content_type)} {content.content_type}
          </span>
        </div>
      )}

      {/* Compact thumbnail */}
      {content.thumbnail_url && compact && (
        <img
          src={content.thumbnail_url}
          alt={content.title}
          style={{
            width: '80px',
            height: '60px',
            objectFit: 'cover',
            borderRadius: '6px',
            flexShrink: 0,
          }}
        />
      )}

      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Creator info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          {content.creator_avatar && (
            <img
              src={content.creator_avatar}
              alt={content.creator_name}
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
              }}
            />
          )}
          <span style={{ fontSize: '13px', color: '#666' }}>{content.creator_name}</span>
          <span style={{ fontSize: '12px', color: '#999' }}>• {formatDate(content.published_at)}</span>
        </div>

        {/* Title */}
        <h3
          style={{
            fontSize: compact ? '14px' : '16px',
            fontWeight: 600,
            color: config.theme?.textColor,
            margin: '0 0 8px 0',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {content.title}
        </h3>

        {/* Summary */}
        {content.summary && !compact && (
          <p
            style={{
              fontSize: '14px',
              color: '#666',
              margin: '0 0 12px 0',
              lineHeight: 1.5,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {content.summary}
          </p>
        )}

        {/* Tags and meta */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center' }}>
          <span
            style={{
              background: config.theme?.primaryColor + '20',
              color: config.theme?.primaryColor,
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: 500,
            }}
          >
            {content.category}
          </span>

          {!compact && content.tags.slice(0, 3).map((tag, i) => (
            <span
              key={i}
              style={{
                background: '#F1F3F4',
                color: '#666',
                padding: '2px 8px',
                borderRadius: '4px',
                fontSize: '11px',
              }}
            >
              {tag}
            </span>
          ))}

          <span
            style={{
              marginLeft: 'auto',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: getSentimentColor(content.sentiment),
            }}
            title={`Sentiment: ${content.sentiment}`}
          />
        </div>
      </div>
    </div>
  );
}

// News Feed Component
export function NewsFeed({
  category,
  creatorId,
  limit = 20,
  layout = 'grid',
  onContentClick,
}: {
  category?: string;
  creatorId?: string;
  limit?: number;
  layout?: 'grid' | 'list' | 'compact';
  onContentClick?: (content: ContentItem) => void;
}) {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const { fetchWithAuth } = useNewsFeedAPI();

  const loadContent = useCallback(async (pageNum: number, append = false) => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pageNum.toString(),
        limit: limit.toString(),
        ...(category && { category }),
        ...(creatorId && { creator_id: creatorId }),
      });

      const data = await fetchWithAuth(`/content?${params}`);

      if (append) {
        setContent((prev) => [...prev, ...data.content]);
      } else {
        setContent(data.content);
      }

      setHasMore(data.content.length === limit);
      setError(null);
    } catch (err) {
      setError('Failed to load content');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [fetchWithAuth, category, creatorId, limit]);

  useEffect(() => {
    loadContent(1);
  }, [loadContent]);

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    loadContent(nextPage, true);
  };

  if (error && content.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#E74C3C' }}>
        {error}
      </div>
    );
  }

  const gridStyles: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: layout === 'grid'
      ? 'repeat(auto-fill, minmax(300px, 1fr))'
      : '1fr',
    gap: layout === 'compact' ? '8px' : '16px',
  };

  return (
    <div>
      <div style={gridStyles}>
        {content.map((item) => (
          <ContentCard
            key={item.id}
            content={item}
            onClick={onContentClick}
            compact={layout === 'compact'}
          />
        ))}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              border: '3px solid #F1F3F4',
              borderTopColor: '#6C5CE7',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto',
            }}
          />
        </div>
      )}

      {hasMore && !loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <button
            onClick={loadMore}
            style={{
              background: '#6C5CE7',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}

// Video Summary Card
export function VideoSummaryCard({
  summary,
  onWatch,
}: {
  summary: VideoSummary;
  onWatch?: (summary: VideoSummary) => void;
}) {
  const config = React.useContext(NewsFeedContext);
  const [expanded, setExpanded] = useState(false);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div
      style={{
        background: config.theme?.cardBackground || '#FFFFFF',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
      }}
    >
      {/* Video thumbnail */}
      <div style={{ position: 'relative' }}>
        {summary.thumbnail_url && (
          <img
            src={summary.thumbnail_url}
            alt={summary.video_title}
            style={{
              width: '100%',
              height: '200px',
              objectFit: 'cover',
            }}
          />
        )}
        <button
          onClick={() => onWatch?.(summary)}
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(0,0,0,0.7)',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>
        <span
          style={{
            position: 'absolute',
            bottom: '8px',
            right: '8px',
            background: 'rgba(0,0,0,0.8)',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
          }}
        >
          {formatDuration(summary.duration_seconds)}
        </span>
      </div>

      {/* Content */}
      <div style={{ padding: '16px' }}>
        <h3
          style={{
            fontSize: '16px',
            fontWeight: 600,
            color: config.theme?.textColor,
            margin: '0 0 8px 0',
          }}
        >
          {summary.video_title}
        </h3>

        <p style={{ fontSize: '13px', color: '#666', margin: '0 0 12px 0' }}>
          By {summary.creator_name}
        </p>

        {/* Summary */}
        <div style={{ marginBottom: '12px' }}>
          <h4 style={{ fontSize: '14px', fontWeight: 600, margin: '0 0 8px 0' }}>
            📝 Summary
          </h4>
          <p
            style={{
              fontSize: '14px',
              color: '#444',
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            {summary.summary}
          </p>
        </div>

        {/* Key Points */}
        {summary.key_points.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 600, margin: '0 0 8px 0' }}>
              🎯 Key Points
            </h4>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              {summary.key_points.slice(0, expanded ? undefined : 3).map((point, i) => (
                <li
                  key={i}
                  style={{
                    fontSize: '13px',
                    color: '#444',
                    marginBottom: '4px',
                    lineHeight: 1.5,
                  }}
                >
                  {point}
                </li>
              ))}
            </ul>
            {summary.key_points.length > 3 && (
              <button
                onClick={() => setExpanded(!expanded)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: config.theme?.primaryColor,
                  fontSize: '13px',
                  cursor: 'pointer',
                  padding: '4px 0',
                }}
              >
                {expanded ? 'Show less' : `Show ${summary.key_points.length - 3} more`}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Search Component
export function NewsFeedSearch({
  onSearch,
  placeholder = 'Search news...',
}: {
  onSearch: (query: string) => void;
  placeholder?: string;
}) {
  const [query, setQuery] = useState('');
  const config = React.useContext(NewsFeedContext);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px' }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        style={{
          flex: 1,
          padding: '12px 16px',
          fontSize: '14px',
          border: '2px solid #E1E5E9',
          borderRadius: '8px',
          outline: 'none',
          transition: 'border-color 0.2s',
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = config.theme?.primaryColor || '#6C5CE7';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = '#E1E5E9';
        }}
      />
      <button
        type="submit"
        style={{
          background: config.theme?.primaryColor || '#6C5CE7',
          color: 'white',
          border: 'none',
          padding: '12px 24px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 500,
          cursor: 'pointer',
        }}
      >
        Search
      </button>
    </form>
  );
}

// Category Filter Component
export function CategoryFilter({
  categories,
  selected,
  onChange,
}: {
  categories: string[];
  selected: string | null;
  onChange: (category: string | null) => void;
}) {
  const config = React.useContext(NewsFeedContext);

  return (
    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
      <button
        onClick={() => onChange(null)}
        style={{
          padding: '8px 16px',
          borderRadius: '20px',
          border: 'none',
          fontSize: '13px',
          fontWeight: 500,
          cursor: 'pointer',
          background: selected === null ? config.theme?.primaryColor : '#F1F3F4',
          color: selected === null ? 'white' : '#666',
          transition: 'all 0.2s',
        }}
      >
        All
      </button>
      {categories.map((category) => (
        <button
          key={category}
          onClick={() => onChange(category)}
          style={{
            padding: '8px 16px',
            borderRadius: '20px',
            border: 'none',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            background: selected === category ? config.theme?.primaryColor : '#F1F3F4',
            color: selected === category ? 'white' : '#666',
            transition: 'all 0.2s',
          }}
        >
          {category.charAt(0).toUpperCase() + category.slice(1)}
        </button>
      ))}
    </div>
  );
}

// Styles
const globalStyles = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// Inject global styles
if (typeof document !== 'undefined') {
  const styleTag = document.createElement('style');
  styleTag.innerHTML = globalStyles;
  document.head.appendChild(styleTag);
}
