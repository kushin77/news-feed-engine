/**
 * ElevatedIQ Social Media Platform - Firestore Schema
 * Consolidated database schema for multi-platform social media management
 *
 * Supports: Instagram, Facebook, Twitter, LinkedIn, TikTok, YouTube,
 * Pinterest, Snapchat, Threads
 *
 * Created: November 25, 2025
 */

// Collection: scheduled_posts
// Purpose: Store all scheduled social media posts across platforms
const scheduledPostSchema = {
  // Basic post information
  platform: 'instagram',          // string: instagram|facebook|twitter|linkedin|tiktok|youtube|pinterest|snapchat|threads
  caption: 'Text content...',     // string: Post caption/text/description
  imageUrl: 'https://...',        // string|null: URL to image in Cloud Storage
  videoUrl: null,                 // string|null: URL to video (required for TikTok/YouTube)
  mediaUrl: 'https://...',        // string|null: Generic media URL (image or video)
  mediaType: 'image',             // string: image|video|carousel|link

  // Scheduling information
  scheduledTime: new Date(),      // timestamp: When to publish
  scheduledBy: 'user@email.com',  // string: Who scheduled it
  businessContext: 'PureBliss',   // string: PureBliss|ElevatedIQ|Custom

  // Content metadata
  hashtags: ['813', 'TampaBay'],  // array: List of hashtags (without #)
  mentions: ['@user'],            // array: User mentions
  link: null,                     // string|null: External link (for link posts)
  location: 'Tampa, FL',          // string|null: Geotagging information

  // Post status tracking
  status: 'scheduled',            // string: scheduled|published|failed|cancelled|draft
  createdAt: new Date(),          // timestamp: When scheduled
  publishedAt: null,              // timestamp|null: When actually published
  externalId: null,               // string|null: Platform's post ID after publishing
  externalUrl: null,              // string|null: Direct URL to published post

  // Error handling and retries
  attempts: 0,                    // number: How many publish attempts
  lastAttempt: null,              // timestamp|null: Last publish attempt
  error: null,                    // string|null: Error message if failed
  retryAfter: null,               // timestamp|null: When to retry if rate limited

  // Analytics preview
  initialMetrics: {               // object|null: First metrics collection
    impressions: 0,
    engagement: 0,
    timestamp: null
  }
};

// Collection: social_metrics
// Purpose: Store engagement metrics for published posts
const socialMetricsSchema = {
  postId: 'doc-id',               // string: Reference to scheduled_posts doc
  platform: 'instagram',         // string: Platform name
  externalId: 'platform-id',     // string: Platform's post ID
  collectedAt: new Date(),       // timestamp: When metrics were collected

  // Universal metrics (available on most platforms)
  impressions: 1234,              // number: How many times shown
  reach: 987,                     // number: Unique accounts reached
  engagement: 156,                // number: Total interactions
  likes: 120,                     // number: Likes/reactions count
  comments: 25,                   // number: Comments count
  shares: 8,                      // number: Shares/retweets count
  clicks: 45,                     // number: Link clicks

  // Platform-specific metrics
  saves: 3,                       // number: Saves (Instagram/Pinterest)
  videoViews: 0,                  // number: Video views (TikTok/YouTube/etc)
  videoDuration: null,            // number|null: How long video was watched
  profileVisits: 0,               // number: Profile visits from post
  websiteClicks: 0,               // number: Website link clicks
  emailClicks: 0,                 // number: Email link clicks
  callClicks: 0,                  // number: Call button clicks
  directionsClicks: 0,            // number: Get directions clicks

  // Engagement quality metrics
  engagementRate: 0.015,          // number: engagement / impressions
  saveRate: 0.002,                // number: saves / impressions
  clickThroughRate: 0.035,        // number: clicks / impressions

  // Demographic breakdowns (if available)
  demographics: {                 // object|null: Audience demographics
    ageRanges: {},                // object: age range percentages
    genders: {},                  // object: gender percentages
    locations: {}                 // object: geographic percentages
  }
};

