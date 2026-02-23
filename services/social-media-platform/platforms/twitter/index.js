/**
 * Twitter/X Platform Module
 * ElevatedIQ Social Media Platform
 *
 * Twitter API v2 Integration with OAuth 1.0a
 * Supports: Text tweets, Image tweets, Video tweets, Thread tweets
 *
 * Created: November 25, 2025
 */

const axios = require('axios');
const OAuth = require('oauth-1.0a');
const crypto = require('crypto');
const FormData = require('form-data');

class TwitterPublisher {
  constructor() {
    this.apiVersion = '2';
    this.baseUrl = 'https://api.twitter.com/2';
    this.uploadUrl = 'https://upload.twitter.com/1.1';
    this.platformName = 'twitter';
  }

  /**
   * Publish a post to Twitter/X
   * @param {Object} post - Post data from Firestore
   * @param {Object} core - SocialMediaCore utilities
   * @returns {Object} - Publishing result
   */
  async publish(post, core) {
    try {
      console.log(`🐦 Publishing Twitter post...`);

      // Get credentials
      const apiKey = await core.getSecret('twitter-api-key');
      const apiSecret = await core.getSecret('twitter-api-secret');
      const accessToken = await core.getSecret('twitter-access-token');
      const accessTokenSecret = await core.getSecret('twitter-access-token-secret');

      if (!apiKey || !apiSecret || !accessToken || !accessTokenSecret) {
        throw new Error('Missing Twitter credentials in Secret Manager');
      }

      // Setup OAuth 1.0a
      const oauth = OAuth({
        consumer: { key: apiKey, secret: apiSecret },
        signature_method: 'HMAC-SHA1',
        hash_function(base_string, key) {
          return crypto
            .createHmac('sha1', key)
            .update(base_string)
            .digest('base64');
        }
      });

      const token = { key: accessToken, secret: accessTokenSecret };

      // Handle different tweet types
      let result;

      if (post.imageUrl || post.videoUrl) {
        result = await this.publishMediaTweet(post, oauth, token);
      } else {
        result = await this.publishTextTweet(post, oauth, token);
      }

      // Track API usage
      await core.trackApiUsage('twitter', 'tweet_publish', 1);

      return {
        success: true,
        externalId: result.id,
        url: `https://twitter.com/i/web/status/${result.id}`,
        tweetType: result.type
      };

    } catch (error) {
      console.error('Twitter publish error:', error);

      // Handle rate limiting
      if (error.response?.status === 429) {
        const resetTime = error.response.headers['x-rate-limit-reset'];
        const retryAfter = resetTime ? (resetTime * 1000 - Date.now()) / 1000 : 3600;
        throw new Error(`Rate limited. Retry after ${Math.ceil(retryAfter)} seconds.`);
      }

      // Handle authentication errors
      if (error.response?.status === 401) {
        throw new Error('Twitter authentication failed. Check credentials.');
      }

      // Handle content policy errors
      if (error.response?.status === 422) {
        throw new Error('Tweet violates Twitter content policy or is a duplicate');
      }

      throw new Error(`Twitter API error: ${error.message}`);
    }
  }

  /**
   * Publish text-only tweet
   */
  async publishTextTweet(post, oauth, token) {
    console.log('📝 Publishing text tweet...');

    // Check character limit (280 for most accounts)
    if (post.caption.length > 280) {
      return await this.publishThread(post, oauth, token);
    }

    const requestData = {
      url: `${this.baseUrl}/tweets`,
      method: 'POST'
    };

    const tweetData = {
      text: post.caption
    };

    // Add location if provided
    if (post.location) {
      tweetData.geo = {
        place_id: post.location
      };
    }

    const response = await axios.post(requestData.url, tweetData, {
      headers: {
        ...oauth.toHeader(oauth.authorize(requestData, token)),
        'Content-Type': 'application/json'
      }
    });

    console.log(`✅ Published text tweet: ${response.data.data.id}`);
    return {
      id: response.data.data.id,
      type: 'text'
    };
  }

