/**
 * ElevatedIQ Social Media Platform - Main Cloud Functions
 * Consolidated social media posting and management system
 *
 * Supports 9+ platforms: Instagram, Facebook, Twitter, LinkedIn, TikTok,
 * YouTube, Pinterest, Snapchat, Threads
 *
 * Security: All credentials stored in Secret Manager
 * Cost optimization: Free tier (1M invocations/month)
 *
 * Created: November 25, 2025
 */

const functions = require('@google-cloud/functions-framework');
const { Firestore } = require('@google-cloud/firestore');
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
const axios = require('axios');

// Import platform-specific handlers
const instagramPublisher = require('./platforms/instagram');
const facebookPublisher = require('./platforms/facebook');
const twitterPublisher = require('./platforms/twitter');
const linkedinPublisher = require('./platforms/linkedin');
const tiktokPublisher = require('./platforms/tiktok');
const youtubePublisher = require('./platforms/youtube');
const pinterestPublisher = require('./platforms/pinterest');
const snapchatPublisher = require('./platforms/snapchat');
const threadsPublisher = require('./platforms/threads');

// Initialize clients
const firestore = new Firestore();
const secretManager = new SecretManagerServiceClient();

// Platform registry for dynamic handler loading
const platformHandlers = {
  instagram: instagramPublisher,
  facebook: facebookPublisher,
  twitter: twitterPublisher,
  linkedin: linkedinPublisher,
  tiktok: tiktokPublisher,
  youtube: youtubePublisher,
  pinterest: pinterestPublisher,
  snapchat: snapchatPublisher,
  threads: threadsPublisher
};

/**
 * Core utilities
 */
