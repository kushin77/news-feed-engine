# 🚀 Quick Start Guide - ElevatedIQ Social Media Platform

Get up and running with the ElevatedIQ Social Media Platform in 15 minutes.

## ⚡ Prerequisites

- Google Cloud Project with billing enabled
- Node.js 20+ installed
- `gcloud` CLI configured
- Admin access to social media accounts

## 🎯 Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/kushin77/elevatedIQ.git
cd elevatedIQ/social-media-platform

# Install dependencies
cd functions
npm install

# Set up environment
cp .env.example .env
# Edit .env with your project settings
```bash

## 🔐 Step 2: Configure Platform Credentials

### Instagram & Facebook

1. **Create Facebook App**:
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create new app → Business → Continue
   - Add Instagram Basic Display and Instagram Graph API

2. **Get Access Tokens**:

   ```bash
   # Get long-lived tokens using Facebook Graph API Explorer
   # Store in Secret Manager
   gcloud secrets create instagram-access-token --data-file=token.txt
   gcloud secrets create instagram-account-id --data-file=account-id.txt
   gcloud secrets create facebook-page-access-token --data-file=page-token.txt
   gcloud secrets create facebook-page-id --data-file=page-id.txt
```bash

### Twitter/X

1. **Create Twitter App**:
   - Go to [Twitter Developer Portal](https://developer.twitter.com/)
   - Create project and app
   - Enable OAuth 1.0a with read/write permissions

2. **Store Credentials**:

   ```bash
   gcloud secrets create twitter-api-key --data-file=api-key.txt
   gcloud secrets create twitter-api-secret --data-file=api-secret.txt
   gcloud secrets create twitter-access-token --data-file=access-token.txt
   gcloud secrets create twitter-access-token-secret --data-file=access-token-secret.txt
```bash

### LinkedIn

1. **Create LinkedIn App**:
   - Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
   - Create app with w_member_social permissions

2. **Store Credentials**:

   ```bash
   gcloud secrets create linkedin-access-token --data-file=linkedin-token.txt
   gcloud secrets create linkedin-person-id --data-file=person-id.txt
```bash

### TikTok

1. **Apply for TikTok Developer Access**:
   - Submit application at [TikTok Developers](https://developers.tiktok.com/)
   - Get approved for Content Posting API

2. **Store Credentials**:

   ```bash
   gcloud secrets create tiktok-access-token --data-file=tiktok-token.txt
```bash

## 🚀 Step 3: Deploy Functions

```bash
# Deploy all functions at once
npm run deploy:all

# Or deploy individually
npm run deploy:schedule    # Scheduling function
npm run deploy:publish     # Publishing function
npm run deploy:analytics   # Analytics function
```bash

Expected output:

```

✅ Deployed schedulePost to <https://region-project.cloudfunctions.net/schedulePost>
✅ Deployed publishScheduledPosts to <https://region-project.cloudfunctions.net/publishScheduledPosts>
✅ Deployed analytics to <https://region-project.cloudfunctions.net/analytics>

```bash

## 📅 Step 4: Set Up Automated Publishing

Create Cloud Scheduler job for automated posting:

```bash
gcloud scheduler jobs create http social-media-publisher \\
  --schedule=\"*/5 * * * *\" \\
  --uri=\"https://region-project.cloudfunctions.net/publishScheduledPosts\" \\
  --http-method=POST \\
  --time-zone=\"America/New_York\"
```bash

## 🧪 Step 5: Test Your Setup

### Test Single Platform

```bash
curl -X POST https://region-project.cloudfunctions.net/schedulePost \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"platforms\": [\"instagram\"],
    \"caption\": \"Testing ElevatedIQ Social Media Platform! 🚀 #Test\",
    \"imageUrl\": \"https://via.placeholder.com/1080x1080/4285f4/ffffff?text=ElevatedIQ+Test\",
    \"scheduledTime\": \"'$(date -d \"+2 minutes\" -Iseconds)'\"
  }'
```bash

Expected response:

```json
{
  \"success\": true,
  \"scheduled\": [
    {
      \"id\": \"abc123xyz\",
      \"platform\": \"instagram\",
      \"scheduledTime\": \"2025-11-26T10:02:00.000Z\"
    }
  ],
  \"summary\": \"Scheduled 1/1 posts successfully\"
}
```bash

### Test Multi-Platform

```bash
curl -X POST https://region-project.cloudfunctions.net/schedulePost \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"platforms\": [\"instagram\", \"facebook\", \"twitter\"],
    \"caption\": \"Multi-platform test from ElevatedIQ! 🌟\",
    \"imageUrl\": \"https://via.placeholder.com/1200x630/ff6b6b/ffffff?text=Multi-Platform+Test\",
    \"scheduledTime\": \"'$(date -d \"+5 minutes\" -Iseconds)'\",
    \"hashtags\": [\"ElevatedIQ\", \"SocialMedia\", \"Automation\"]
  }'
