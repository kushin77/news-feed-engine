/**
 * Threads Platform Module
 * ElevatedIQ Social Media Platform
 *
 * Meta Threads API Integration
 * Supports: Text posts, Image posts
 *
 * Created: November 25, 2025
 */

const axios = require('axios');

class ThreadsPublisher {
  constructor() {
    this.baseUrl = 'https://graph.threads.net/v1.0';
    this.platformName = 'threads';
  }

  async publish(post, core) {
    try {
      console.log(`🧵 Publishing Threads post...`);

      const accessToken = await core.getSecret('threads-access-token');
      const userId = await core.getSecret('threads-user-id');

      if (!accessToken || !userId) {
        throw new Error('Threads requires access token and user ID');
      }

      const result = await this.createPost(post, accessToken, userId);
      await core.trackApiUsage('threads', 'post_create', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://threads.net/@username/post/${result.id}`,
        postType: 'text'
      };

    } catch (error) {
      throw new Error(`Threads API error: ${error.message}`);
    }
  }

  async createPost(post, accessToken, userId) {
    const postData = {
      media_type: post.imageUrl ? 'IMAGE' : 'TEXT',
      text: post.caption
    };

    if (post.imageUrl) {
      postData.image_url = post.imageUrl;
    }

    // Step 1: Create container
    const containerResponse = await axios.post(`${this.baseUrl}/${userId}/threads`, postData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    const creationId = containerResponse.data.id;

    // Step 2: Publish container
    const publishResponse = await axios.post(`${this.baseUrl}/${userId}/threads_publish`, {
      creation_id: creationId
    }, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    return publishResponse.data;
  }

  validatePost(post) {
    if (!post.caption) {
      throw new Error('Threads requires text content');
    }

    if (post.caption.length > 500) {
      throw new Error('Threads posts cannot exceed 500 characters');
    }

    return true;
  }

  getGuidelines() {
    return {
      platform: 'threads',
      contentLimits: {
        characterLimit: 500,
        hashtagRecommendation: '2-3 hashtags'
      },
      postingGuidelines: {
        optimalPostingTimes: ['9AM-11AM', '7PM-9PM'],
        recommendedFrequency: '2-3 posts per day',
        bestPractices: [
          'Keep posts conversational',
          'Engage with community discussions',
          'Share authentic thoughts',
          'Use relevant hashtags sparingly'
        ]
      }
    };
  }
}

module.exports = new ThreadsPublisher();
