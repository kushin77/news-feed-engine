# Platform Integration Template

Use this template to add new social media platforms to the ElevatedIQ Social Media Platform.

## 📁 Required Files

### 1. Platform Module (`platforms/{platform}/index.js`)

```javascript
// platforms/{platform}/index.js
// {Platform Name} Integration for ElevatedIQ Social Media Platform

const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
const { getFirestore } = require('firebase-admin/firestore');

/**
 * {Platform Name} platform integration
 * Implements standard interface for social media posting
 */
class {PlatformName}Platform {
    constructor() {
        this.name = '{platform}';
        this.displayName = '{Platform Name}';
        this.secretManager = new SecretManagerServiceClient();
        this.db = getFirestore();
    }

    /**
     * Get platform-specific credentials from Secret Manager
     * @returns {Object} Platform credentials
     */
    async getCredentials() {
        try {
            // TODO: Replace with actual secret names for your platform
            const [accessTokenSecret] = await this.secretManager.accessSecretVersion({
                name: `projects/${process.env.GOOGLE_CLOUD_PROJECT}/secrets/social-media-{platform}-access_token/versions/latest`
            });
            
            const accessToken = accessTokenSecret.payload.data.toString();
            
            return {
                accessToken,
                // Add other required credentials
            };
        } catch (error) {
            console.error(`Failed to get {platform} credentials:`, error);
            throw new Error(`{Platform Name} credentials not configured`);
        }
    }

    /**
     * Validate post content against platform guidelines
     * @param {Object} post - Post data to validate
     * @returns {Object} Validation result
     */
    validatePost(post) {
        const errors = [];
        const warnings = [];

        // TODO: Implement platform-specific validation rules
        
        // Example validations:
        if (!post.caption) {
            errors.push('Caption is required');
        }
        
        if (post.caption && post.caption.length > 2200) { // Example character limit
            errors.push('Caption exceeds maximum length (2200 characters)');
        }
        
        if (post.imageUrl && !this.isValidImageUrl(post.imageUrl)) {
            errors.push('Invalid image URL format');
        }

        return {
            valid: errors.length === 0,
            errors,
            warnings
        };
    }

    /**
     * Publish content to the platform
     * @param {Object} post - Post data
     * @returns {Object} Publication result
     */
    async publish(post) {
        try {
            console.log(`Publishing to ${this.displayName}:`, { 
                caption: post.caption?.substring(0, 100) + '...',
                hasMedia: !!post.imageUrl 
            });

            // Validate post first
            const validation = this.validatePost(post);
            if (!validation.valid) {
                throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
            }

            // Get credentials
            const credentials = await this.getCredentials();

            // TODO: Implement actual API call to publish content
            // This is where you'll integrate with the platform's API
            
            // Example API call structure:
            const apiResponse = await this.makeApiRequest({
                method: 'POST',
                url: 'https://api.{platform}.com/v1/posts', // Replace with actual API endpoint
                headers: {
                    'Authorization': `Bearer ${credentials.accessToken}`,
                    'Content-Type': 'application/json'
                },
                data: {
                    caption: post.caption,
                    image_url: post.imageUrl,
                    // Add other platform-specific fields
                }
            });

            // Store metrics in Firestore
            await this.recordMetrics(post, apiResponse);

            return {
                success: true,
                platform: this.name,
                postId: apiResponse.id, // Platform's post ID
                url: apiResponse.permalink_url || null, // Public URL if available
                publishedAt: new Date().toISOString(),
                metrics: {
                    reach: 0, // Will be updated later
                    engagement: 0,
                    impressions: 0
                }
            };

        } catch (error) {
            console.error(`${this.displayName} publishing error:`, error);
            
            // Store error metrics
            await this.recordError(post, error);
            
            return {
                success: false,
                platform: this.name,
                error: error.message,
                publishedAt: new Date().toISOString()
            };
        }
    }

    /**
     * Get analytics data for posts
     * @param {Object} options - Analytics options
     * @returns {Object} Analytics data
     */
    async getAnalytics(options = {}) {
        try {
            const credentials = await this.getCredentials();
            
            // TODO: Implement analytics API calls
            // Most platforms provide insights/analytics APIs
            
            const analyticsData = await this.makeApiRequest({
                method: 'GET',
                url: 'https://api.{platform}.com/v1/insights', // Replace with actual endpoint
                headers: {
                    'Authorization': `Bearer ${credentials.accessToken}`
                },
                params: {
                    since: options.startDate,
                    until: options.endDate,
                    // Add platform-specific parameters
                }
            });

            return {
                platform: this.name,
                period: {
                    startDate: options.startDate,
                    endDate: options.endDate
                },
                metrics: {
                    totalPosts: analyticsData.total_posts || 0,
                    totalReach: analyticsData.total_reach || 0,
                    totalEngagement: analyticsData.total_engagement || 0,
                    totalImpressions: analyticsData.total_impressions || 0
                },
                posts: analyticsData.posts || []
            };

        } catch (error) {
            console.error(`${this.displayName} analytics error:`, error);
            return {
                platform: this.name,
                error: error.message,
                metrics: null
            };
        }
    }

    /**
     * Get platform-specific posting guidelines
     * @returns {Object} Guidelines and best practices
     */
    getGuidelines() {
        return {
            platform: this.name,
            displayName: this.displayName,
            
            // Content guidelines
            content: {
                maxCaptionLength: 2200, // Replace with actual limits
                supportedFormats: ['jpg', 'jpeg', 'png', 'gif'], // Replace with actual formats
                aspectRatios: ['1:1', '4:5', '16:9'], // Replace with supported ratios
                maxFileSize: '10MB', // Replace with actual limit
                videoLength: '60s' // If video is supported
            },
            
            // Hashtag guidelines
            hashtags: {
                maxCount: 30, // Replace with actual limit
                placement: 'caption', // or 'comment'
                recommendations: [
                    'Use relevant hashtags for better reach',
                    'Mix popular and niche hashtags',
                    'Avoid banned or shadowbanned hashtags'
                ]
            },
            
            // Posting best practices
            bestPractices: [
                'Post during peak engagement hours',
                'Include a clear call-to-action',
                'Use high-quality visuals',
                'Engage with comments promptly',
                'Maintain consistent posting schedule'
            ],
            
            // API limitations
            limitations: {
                postsPerHour: 60, // Replace with actual rate limits
                postsPerDay: 1000,
                apiCallsPerHour: 3600
            }
        };
    }

    /**
     * Helper method to make HTTP requests to platform API
     */
    async makeApiRequest(options) {
        // TODO: Implement HTTP request logic
        // You can use libraries like axios, node-fetch, or built-in fetch
        
        // Example implementation:
        const response = await fetch(options.url, {
            method: options.method || 'GET',
            headers: options.headers || {},
            body: options.data ? JSON.stringify(options.data) : undefined
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    }

    /**
     * Helper method to validate image URLs
     */
    isValidImageUrl(url) {
        try {
            new URL(url);
            return /\\.(jpg|jpeg|png|gif|webp)$/i.test(url);
        } catch {
            return false;
        }
    }

    /**
     * Record successful posting metrics
     */
    async recordMetrics(post, apiResponse) {
        try {
            await this.db.collection('social_metrics').add({
                platform: this.name,
                postId: apiResponse.id,
                caption: post.caption?.substring(0, 100), // Store truncated caption
                publishedAt: new Date(),
                initialMetrics: {
                    likes: 0,
                    comments: 0,
                    shares: 0,
                    reach: 0,
                    impressions: 0
                },
                status: 'published'
            });
        } catch (error) {
            console.error('Failed to record metrics:', error);
        }
    }

    /**
     * Record publishing errors
     */
    async recordError(post, error) {
        try {
            await this.db.collection('social_metrics').add({
                platform: this.name,
                caption: post.caption?.substring(0, 100),
                publishedAt: new Date(),
                status: 'failed',
                error: error.message
            });
        } catch (recordError) {
            console.error('Failed to record error:', recordError);
        }
    }
}

module.exports = {
    {PlatformName}Platform,
    publish: async (post) => {
        const platform = new {PlatformName}Platform();
        return platform.publish(post);
    },
    validatePost: (post) => {
        const platform = new {PlatformName}Platform();
        return platform.validatePost(post);
    },
    getGuidelines: () => {
        const platform = new {PlatformName}Platform();
        return platform.getGuidelines();
    },
    getAnalytics: async (options) => {
        const platform = new {PlatformName}Platform();
        return platform.getAnalytics(options);
    }
};
```bash

