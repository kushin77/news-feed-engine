/**
 * LinkedIn Platform Module
 * ElevatedIQ Social Media Platform
 *
 * LinkedIn Marketing API Integration
 * Supports: Text posts, Image posts, Video posts, Article sharing
 *
 * Created: November 25, 2025
 */

const axios = require('axios');
const FormData = require('form-data');

class LinkedInPublisher {
  constructor() {
    this.apiVersion = 'v2';
    this.baseUrl = 'https://api.linkedin.com/v2';
    this.platformName = 'linkedin';
  }

  /**
   * Publish a post to LinkedIn
   * @param {Object} post - Post data from Firestore
   * @param {Object} core - SocialMediaCore utilities
   * @returns {Object} - Publishing result
   */
  async publish(post, core) {
    try {
      console.log(`🔷 Publishing LinkedIn post...`);

      // Get credentials
      const accessToken = await core.getSecret('linkedin-access-token');
      const personId = await core.getSecret('linkedin-person-id'); // or organization ID

      if (!accessToken || !personId) {
        throw new Error('Missing LinkedIn credentials in Secret Manager');
      }

      // Determine if posting as person or organization
      const isOrganization = personId.startsWith('urn:li:organization:');
      const authorUrn = isOrganization ? personId : `urn:li:person:${personId}`;

      let result;

      if (post.imageUrl) {
        result = await this.publishImagePost(post, accessToken, authorUrn);
      } else if (post.videoUrl) {
        result = await this.publishVideoPost(post, accessToken, authorUrn);
      } else if (post.link) {
        result = await this.publishArticlePost(post, accessToken, authorUrn);
      } else {
        result = await this.publishTextPost(post, accessToken, authorUrn);
      }

      // Track API usage
      await core.trackApiUsage('linkedin', 'post_publish', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://www.linkedin.com/feed/update/${result.id}`,
        postType: result.type
      };

    } catch (error) {
      console.error('LinkedIn publish error:', error);

      // Handle rate limiting
      if (error.response?.status === 429) {
        throw new Error('LinkedIn rate limit exceeded. Try again later.');
      }

      // Handle authentication errors
      if (error.response?.status === 401) {
        throw new Error('LinkedIn access token expired or invalid');
      }

      // Handle content policy errors
      if (error.response?.status === 422) {
        throw new Error('LinkedIn post content violates platform policies');
      }

      throw new Error(`LinkedIn API error: ${error.message}`);
    }
  }

