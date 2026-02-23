# Contributing to ElevatedIQ Social Media Platform

Welcome to the ElevatedIQ Social Media Platform! We're excited to have you contribute to making social media management more accessible and powerful. This guide will help you understand our contribution process and standards.

## 🌟 Ways to Contribute

### 🐛 Bug Fixes

- Fix issues in existing platform integrations
- Resolve performance or security vulnerabilities
- Improve error handling and user experience

### ✨ New Features  

- Add support for new social media platforms
- Enhance existing platform capabilities
- Improve analytics and reporting features
- Add new deployment and configuration options

### 📚 Documentation

- Improve setup and deployment guides
- Add platform-specific tutorials
- Create troubleshooting resources
- Translate documentation to other languages

### 🧪 Testing

- Add unit tests for platform integrations
- Create integration test scenarios
- Improve test coverage and reliability
- Performance and load testing

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Node.js 20+** installed
- **Google Cloud SDK** configured
- **Git** for version control
- **Basic knowledge** of JavaScript, Cloud Functions, and social media APIs

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/elevatediq-ai.git
   cd elevatediq-ai/social-media-platform

```bash

2. **Install Dependencies**

   ```bash
   npm install
```bash

3. **Setup Development Environment**

   ```bash
   # Linux/Mac
   ./scripts/setup/setup.sh --project-id YOUR_DEV_PROJECT --development
   
   # Windows
   .\scripts\setup\setup.ps1 -ProjectId YOUR_DEV_PROJECT -Development
```bash

4. **Configure Test Credentials**

   ```bash
   # Use development/test accounts only
   ./scripts/config/config.sh interactive
```bash

5. **Run Tests**

   ```bash
   npm test
   npm run test:integration
```bash

## 📝 Contribution Guidelines

### Code Standards

#### **JavaScript Style Guide**

We follow modern ES6+ JavaScript standards:

```javascript
// ✅ Good: Use const/let, arrow functions, async/await
const publishPost = async (post) => {
    try {
        const result = await platform.publish(post);
        return { success: true, ...result };
    } catch (error) {
        console.error('Publishing failed:', error);
        return { success: false, error: error.message };
    }
};

// ❌ Avoid: var, callbacks, function declarations in blocks
var publishPost = function(post, callback) {
    platform.publish(post, function(error, result) {
        if (error) {
            callback(error);
        } else {
            callback(null, result);
        }
    });
};
```bash

#### **Error Handling Standards**

```javascript
// ✅ Comprehensive error handling
async function publishToInstagram(post) {
    try {
        // Validate input
        if (!post || !post.caption) {
            throw new Error('Post caption is required');
        }
        
        // Get credentials
        const credentials = await getCredentials('instagram');
        if (!credentials) {
            throw new Error('Instagram credentials not configured');
        }
        
        // Make API call
        const response = await makeInstagramAPICall(post, credentials);
        
        // Log success
        console.log('Instagram post published:', { 
            postId: response.id, 
            timestamp: new Date().toISOString() 
        });
        
        return {
            success: true,
            platform: 'instagram',
            externalId: response.id,
            url: response.permalink
        };
        
    } catch (error) {
        // Log error with context
        console.error('Instagram publishing failed:', {
            error: error.message,
            post: { caption: post.caption?.substring(0, 50) + '...' },
            timestamp: new Date().toISOString()
        });
        
        // Return standardized error response
        return {
            success: false,
            platform: 'instagram',
            error: error.message
        };
    }
}
```bash

#### **Documentation Standards**

```javascript
/**
 * Publish content to Instagram using Graph API
 * @param {Object} post - Post data
 * @param {string} post.caption - Post caption (required)
 * @param {string} post.imageUrl - Image URL (required)
 * @param {string[]} [post.hashtags] - Array of hashtags (optional)
 * @param {Object} core - Core utilities instance
 * @returns {Promise<Object>} Publication result
 * @throws {Error} When credentials are missing or API call fails
 * 
 * @example
 * const result = await publishToInstagram({
 *   caption: 'Hello Instagram!',
 *   imageUrl: 'https://example.com/image.jpg',
 *   hashtags: ['hello', 'instagram']
 * }, coreUtils);
 */
