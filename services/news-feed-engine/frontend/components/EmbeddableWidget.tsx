'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';

interface EmbeddableNewsFeedProps {
  apiUrl: string;
  tenantId?: string;
  authToken?: string;
  theme?: {
    primaryColor?: string;
    fontFamily?: string;
    borderRadius?: string;
  };
  layout?: 'grid' | 'list' | 'carousel';
  category?: string;
  limit?: number;
  showSearch?: boolean;
  showFilters?: boolean;
  height?: string;
  width?: string;
}

interface ContentItem {
  id: string;
  title: string;
  summary?: string;
  thumbnail_url?: string;
  source_url: string;
  creator_name: string;
  published_at: string;
  category: string;
  content_type: string;
}

/**
 * Embeddable News Feed Widget
 *
 * This component can be embedded in any website via iframe or directly imported.
 *
 * Usage (iframe):
 * <iframe
 *   src="https://news-feed.elevatediq.com/embed?tenant=your-tenant&theme=dark"
 *   width="100%"
 *   height="600"
 *   frameBorder="0"
 * />
 *
 * Usage (React):
 * import { EmbeddableNewsFeed } from '@elevatediq/news-feed-widget';
 * <EmbeddableNewsFeed
 *   apiUrl="https://api.example.com"
 *   tenantId="your-tenant"
 *   layout="grid"
 * />
 */