### 2. Platform Documentation (`docs/platforms/{platform}.md`)

```markdown
# {Platform Name} Integration

Integration guide for {Platform Name} social media platform.

## 📋 Overview

- **Platform:** {Platform Name}
- **API Version:** {API Version}
- **Documentation:** {Official API Docs URL}
- **Developer Portal:** {Developer Portal URL}

## 🔧 Setup Requirements

### API Credentials

1. **Access Token:** OAuth 2.0 access token with posting permissions
2. **App ID:** Application identifier (if required)
3. **App Secret:** Application secret key (if required)

### Required Permissions

- `{permission_1}`: Description
- `{permission_2}`: Description  
- `{permission_3}`: Description

## 🚀 Getting Started

### 1. Create Developer Account

1. Visit [{Platform Name} Developer Portal]({Developer Portal URL})
2. Create or login to your developer account
3. Create a new application

### 2. Configure Application

1. Set application type to "Web Application"
2. Add redirect URIs for OAuth flow
3. Configure required permissions
4. Note down App ID and App Secret

### 3. Generate Access Token

```bash
# Example OAuth flow (replace with actual URLs)
<https://api.{platform}.com/oauth/authorize?>
  client_id=YOUR_APP_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  scope={required_scopes}&
  response_type=code

# Exchange code for access token
curl -X POST <https://api.{platform}.com/oauth/access_token> \\
  -d client_id=YOUR_APP_ID \\
  -d client_secret=YOUR_APP_SECRET \\
  -d code=AUTHORIZATION_CODE \\
  -d redirect_uri=YOUR_REDIRECT_URI