// Collection: platform_credentials
// Purpose: Store OAuth tokens and platform-specific credentials
const platformCredentialsSchema = {
  platform: 'instagram',          // string: Platform name
  credentialType: 'oauth_token',  // string: oauth_token|api_key|webhook_secret
  secretManagerName: 'ig-token',  // string: Secret Manager secret name

  // Token lifecycle
  expiresAt: new Date(),          // timestamp|null: Token expiration
  lastRefreshed: new Date(),      // timestamp: Last token refresh
  refreshToken: 'sm-secret-name', // string|null: Refresh token secret name

  // Platform-specific IDs
  userId: 'platform-user-id',     // string: Platform user ID
  pageId: 'platform-page-id',     // string|null: Business page ID (Facebook/LinkedIn)
  accountId: 'ad-account-id',     // string|null: Advertising account ID

  // Permissions and scope
  scope: ['publish', 'insights'], // array: Granted permissions
  permissions: [],                // array: Detailed permission list

  // Status and validation
  isActive: true,                 // boolean: Whether credentials are valid
  lastValidated: new Date(),      // timestamp: Last validation check
  validationError: null,          // string|null: Last validation error

  // Usage tracking
  dailyApiCalls: 0,               // number: API calls today
  monthlyApiCalls: 0,             // number: API calls this month
  rateLimit: {                    // object: Rate limit info
    remaining: 200,
    resetTime: new Date(),
    maxRequests: 200
  }
};

// Collection: content_templates
// Purpose: Store reusable content templates and AI-generated suggestions
const contentTemplatesSchema = {
  templateName: 'product_launch',  // string: Template identifier
  businessContext: 'PureBliss',   // string: Business context
  platforms: ['instagram', 'facebook'], // array: Supported platforms

  // Content structure
  captionTemplate: 'New {product} now available! {description} {cta}', // string: Template with variables
  hashtagSuggestions: ['New', 'Launch'], // array: Suggested hashtags
  imageSuggestions: ['product-shot', 'lifestyle'], // array: Image style suggestions

  // AI enhancement
  aiPrompt: 'Generate engaging caption for product launch', // string: AI generation prompt
  generatedVariations: [],        // array: AI-generated variations

  // Usage tracking
  timesUsed: 45,                 // number: How often template is used
  avgEngagement: 0.025,          // number: Average engagement rate
  lastUsed: new Date(),          // timestamp: Last time used

  // Template metadata
  createdAt: new Date(),         // timestamp: Template creation
  createdBy: 'user@email.com',   // string: Template creator
  category: 'marketing',         // string: product|event|educational|ugc|marketing
  isActive: true                 // boolean: Whether template is available
};

// Collection: campaign_management
// Purpose: Organize posts into marketing campaigns
const campaignManagementSchema = {
  campaignName: 'Summer Launch 2025', // string: Campaign name
  campaignType: 'product_launch',     // string: product_launch|seasonal|event|ongoing
  description: 'Summer menu launch campaign', // string: Campaign description

  // Campaign timeline
  startDate: new Date(),          // timestamp: Campaign start
  endDate: new Date(),            // timestamp: Campaign end
  status: 'active',               // string: planning|active|paused|completed

  // Target platforms and content
  platforms: ['instagram', 'facebook'], // array: Included platforms
  postIds: ['post-1', 'post-2'],  // array: Associated scheduled_posts IDs
  targetHashtags: ['SummerFresh'], // array: Campaign hashtags

  // Goals and KPIs
  goals: {                        // object: Campaign objectives
    impressions: 50000,
    engagement: 2500,
    websiteClicks: 500,
    conversions: 50
  },

  // Budget and spend (if applicable)
  budget: {                       // object|null: Campaign budget
    total: 1000,
    spent: 450,
    currency: 'USD'
  },

  // Performance tracking
  currentMetrics: {               // object: Real-time performance
    impressions: 32000,
    engagement: 1800,
    websiteClicks: 320,
    conversions: 28,
    updatedAt: new Date()
  },

  // Team and collaboration
  createdBy: 'user@email.com',    // string: Campaign creator
  assignedTo: ['user1@email.com'], // array: Team members
  approvalRequired: false,        // boolean: Whether posts need approval

  // Campaign metadata
  createdAt: new Date(),          // timestamp: Campaign creation
  updatedAt: new Date()           // timestamp: Last update
};