async function publishToInstagram(post, core) {
    // Implementation...
}
```bash

### Testing Requirements

#### **Unit Tests**

Every new function must have unit tests:

```javascript
// test/platforms/instagram.test.js
const { publishToInstagram } = require('../../platforms/instagram');

describe('Instagram Platform', () => {
    describe('publishToInstagram', () => {
        it('should publish post successfully', async () => {
            const mockPost = {
                caption: 'Test post',
                imageUrl: 'https://example.com/test.jpg'
            };
            
            const result = await publishToInstagram(mockPost, mockCore);
            
            expect(result.success).toBe(true);
            expect(result.platform).toBe('instagram');
            expect(result.externalId).toBeDefined();
        });
        
        it('should handle missing caption error', async () => {
            const invalidPost = { imageUrl: 'https://example.com/test.jpg' };
            
            const result = await publishToInstagram(invalidPost, mockCore);
            
            expect(result.success).toBe(false);
            expect(result.error).toContain('caption is required');
        });
    });
});
```bash

#### **Integration Tests**

Platform integrations require integration tests:

```javascript
// test/integration/instagram.integration.test.js
describe('Instagram Integration', () => {
    it('should publish to real Instagram API', async () => {
        // Use test credentials
        const testPost = {
            caption: 'Integration test post #elevatediq #testing',
            imageUrl: 'https://picsum.photos/1080/1080'
        };
        
        const result = await publishToInstagram(testPost, testCore);
        
        expect(result.success).toBe(true);
        expect(result.externalId).toMatch(/^\d+$/); // Instagram post ID pattern
        
        // Clean up - delete the test post
        await deleteInstagramPost(result.externalId);
    });
});
```bash

#### **Test Coverage Requirements**

- **Unit Tests:** Minimum 90% coverage for new code
- **Integration Tests:** Cover all critical API paths
- **Error Scenarios:** Test all error conditions
- **Platform Guidelines:** Validate against platform requirements

### Platform Integration Requirements

#### **Required Implementation**

When adding a new platform, you must implement:

1. **Platform Class** following the standard interface
2. **Validation Logic** for platform-specific content rules
3. **Error Handling** for all API error scenarios
4. **Rate Limiting** to respect platform API limits
5. **Analytics Collection** for performance metrics
6. **Documentation** with setup and usage instructions
7. **Tests** covering all functionality

#### **Platform Class Template**

```javascript
// platforms/newplatform/index.js
class NewPlatformPublisher {
    constructor() {
        this.name = 'newplatform';
        this.displayName = 'New Platform';
        this.rateLimiter = new RateLimiter(100, 'hour'); // Adjust limits
    }
    
    /**
     * Publish content to the platform
     * @param {Object} post - Post content and metadata
     * @param {Object} core - Core utilities (logging, secrets, etc.)
     * @returns {Promise<Object>} Publication result
     */
    async publish(post, core) {
        // Implementation required
    }
    
    /**
     * Validate post content against platform rules
     * @param {Object} post - Post to validate
     * @returns {Object} Validation result with errors/warnings
     */
    validatePost(post) {
        // Implementation required
    }
    
    /**
     * Get platform posting guidelines
     * @returns {Object} Platform requirements and best practices
     */
    getGuidelines() {
        // Implementation required
    }
}

// Export standard interface
module.exports = {
    NewPlatformPublisher,
    publish: async (post, core) => {
        const platform = new NewPlatformPublisher();
        return platform.publish(post, core);
    },
    validatePost: (post) => {
        const platform = new NewPlatformPublisher();
        return platform.validatePost(post);
    },
    getGuidelines: () => {
        const platform = new NewPlatformPublisher();
        return platform.getGuidelines();
    }
};
```bash

## 🔄 Development Workflow

### Branch Strategy

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/add-tiktok-video-support
   # or
   git checkout -b fix/instagram-rate-limiting
   # or  
   git checkout -b docs/improve-setup-guide
```bash

2. **Make Changes**
   - Follow code standards
   - Add tests for new functionality
   - Update documentation as needed
   - Test locally and run full test suite

3. **Commit Changes**

   ```bash
   # Use conventional commit format
   git commit -m "feat(tiktok): add video upload support
   
   - Implement video validation for TikTok format requirements
   - Add multipart form upload for video files
   - Include video duration and resolution validation
   - Add integration tests for video posting
   
   Closes #123"
```bash

