/**
 * Pinterest Platform Module
 * ElevatedIQ Social Media Platform
 *
 * Pinterest API v5 Integration
 * Supports: Pin creation with images
 *
 * Created: November 25, 2025
 */

const axios = require('axios');

class PinterestPublisher {
  constructor() {
    this.baseUrl = 'https://api.pinterest.com/v5';
    this.platformName = 'pinterest';
  }

  async publish(post, core) {
    try {
      console.log(`📌 Publishing Pinterest pin...`);

      const accessToken = await core.getSecret('pinterest-access-token');

      if (!accessToken || !post.imageUrl) {
        throw new Error('Pinterest requires access token and image content');
      }

      const result = await this.createPin(post, accessToken);
      await core.trackApiUsage('pinterest', 'pin_create', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://pinterest.com/pin/${result.id}`,
        postType: 'pin'
      };

    } catch (error) {
      throw new Error(`Pinterest API error: ${error.message}`);
    }
  }

  async createPin(post, accessToken) {
    const pinData = {
      link: post.link || 'https://elevatediq.ai',
      title: post.title || post.caption?.substring(0, 100),
      description: post.caption || '',
      media_source: {
        source_type: 'image_url',
        url: post.imageUrl
      }
    };

    const response = await axios.post(`${this.baseUrl}/pins`, pinData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data;
  }

  validatePost(post) {
    if (!post.imageUrl) {
      throw new Error('Pinterest requires image content');
    }
    return true;
  }

  getGuidelines() {
    return {
      platform: 'pinterest',
      mediaRequirements: {
        image: {
          formats: ['PNG', 'JPEG', 'GIF'],
          maxSize: '20MB',
          recommendedDimensions: '1000x1500',
          aspectRatio: '2:3'
        }
      }
    };
  }
}

module.exports = new PinterestPublisher();