class SocialMediaCore {
  /**
   * Track API usage for quota monitoring
   */
  static async trackApiUsage(service, operation, count = 1) {
    try {
      const response = await axios.post(
        process.env.USAGE_TRACKING_ENDPOINT || 'https://us-central1-purebliss-3316.cloudfunctions.net/trackUsage',
        { service, operation, count }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to track API usage:', error.message);
      // Don't throw - tracking failures shouldn't break main functionality
    }
  }

  /**
   * Get secret from Secret Manager
   */
  static async getSecret(secretName) {
    try {
      const projectId = process.env.GOOGLE_CLOUD_PROJECT || 'purebliss-3316';
      const [version] = await secretManager.accessSecretVersion({
        name: `projects/${projectId}/secrets/${secretName}/versions/latest`
      });
      return version.payload.data.toString('utf8');
    } catch (error) {
      console.error(`Failed to get secret ${secretName}:`, error);
      throw error;
    }
  }

  /**
   * Validate post content based on platform requirements
   */
  static validatePostContent(platform, content) {
    const platformLimits = {
      instagram: { maxCaptionLength: 2200, requiresMedia: true },
      facebook: { maxCaptionLength: 63206, requiresMedia: false },
      twitter: { maxCaptionLength: 280, requiresMedia: false },
      linkedin: { maxCaptionLength: 3000, requiresMedia: false },
      tiktok: { maxCaptionLength: 150, requiresMedia: true, videoOnly: true },
      youtube: { maxTitleLength: 100, maxDescriptionLength: 5000, requiresMedia: true, videoOnly: true },
      pinterest: { maxDescriptionLength: 500, requiresMedia: true },
      snapchat: { maxCaptionLength: 250, requiresMedia: true },
      threads: { maxCaptionLength: 500, requiresMedia: false }
    };

    const limits = platformLimits[platform];
    if (!limits) {
      throw new Error(`Unsupported platform: ${platform}`);
    }

    // Validate caption/description length
    const captionLength = content.caption?.length || 0;
    const maxLength = limits.maxCaptionLength || limits.maxDescriptionLength || limits.maxTitleLength;

    if (captionLength > maxLength) {
      throw new Error(`Caption too long for ${platform}. Max ${maxLength} characters, got ${captionLength}.`);
    }

    // Validate media requirements
    if (limits.requiresMedia && !content.mediaUrl && !content.imageUrl && !content.videoUrl) {
      throw new Error(`${platform} requires media content (image or video).`);
    }

    if (limits.videoOnly && content.imageUrl && !content.videoUrl) {
      throw new Error(`${platform} only supports video content.`);
    }

    return true;
  }

  /**
   * Add platform-specific hashtags and formatting
   */
  static formatContentForPlatform(platform, content, businessContext = 'PureBliss') {
    const { caption, hashtags = [] } = content;

    // Add business-specific hashtags based on context
    let defaultHashtags = [];
    if (businessContext === 'PureBliss') {
      defaultHashtags = ['813', 'TampaBay', 'PureBliss', 'HealthyLiving', 'Organic'];
    } else {
      defaultHashtags = ['ElevatedIQ', 'SocialMedia', 'Automation'];
    }

    const finalHashtags = [...new Set([...hashtags, ...defaultHashtags])];

    // Platform-specific formatting
    switch (platform) {
      case 'twitter':
        // Twitter hashtags are limited by character count
        const hashtagText = finalHashtags.slice(0, 5).map(h => `#${h}`).join(' ');
        return {
          ...content,
          caption: `${caption}\n\n${hashtagText}`,
          hashtags: finalHashtags.slice(0, 5)
        };

      case 'linkedin':
        // LinkedIn prefers hashtags at the end
        const linkedinHashtags = finalHashtags.map(h => `#${h}`).join(' ');
        return {
          ...content,
          caption: `${caption}\n\n${linkedinHashtags}`,
          hashtags: finalHashtags
        };

      case 'instagram':
      case 'facebook':
      case 'threads':
        const instaHashtags = finalHashtags.map(h => `#${h}`).join(' ');
        return {
          ...content,
          caption: `${caption}\n\n${instaHashtags}`,
          hashtags: finalHashtags
        };

      default:
        return {
          ...content,
          hashtags: finalHashtags
        };
    }
  }
}

/**
 * Schedule a post across one or multiple platforms
 * POST /schedulePost
 * Body: { platforms[], caption, imageUrl?, videoUrl?, scheduledTime, hashtags[]? }
 */
functions.http('schedulePost', async (req, res) => {
  // CORS headers
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(204).send('');
  }

  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const {
      platforms,
      platform,
      caption,
      imageUrl,
      videoUrl,
      scheduledTime,
      hashtags = [],
      businessContext = 'PureBliss'
    } = req.body;

    // Support both single platform and multiple platforms
    const targetPlatforms = platforms || (platform ? [platform] : []);

    // Input validation
    if (!targetPlatforms.length || !caption || !scheduledTime) {
      return res.status(400).json({
        error: 'Missing required fields: platforms (or platform), caption, scheduledTime'
      });
    }

    // Validate all platforms are supported
    const supportedPlatforms = Object.keys(platformHandlers);
    const invalidPlatforms = targetPlatforms.filter(p => !supportedPlatforms.includes(p));

    if (invalidPlatforms.length > 0) {
      return res.status(400).json({
        error: `Unsupported platforms: ${invalidPlatforms.join(', ')}. Supported: ${supportedPlatforms.join(', ')}`
      });
    }

    const scheduledPosts = [];

    // Create scheduled post for each platform
    for (const targetPlatform of targetPlatforms) {
      try {
        const content = {
          caption,
          imageUrl,
          videoUrl,
          mediaUrl: imageUrl || videoUrl,
          hashtags
        };

        // Validate content for this platform
        SocialMediaCore.validatePostContent(targetPlatform, content);

        // Format content for platform
        const formattedContent = SocialMediaCore.formatContentForPlatform(targetPlatform, content, businessContext);

        // Create scheduled post document
        const postDoc = {
          platform: targetPlatform,
          caption: formattedContent.caption,
          imageUrl: formattedContent.imageUrl,
          videoUrl: formattedContent.videoUrl,
          mediaUrl: formattedContent.mediaUrl,
          scheduledTime: new Date(scheduledTime),
          hashtags: formattedContent.hashtags,
          status: 'scheduled',
          createdAt: new Date(),
          createdBy: req.headers.authorization || 'system',
          attempts: 0,
          lastAttempt: null,
          publishedAt: null,
          externalId: null,
          error: null,
          businessContext
        };

        // Save to Firestore
        const docRef = await firestore.collection('scheduled_posts').add(postDoc);

        scheduledPosts.push({
          id: docRef.id,
          platform: targetPlatform,
          scheduledTime: postDoc.scheduledTime
        });

        console.log(`✅ Scheduled ${targetPlatform} post: ${docRef.id} for ${scheduledTime}`);
      } catch (platformError) {
        console.error(`Failed to schedule ${targetPlatform} post:`, platformError);
        scheduledPosts.push({
          platform: targetPlatform,
          error: platformError.message,
          success: false
        });
      }
    }

    // Track Firestore writes
    await SocialMediaCore.trackApiUsage('firestore', 'writes', scheduledPosts.filter(p => p.id).length);

    const successful = scheduledPosts.filter(p => p.id);
    const failed = scheduledPosts.filter(p => p.error);

    res.status(successful.length > 0 ? 201 : 400).json({
      success: successful.length > 0,
      scheduled: successful,
      failed: failed,
      summary: `Scheduled ${successful.length}/${targetPlatforms.length} posts successfully`
    });

  } catch (error) {
    console.error('Schedule post error:', error);
    res.status(500).json({
      error: 'Failed to schedule posts',
      message: error.message
    });
  }
});

/**
 * Publish scheduled posts (triggered by Cloud Scheduler every 5 minutes)
 * POST /publishScheduledPosts
 */