```bash

### 4. Add to Secret Manager

```bash
# Add credentials to Google Secret Manager
./scripts/config/config.sh add {platform} access_token --interactive
./scripts/config/config.sh add {platform} app_id --interactive
./scripts/config/config.sh add {platform} app_secret --interactive
```bash

## 📐 Content Guidelines

### Image Requirements

- **Formats:** JPG, PNG, GIF
- **Size:** Max 10MB
- **Dimensions:** 1080x1080 (recommended)
- **Aspect Ratios:** 1:1, 4:5, 16:9

### Text Requirements  

- **Caption Length:** Max 2,200 characters
- **Hashtags:** Max 30 per post
- **Mentions:** Max 20 per post

### Video Requirements (if supported)

- **Formats:** MP4, MOV
- **Length:** 3 seconds - 60 seconds
- **Size:** Max 100MB
- **Resolution:** 720p minimum

## 🔄 API Endpoints

### Publishing

```

POST <https://api.{platform}.com/v1/posts>

```bash

### Analytics

```

GET <https://api.{platform}.com/v1/insights>

```bash

### Media Upload

```

POST <https://api.{platform}.com/v1/media>

```bash

## 📊 Available Metrics

- **Reach:** Number of unique users who saw the post
- **Impressions:** Total number of times the post was displayed
- **Engagement:** Likes, comments, shares combined
- **Click-through Rate:** Percentage of users who clicked links
- **Save Rate:** Percentage of users who saved the post

## ⚠️ Rate Limits

- **Posts per hour:** 60
- **Posts per day:** 1,000  
- **API calls per hour:** 3,600
- **Media uploads per hour:** 100

## 🐛 Common Issues

### Authentication Errors

- Verify access token is still valid
- Check required permissions are granted
- Ensure app is approved for production use

### Publishing Errors

- Validate content meets platform guidelines
- Check image format and size requirements
- Verify rate limits haven't been exceeded

### Analytics Issues

- Ensure insights permissions are granted
- Check date range is valid
- Verify post IDs exist and are accessible

## 📚 Additional Resources

- [Official API Documentation]({API Docs URL})
- [Developer Community]({Community URL})
- [Best Practices Guide]({Best Practices URL})
- [Troubleshooting Guide]({Troubleshooting URL})

```bash

### 3. Test Cases (`test/platforms/{platform}.test.js`)