export function EmbeddableNewsFeed({
  apiUrl,
  tenantId,
  authToken,
  theme = {},
  layout = 'grid',
  category,
  limit = 12,
  showSearch = true,
  showFilters = true,
  height = '600px',
  width = '100%',
}: EmbeddableNewsFeedProps) {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(category || '');
  const [categories, setCategories] = useState<string[]>([]);
  const carouselRef = useRef<HTMLDivElement>(null);

  const primaryColor = theme.primaryColor || '#6C5CE7';
  const fontFamily = theme.fontFamily || 'system-ui, -apple-system, sans-serif';
  const borderRadius = theme.borderRadius || '8px';

  // Fetch content
  const fetchContent = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: limit.toString(),
        ...(selectedCategory && { category: selectedCategory }),
        ...(searchQuery && { q: searchQuery }),
      });

      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(authToken && { Authorization: `Bearer ${authToken}` }),
        ...(tenantId && { 'X-Tenant-ID': tenantId }),
      };

      const response = await fetch(`${apiUrl}/content?${params}`, { headers });

      if (!response.ok) {
        throw new Error('Failed to fetch content');
      }

      const data = await response.json();
      setContent(data.content || []);

      // Extract unique categories
      const uniqueCategories = [...new Set(data.content.map((c: ContentItem) => c.category))];
      setCategories(uniqueCategories as string[]);

      setError(null);
    } catch (err) {
      setError('Unable to load content');
      console.error('News feed error:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, authToken, tenantId, limit, selectedCategory, searchQuery]);

  useEffect(() => {
    fetchContent();
  }, [fetchContent]);

  // Carousel navigation
  const scrollCarousel = (direction: 'left' | 'right') => {
    if (carouselRef.current) {
      const scrollAmount = 320;
      carouselRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth',
      });
    }
  };

  // Format date
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

  // Handle click
  const handleContentClick = (item: ContentItem) => {
    window.open(item.source_url, '_blank', 'noopener,noreferrer');
  };

  // Render content card
  const renderCard = (item: ContentItem, compact = false) => (
    <div
      key={item.id}
      onClick={() => handleContentClick(item)}
      style={{
        background: '#FFFFFF',
        borderRadius,
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'transform 0.2s, box-shadow 0.2s',
        ...(layout === 'carousel' && {
          minWidth: '300px',
          flexShrink: 0,
        }),
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
      }}
    >
      {item.thumbnail_url && !compact && (
        <img
          src={item.thumbnail_url}
          alt={item.title}
          style={{
            width: '100%',
            height: layout === 'list' ? '120px' : '160px',
            objectFit: 'cover',
          }}
          loading="lazy"
        />
      )}
      <div style={{ padding: compact ? '12px' : '16px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px',
            fontSize: '12px',
            color: '#888',
          }}
        >
          <span>{item.creator_name}</span>
          <span>•</span>
          <span>{formatDate(item.published_at)}</span>
        </div>
        <h3
          style={{
            margin: '0 0 8px 0',
            fontSize: compact ? '14px' : '15px',
            fontWeight: 600,
            lineHeight: 1.4,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {item.title}
        </h3>
        {item.summary && !compact && (
          <p
            style={{
              margin: '0 0 8px 0',
              fontSize: '13px',
              color: '#666',
              lineHeight: 1.5,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {item.summary}
          </p>
        )}
        <span
          style={{
            display: 'inline-block',
            background: `${primaryColor}15`,
            color: primaryColor,
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: 500,
          }}
        >
          {item.category}
        </span>
      </div>
    </div>
  );

  return (
    <div
      style={{
        fontFamily,
        width,
        height,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        background: '#F8F9FA',
        borderRadius,
      }}
    >
      {/* Header */}
      {(showSearch || showFilters) && (
        <div
          style={{
            padding: '16px',
            background: '#FFFFFF',
            borderBottom: '1px solid #E5E7EB',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          {/* Search */}
          {showSearch && (
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                placeholder="Search news..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchContent()}
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  border: '1px solid #E5E7EB',
                  borderRadius,
                  fontSize: '14px',
                  outline: 'none',
                }}
              />
              <button
                onClick={fetchContent}
                style={{
                  padding: '10px 20px',
                  background: primaryColor,
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius,
                  fontSize: '14px',
                  fontWeight: 500,
                  cursor: 'pointer',
                }}
              >
                Search
              </button>
            </div>
          )}

          {/* Category filters */}
          {showFilters && categories.length > 0 && (
            <div
              style={{
                display: 'flex',
                gap: '8px',
                overflowX: 'auto',
                paddingBottom: '4px',
              }}
            >
              <button
                onClick={() => setSelectedCategory('')}
                style={{
                  padding: '6px 14px',
                  borderRadius: '16px',
                  border: 'none',
                  fontSize: '13px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  background: !selectedCategory ? primaryColor : '#F1F3F4',
                  color: !selectedCategory ? '#FFFFFF' : '#666',
                }}
              >
                All
              </button>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '16px',
                    border: 'none',
                    fontSize: '13px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    background: selectedCategory === cat ? primaryColor : '#F1F3F4',
                    color: selectedCategory === cat ? '#FFFFFF' : '#666',
                  }}
                >
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Content area */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px',
        }}
      >
        {loading && (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '200px',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                border: '3px solid #E5E7EB',
                borderTopColor: primaryColor,
                borderRadius: '50%',
                animation: 'nf-spin 1s linear infinite',
              }}
            />
          </div>
        )}

        {error && (
          <div
            style={{
              textAlign: 'center',
              padding: '40px',
              color: '#EF4444',
            }}
          >
            {error}
          </div>
        )}

        {!loading && !error && content.length === 0 && (
          <div
            style={{
              textAlign: 'center',
              padding: '40px',
              color: '#888',
            }}
          >
            No content found
          </div>
        )}

        {!loading && !error && content.length > 0 && (
          <>
            {/* Grid layout */}
            {layout === 'grid' && (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: '16px',
                }}
              >
                {content.map((item) => renderCard(item))}
              </div>
            )}

            {/* List layout */}
            {layout === 'list' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {content.map((item) => (
                  <div
                    key={item.id}
                    style={{ display: 'flex', gap: '16px' }}
                  >
                    {item.thumbnail_url && (
                      <img
                        src={item.thumbnail_url}
                        alt={item.title}
                        style={{
                          width: '120px',
                          height: '80px',
                          objectFit: 'cover',
                          borderRadius,
                          flexShrink: 0,
                        }}
                      />
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      {renderCard(item, true)}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Carousel layout */}
            {layout === 'carousel' && (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={() => scrollCarousel('left')}
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    zIndex: 10,
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    border: 'none',
                    background: '#FFFFFF',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                    cursor: 'pointer',
                    fontSize: '18px',
                  }}
                >
                  ‹
                </button>
                <div
                  ref={carouselRef}
                  style={{
                    display: 'flex',
                    gap: '16px',
                    overflowX: 'auto',
                    scrollbarWidth: 'none',
                    msOverflowStyle: 'none',
                    padding: '4px',
                  }}
                >
                  {content.map((item) => renderCard(item))}
                </div>
                <button
                  onClick={() => scrollCarousel('right')}
                  style={{
                    position: 'absolute',
                    right: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    zIndex: 10,
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    border: 'none',
                    background: '#FFFFFF',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                    cursor: 'pointer',
                    fontSize: '18px',
                  }}
                >
                  ›
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div
        style={{
          padding: '12px 16px',
          background: '#FFFFFF',
          borderTop: '1px solid #E5E7EB',
          textAlign: 'center',
          fontSize: '11px',
          color: '#888',
        }}
      >
        Powered by{' '}
        <a
          href="https://elevatediq.com"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: primaryColor, textDecoration: 'none' }}
        >
          ElevatedIQ
        </a>
      </div>

      {/* Styles */}
      <style>{`
        @keyframes nf-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

/**
 * Embed script for non-React websites
 *
 * Usage:
 * <div id="elevatediq-news-feed"
 *      data-api-url="https://api.example.com"
 *      data-tenant-id="your-tenant"
 *      data-layout="grid">
 * </div>
 * <script src="https://cdn.elevatediq.com/news-feed-widget.js"></script>
 */
export function initEmbedWidget() {
  if (typeof window === 'undefined') return;

  const containers = document.querySelectorAll('[data-elevatediq-news-feed]');

  containers.forEach((container) => {
    const config = {
      apiUrl: container.getAttribute('data-api-url') || '',
      tenantId: container.getAttribute('data-tenant-id') || undefined,
      layout: container.getAttribute('data-layout') as 'grid' | 'list' | 'carousel' || 'grid',
      theme: {
        primaryColor: container.getAttribute('data-primary-color') || undefined,
      },
    };

    // Note: In production, this would use ReactDOM.createRoot to render the component
    console.log('ElevatedIQ News Feed Widget initialized with config:', config);
  });
}

export default EmbeddableNewsFeed;