4. **Push and Create PR**

   ```bash
   git push origin feature/add-tiktok-video-support
```bash

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```

type(scope): short description

Longer description explaining the change in detail.
Include motivation, context, and impact.

- List key changes
- Include breaking changes
- Reference issue numbers

Closes #123

```bash

## Types

- `feat`: New features
- `fix`: Bug fixes  
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## Scopes

- `instagram`, `facebook`, `twitter`, etc. for platform-specific changes
- `core` for main function logic
- `config` for configuration changes
- `deploy` for deployment scripts
- `docs` for documentation

### Pull Request Process

#### **PR Template**

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Platform Impact
- [ ] Instagram
- [ ] Facebook  
- [ ] Twitter
- [ ] LinkedIn
- [ ] TikTok
- [ ] YouTube
- [ ] Pinterest
- [ ] Snapchat
- [ ] Threads

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Test coverage maintained/improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings or errors introduced

## Screenshots/Logs
Include relevant screenshots or log outputs if applicable.
```bash

#### **Review Process**

1. **Automated Checks**
   - Code style validation (ESLint)
   - Unit test execution
   - Integration test execution
   - Security scanning
   - Test coverage analysis

2. **Manual Review**
   - Code quality and standards compliance
   - Architecture and design review
   - Security considerations
   - Documentation completeness

3. **Approval Requirements**
   - At least 1 maintainer approval
   - All automated checks passing
   - Conflicts resolved
   - Documentation updated

## 🔒 Security Guidelines

### Credential Management

#### **Never commit secrets**

```bash
# ❌ Never do this
const apiKey = 'sk-1234567890abcdef';

# ✅ Use environment variables or Secret Manager
const apiKey = process.env.PLATFORM_API_KEY;
const apiKey = await getSecret('platform-api-key');
```bash

#### **Use test credentials only**

- Create separate test/development accounts for each platform
- Use limited-permission API keys when possible
- Rotate test credentials regularly
- Never use production credentials in development

#### **Validate input data**

```javascript
// ✅ Validate and sanitize all inputs
function validatePost(post) {
    if (!post || typeof post !== 'object') {
        throw new Error('Invalid post data');
    }
    
    // Sanitize caption
    if (post.caption) {
        post.caption = post.caption.trim().substring(0, MAX_CAPTION_LENGTH);
    }
    
    // Validate image URL
    if (post.imageUrl && !isValidUrl(post.imageUrl)) {
        throw new Error('Invalid image URL');
    }
    
    return post;
}
```bash

### Platform API Security

#### **OAuth Token Management**

```javascript
// ✅ Proper token management
class TokenManager {
    async getValidToken(platform) {
        const token = await this.getStoredToken(platform);
        
        // Check expiration
        if (this.isTokenExpired(token)) {
            return this.refreshToken(platform);
        }
        
        return token;
    }
    
    async refreshToken(platform) {
        // Implement token refresh logic
        // Store new token securely
        // Log token refresh event
    }
}
```bash

#### **Rate Limiting**

```javascript
// ✅ Implement rate limiting
class RateLimiter {
    constructor(limit, window) {
        this.limit = limit;
        this.window = window;
        this.requests = new Map();
    }
    
    async checkLimit(platform) {
        const key = `${platform}-${Date.now()}`;
        const windowStart = Date.now() - this.window;
        
        // Clean old requests
        this.cleanOldRequests(windowStart);
        
        // Check current count
        const currentCount = this.getCurrentRequestCount(platform);
        if (currentCount >= this.limit) {
            throw new Error(`Rate limit exceeded for ${platform}`);
        }
        
        // Record request
        this.recordRequest(platform);
    }
}
```bash

## 🧪 Testing Guidelines

### Local Testing Setup

#### **Test Environment**

```bash
# Setup isolated test environment
export NODE_ENV=test
export GOOGLE_CLOUD_PROJECT=elevatediq-test

# Use test database
export FIRESTORE_EMULATOR_HOST=localhost:8080