  /**
   * Publish text-only post
   */
  async publishTextPost(post, accessToken, authorUrn) {
    console.log('📝 Publishing text post to LinkedIn...');

    const postData = {
      author: authorUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text: post.caption
          },
          shareMediaCategory: 'NONE'
        }
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
      }
    };

    const response = await axios.post(`${this.baseUrl}/ugcPosts`, postData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
      }
    });

    const postId = response.headers['x-restli-id'];
    console.log(`✅ Published LinkedIn text post: ${postId}`);

    return {
      id: postId,
      type: 'text'
    };
  }

  /**
   * Publish image post
   */
  async publishImagePost(post, accessToken, authorUrn) {
    console.log('📸 Publishing image post to LinkedIn...');

    // Step 1: Register image upload
    const registerUploadRequest = {
      registerUploadRequest: {
        recipes: ['urn:li:digitalmediaRecipe:feedshare-image'],
        owner: authorUrn,
        serviceRelationships: [{
          relationshipType: 'OWNER',
          identifier: 'urn:li:userGeneratedContent'
        }]
      }
    };

    const uploadResponse = await axios.post(`${this.baseUrl}/assets?action=registerUpload`, registerUploadRequest, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    const uploadUrl = uploadResponse.data.value.uploadMechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'].uploadUrl;
    const asset = uploadResponse.data.value.asset;

    // Step 2: Upload image
    const imageResponse = await axios.get(post.imageUrl, { responseType: 'arraybuffer' });
    const imageBuffer = Buffer.from(imageResponse.data);

    await axios.post(uploadUrl, imageBuffer, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/octet-stream'
      }
    });

    // Step 3: Create post with image
    const postData = {
      author: authorUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text: post.caption
          },
          shareMediaCategory: 'IMAGE',
          media: [{
            status: 'READY',
            description: {
              text: post.caption
            },
            media: asset,
            title: {
              text: 'Image Post'
            }
          }]
        }
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
      }
    };

    const response = await axios.post(`${this.baseUrl}/ugcPosts`, postData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
      }
    });

    const postId = response.headers['x-restli-id'];
    console.log(`✅ Published LinkedIn image post: ${postId}`);

    return {
      id: postId,
      type: 'image'
    };
  }

  /**
   * Publish video post
   */
  async publishVideoPost(post, accessToken, authorUrn) {
    console.log('🎥 Publishing video post to LinkedIn...');

    // Step 1: Register video upload
    const registerUploadRequest = {
      registerUploadRequest: {
        recipes: ['urn:li:digitalmediaRecipe:feedshare-video'],
        owner: authorUrn,
        serviceRelationships: [{
          relationshipType: 'OWNER',
          identifier: 'urn:li:userGeneratedContent'
        }]
      }
    };

    const uploadResponse = await axios.post(`${this.baseUrl}/assets?action=registerUpload`, registerUploadRequest, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    const uploadUrl = uploadResponse.data.value.uploadMechanism['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'].uploadUrl;
    const asset = uploadResponse.data.value.asset;

    // Step 2: Upload video
    const videoResponse = await axios.get(post.videoUrl, { responseType: 'arraybuffer' });
    const videoBuffer = Buffer.from(videoResponse.data);

    await axios.post(uploadUrl, videoBuffer, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/octet-stream'
      }
    });

    // Step 3: Create post with video
    const postData = {
      author: authorUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text: post.caption
          },
          shareMediaCategory: 'VIDEO',
          media: [{
            status: 'READY',
            description: {
              text: post.caption
            },
            media: asset,
            title: {
              text: 'Video Post'
            }
          }]
        }
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
      }
    };

    const response = await axios.post(`${this.baseUrl}/ugcPosts`, postData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
      }
    });

    const postId = response.headers['x-restli-id'];
    console.log(`✅ Published LinkedIn video post: ${postId}`);

    return {
      id: postId,
      type: 'video'
    };
  }

  /**
   * Publish article/link post
   */
  async publishArticlePost(post, accessToken, authorUrn) {
    console.log('🔗 Publishing article post to LinkedIn...');

    const postData = {
      author: authorUrn,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text: post.caption
          },
          shareMediaCategory: 'ARTICLE',
          media: [{
            status: 'READY',
            originalUrl: post.link
          }]
        }
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
      }
    };

    const response = await axios.post(`${this.baseUrl}/ugcPosts`, postData, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
      }
    });

    const postId = response.headers['x-restli-id'];
    console.log(`✅ Published LinkedIn article post: ${postId}`);

    return {
      id: postId,
      type: 'article'
    };
  }

  /**
   * Get LinkedIn post analytics
   */
  async getAnalytics(postId, accessToken) {
    try {
      const response = await axios.get(`${this.baseUrl}/socialActions/${postId}/comments`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      // Note: LinkedIn analytics require additional permissions and endpoints
      // This is a simplified version
      return {
        comments: response.data.elements?.length || 0,
        likes: 0, // Would need separate API call
        shares: 0, // Would need separate API call
        impressions: 0 // Requires LinkedIn Marketing API
      };
    } catch (error) {
      console.error('Failed to get LinkedIn analytics:', error);
      return null;
    }
  }

  /**
   * Validate LinkedIn-specific post requirements
   */
  validatePost(post) {
    // Caption length limit
    if (post.caption && post.caption.length > 3000) {
      throw new Error('LinkedIn post caption cannot exceed 3000 characters');
    }

    // Minimum content requirement
    if (!post.caption || post.caption.trim().length < 10) {
      throw new Error('LinkedIn posts should have meaningful content (at least 10 characters)');
    }

    return true;
  }

  /**
   * Get platform-specific posting guidelines
   */
  getGuidelines() {
    return {
      platform: 'linkedin',
      mediaRequirements: {
        image: {
          formats: ['JPG', 'PNG', 'GIF'],
          maxSize: '20MB',
          recommendedDimensions: '1200x627',
          aspectRatios: ['1.91:1', '1:1']
        },
        video: {
          formats: ['MP4', 'AVI', 'MOV', 'MPEG-1', 'WMV'],
          maxSize: '5GB',
          maxDuration: '10 minutes',
          minDuration: '3 seconds',
          recommendedDimensions: '1920x1080'
        }
      },
      contentLimits: {
        captionLength: 3000,
        hashtagRecommendation: '3-5 hashtags',
        mentionLimit: 5
      },
      postingGuidelines: {
        optimalPostingTimes: ['7AM-9AM', '12PM-2PM', '5PM-6PM'],
        recommendedFrequency: '1 post per day',
        bestPractices: [
          'Share industry insights and thought leadership',
          'Use professional tone and language',
          'Include relevant hashtags',
          'Engage with comments professionally',
          'Share company updates and achievements',
          'Post educational and valuable content'
        ]
      },
      audienceConsiderations: {
        platform: 'Professional networking',
        content: 'Business-focused, educational, thought leadership',
        tone: 'Professional, informative, authoritative'
      }
    };
  }
}

// Export the publisher
module.exports = new LinkedInPublisher();
