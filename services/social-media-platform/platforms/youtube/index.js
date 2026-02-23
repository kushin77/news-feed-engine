/**
 * YouTube Platform Module
 * ElevatedIQ Social Media Platform
 *
 * YouTube Data API v3 Integration
 * Supports: Video uploads with metadata
 *
 * Created: November 25, 2025
 */

const axios = require('axios');

class YouTubePublisher {
  constructor() {
    this.baseUrl = 'https://www.googleapis.com/youtube/v3';
    this.uploadUrl = 'https://www.googleapis.com/upload/youtube/v3';
    this.platformName = 'youtube';
  }

  async publish(post, core) {
    try {
      console.log(`📺 Publishing YouTube video...`);

      const accessToken = await core.getSecret('youtube-access-token');

      if (!accessToken || !post.videoUrl) {
        throw new Error('YouTube requires access token and video content');
      }

      const result = await this.uploadVideo(post, accessToken);
      await core.trackApiUsage('youtube', 'video_upload', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://www.youtube.com/watch?v=${result.id}`,
        postType: 'video'
      };

    } catch (error) {
      throw new Error(`YouTube API error: ${error.message}`);
    }
  }

  async uploadVideo(post, accessToken) {
    const videoData = {
      snippet: {
        title: post.title || post.caption?.substring(0, 100) || 'Video Upload',
        description: post.caption || '',
        tags: post.hashtags || [],
        categoryId: '22' // People & Blogs
      },
      status: {
        privacyStatus: 'public'
      }
    };

    // This is simplified - actual YouTube upload requires multipart form data
    const response = await axios.post(`${this.baseUrl}/videos?part=snippet,status`, videoData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data;
  }

  validatePost(post) {
    if (!post.videoUrl) {
      throw new Error('YouTube requires video content');
    }
    return true;
  }

  getGuidelines() {
    return {
      platform: 'youtube',
      mediaRequirements: {
        video: {
          formats: ['MP4', 'MOV', 'AVI', 'WMV', 'MPEG4', '3GPP', 'WebM'],
          maxSize: '128GB',
          maxDuration: '12 hours',
          recommendedDimensions: '1920x1080'
        }
      }
    };
  }
}

module.exports = new YouTubePublisher();