// Collection: user_generated_content
// Purpose: Track and manage user-generated content and hashtag campaigns
const ugcTrackingSchema = {
  platform: 'instagram',          // string: Where UGC was found
  externalId: 'post-id',          // string: Platform post ID
  externalUrl: 'https://...',     // string: Direct URL to post

  // Creator information
  username: '@user',              // string: Creator username
  displayName: 'User Name',       // string: Creator display name
  followerCount: 1500,            // number|null: Creator's followers
  isVerified: false,              // boolean: Creator verification status

  // Content details
  caption: 'User content...',     // string: Post caption
  mediaUrl: 'https://...',        // string: Media URL
  mediaType: 'image',             // string: image|video|carousel
  hashtags: ['PureBlissVibesChallenge'], // array: Hashtags used
  mentions: ['@purebliss'],       // array: Brand mentions

  // Discovery and tracking
  detectedAt: new Date(),         // timestamp: When discovered (webhook/crawl)
  discoveryMethod: 'hashtag',     // string: hashtag|mention|manual|api
  campaignId: 'campaign-123',     // string|null: Associated campaign

  // Engagement and quality
  likes: 150,                     // number: Post likes
  comments: 25,                   // number: Post comments
  shares: 8,                      // number: Post shares
  engagement: 183,                // number: Total engagement
  qualityScore: 0.85,             // number: AI-assessed content quality (0-1)
  brandAlignment: 0.90,           // number: Brand alignment score (0-1)

  // Moderation and approval
  status: 'pending',              // string: pending|approved|rejected|featured|rewarded
  moderatedBy: null,              // string|null: Who reviewed it
  moderatedAt: null,              // timestamp|null: When reviewed
  moderationNotes: null,          // string|null: Moderation notes

  // Rewards and engagement
  rewardSent: false,              // boolean: Whether creator got reward
  rewardType: null,               // string|null: discount|free_product|cash|exposure
  rewardValue: 0,                 // number: Reward monetary value
  rewardSentAt: null,             // timestamp|null: When reward sent

  // Brand response
  featuredPostId: null,           // string|null: If we reposted/featured it
  brandResponseType: null,        // string|null: repost|story_share|comment|dm
  responseAt: null                // timestamp|null: When we responded
};