# Install test dependencies
npm install --include=dev
```bash

#### **Mock External APIs**

```javascript
// test/mocks/instagram-api.js
class MockInstagramAPI {
    static mockResponses = {
        success: { id: 'test_post_123', permalink: 'https://instagram.com/p/test' },
        rateLimitError: { error: { code: 4, message: 'Application request limit reached' } },
        authError: { error: { code: 190, message: 'Invalid OAuth access token' } }
    };
    
    static setMockResponse(type) {
        // Configure mock behavior
    }
}
```bash

#### **Test Data Management**

```javascript
// test/fixtures/test-posts.js
export const validPosts = {
    instagram: {
        caption: 'Test Instagram post #testing',
        imageUrl: 'https://picsum.photos/1080/1080',
        hashtags: ['testing', 'elevatediq']
    },
    
    twitter: {
        caption: 'Test Twitter post #testing',
        imageUrl: 'https://picsum.photos/1200/675'
    }
};

export const invalidPosts = {
    tooLong: {
        caption: 'a'.repeat(10000), // Exceeds all platform limits
        imageUrl: 'https://picsum.photos/1080/1080'
    },
    
    noImage: {
        caption: 'Post without image',
        imageUrl: null
    }
};
```bash

### Performance Testing

#### **Load Testing**

```javascript
// test/performance/load-test.js
describe('Platform Load Tests', () => {
    it('should handle concurrent posts', async () => {
        const posts = Array(50).fill().map(() => generateTestPost());
        const startTime = Date.now();
        
        const results = await Promise.all(
            posts.map(post => publishToInstagram(post, mockCore))
        );
        
        const duration = Date.now() - startTime;
        const successRate = results.filter(r => r.success).length / results.length;
        
        expect(successRate).toBeGreaterThan(0.95); // 95% success rate
        expect(duration).toBeLessThan(30000); // Under 30 seconds
    });
});
```bash

## 📚 Documentation Standards

### Code Documentation

#### **Function Documentation**

```javascript
/**
 * Retrieves analytics data for a specific platform and time period
 * 
 * @async
 * @function getAnalytics
 * @param {string} platform - Platform identifier (instagram, facebook, etc.)
 * @param {Object} options - Analytics options
 * @param {string} options.startDate - Start date in ISO format
 * @param {string} options.endDate - End date in ISO format  
 * @param {string[]} [options.metrics] - Specific metrics to retrieve
 * @param {string} [options.granularity='day'] - Data granularity (hour, day, week)
 * @returns {Promise<Object>} Analytics data object
 * @throws {Error} When platform is not supported or date range is invalid
 * 
 * @example
 * // Get Instagram analytics for last 30 days
 * const analytics = await getAnalytics('instagram', {
 *   startDate: '2024-10-25T00:00:00Z',
 *   endDate: '2024-11-25T00:00:00Z',
 *   metrics: ['reach', 'engagement', 'impressions']
 * });
 * 
 * @example
 * // Get all available metrics with hourly granularity
 * const detailedAnalytics = await getAnalytics('twitter', {
 *   startDate: '2024-11-24T00:00:00Z',
 *   endDate: '2024-11-25T00:00:00Z',
 *   granularity: 'hour'
 * });
 */
```bash

#### **README Structure**

Each platform integration should include:

```markdown
# Platform Name Integration

## Overview
Brief description of the platform and integration capabilities.

## Setup
Step-by-step setup instructions including:
- Developer account creation
- App registration
- API key generation
- Credential configuration

## Features
- [x] Text posts
- [x] Image posts  
- [x] Video posts (if supported)
- [x] Scheduling
- [x] Analytics
- [ ] Stories (if applicable)

## API Limits
- Posts per hour: X
- Posts per day: Y
- API calls per hour: Z

## Content Guidelines
- Maximum caption length: X characters
- Supported image formats: JPG, PNG, GIF
- Maximum file size: X MB
- Recommended aspect ratios: 1:1, 4:5, 16:9

## Examples
Code examples for common use cases.

## Troubleshooting
Common issues and solutions.