```javascript
// test/platforms/{platform}.test.js
const assert = require('assert');
const { {PlatformName}Platform } = require('../../platforms/{platform}/index.js');

describe('{Platform Name} Platform Integration', () => {
    let platform;

    beforeEach(() => {
        platform = new {PlatformName}Platform();
    });

    describe('Post Validation', () => {
        it('should validate required caption', () => {
            const post = { imageUrl: 'https://example.com/image.jpg' };
            const result = platform.validatePost(post);
            
            assert.strictEqual(result.valid, false);
            assert(result.errors.includes('Caption is required'));
        });

        it('should validate caption length', () => {
            const longCaption = 'a'.repeat(2201); // Exceeds limit
            const post = { 
                caption: longCaption,
                imageUrl: 'https://example.com/image.jpg' 
            };
            const result = platform.validatePost(post);
            
            assert.strictEqual(result.valid, false);
            assert(result.errors.some(error => 
                error.includes('Caption exceeds maximum length')
            ));
        });

        it('should validate image URL format', () => {
            const post = { 
                caption: 'Test post',
                imageUrl: 'not-a-valid-url' 
            };
            const result = platform.validatePost(post);
            
            assert.strictEqual(result.valid, false);
            assert(result.errors.includes('Invalid image URL format'));
        });

        it('should pass validation for valid post', () => {
            const post = { 
                caption: 'Valid test post',
                imageUrl: 'https://example.com/image.jpg' 
            };
            const result = platform.validatePost(post);
            
            assert.strictEqual(result.valid, true);
            assert.strictEqual(result.errors.length, 0);
        });
    });

    describe('Guidelines', () => {
        it('should return platform guidelines', () => {
            const guidelines = platform.getGuidelines();
            
            assert.strictEqual(guidelines.platform, '{platform}');
            assert.strictEqual(guidelines.displayName, '{Platform Name}');
            assert(guidelines.content);
            assert(guidelines.hashtags);
            assert(guidelines.bestPractices);
            assert(guidelines.limitations);
        });

        it('should include content requirements', () => {
            const guidelines = platform.getGuidelines();
            
            assert(typeof guidelines.content.maxCaptionLength === 'number');
            assert(Array.isArray(guidelines.content.supportedFormats));
            assert(Array.isArray(guidelines.content.aspectRatios));
        });
    });

    describe('URL Validation', () => {
        it('should validate correct image URLs', () => {
            const validUrls = [
                'https://example.com/image.jpg',
                'https://example.com/image.jpeg', 
                'https://example.com/image.png',
                'https://example.com/image.gif'
            ];

            validUrls.forEach(url => {
                assert(platform.isValidImageUrl(url), `Should validate: ${url}`);
            });
        });

        it('should reject invalid URLs', () => {
            const invalidUrls = [
                'not-a-url',
                'https://example.com/document.pdf',
                'ftp://example.com/image.jpg',
                ''
            ];

            invalidUrls.forEach(url => {
                assert(!platform.isValidImageUrl(url), `Should reject: ${url}`);
            });
        });
    });
});
```bash

## 🔧 Integration Steps

### 1. Copy Template Files

```bash
# Create platform directory
mkdir -p platforms/{platform}

# Copy and customize template
cp docs/templates/platform-template.js platforms/{platform}/index.js
```bash

### 2. Replace Template Variables

Replace all template variables in the copied files:

- `{platform}` → Platform identifier (lowercase, e.g., 'instagram')
- `{Platform Name}` → Display name (e.g., 'Instagram')
- `{PlatformName}` → Class name (e.g., 'Instagram')
- `{API Version}` → API version (e.g., 'v18.0')
- `{Official API Docs URL}` → Link to official documentation

### 3. Implement Platform-Specific Logic

- **API Integration:** Implement actual API calls in `makeApiRequest()`
- **Validation Rules:** Add platform-specific content validation
- **Analytics:** Implement metrics collection and analytics
- **Error Handling:** Add platform-specific error handling

### 4. Update Main Platform Registry

Add your platform to the main registry in `functions/index.js`:

```javascript
// Add to platform registry
const platforms = {
    // ... existing platforms
    {platform}: require('./platforms/{platform}/index.js')
};
```bash

### 5. Add Configuration Support

Update configuration scripts to include your platform:

```bash
# Add platform to config scripts
# Edit scripts/config/config.sh and scripts/config/config.ps1
```bash

### 6. Test Integration

```bash
# Run platform-specific tests
npm test -- --grep "{Platform Name}"

# Test configuration
./scripts/config/config.sh validate

# Test deployment
./scripts/deployment/deploy.sh
```bash

## 📋 Checklist

Before submitting your platform integration:

- [ ] ✅ Platform module implements all required methods
- [ ] 🧪 All test cases pass
- [ ] 📚 Documentation is complete and accurate  
- [ ] 🔐 Credentials are properly configured in Secret Manager
- [ ] ✅ Validation handles all edge cases
- [ ] 📊 Analytics integration works correctly
- [ ] 🚨 Error handling is comprehensive
- [ ] 🔄 Rate limiting is implemented
- [ ] 📐 Content guidelines are enforced
- [ ] 🎯 Code follows project coding standards

## 🆘 Getting Help

- **Documentation:** Review existing platform integrations in `platforms/` directory
- **Issues:** Create issue at <https://github.com/kushin77/elevatedIQ/issues>
- **Discussions:** Join community discussions for integration questions
- **Code Review:** Submit pull request for review and feedback

---

**Ready to integrate your platform?** Follow this template and join the ElevatedIQ ecosystem! 🚀