```bash

## 📊 Step 6: Verify Analytics

Check analytics endpoint:

```bash
curl https://region-project.cloudfunctions.net/analytics?timeframe=1d
```bash

Expected response:

```json
{
  \"success\": true,
  \"timeframe\": \"1d\",
  \"stats\": {
    \"total\": 1,
    \"scheduled\": 0,
    \"published\": 1,
    \"failed\": 0,
    \"byPlatform\": {
      \"instagram\": 1
    }
  }
}
```bash

## 🎨 Step 7: Create Your First Campaign

```bash
# Schedule a series of posts
for platform in instagram facebook twitter; do
  curl -X POST https://region-project.cloudfunctions.net/schedulePost \\
    -H \"Content-Type: application/json\" \\
    -d \"{
      \\\"platforms\\\": [\\\"$platform\\\"],
      \\\"caption\\\": \\\"Welcome to our $platform community! Join us for amazing content 🎉\\\",
      \\\"imageUrl\\\": \\\"https://via.placeholder.com/1080x1080/00d4aa/ffffff?text=Welcome+to+$platform\\\",
      \\\"scheduledTime\\\": \\\"$(date -d \\\"+$((RANDOM % 60 + 1)) minutes\\\" -Iseconds)\\\",
      \\\"hashtags\\\": [\\\"Welcome\\\", \\\"Community\\\", \\\"ElevatedIQ\\\"]
    }\"
  
  sleep 2  # Rate limit protection
done
```bash

## ⚙️ Step 8: Enable Real-Time Posting

By default, posting is disabled for safety. Enable it:

```bash
# Enable posting through Firestore
gcloud firestore documents create --collection=posting_settings --document-id=posting_enabled --data='{\"enabled\": true}'

# Or use the Firebase Console
# 1. Go to Firestore in Firebase Console
# 2. Create collection: posting_settings
# 3. Create document: posting_enabled
# 4. Add field: enabled (boolean) = true
```bash

## 🔍 Step 9: Monitor Your Posts

### Check Scheduled Posts

```bash
# View scheduled posts in Firestore
gcloud firestore documents list --collection=scheduled_posts --limit=5
```bash

### Monitor Publishing

```bash
# Check Cloud Functions logs
gcloud functions logs read publishScheduledPosts --limit=10

# View in real-time
gcloud functions logs tail publishScheduledPosts
```bash

### Analytics Dashboard

Create a simple monitoring script:

```javascript
// monitor.js
const axios = require('axios');

async function checkStatus() {
  try {
    const response = await axios.get('https://region-project.cloudfunctions.net/analytics?timeframe=1d');
    console.log('📊 Daily Stats:', response.data.stats);
    
    if (response.data.stats.failed > 0) {
      console.log('⚠️  Some posts failed - check logs!');
    }
    
    console.log('✅ System healthy');
  } catch (error) {
    console.error('❌ System error:', error.message);
  }
}

setInterval(checkStatus, 60000); // Check every minute
```bash

## 🎯 Step 10: Customize for Your Brand

### Update Business Context

Edit the default hashtags and branding in your posts:

```javascript
// In your requests, add businessContext
{
  \"platforms\": [\"instagram\"],
  \"caption\": \"Your branded message\",
  \"businessContext\": \"YourBrandName\",  // This adds your hashtags
  \"hashtags\": [\"YourBrand\", \"CustomTag\"]
}
```bash

### Platform-Specific Optimization

```bash
# Instagram - Visual content focus
{
  \"platforms\": [\"instagram\"],
  \"caption\": \"Short, engaging caption with emoji! 📸✨\",
  \"imageUrl\": \"high-quality-square-image.jpg\",
  \"hashtags\": [\"Visual\", \"Engaging\", \"Instagram\"]
}

# Twitter - Concise and timely
{
  \"platforms\": [\"twitter\"],
  \"caption\": \"Breaking: Quick update with trending hashtag! 🔥\",
  \"hashtags\": [\"Breaking\", \"News\", \"Trending\"]
}

# LinkedIn - Professional tone
{
  \"platforms\": [\"linkedin\"],
  \"caption\": \"Sharing insights about our industry leadership and innovation in social media automation.\",
  \"hashtags\": [\"Leadership\", \"Innovation\", \"B2B\"]
}
```bash

## ✅ Success Checklist

- [ ] All platform credentials stored in Secret Manager
- [ ] Functions deployed successfully
- [ ] Cloud Scheduler job created
- [ ] Test posts scheduled and published
- [ ] Analytics endpoint responding
- [ ] Real-time posting enabled
- [ ] Monitoring setup complete
- [ ] Brand customization applied

## 🚨 Troubleshooting

### Common Issues

1. **\"Missing credentials\" error**:

   ```bash
   # Verify secrets exist
   gcloud secrets list --filter=\"name:instagram OR name:facebook OR name:twitter\"
   
   # Check function has access
   gcloud functions describe schedulePost --format=\"value(serviceAccountEmail)\"
```bash

2. **\"Rate limit exceeded\"**:
   - Posts will automatically retry
   - Check platform-specific rate limits in logs
   - Consider spreading posts across more time

3. **\"Function timeout\"**:

   ```bash
   # Increase timeout
   gcloud functions deploy schedulePost --timeout=540s
```bash

4. **Posts not publishing**:

   ```bash
   # Check if posting is enabled
   gcloud firestore documents get posting_settings/posting_enabled
   
   # Manually trigger publisher
   curl -X POST https://region-project.cloudfunctions.net/publishScheduledPosts
```bash

## 🎉 Next Steps

1. **Set up monitoring alerts**: Configure Cloud Monitoring for function failures
2. **Create content templates**: Build reusable content structures
3. **Implement A/B testing**: Test different post formats and times
4. **Add team collaboration**: Multiple user access and approval workflows
5. **Scale up**: Add more platforms and advanced features

## 📞 Get Help

- **Documentation**: Full docs in `/docs` folder
- **Issues**: Report bugs on GitHub Issues
- **Community**: Join our Discord for support
- **Enterprise**: Contact <sales@elevatediq.ai> for enterprise features

---

**🎊 Congratulations!** You now have a fully functional multi-platform social media automation system. Start creating amazing content! 🚀
