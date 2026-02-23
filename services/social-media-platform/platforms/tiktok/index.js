/**
 * TikTok Platform Module
 * ElevatedIQ Social Media Platform
 *
 * TikTok Content Posting API Integration
 * Supports: Video posts with captions
 *
 * Created: November 25, 2025
 */

const axios = require('axios');

class TikTokPublisher {
  constructor() {
    this.baseUrl = 'https://open-api.tiktok.com';
    this.platformName = 'tiktok';
  }

  /**
   * Publish a video to TikTok
   * @param {Object} post - Post data from Firestore
   * @param {Object} core - SocialMediaCore utilities
   * @returns {Object} - Publishing result
   */
  async publish(post, core) {
    try {
      console.log(`🎵 Publishing TikTok video...`);

      // Get credentials
      const accessToken = await core.getSecret('tiktok-access-token');

      if (!accessToken) {
        throw new Error('Missing TikTok credentials in Secret Manager');
      }

      // TikTok only supports video content
      if (!post.videoUrl) {
        throw new Error('TikTok requires video content');
      }

      const result = await this.publishVideo(post, accessToken);

      // Track API usage
      await core.trackApiUsage('tiktok', 'video_publish', 1);

      return {
        success: true,
        externalId: result.share_id,
        url: `https://www.tiktok.com/@username/video/${result.share_id}`,
        postType: 'video'
      };

    } catch (error) {
      console.error('TikTok publish error:', error);

      if (error.response?.status === 429) {
        throw new Error('TikTok rate limit exceeded. Try again later.');
      }

      if (error.response?.status === 401) {
        throw new Error('TikTok access token expired or invalid');
      }

      throw new Error(`TikTok API error: ${error.message}`);
    }
  }

  /**
   * Publish video to TikTok
   */
  async publishVideo(post, accessToken) {
    console.log('🎥 Publishing video to TikTok...');

    const postData = {
      video: {
        video_url: post.videoUrl
      },
      post_info: {
        title: post.caption || '',
        privacy_level: 'EVERYONE',
        disable_duet: false,
        disable_comment: false,
        disable_stitch: false,
        video_cover_timestamp_ms: 1000
      },
      source_info: {
        source: 'PULL_FROM_URL',
        video_url: post.videoUrl
      }
    };

    const response = await axios.post(`${this.baseUrl}/v2/post/publish/video/init/`, postData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    console.log(`✅ Published TikTok video: ${response.data.data.publish_id}`);

    return {
      share_id: response.data.data.publish_id,
      type: 'video'
    };
  }

  /**
   * Validate TikTok-specific requirements
   */
  validatePost(post) {
    if (!post.videoUrl) {
      throw new Error('TikTok requires video content');
    }

    if (post.caption && post.caption.length > 150) {
      throw new Error('TikTok caption cannot exceed 150 characters');
    }

    return true;
  }

  /**
   * Get platform guidelines
   */
  getGuidelines() {
    return {
      platform: 'tiktok',
      mediaRequirements: {
        video: {
          formats: ['MP4', 'MOV', 'MPEG', 'AVI', 'WMV', '3GPP', 'WEBM'],
          maxSize: '287MB',
          minDuration: '15 seconds',
          maxDuration: '10 minutes',
          recommendedDimensions: '1080x1920',
          aspectRatio: '9:16'
        }
      },
      contentLimits: {
        captionLength: 150,
        hashtagRecommendation: '3-5 hashtags'
      },
      postingGuidelines: {
        optimalPostingTimes: ['6AM-10AM', '7PM-9PM'],
        recommendedFrequency: '1-3 videos per day',
        bestPractices: [
          'Create engaging, authentic content',
          'Use trending sounds and hashtags',
          'Keep videos entertaining and concise',
          'Participate in challenges and trends',
          'Use vertical video format (9:16)',
          'Hook viewers in the first 3 seconds'
        ]
      }
    };
  }
}

module.exports = new TikTokPublisher();