functions.http('publishScheduledPosts', async (req, res) => {
  try {
    // Check if posting is enabled (default: disabled for safety)
    const settingsDoc = await firestore.collection('posting_settings').doc('posting_enabled').get();
    const postingEnabled = settingsDoc.exists && settingsDoc.data().enabled === true;

    await SocialMediaCore.trackApiUsage('firestore', 'reads', 1);

    if (!postingEnabled) {
      console.log('⏸️  Posting is currently disabled');
      return res.status(200).json({
        success: true,
        processed: 0,
        message: 'Posting is currently disabled. Enable it from the admin dashboard.'
      });
    }

    const now = new Date();

    // Query posts scheduled for now or earlier, not yet published
    const snapshot = await firestore.collection('scheduled_posts')
      .where('status', '==', 'scheduled')
      .where('scheduledTime', '<=', now)
      .limit(10) // Process max 10 per invocation to avoid timeouts
      .get();

    await SocialMediaCore.trackApiUsage('firestore', 'reads', snapshot.size);

    if (snapshot.empty) {
      console.log('No posts to publish');
      return res.status(200).json({
        success: true,
        processed: 0,
        message: 'No posts scheduled for publishing'
      });
    }

    const results = [];

    for (const doc of snapshot.docs) {
      const post = doc.data();
      const postId = doc.id;

      try {
        // Get platform handler
        const handler = platformHandlers[post.platform];
        if (!handler) {
          throw new Error(`No handler found for platform: ${post.platform}`);
        }

        // Publish to platform
        console.log(`📤 Publishing ${post.platform} post: ${postId}`);
        const result = await handler.publish(post, SocialMediaCore);

        // Update post status in Firestore
        await doc.ref.update({
          status: 'published',
          publishedAt: new Date(),
          externalId: result.externalId,
          error: null,
          attempts: (post.attempts || 0) + 1,
          lastAttempt: new Date()
        });

        await SocialMediaCore.trackApiUsage('firestore', 'writes', 1);

        results.push({
          id: postId,
          platform: post.platform,
          status: 'success',
          externalId: result.externalId,
          url: result.url
        });

        console.log(`✅ Published ${post.platform} post: ${postId} -> ${result.externalId}`);

      } catch (error) {
        console.error(`❌ Failed to publish ${post.platform} post ${postId}:`, error);

        // Update post status with error
        await doc.ref.update({
          status: 'failed',
          error: error.message,
          attempts: (post.attempts || 0) + 1,
          lastAttempt: new Date()
        });

        await SocialMediaCore.trackApiUsage('firestore', 'writes', 1);

        results.push({
          id: postId,
          platform: post.platform,
          status: 'failed',
          error: error.message
        });
      }
    }

    const successful = results.filter(r => r.status === 'success');
    const failed = results.filter(r => r.status === 'failed');

    res.status(200).json({
      success: true,
      processed: results.length,
      successful: successful.length,
      failed: failed.length,
      results
    });

  } catch (error) {
    console.error('Publish scheduled posts error:', error);
    res.status(500).json({
      error: 'Failed to publish scheduled posts',
      message: error.message
    });
  }
});

/**
 * Get posting analytics and statistics
 * GET /analytics
 */
functions.http('analytics', async (req, res) => {
  try {
    const { timeframe = '7d' } = req.query;

    // Calculate date range
    const now = new Date();
    const startDate = new Date();

    switch (timeframe) {
      case '1d':
        startDate.setDate(now.getDate() - 1);
        break;
      case '7d':
        startDate.setDate(now.getDate() - 7);
        break;
      case '30d':
        startDate.setDate(now.getDate() - 30);
        break;
      default:
        startDate.setDate(now.getDate() - 7);
    }

    // Query posts within timeframe
    const snapshot = await firestore.collection('scheduled_posts')
      .where('createdAt', '>=', startDate)
      .get();

    await SocialMediaCore.trackApiUsage('firestore', 'reads', snapshot.size);

    // Aggregate statistics
    const stats = {
      total: 0,
      scheduled: 0,
      published: 0,
      failed: 0,
      byPlatform: {},
      byStatus: {},
      recentPosts: []
    };

    snapshot.forEach(doc => {
      const post = doc.data();
      stats.total++;

      // Count by status
      stats.byStatus[post.status] = (stats.byStatus[post.status] || 0) + 1;
      stats[post.status] = (stats[post.status] || 0) + 1;

      // Count by platform
      stats.byPlatform[post.platform] = (stats.byPlatform[post.platform] || 0) + 1;

      // Add to recent posts (limit 10)
      if (stats.recentPosts.length < 10) {
        stats.recentPosts.push({
          id: doc.id,
          platform: post.platform,
          status: post.status,
          scheduledTime: post.scheduledTime,
          publishedAt: post.publishedAt,
          caption: post.caption?.substring(0, 100) + '...'
        });
      }
    });

    res.status(200).json({
      success: true,
      timeframe,
      stats
    });

  } catch (error) {
    console.error('Analytics error:', error);
    res.status(500).json({
      error: 'Failed to get analytics',
      message: error.message
    });
  }
});

// Export for testing
module.exports = {
  SocialMediaCore,
  platformHandlers
};
