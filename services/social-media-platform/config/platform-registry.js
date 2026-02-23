// ElevatedIQ Social Media Platform - Platform Registry
// Centralized configuration for all supported platforms

/**
 * Platform Registry Configuration
 * This file defines all supported social media platforms and their configurations
 */

const platformRegistry = {
    // Instagram Configuration
    instagram: {
        name: 'instagram',
        displayName: 'Instagram',
        description: 'Instagram Graph API v18.0 integration',
        apiVersion: 'v18.0',

        // API Configuration
        api: {
            baseUrl: 'https://graph.facebook.com',
            authType: 'oauth2',
            documentationUrl: 'https://developers.facebook.com/docs/instagram-api'
        },

        // Required credentials
        credentials: {
            required: ['access_token', 'app_id', 'app_secret'],
            optional: ['page_id']
        },

        // Content limitations
        content: {
            maxCaptionLength: 2200,
            maxHashtags: 30,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif'],
            aspectRatios: ['1:1', '4:5', '16:9'],
            maxFileSize: '8MB'
        },

        // Rate limits
        rateLimits: {
            postsPerHour: 25,
            postsPerDay: 200,
            apiCallsPerHour: 200
        },

        // Features
        features: {
            scheduling: true,
            analytics: true,
            stories: true,
            reels: true,
            carousel: true
        },

        // Status
        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // Facebook Configuration
    facebook: {
        name: 'facebook',
        displayName: 'Facebook',
        description: 'Facebook Pages API integration',
        apiVersion: 'v18.0',

        api: {
            baseUrl: 'https://graph.facebook.com',
            authType: 'oauth2',
            documentationUrl: 'https://developers.facebook.com/docs/pages'
        },

        credentials: {
            required: ['access_token', 'page_id', 'app_secret'],
            optional: ['app_id']
        },

        content: {
            maxCaptionLength: 63206,
            maxHashtags: 30,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif', 'mp4'],
            aspectRatios: ['16:9', '9:16', '1:1', '4:5'],
            maxFileSize: '1GB'
        },

        rateLimits: {
            postsPerHour: 100,
            postsPerDay: 1000,
            apiCallsPerHour: 7200
        },

        features: {
            scheduling: true,
            analytics: true,
            stories: true,
            video: true,
            liveVideo: false
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // Twitter Configuration
    twitter: {
        name: 'twitter',
        displayName: 'Twitter',
        description: 'Twitter API v2 integration',
        apiVersion: 'v2',

        api: {
            baseUrl: 'https://api.twitter.com',
            authType: 'oauth1a',
            documentationUrl: 'https://developer.twitter.com/en/docs/twitter-api'
        },

        credentials: {
            required: ['api_key', 'api_secret', 'access_token', 'access_secret'],
            optional: ['bearer_token']
        },

        content: {
            maxCaptionLength: 280,
            maxHashtags: 10,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif', 'mp4'],
            aspectRatios: ['16:9', '9:16', '1:1'],
            maxFileSize: '5MB'
        },

        rateLimits: {
            postsPerHour: 300,
            postsPerDay: 2400,
            apiCallsPerHour: 1500
        },

        features: {
            scheduling: true,
            analytics: true,
            threads: true,
            spaces: false,
            polls: true
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // LinkedIn Configuration
    linkedin: {
        name: 'linkedin',
        displayName: 'LinkedIn',
        description: 'LinkedIn UGC API integration',
        apiVersion: 'v2',

        api: {
            baseUrl: 'https://api.linkedin.com',
            authType: 'oauth2',
            documentationUrl: 'https://docs.microsoft.com/linkedin/marketing/integrations/community-management/shares/ugc-post-api'
        },

        credentials: {
            required: ['access_token', 'client_id', 'client_secret'],
            optional: ['person_id', 'organization_id']
        },

        content: {
            maxCaptionLength: 3000,
            maxHashtags: 20,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif', 'mp4'],
            aspectRatios: ['1.91:1', '1:1', '9:16'],
            maxFileSize: '200MB'
        },

        rateLimits: {
            postsPerHour: 60,
            postsPerDay: 500,
            apiCallsPerHour: 2000
        },

        features: {
            scheduling: true,
            analytics: true,
            video: true,
            articles: true,
            polls: true
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // TikTok Configuration
    tiktok: {
        name: 'tiktok',
        displayName: 'TikTok',
        description: 'TikTok Content Posting API integration',
        apiVersion: 'v1.3',

        api: {
            baseUrl: 'https://open-api.tiktok.com',
            authType: 'oauth2',
            documentationUrl: 'https://developers.tiktok.com/doc/content-posting-api-get-started'
        },

        credentials: {
            required: ['access_token', 'client_key', 'client_secret'],
            optional: ['refresh_token']
        },

        content: {
            maxCaptionLength: 300,
            maxHashtags: 100,
            supportedFormats: ['mp4', 'mov', 'mpeg', 'flv', 'webm'],
            aspectRatios: ['9:16', '1:1'],
            maxFileSize: '500MB'
        },

        rateLimits: {
            postsPerHour: 10,
            postsPerDay: 50,
            apiCallsPerHour: 1000
        },

        features: {
            scheduling: false, // Direct posting only
            analytics: true,
            video: true,
            effects: false,
            sounds: false
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // YouTube Configuration
    youtube: {
        name: 'youtube',
        displayName: 'YouTube',
        description: 'YouTube Data API v3 integration',
        apiVersion: 'v3',

        api: {
            baseUrl: 'https://www.googleapis.com/youtube',
            authType: 'oauth2',
            documentationUrl: 'https://developers.google.com/youtube/v3'
        },

        credentials: {
            required: ['api_key', 'client_id', 'client_secret', 'refresh_token'],
            optional: ['channel_id']
        },

        content: {
            maxCaptionLength: 5000,
            maxHashtags: 15,
            supportedFormats: ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
            aspectRatios: ['16:9', '9:16', '1:1', '4:3'],
            maxFileSize: '256GB'
        },

        rateLimits: {
            postsPerHour: 6,
            postsPerDay: 50,
            apiCallsPerHour: 10000
        },

        features: {
            scheduling: true,
            analytics: true,
            livestream: false,
            shorts: true,
            playlists: false
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // Pinterest Configuration
    pinterest: {
        name: 'pinterest',
        displayName: 'Pinterest',
        description: 'Pinterest API v5 integration',
        apiVersion: 'v5',

        api: {
            baseUrl: 'https://api.pinterest.com',
            authType: 'oauth2',
            documentationUrl: 'https://developers.pinterest.com/docs/api/v5/'
        },

        credentials: {
            required: ['access_token', 'app_id', 'app_secret'],
            optional: ['board_id']
        },

        content: {
            maxCaptionLength: 500,
            maxHashtags: 20,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif'],
            aspectRatios: ['2:3', '1:1', '9:16', '16:9'],
            maxFileSize: '20MB'
        },

        rateLimits: {
            postsPerHour: 150,
            postsPerDay: 1000,
            apiCallsPerHour: 1000
        },

        features: {
            scheduling: true,
            analytics: true,
            boards: true,
            shopping: false,
            stories: false
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // Snapchat Configuration
    snapchat: {
        name: 'snapchat',
        displayName: 'Snapchat',
        description: 'Snapchat Marketing API integration',
        apiVersion: 'v1',

        api: {
            baseUrl: 'https://adsapi.snapchat.com',
            authType: 'oauth2',
            documentationUrl: 'https://marketingapi.snapchat.com/'
        },

        credentials: {
            required: ['access_token', 'client_id', 'client_secret'],
            optional: ['ad_account_id']
        },

        content: {
            maxCaptionLength: 250,
            maxHashtags: 10,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif', 'mp4'],
            aspectRatios: ['9:16', '1:1'],
            maxFileSize: '32MB'
        },

        rateLimits: {
            postsPerHour: 50,
            postsPerDay: 200,
            apiCallsPerHour: 2000
        },

        features: {
            scheduling: true,
            analytics: true,
            stories: true,
            lenses: false,
            geofilters: false
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    },

    // Threads Configuration
    threads: {
        name: 'threads',
        displayName: 'Threads',
        description: 'Meta Threads API integration',
        apiVersion: 'v1.0',

        api: {
            baseUrl: 'https://graph.threads.net',
            authType: 'oauth2',
            documentationUrl: 'https://developers.facebook.com/docs/threads'
        },

        credentials: {
            required: ['access_token', 'app_id', 'app_secret'],
            optional: ['user_id']
        },

        content: {
            maxCaptionLength: 500,
            maxHashtags: 30,
            supportedFormats: ['jpg', 'jpeg', 'png', 'gif', 'mp4'],
            aspectRatios: ['1:1', '4:5', '9:16'],
            maxFileSize: '100MB'
        },

        rateLimits: {
            postsPerHour: 250,
            postsPerDay: 1000,
            apiCallsPerHour: 10000
        },

        features: {
            scheduling: true,
            analytics: true,
            replies: true,
            reposts: true,
            quotes: true
        },

        status: 'active',
        lastUpdated: '2024-11-25'
    }
};

/**
 * Platform Registry Helper Functions
 */
class PlatformRegistry {
    /**
     * Get all registered platforms
     */
    static getAllPlatforms() {
        return Object.keys(platformRegistry);
    }

    /**
     * Get platform configuration
     */
    static getPlatform(platformName) {
        return platformRegistry[platformName] || null;
    }

    /**
     * Check if platform is supported
     */
    static isSupported(platformName) {
        return platformName in platformRegistry;
    }

    /**
     * Get platforms by feature
     */
    static getPlatformsByFeature(feature) {
        return Object.keys(platformRegistry).filter(platform =>
            platformRegistry[platform].features[feature] === true
        );
    }

    /**
     * Get active platforms only
     */
    static getActivePlatforms() {
        return Object.keys(platformRegistry).filter(platform =>
            platformRegistry[platform].status === 'active'
        );
    }

    /**
     * Get platform rate limits
     */
    static getRateLimits(platformName) {
        const platform = this.getPlatform(platformName);
        return platform ? platform.rateLimits : null;
    }

    /**
     * Get platform content guidelines
     */
    static getContentGuidelines(platformName) {
        const platform = this.getPlatform(platformName);
        return platform ? platform.content : null;
    }

    /**
     * Get required credentials for platform
     */
    static getRequiredCredentials(platformName) {
        const platform = this.getPlatform(platformName);
        return platform ? platform.credentials.required : [];
    }

    /**
     * Validate platform configuration
     */
    static validatePlatformConfig(platformName, config) {
        const platform = this.getPlatform(platformName);
        if (!platform) {
            throw new Error(`Unknown platform: ${platformName}`);
        }

        const errors = [];

        // Check required credentials
        for (const credential of platform.credentials.required) {
            if (!config[credential]) {
                errors.push(`Missing required credential: ${credential}`);
            }
        }

        return {
            valid: errors.length === 0,
            errors,
            platform
        };
    }

    /**
     * Register a new platform (for dynamic registration)
     */
    static registerPlatform(platformName, config) {
        // Validate required fields
        const requiredFields = ['name', 'displayName', 'api', 'credentials', 'content', 'rateLimits'];
        for (const field of requiredFields) {
            if (!config[field]) {
                throw new Error(`Platform config missing required field: ${field}`);
            }
        }

        platformRegistry[platformName] = {
            ...config,
            status: config.status || 'active',
            lastUpdated: new Date().toISOString().split('T')[0]
        };

        return true;
    }

    /**
     * Get platform statistics
     */
    static getStats() {
        const platforms = Object.values(platformRegistry);

        return {
            totalPlatforms: platforms.length,
            activePlatforms: platforms.filter(p => p.status === 'active').length,
            supportedFeatures: {
                scheduling: platforms.filter(p => p.features.scheduling).length,
                analytics: platforms.filter(p => p.features.analytics).length,
                video: platforms.filter(p => p.features.video || p.features.stories).length
            },
            apiVersions: [...new Set(platforms.map(p => p.apiVersion))],
            authTypes: [...new Set(platforms.map(p => p.api.authType))]
        };
    }
}

module.exports = {
    platformRegistry,
    PlatformRegistry
};