## References
Links to official documentation and resources.
```bash

## 🎯 Performance Standards

### Response Time Requirements

- **API Endpoints:** < 500ms average response time
- **Publishing Functions:** < 5 seconds per post
- **Analytics Queries:** < 2 seconds for standard timeframes
- **Batch Operations:** < 30 seconds for up to 50 items

### Resource Efficiency

- **Memory Usage:** Cloud Functions should use < 512MB for typical operations
- **Database Queries:** Minimize Firestore reads/writes
- **API Calls:** Batch operations when possible
- **Caching:** Implement appropriate caching strategies

### Scalability Targets

- **Concurrent Users:** Support 1000+ simultaneous users
- **Daily Posts:** Handle 100,000+ posts per day
- **Platform APIs:** Respect and optimize for rate limits
- **Error Rate:** Maintain < 1% error rate under normal conditions

## 🚨 Troubleshooting Contributions

### Common Issues

#### **Setup Problems**

```bash
# Permission errors
chmod +x scripts/setup/setup.sh

# Node version issues  
nvm use 20

# gcloud authentication
gcloud auth login
gcloud config set project YOUR_PROJECT
```bash

#### **Test Failures**

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Run tests with verbose output
npm test -- --verbose

# Run specific test file
npm test -- platforms/instagram.test.js
```bash

#### **Platform API Issues**

- Verify credentials are correctly configured
- Check API rate limits and quotas
- Validate request format against platform documentation
- Use platform API explorers for testing

### Getting Help

1. **Documentation:** Check existing documentation first
2. **Issues:** Search existing GitHub issues
3. **Discussions:** Use GitHub Discussions for questions  
4. **Community:** Join our Discord/Slack community
5. **Maintainers:** Tag maintainers for urgent issues

### Issue Templates

#### **Bug Report**

```markdown
## Bug Description
Clear description of the issue.

## Steps to Reproduce
1. Step one
2. Step two  
3. Step three

## Expected Behavior
What should have happened.

## Actual Behavior
What actually happened.

## Environment
- Node.js version:
- Platform: 
- Operating System:

## Additional Context
Screenshots, logs, or other relevant information.
```bash

#### **Feature Request**

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've considered.

## Additional Context
Any other relevant information.
```bash

## 🏆 Recognition

### Contributor Levels

#### **First-time Contributors**

- Welcome package and mentorship
- Simple good-first-issues to start with
- Recognition in release notes

#### **Regular Contributors**

- Direct collaborator access
- Ability to review PRs
- Recognition in project README

#### **Core Contributors**

- Maintainer privileges
- Architectural decision participation
- Speaker opportunities at events

### Contribution Rewards

- **GitHub Achievements:** Contribution badges and stats
- **Project Recognition:** Listed in contributors section
- **Community Recognition:** Featured in blog posts and newsletters
- **Learning Opportunities:** Early access to new features and APIs
- **Networking:** Connect with other contributors and maintainers

## 📋 Contribution Checklist

Before submitting your contribution:

### Code Quality

- [ ] Follows JavaScript style guide
- [ ] Includes comprehensive error handling
- [ ] Has proper JSDoc documentation
- [ ] Passes all linting checks
- [ ] No hardcoded secrets or credentials

### Testing

- [ ] Unit tests written and passing
- [ ] Integration tests for new platforms
- [ ] Manual testing completed
- [ ] Test coverage maintained (>90%)
- [ ] Performance tests for critical paths

### Documentation

- [ ] README updated for new features
- [ ] API documentation updated
- [ ] Platform-specific guides created
- [ ] Examples and tutorials included
- [ ] Troubleshooting section updated

### Security

- [ ] Security review completed
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Rate limiting considered
- [ ] OAuth best practices followed

### Platform Integration (if applicable)

- [ ] Platform class implements standard interface
- [ ] Validation rules implemented
- [ ] Rate limiting implemented
- [ ] Analytics collection included
- [ ] Platform guidelines documented
- [ ] Configuration scripts updated

---

## 🎉 Welcome to the Community

Thank you for your interest in contributing to the ElevatedIQ Social Media Platform! Your contributions help make social media management more accessible and powerful for everyone.

**Questions?** Don't hesitate to ask! Create an issue, start a discussion, or reach out to the maintainers. We're here to help you succeed.

**Ready to contribute?** Check out our [good first issues](https://github.com/kushin77/elevatediq-ai/labels/good%20first%20issue) to get started!

---

**Happy coding!** 🚀 Together, we're building the future of social media management.