  /**
   * Publish tweet with media (image or video)
   */
  async publishMediaTweet(post, oauth, token) {
    console.log('📸 Publishing media tweet...');

    let mediaIds = [];

    // Upload media first
    if (post.imageUrl) {
      const mediaId = await this.uploadImage(post.imageUrl, oauth, token);
      mediaIds.push(mediaId);
    }

    if (post.videoUrl) {
      const mediaId = await this.uploadVideo(post.videoUrl, oauth, token);
      mediaIds.push(mediaId);
    }

    // Create tweet with media
    const requestData = {
      url: `${this.baseUrl}/tweets`,
      method: 'POST'
    };

    const tweetData = {
      text: post.caption,
      media: {
        media_ids: mediaIds
      }
    };

    const response = await axios.post(requestData.url, tweetData, {
      headers: {
        ...oauth.toHeader(oauth.authorize(requestData, token)),
        'Content-Type': 'application/json'
      }
    });

    console.log(`✅ Published media tweet: ${response.data.data.id}`);
    return {
      id: response.data.data.id,
      type: 'media',
      mediaCount: mediaIds.length
    };
  }

  /**
   * Publish thread (for long content)
   */
  async publishThread(post, oauth, token) {
    console.log('🧵 Publishing Twitter thread...');

    const text = post.caption;
    const tweets = this.splitIntoTweets(text);
    const tweetIds = [];

    for (let i = 0; i < tweets.length; i++) {
      const tweetText = `${tweets[i]} ${i < tweets.length - 1 ? `(${i + 1}/${tweets.length})` : ''}`;

      const requestData = {
        url: `${this.baseUrl}/tweets`,
        method: 'POST'
      };

      const tweetData = {
        text: tweetText
      };

      // Reply to previous tweet to create thread
      if (i > 0) {
        tweetData.reply = {
          in_reply_to_tweet_id: tweetIds[i - 1]
        };
      }

      const response = await axios.post(requestData.url, tweetData, {
        headers: {
          ...oauth.toHeader(oauth.authorize(requestData, token)),
          'Content-Type': 'application/json'
        }
      });

      tweetIds.push(response.data.data.id);

      // Small delay between thread tweets
      if (i < tweets.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    console.log(`✅ Published Twitter thread: ${tweetIds.length} tweets`);
    return {
      id: tweetIds[0], // Return first tweet ID
      type: 'thread',
      threadLength: tweetIds.length,
      allTweetIds: tweetIds
    };
  }

  /**
   * Upload image to Twitter
   */
  async uploadImage(imageUrl, oauth, token) {
    console.log('📷 Uploading image to Twitter...');

    // Download image first
    const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const imageBuffer = Buffer.from(imageResponse.data);

    // Upload to Twitter
    const form = new FormData();
    form.append('media', imageBuffer, {
      filename: 'image.jpg',
      contentType: 'image/jpeg'
    });

    const requestData = {
      url: `${this.uploadUrl}/media/upload.json`,
      method: 'POST'
    };

    const response = await axios.post(requestData.url, form, {
      headers: {
        ...oauth.toHeader(oauth.authorize(requestData, token)),
        ...form.getHeaders()
      }
    });

    console.log(`✅ Uploaded image: ${response.data.media_id_string}`);
    return response.data.media_id_string;
  }

  /**
   * Upload video to Twitter (chunked upload for large files)
   */
  async uploadVideo(videoUrl, oauth, token) {
    console.log('🎥 Uploading video to Twitter...');

    // Download video
    const videoResponse = await axios.get(videoUrl, { responseType: 'arraybuffer' });
    const videoBuffer = Buffer.from(videoResponse.data);

    // Initialize upload
    const initData = {
      command: 'INIT',
      media_type: 'video/mp4',
      total_bytes: videoBuffer.length
    };

    const initRequest = {
      url: `${this.uploadUrl}/media/upload.json`,
      method: 'POST'
    };

    const initResponse = await axios.post(initRequest.url, initData, {
      headers: {
        ...oauth.toHeader(oauth.authorize(initRequest, token)),
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const mediaId = initResponse.data.media_id_string;

    // Upload in chunks (5MB max per chunk)
    const chunkSize = 5 * 1024 * 1024;
    let segmentIndex = 0;

    for (let i = 0; i < videoBuffer.length; i += chunkSize) {
      const chunk = videoBuffer.slice(i, i + chunkSize);

      const form = new FormData();
      form.append('command', 'APPEND');
      form.append('media_id', mediaId);
      form.append('segment_index', segmentIndex.toString());
      form.append('media', chunk);

      const appendRequest = {
        url: `${this.uploadUrl}/media/upload.json`,
        method: 'POST'
      };

      await axios.post(appendRequest.url, form, {
        headers: {
          ...oauth.toHeader(oauth.authorize(appendRequest, token)),
          ...form.getHeaders()
        }
      });

      segmentIndex++;
    }

    // Finalize upload
    const finalizeData = {
      command: 'FINALIZE',
      media_id: mediaId
    };

    const finalizeRequest = {
      url: `${this.uploadUrl}/media/upload.json`,
      method: 'POST'
    };

    await axios.post(finalizeRequest.url, finalizeData, {
      headers: {
        ...oauth.toHeader(oauth.authorize(finalizeRequest, token)),
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    console.log(`✅ Uploaded video: ${mediaId}`);
    return mediaId;
  }

  /**
   * Split long text into multiple tweets
   */
  splitIntoTweets(text, maxLength = 250) {
    const tweets = [];
    let currentTweet = '';

    const sentences = text.split('. ');

    for (const sentence of sentences) {
      if ((currentTweet + sentence + '. ').length <= maxLength) {
        currentTweet += sentence + '. ';
      } else {
        if (currentTweet) {
          tweets.push(currentTweet.trim());
        }
        currentTweet = sentence + '. ';
      }
    }

    if (currentTweet) {
      tweets.push(currentTweet.trim());
    }

    return tweets;
  }

  /**
   * Get Twitter metrics for a tweet
   */
  async getMetrics(tweetId, oauth, token) {
    try {
      const requestData = {
        url: `${this.baseUrl}/tweets/${tweetId}`,
        method: 'GET'
      };

      const params = new URLSearchParams({
        'tweet.fields': 'public_metrics,organic_metrics'
      });

      const response = await axios.get(`${requestData.url}?${params}`, {
        headers: oauth.toHeader(oauth.authorize(requestData, token))
      });

      return this.formatMetrics(response.data.data);
    } catch (error) {
      console.error('Failed to get Twitter metrics:', error);
      return null;
    }
  }

  /**
   * Format metrics to standard format
   */
  formatMetrics(tweetData) {
    const publicMetrics = tweetData.public_metrics || {};
    const organicMetrics = tweetData.organic_metrics || {};

    return {
      impressions: organicMetrics.impression_count || 0,
      engagement: publicMetrics.like_count + publicMetrics.reply_count + publicMetrics.retweet_count,
      likes: publicMetrics.like_count || 0,
      retweets: publicMetrics.retweet_count || 0,
      replies: publicMetrics.reply_count || 0,
      quotes: publicMetrics.quote_count || 0,
      clicks: organicMetrics.url_link_clicks || 0,
      profileClicks: organicMetrics.user_profile_clicks || 0
    };
  }

  /**
   * Validate Twitter-specific post requirements
   */
  validatePost(post) {
    // Check for required content
    if (!post.caption || post.caption.trim().length === 0) {
      throw new Error('Twitter posts require text content');
    }

    // Check if it's too short
    if (post.caption.trim().length < 3) {
      throw new Error('Twitter posts must be at least 3 characters long');
    }

    return true;
  }

  /**
   * Get platform-specific posting guidelines
   */
  getGuidelines() {
    return {
      platform: 'twitter',
      mediaRequirements: {
        image: {
          formats: ['JPG', 'PNG', 'GIF', 'WEBP'],
          maxSize: '5MB',
          maxImages: 4,
          recommendedDimensions: '1200x675'
        },
        video: {
          formats: ['MP4', 'MOV'],
          maxSize: '512MB',
          maxDuration: '140 seconds',
          recommendedDimensions: '1280x720'
        }
      },
      contentLimits: {
        characterLimit: 280,
        hashtagRecommendation: '1-2 hashtags',
        mentionLimit: 10
      },
      postingGuidelines: {
        optimalPostingTimes: ['8AM-10AM', '7PM-9PM'],
        recommendedFrequency: '3-5 tweets per day',
        bestPractices: [
          'Keep tweets concise and engaging',
          'Use trending hashtags sparingly',
          'Engage with replies quickly',
          'Share timely, relevant content',
          'Use Twitter Spaces for live audio'
        ]
      }
    };
  }
}

// Export the publisher
module.exports = new TwitterPublisher();
