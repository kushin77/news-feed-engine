/**
 * Facebook Platform Module
 * ElevatedIQ Social Media Platform
 *
 * Facebook Graph API v18.0 Integration
 * Supports: Text posts, Photo posts, Video posts, Link sharing
 *
 * Created: November 25, 2025
 */

const axios = require('axios');
const FormData = require('form-data');

class FacebookPublisher {
  constructor() {
    this.apiVersion = 'v18.0';
    this.baseUrl = `https://graph.facebook.com/${this.apiVersion}`;
    this.platformName = 'facebook';
  }

  /**
   * Publish a post to Facebook Page
   * @param {Object} post - Post data from Firestore
   * @param {Object} core - SocialMediaCore utilities
   * @returns {Object} - Publishing result
   */
  async publish(post, core) {
    try {
      console.log(`📘 Publishing Facebook post...`);

      // Get credentials
      const pageAccessToken = await core.getSecret('facebook-page-access-token');
      const pageId = await core.getSecret('facebook-page-id');

      if (!pageAccessToken || !pageId) {
        throw new Error('Missing Facebook credentials in Secret Manager');
      }

      // Determine post type and publish accordingly
      let result;

      if (post.videoUrl) {
        result = await this.publishVideo(post, pageAccessToken, pageId);
      } else if (post.imageUrl) {
        result = await this.publishPhoto(post, pageAccessToken, pageId);
      } else if (post.link) {
        result = await this.publishLink(post, pageAccessToken, pageId);
      } else {
        result = await this.publishText(post, pageAccessToken, pageId);
      }

      // Track API usage
      await core.trackApiUsage('facebook', 'post_publish', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://www.facebook.com/${result.id.replace('_', '/posts/')}`,
        postType: result.type
      };

    } catch (error) {
      console.error('Facebook publish error:', error);

      // Handle rate limiting
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'] || 3600;
        throw new Error(`Rate limited. Retry after ${retryAfter} seconds.`);
      }

      // Handle token errors
      if (error.response?.status === 401) {
        throw new Error('Facebook access token expired or invalid');
      }

      // Handle content policy errors
      if (error.response?.data?.error?.code === 368) {
        throw new Error('Content violates Facebook community standards');
      }

      throw new Error(`Facebook API error: ${error.message}`);
    }
  }

  /**
   * Publish text-only post
   */
  async publishText(post, pageAccessToken, pageId) {
    console.log('📝 Publishing text post to Facebook...');

    const response = await axios.post(`${this.baseUrl}/${pageId}/feed`, {
      message: post.caption,
      access_token: pageAccessToken
    });

    console.log(`✅ Published Facebook text post: ${response.data.id}`);
    return {
      id: response.data.id,
      type: 'text'
    };
  }

  /**
   * Publish photo post
   */
  async publishPhoto(post, pageAccessToken, pageId) {
    console.log('📸 Publishing photo post to Facebook...');

    const response = await axios.post(`${this.baseUrl}/${pageId}/photos`, {
      url: post.imageUrl,
      caption: post.caption,
      access_token: pageAccessToken
    });

    console.log(`✅ Published Facebook photo post: ${response.data.id}`);
    return {
      id: response.data.post_id,
      type: 'photo'
    };
  }

  /**
   * Publish video post
   */
  async publishVideo(post, pageAccessToken, pageId) {
    console.log('🎥 Publishing video post to Facebook...');

    // For large videos, we should use resumable upload
    // For now, using direct URL method
    const response = await axios.post(`${this.baseUrl}/${pageId}/videos`, {
      file_url: post.videoUrl,
      description: post.caption,
      access_token: pageAccessToken
    });

    console.log(`✅ Published Facebook video post: ${response.data.id}`);
    return {
      id: response.data.id,
      type: 'video'
    };
  }

  /**
   * Publish link post
   */
  async publishLink(post, pageAccessToken, pageId) {
    console.log('🔗 Publishing link post to Facebook...');

    const response = await axios.post(`${this.baseUrl}/${pageId}/feed`, {
      message: post.caption,
      link: post.link,
      access_token: pageAccessToken
    });

    console.log(`✅ Published Facebook link post: ${response.data.id}`);
    return {
      id: response.data.id,
      type: 'link'
    };
  }

  /**
   * Publish carousel/album post
   */
  async publishAlbum(post, pageAccessToken, pageId) {
    console.log('🖼️ Publishing album to Facebook...');

    // Create unpublished photos first
    const photoIds = [];

    for (const imageUrl of post.imageUrls) {
      const photoResponse = await axios.post(`${this.baseUrl}/${pageId}/photos`, {
        url: imageUrl,
        published: false,
        access_token: pageAccessToken
      });
      photoIds.push({ media_fbid: photoResponse.data.id });
    }

    // Create album post
    const response = await axios.post(`${this.baseUrl}/${pageId}/feed`, {
      message: post.caption,
      attached_media: JSON.stringify(photoIds),
      access_token: pageAccessToken
    });

    console.log(`✅ Published Facebook album: ${response.data.id}`);
    return {
      id: response.data.id,
      type: 'album'
    };
  }

  /**
   * Get Facebook insights/metrics for a published post
   */
  async getInsights(postId, pageAccessToken) {
    try {
      // Get post insights
      const response = await axios.get(`${this.baseUrl}/${postId}/insights`, {
        params: {
          metric: 'post_impressions,post_reach,post_engaged_users,post_reactions_like_total,post_comments,post_shares',
          access_token: pageAccessToken
        }
      });

      return this.formatInsights(response.data.data);
    } catch (error) {
      console.error('Failed to get Facebook insights:', error);
      return null;
    }
  }

  /**
   * Format insights data to standard metrics format
   */
  formatInsights(insightsData) {
    const metrics = {
      impressions: 0,
      reach: 0,
      engagement: 0,
      likes: 0,
      comments: 0,
      shares: 0
    };

    insightsData.forEach(insight => {
      const value = insight.values[0]?.value || 0;

      switch (insight.name) {
        case 'post_impressions':
          metrics.impressions = value;
          break;
        case 'post_reach':
          metrics.reach = value;
          break;
        case 'post_engaged_users':
          metrics.engagement = value;
          break;
        case 'post_reactions_like_total':
          metrics.likes = value;
          break;
        case 'post_comments':
          metrics.comments = value;
          break;
        case 'post_shares':
          metrics.shares = value;
          break;
      }
    });

    return metrics;
  }

  /**
   * Get Facebook Page information
   */
  async getPageInfo(pageId, pageAccessToken) {
    try {
      const response = await axios.get(`${this.baseUrl}/${pageId}`, {
        params: {
          fields: 'id,name,username,followers_count,fan_count,verification_status',
          access_token: pageAccessToken
        }
      });

      return response.data;
    } catch (error) {
      console.error('Failed to get Facebook page info:', error);
      return null;
    }
  }

  /**
   * Validate Facebook-specific post requirements
   */
  validatePost(post) {
    // Caption length limit (Facebook allows up to 63,206 characters)
    if (post.caption && post.caption.length > 63206) {
      throw new Error('Facebook post caption cannot exceed 63,206 characters');
    }

    // Check for spam-like content
    if (post.caption && post.caption.includes('🔥'.repeat(5))) {
      throw new Error('Content may be flagged as spam');
    }

    return true;
  }

  /**
   * Get platform-specific posting guidelines
   */
  getGuidelines() {
    return {
      platform: 'facebook',
      mediaRequirements: {
        image: {
          formats: ['JPG', 'PNG', 'GIF'],
          maxSize: '10MB',
          recommendedDimensions: '1200x630',
          aspectRatios: ['16:9', '1:1', '4:5']
        },
        video: {
          formats: ['MP4', 'MOV', 'AVI'],
          maxSize: '4GB',
          maxDuration: '240 minutes',
          minDuration: '1 second',
          recommendedDimensions: '1280x720'
        }
      },
      contentLimits: {
        captionLength: 63206,
        hashtagRecommendation: '2-5 hashtags',
        linkLimit: 1
      },
      postingGuidelines: {
        optimalPostingTimes: ['1PM-3PM', '3PM-4PM'],
        recommendedFrequency: '1-2 posts per day',
        bestPractices: [
          'Ask questions to encourage engagement',
          'Use Facebook-native video when possible',
          'Share behind-the-scenes content',
          'Respond to comments promptly',
          'Use Facebook Stories for timely content'
        ]
      },
      contentPolicies: {
        prohibitedContent: [
          'Misleading health claims',
          'Adult content',
          'Violence or graphic content',
          'Spam or fake engagement'
        ],
        guidelines: [
          'Be authentic and transparent',
          'Respect user privacy',
          'Follow community standards',
          'Disclose paid partnerships'
        ]
      }
    };
  }

  /**
   * Schedule a post for later publishing (Facebook native scheduling)
   */
  async schedulePost(post, pageAccessToken, pageId, publishTime) {
    try {
      console.log('⏰ Scheduling Facebook post...');

      const response = await axios.post(`${this.baseUrl}/${pageId}/feed`, {
        message: post.caption,
        link: post.link,
        scheduled_publish_time: Math.floor(new Date(publishTime).getTime() / 1000),
        published: false,
        access_token: pageAccessToken
      });

      console.log(`✅ Scheduled Facebook post: ${response.data.id}`);
      return {
        id: response.data.id,
        type: 'scheduled',
        publishTime: publishTime
      };
    } catch (error) {
      throw new Error(`Failed to schedule Facebook post: ${error.message}`);
    }
  }
}

// Export the publisher
module.exports = new FacebookPublisher();
