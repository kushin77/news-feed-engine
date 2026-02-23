/**
 * Instagram Platform Module
 * ElevatedIQ Social Media Platform
 *
 * Instagram Graph API v18.0 Integration
 * Supports: Feed posts, Reels, Stories, Carousels
 *
 * Created: November 25, 2025
 */

const axios = require('axios');

class InstagramPublisher {
  constructor() {
    this.apiVersion = 'v18.0';
    this.baseUrl = `https://graph.facebook.com/${this.apiVersion}`;
    this.platformName = 'instagram';
  }

  /**
   * Publish a post to Instagram
   * @param {Object} post - Post data from Firestore
   * @param {Object} core - SocialMediaCore utilities
   * @returns {Object} - Publishing result
   */
  async publish(post, core) {
    try {
      console.log(`📸 Publishing Instagram post...`);

      // Get credentials
      const accessToken = await core.getSecret('instagram-access-token');
      const accountId = await core.getSecret('instagram-account-id');

      if (!accessToken || !accountId) {
        throw new Error('Missing Instagram credentials in Secret Manager');
      }

      // Determine media type
      const mediaType = this.getMediaType(post);

      // Create and publish based on media type
      let result;
      switch (mediaType) {
        case 'IMAGE':
          result = await this.publishImage(post, accessToken, accountId);
          break;
        case 'VIDEO':
          result = await this.publishVideo(post, accessToken, accountId);
          break;
        case 'CAROUSEL_ALBUM':
          result = await this.publishCarousel(post, accessToken, accountId);
          break;
        default:
          throw new Error(`Unsupported media type: ${mediaType}`);
      }

      // Track API usage
      await core.trackApiUsage('instagram', 'post_publish', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://www.instagram.com/p/${result.id}`,
        mediaType: mediaType
      };

    } catch (error) {
      console.error('Instagram publish error:', error);

      // Handle rate limiting
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'] || 3600;
        throw new Error(`Rate limited. Retry after ${retryAfter} seconds.`);
      }

      // Handle token errors
      if (error.response?.status === 401) {
        throw new Error('Instagram access token expired or invalid');
      }

      throw new Error(`Instagram API error: ${error.message}`);
    }
  }

  /**
   * Determine media type from post content
   */
  getMediaType(post) {
    if (post.videoUrl) {
      return 'VIDEO';
    }

    // Check if multiple images (carousel)
    if (post.imageUrls && post.imageUrls.length > 1) {
      return 'CAROUSEL_ALBUM';
    }

    if (post.imageUrl) {
      return 'IMAGE';
    }

    throw new Error('No media content found for Instagram post');
  }

  /**
   * Publish single image post
   */
  async publishImage(post, accessToken, accountId) {
    console.log('📷 Publishing image to Instagram...');

    // Step 1: Create media container
    const containerResponse = await axios.post(`${this.baseUrl}/${accountId}/media`, {
      image_url: post.imageUrl,
      caption: post.caption,
      access_token: accessToken
    });

    const creationId = containerResponse.data.id;
    console.log(`✅ Created media container: ${creationId}`);

    // Step 2: Publish media container
    const publishResponse = await axios.post(`${this.baseUrl}/${accountId}/media_publish`, {
      creation_id: creationId,
      access_token: accessToken
    });

    console.log(`🎉 Published Instagram image: ${publishResponse.data.id}`);
    return publishResponse.data;
  }

  /**
   * Publish video post (Reel)
   */
  async publishVideo(post, accessToken, accountId) {
    console.log('🎥 Publishing video to Instagram...');

    // Step 1: Create video container
    const containerResponse = await axios.post(`${this.baseUrl}/${accountId}/media`, {
      media_type: 'REELS',
      video_url: post.videoUrl,
      caption: post.caption,
      access_token: accessToken
    });

    const creationId = containerResponse.data.id;
    console.log(`✅ Created video container: ${creationId}`);

    // Step 2: Wait for video processing
    await this.waitForVideoProcessing(creationId, accessToken);

    // Step 3: Publish video container
    const publishResponse = await axios.post(`${this.baseUrl}/${accountId}/media_publish`, {
      creation_id: creationId,
      access_token: accessToken
    });

    console.log(`🎉 Published Instagram video: ${publishResponse.data.id}`);
    return publishResponse.data;
  }

  /**
   * Publish carousel post (multiple images)
   */
  async publishCarousel(post, accessToken, accountId) {
    console.log('🖼️ Publishing carousel to Instagram...');

    const imageUrls = post.imageUrls || [post.imageUrl];
    const childContainers = [];

    // Step 1: Create containers for each image
    for (let i = 0; i < imageUrls.length; i++) {
      const containerResponse = await axios.post(`${this.baseUrl}/${accountId}/media`, {
        image_url: imageUrls[i],
        is_carousel_item: true,
        access_token: accessToken
      });

      childContainers.push(containerResponse.data.id);
      console.log(`✅ Created carousel item ${i + 1}: ${containerResponse.data.id}`);
    }

    // Step 2: Create carousel container
    const carouselResponse = await axios.post(`${this.baseUrl}/${accountId}/media`, {
      media_type: 'CAROUSEL',
      children: childContainers.join(','),
      caption: post.caption,
      access_token: accessToken
    });

    const creationId = carouselResponse.data.id;
    console.log(`✅ Created carousel container: ${creationId}`);

    // Step 3: Publish carousel
    const publishResponse = await axios.post(`${this.baseUrl}/${accountId}/media_publish`, {
      creation_id: creationId,
      access_token: accessToken
    });

    console.log(`🎉 Published Instagram carousel: ${publishResponse.data.id}`);
    return publishResponse.data;
  }

  /**
   * Wait for video processing to complete
   */
  async waitForVideoProcessing(containerId, accessToken, maxAttempts = 30) {
    console.log(`⏳ Waiting for video processing: ${containerId}`);

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await axios.get(`${this.baseUrl}/${containerId}`, {
          params: {
            fields: 'status_code',
            access_token: accessToken
          }
        });

        const statusCode = response.data.status_code;

        if (statusCode === 'FINISHED') {
          console.log(`✅ Video processing completed`);
          return;
        }

        if (statusCode === 'ERROR') {
          throw new Error('Video processing failed');
        }

        // Wait 5 seconds before checking again
        await new Promise(resolve => setTimeout(resolve, 5000));

      } catch (error) {
        if (attempt === maxAttempts - 1) {
          throw new Error(`Video processing timeout after ${maxAttempts} attempts`);
        }
        console.log(`⏳ Video still processing... (attempt ${attempt + 1}/${maxAttempts})`);
      }
    }
  }

  /**
   * Get Instagram insights/metrics for a published post
   */
  async getInsights(postId, accessToken) {
    try {
      const response = await axios.get(`${this.baseUrl}/${postId}/insights`, {
        params: {
          metric: 'impressions,reach,engagement,likes,comments,shares,saves',
          access_token: accessToken
        }
      });

      return this.formatInsights(response.data.data);
    } catch (error) {
      console.error('Failed to get Instagram insights:', error);
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
      shares: 0,
      saves: 0
    };

    insightsData.forEach(insight => {
      if (metrics.hasOwnProperty(insight.name)) {
        metrics[insight.name] = insight.values[0]?.value || 0;
      }
    });

    return metrics;
  }

  /**
   * Validate Instagram-specific post requirements
   */
  validatePost(post) {
    // Instagram requires media
    if (!post.imageUrl && !post.videoUrl && !post.imageUrls) {
      throw new Error('Instagram requires at least one image or video');
    }

    // Caption length limit
    if (post.caption && post.caption.length > 2200) {
      throw new Error('Instagram caption cannot exceed 2200 characters');
    }

    // Hashtag limit
    if (post.hashtags && post.hashtags.length > 30) {
      throw new Error('Instagram posts cannot have more than 30 hashtags');
    }

    // Carousel limit
    if (post.imageUrls && post.imageUrls.length > 10) {
      throw new Error('Instagram carousels cannot have more than 10 images');
    }

    return true;
  }

  /**
   * Get platform-specific posting guidelines
   */
  getGuidelines() {
    return {
      platform: 'instagram',
      mediaRequirements: {
        image: {
          formats: ['JPG', 'PNG'],
          maxSize: '30MB',
          minDimensions: '320x320',
          recommendedDimensions: '1080x1080',
          aspectRatios: ['1:1', '4:5', '9:16']
        },
        video: {
          formats: ['MP4', 'MOV'],
          maxSize: '4GB',
          maxDuration: '90 seconds',
          minDuration: '3 seconds',
          recommendedDimensions: '1080x1920',
          aspectRatios: ['9:16', '1:1', '4:5']
        }
      },
      contentLimits: {
        captionLength: 2200,
        hashtagLimit: 30,
        mentionLimit: 20,
        carouselLimit: 10
      },
      postingGuidelines: {
        optimalPostingTimes: ['11AM-1PM', '7PM-9PM'],
        recommendedFrequency: '1-2 posts per day',
        bestPractices: [
          'Use high-quality, visually appealing images',
          'Include relevant hashtags',
          'Engage with comments quickly',
          'Post consistently',
          'Use Stories for behind-the-scenes content'
        ]
      }
    };
  }
}

// Export the publisher
module.exports = new InstagramPublisher();