// Collection: analytics_dashboard
// Purpose: Aggregated analytics for reporting dashboards
const analyticsDashboardSchema = {
  period: 'daily',                // string: hourly|daily|weekly|monthly|quarterly
  periodStart: new Date('2025-10-21'), // date: Start of period
  periodEnd: new Date('2025-10-22'),   // date: End of period

  // Scope
  platforms: ['instagram'],       // array: Included platforms
  campaigns: ['campaign-123'],    // array: Included campaigns (null = all)
  businessContext: 'PureBliss',   // string: Business context filter

  // Posting metrics
  postsScheduled: 5,              // number: Posts scheduled in period
  postsPublished: 3,              // number: Posts successfully published
  postsFailed: 0,                 // number: Posts that failed
  postsInReview: 2,               // number: Posts awaiting approval

  // Engagement metrics
  totalImpressions: 15678,        // number: Total impressions
  totalReach: 12321,              // number: Total reach
  totalEngagement: 1567,          // number: Total engagement
  avgEngagementRate: 0.018,       // number: Average engagement rate
  totalClicks: 234,               // number: Total link clicks
  totalShares: 89,                // number: Total shares

  // Growth metrics
  followerGrowth: 45,             // number: Net follower change
  followerGrowthRate: 0.003,      // number: Growth rate percentage
  profileVisits: 567,             // number: Profile page visits
  websiteTraffic: 234,            // number: Website visits from social

  // Top performers
  topPost: {                      // object|null: Best performing post
    id: 'post-123',
    platform: 'instagram',
    engagement: 456,
    engagementRate: 0.035
  },
  topHashtag: {                   // object|null: Best performing hashtag
    tag: '813',
    usage: 15,
    avgEngagement: 0.025
  },
  topPlatform: {                  // object|null: Best performing platform
    platform: 'instagram',
    postsPublished: 8,
    avgEngagement: 0.022
  },

  // Quality metrics
  avgQualityScore: 0.87,          // number: Average content quality
  avgBrandAlignment: 0.92,        // number: Average brand alignment
  ugcCollected: 12,               // number: UGC pieces collected
  ugcFeatured: 4,                 // number: UGC pieces featured

  // Cost and ROI (if applicable)
  totalSpend: 450.00,             // number: Total campaign spend
  costPerImpression: 0.029,       // number: CPM
  costPerEngagement: 0.287,       // number: Cost per engagement
  estimatedReach: 25000,          // number: Estimated organic reach value

  // Metadata
  generatedAt: new Date(),        // timestamp: When report was generated
  generatedBy: 'analytics-engine', // string: Who/what generated it
  dataVersion: '2.0'              // string: Schema version for migrations
};

// Collection: platform_status
// Purpose: Track platform health, API limits, and service status
const platformStatusSchema = {
  platform: 'instagram',          // string: Platform name

  // API Health
  isHealthy: true,                // boolean: Overall platform health
  lastHealthCheck: new Date(),    // timestamp: Last health check
  healthCheckUrl: 'https://...',  // string: Platform status page URL

  // Rate limiting
  currentRateLimit: {             // object: Current rate limit status
    remaining: 150,
    total: 200,
    resetTime: new Date(),
    period: 'hour'                // string: hour|day|month
  },

  // API performance
  avgResponseTime: 250,           // number: Average API response time (ms)
  successRate: 0.995,             // number: API success rate (0-1)
  errorRate: 0.005,               // number: API error rate (0-1)

  // Recent errors
  recentErrors: [                 // array: Recent API errors
    {
      timestamp: new Date(),
      errorCode: '429',
      errorMessage: 'Rate limit exceeded',
      endpoint: '/media',
      retryAfter: 3600
    }
  ],

  // Maintenance windows
  scheduledMaintenance: null,     // object|null: Upcoming maintenance

  // Feature flags
  featuresEnabled: {              // object: Platform feature availability
    posting: true,
    analytics: true,
    stories: true,
    reels: true,
    livestream: false
  },

  // Monitoring
  lastUpdate: new Date(),         // timestamp: Last status update
  alertsEnabled: true,            // boolean: Whether to send alerts
  alertThresholds: {              // object: Alert trigger thresholds
    errorRate: 0.05,
    responseTime: 5000,
    successRate: 0.90
  }
};

// Export all schemas for use in the application
module.exports = {
  scheduledPostSchema,
  socialMetricsSchema,
  platformCredentialsSchema,
  contentTemplatesSchema,
  campaignManagementSchema,
  ugcTrackingSchema,
  analyticsDashboardSchema,
  platformStatusSchema,

  // Helper functions for schema validation
  validatePost: (post) => {
    const required = ['platform', 'caption', 'scheduledTime'];
    return required.every(field => post[field] !== undefined);
  },

  validatePlatform: (platform) => {
    const supported = ['instagram', 'facebook', 'twitter', 'linkedin', 'tiktok',
                      'youtube', 'pinterest', 'snapchat', 'threads'];
    return supported.includes(platform);
  },

  getSupportedPlatforms: () => {
    return ['instagram', 'facebook', 'twitter', 'linkedin', 'tiktok',
            'youtube', 'pinterest', 'snapchat', 'threads'];
  }
};
