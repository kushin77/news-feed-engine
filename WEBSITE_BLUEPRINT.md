# 🗂️ Complete Website Blueprint - The Feed Portal

**Status**: Planning Phase  
**Version**: 1.0  
**Date**: March 17, 2026

---

## 📊 Executive Summary

This document outlines the **complete website structure** for The Feed portal, including:
- ✅ All pages and sections
- ✅ Every button and its action
- ✅ Navigation hierarchy
- ✅ User flows and workflows
- ✅ Implementation roadmap

**Total Pages**: 12 main pages + modals  
**Total Primary Buttons**: 47  
**Total Secondary Actions**: 80+

---

## 🏗️ SITE MAP

```
The Feed Portal
│
├─ PUBLIC PAGES (No Auth Required)
│  ├─ Landing Page (index.html)
│  └─ Public Feed View (/feed)
│
├─ AUTHENTICATED PAGES (Auth Required)
│  ├─ Dashboard (/dashboard)
│  ├─ Content Management
│  │  ├─ Content Library (/content)
│  │  ├─ Compose New (/content/new)
│  │  └─ Edit Content (/content/:id)
│  ├─ Social Connectors
│  │  ├─ Connectors List (/connectors)
│  │  ├─ Add Connector (/connectors/add)
│  │  └─ Connector Settings (/connectors/:id)
│  ├─ Publishing
│  │  ├─ Publish Schedule (/publishing)
│  │  ├─ Scheduled Posts (/publishing/scheduled)
│  │  └─ Publishing History (/publishing/history)
│  ├─ Analytics
│  │  ├─ Overview (/analytics)
│  │  ├─ Trending Content (/analytics/trending)
│  │  ├─ Engagement (/analytics/engagement)
│  │  └─ Performance Reports (/analytics/reports)
│  ├─ AI Tools
│  │  ├─ Content Generator (/ai/generator)
│  │  ├─ Video Generator (/ai/video)
│  │  └─ AI Assistant (/ai/assistant)
│  ├─ Settings
│  │  ├─ Account Settings (/settings/account)
│  │  ├─ Team Management (/settings/team)
│  │  ├─ Platform Integrations (/settings/integrations)
│  │  ├─ Billing & Subscription (/settings/billing)
│  │  └─ API Keys (/settings/api)
│  └─ Help & Support
│     ├─ Documentation (/help/docs)
│     ├─ Contact Support (/help/support)
│     └─ Feedback (/help/feedback)
│
└─ MODALS & OVERLAYS
   ├─ Authentication (Login/Signup)
   ├─ Confirmation Dialogs
   ├─ Error States
   └─ Success Messages
```

---

## 📄 PAGE DETAILS & BUTTONS

### 1. **LANDING PAGE** `/` 
**Purpose**: Public-facing homepage. First impression.

#### Layout:
```
[Header with Logo + Nav Menu + Login/Signup]
    ↓
[Hero Section]
    ↓
[Features Overview]
    ↓
[How It Works]
    ↓
[Pricing]
    ↓
[Testimonials]
    ↓
[CTA Section]
    ↓
[Footer]
```

#### Buttons:
| Button | Action | Goes To |
|--------|--------|---------|
| **Get Started** | Sign up for account | `/auth/signup` |
| **View Demo** | See live dashboard | `/demo` |
| **Learn More** (Features) | Scroll to section | `#features` |
| **View Pricing** | Scroll to pricing | `#pricing` |
| **Contact Sales** | Open contact form | Contact modal |
| **Login** (Header) | Sign in | `/auth/login` |
| **Sign Up** (Header) | Register | `/auth/signup` |
| **View Docs** (Footer) | Go to Help | `/help/docs` |
| **GitHub** (Footer) | External link | External |
| **Twitter / LinkedIn** (Footer) | Social links | External |

---

### 2. **AUTH PAGES** (`/auth/login`, `/auth/signup`)

#### 2a. **Login Page** `/auth/login`
```
[The Feed Logo]
    ↓
[Email Input]
[Password Input]
    ↓
[Forgot Password Link]
    ↓
[Login Button]
[Sign Up Link]
```

#### Buttons:
| Button | Action | Effect |
|--------|--------|--------|
| **Login** | Submit credentials | Validate → Dashboard |
| **Forgot Password?** | Reset password flow | `/auth/forgot-password` |
| **Sign Up** (Link) | Go to signup | `/auth/signup` |
| **Continue with Google** | OAuth flow | Authenticate → Dashboard |
| **Continue with GitHub** | OAuth flow | Authenticate → Dashboard |

---

#### 2b. **Signup Page** `/auth/signup`
```
[The Feed Logo]
    ↓
[Full Name Input]
[Email Input]
[Password Input]
[Confirm Password Input]
    ↓
[Terms & Privacy Checkbox]
    ↓
[Create Account Button]
[Already Have Account? Login Link]
```

#### Buttons:
| Button | Action | Effect |
|--------|--------|--------|
| **Create Account** | Register new user | Validate → Onboarding |
| **Login** (Link) | Go to login | `/auth/login` |
| **Continue with Google** | OAuth signup | Register → Dashboard |
| **Continue with GitHub** | OAuth signup | Register → Dashboard |
| **View Terms** | Open terms popup | Terms modal |
| **View Privacy** | Open privacy popup | Privacy modal |

---

### 3. **DASHBOARD** `/dashboard`
**Purpose**: Main hub after login. Overview of all activity.

```
[Header: Logo + Search + Notifications + User Menu]
    ↓
[Sidebar: Navigation]
    ↓
+───────────────────────────────────────────────────+
| Tab: Overview | Connectors | Quick Actions       |
+───────────────────────────────────────────────────+
    ↓
[Stats Row: Posts Today | Reach | Engagement | Scheduled]
    ↓
[Recent Activity Feed]
    ↓
[Quick Action Cards]
```

#### Buttons:

**Header**:
| Button | Action | Effect |
|--------|--------|--------|
| **Search Box** | Search content | Show results dropdown |
| **Notifications** | View notifications | Notification pop-over |
| **User Avatar** | User menu | Dropdown menu |
| **Settings** (dropdown) | Go to settings | `/settings/account` |
| **Logout** (dropdown) | Sign out | `/auth/login` |
| **Help** (dropdown) | Go to help | `/help/docs` |

**Overview Tab**:
| Button | Action | Effect |
|--------|--------|--------|
| **New Post** | Create content | `/content/new` |
| **Schedule Post** | Schedule content | `/publishing` |
| **View Analytics** | See full analytics | `/analytics` |
| **Add Connector** | Add social account | `/connectors/add` |
| **Refresh** | Reload dashboard data | Re-fetch stats |
| **View Recent Post** (Card click) | Open post | `/content/:id` |

**Connectors Tab**:
| Button | Action | Effect |
|--------|--------|--------|
| **Connect Account** | Add social platform | `/connectors/add` |
| **Settings** (per connector) | Configure connector | `/connectors/:id` |
| **Disconnect** | Remove connector | Confirm → Remove |
| **Refresh** | Re-sync connector data | Re-fetch status |

**Sidebar Navigation**:
| Link | Goes To | Icon |
|------|---------|------|
| **Dashboard** | `/dashboard` | 📊 |
| **Content** | `/content` | 📝 |
| **Publishing** | `/publishing` | 📤 |
| **Analytics** | `/analytics` | 📈 |
| **Connectors** | `/connectors` | 🔗 |
| **AI Tools** | `/ai/generator` | 🤖 |
| **Settings** | `/settings/account` | ⚙️ |
| **Help** | `/help/docs` | ❓ |

---

### 4. **CONTENT MANAGEMENT** `/content`
**Purpose**: Manage all content pieces.

```
[Header: "Your Content"]
    ↓
[Search + Filter Boxes]
    ↓
[New Content Button]
    ↓
[Content Grid/Table]
│
├─ Content Item 1
├─ Content Item 2
└─ ...
```

#### Buttons:

**Toolbar**:
| Button | Action | Effect |
|--------|--------|--------|
| **+ New Content** | Create post | `/content/new` |
| **Search** | Filter by title/tag | Filter results |
| **Filter** | Advanced filters | Show filter panel |
| **Sort By** | Change sort order | Sort results |
| **Bulk Actions** | Multi-select | Enable checkboxes |
| **Import** | Import from CSV | Upload modal |
| **Export** | Export as CSV | Download file |

**Per Content Item** (Card or Row):
| Button | Action | Effect |
|--------|--------|--------|
| **Edit** | Open editor | `/content/:id` |
| **Preview** | See preview | Preview modal |
| **Schedule** | Set publish date | Schedule modal |
| **Publish Now** | Immediate publish | Confirm → Publish |
| **Share** | Show share options | Share modal |
| **Duplicate** | Create copy | Duplicate modal |
| **Delete** | Remove content | Confirm → Delete |
| **View Analytics** | See performance | `/analytics?content=:id` |
| **...** (More menu) | Additional actions | Dropdown menu |

---

### 5. **COMPOSE / EDITOR** `/content/new` & `/content/:id`
**Purpose**: Create or edit content.

```
[Header: "Create New Post"]
    ↓
[Title Input]
    ↓
[Rich Text Editor]
    ↓
[Upload Media]
    ↓
[Tags/Categories]
    ↓
[Sidebar: Scheduling, Platforms, AI Options]
    ↓
[Action Buttons: Save, Publish, Schedule, Preview, Discard]
```

#### Buttons:

**Main Toolbar**:
| Button | Action | Effect |
|--------|--------|--------|
| **Save Draft** | Save as draft | Save locally |
| **Preview** | Show preview | Preview modal |
| **Publish Now** | Publish immediately | Confirm → Publish |
| **Schedule** | Set publish time | Schedule picker |
| **AI Generate** | Use AI tools | AI modal |
| **Discard** | Delete & go back | Confirm → /content |
| **Back** | Go to content list | /content |

**Editor Toolbar** (Text formatting):
| Button | Action | Effect |
|--------|--------|--------|
| **Bold** | B button | Toggle bold |
| **Italic** | I button | Toggle italic |
| **Underline** | U button | Toggle underline |
| **Link** | Link icon | Add link modal |
| **Heading** | H dropdown | Change heading level |
| **List** | List icon | Create list |
| **Quote** | Quote icon | Add quote |
| **Code** | Code icon | Add code block |
| **Undo** | ← arrow | Undo last edit |
| **Redo** | → arrow | Redo last undo |
| **Format Clear** | Clear all | Remove all formatting |

**Media Sidebar**:
| Button | Action | Effect |
|--------|--------|--------|
| **Upload Image** | + Image | File picker |
| **Upload Video** | + Video | File picker |
| **Insert Link** | + Link | Link modal |
| **Insert Embed** | + Embed | Embed modal |

**Publishing Sidebar**:
| Button | Action | Effect |
|--------|--------|--------|
| **Select Platforms** | Checkboxes | Choose social media |
| **Schedule Time** | Date/time picker | Set publish time |
| **Auto-optimize** | Toggle | Auto-format for each platform |
| **Add to Collection** | Dropdown | Group with other posts |

**AI Options Sidebar**:
| Button | Action | Effect |
|--------|--------|--------|
| **Generate Title** | Suggest titles | Show options |
| **Generate Caption** | Social caption | Show options |
| **Generate Thumbnail** | AI image | Generate image |
| **Translate** | Language picker | Translate text |
| **Shorten** | Compress text | Rewrite shorter |
| **Expand** | Add detail | Rewrite longer |
| **Change Tone** | Tone selector | Rewrite tone |

---

### 6. **CONNECTORS** `/connectors`
**Purpose**: Manage social media accounts.

```
[Header: "Social Connectors"]
    ↓
[Add Connector Button]
    ↓
[Connected Accounts Grid]
│
├─ Instagram (Connected)
├─ TikTok (Disconnected)
├─ YouTube (Connected)
└─ ...
```

#### Buttons:

**Main**:
| Button | Action | Effect |
|--------|--------|--------|
| **+ Add Account** | Connect new | Account picker modal |
| **Refresh All** | Re-sync all accounts | Reload all statuses |

**Per Connector Card**:
| Button | Action | Effect |
|--------|--------|--------|
| **Connect** | Link account | OAuth flow |
| **Disconnect** | Unlink account | Confirm → Remove |
| **Settings** | Configure options | `/connectors/:id` |
| **Test Connection** | Verify status | Show status |
| **View Analytics** | See platform stats | Platform analytics |
| **Manage Handles** | Edit profile info | Modal to edit |
| **...** (More) | Additional options | Dropdown |

---

### 7. **CONNECTOR SETTINGS** `/connectors/:id`
**Purpose**: Configure individual connector.

```
[Header: "Instagram Settings - @yourhandle"]
    ↓
[Account Info Section]
    ↓
[Publishing Options]
    ↓
[Hashtag Settings]
    ↓
[Best Time to Post]
    ↓
[Action Buttons: Save, Disconnect, Back]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Save Settings** | Update config | Save → Success message |
| **Disconnect** | Remove connector | Confirm → Remove |
| **Test Post** | Send test post | Send → Show result |
| **Auto-detect Best Time** | Analyze audience | Analyze → Show suggestion |
| **Add Hashtags** | Input group | Open hashtag picker |
| **Add Watermark** | Configure watermark | Watermark settings modal |
| **Auto-caption** | Enable/disable | Toggle setting |
| **Back** | Go to connectors | `/connectors` |
| **Refresh Status** | Check connection | Reload status |

---

### 8. **PUBLISHING** `/publishing`
**Purpose**: Schedule and manage post publishing.

```
[Header: "Publishing Schedule"]
    ↓
[Calendar View / Timeline View Toggle]
    ↓
[Calendar with Scheduled Posts]
    ↓
[Upcoming Posts List]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **+ Schedule Post** | Create scheduled post | `/content/new?schedule=true` |
| **View Calendar** | Show calendar | Toggle calendar view |
| **View List** | Show list view | Toggle list view |
| **Today** | Jump to today | Scroll to today |
| **Previous Month** | Go back | Previous month |
| **Next Month** | Go forward | Next month |
| **Edit** (per post) | Modify post | `/content/:id` |
| **Reschedule** (per post) | Change time | Schedule picker |
| **Publish Now** (per post) | Publish immediately | Confirm → Publish |
| **Cancel** (per post) | Delete scheduled | Confirm → Delete |
| **View** (per post) | See post preview | Preview modal |
| **Show Details** (per post) | Expand info | Expand details |
| **Failed Notification** | Retry failed post | Confirm → Retry |

---

### 9. **HISTORY** `/publishing/history`
**Purpose**: View past published posts.

```
[Header: "Publishing History"]
    ↓
[Search + Filter]
    ↓
[Published Posts Table]
    ↓
[Pagination Controls]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Search** | Find posts | Filter results |
| **Filter by Platform** | Platform selector | Show selected platform |
| **Filter by Date** | Date range picker | Show date range |
| **View** (per post) | See post details | Details modal |
| **Edit** (per post) | Modify post | `/content/:id` |
| **View on Platform** (per post) | Open social link | External link |
| **Repost** (per post) | Post again | Confirm → Create copy |
| **Analytics** (per post) | See performance | `/analytics?post=:id` |
| **Delete** (per post) | Remove from history | Confirm → Delete |
| **Export** | Download as CSV | Download file |
| **Previous Page** | Go back | Show page -1 |
| **Next Page** | Go forward | Show page +1 |

---

### 10. **ANALYTICS** `/analytics`
**Purpose**: View performance metrics.

```
[Header: "Analytics Dashboard"]
    ↓
[Date Range Selector]
    ↓
[KPI Cards: Reach, Engagement, Followers, Conversions]
    ↓
[Charts: Traffic Over Time, Top Posts, Audience Geography]
    ↓
[Detailed Metrics Table]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Date Range Picker** | Select timeframe | Show calendar |
| **Last 7 Days** | Quick filter | Show 7-day data |
| **Last 30 Days** | Quick filter | Show 30-day data |
| **Last 90 Days** | Quick filter | Show 90-day data |
| **Custom Range** | Date picker | Custom date range |
| **Platform Filter** | Select platforms | Show selected platforms |
| **Export Report** | Download PDF | Generate & download |
| **Email Report** | Send via email | Send to inbox |
| **View Trending** | Trending posts | `/analytics/trending` |
| **View Engagement** | Engagement details | `/analytics/engagement` |
| **Drill Down** (per metric) | See breakdown | Show detailed view |
| **Refresh** | Reload data | Re-fetch analytics |

---

### 11. **TRENDING** `/analytics/trending`
**Purpose**: See top-performing content.

```
[Header: "Trending Content"]
    ↓
[Sort Options: By Likes, Comments, Shares, Reach]
    ↓
[Trending Posts Grid]
    ↓
[Trend Analysis]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Sort by Likes** | Change sort | Sort by likes |
| **Sort by Comments** | Change sort | Sort by comments |
| **Sort by Shares** | Change sort | Sort by shares |
| **Sort by Reach** | Change sort | Sort by reach |
| **View Details** (per post) | See full metrics | Details modal |
| **Repost** (per post) | Post again | Confirm → Create copy |
| **View on Platform** (per post) | Open social | External link |
| **Save Insight** | Pin finding | Save to insights list |
| **Download Dataset** | Export trending posts | Download CSV |

---

### 12. **AI TOOLS** `/ai/generator`
**Purpose**: AI-powered content generation.

```
[Header: "Content Generator (AI)"]
    ↓
[Topic Input]
[Style/Tone Selector]
[Platform Selector]
[Length Selector]
    ↓
[Generate Button]
    ↓
[Generated Content Preview]
    ↓
[Edit / Regenerate / Save Buttons]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Generate** | Create content | Show loading → Content |
| **Regenerate** | Try again | New variation |
| **Edit** | Modify generated text | Open editor |
| **Save as Draft** | Save for later | Save → /content |
| **Publish Now** | Publish immediately | Confirm → Publish |
| **Copy to Clipboard** | Copy text | Copy → Show toast |
| **Like** | Mark as good | Add to favorites |
| **Show More Options** | Advanced settings | Expand options |
| **Clear** | Reset form | Clear all inputs |
| **Feedback** (thumbs up/down) | Rate generation | Send feedback |

**AI Video Generator** `/ai/video`:
| Button | Action | Effect |
|--------|--------|--------|
| **Upload Script** | Add text | File picker or paste |
| **Select Avatar** | Choose presenter | Avatar picker |
| **Select Voice** | Choose narrator | Voice picker |
| **Set Background** | Choose scene | Background picker |
| **Generate Video** | Create video | Show loading → Video |
| **Preview** | Watch video | Video player modal |
| **Download** | Save video | Download file |
| **Share** | Copy share link | Copy link → Paste |
| **Publish to Social** | Post to platforms | Platform selector |

---

### 13. **SETTINGS** `/settings/account`
**Purpose**: User account and platform settings.

#### 13a. **Account Settings**
```
[Header: "Account Settings"]
    ↓
[Profile Picture Upload]
    ↓
[Full Name | Email | Password]
    ↓
[Timezone | Language | Theme]
    ↓
[Two-Factor Authentication]
    ↓
[Save Changes Button]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Upload Photo** | Change avatar | File picker |
| **Remove Photo** | Delete avatar | Confirm → Remove |
| **Edit Full Name** | Change name | Update field |
| **Edit Email** | Change email | Verify new email |
| **Change Password** | Reset password | Password modal |
| **Enable 2FA** | Setup 2-step auth | 2FA setup modal |
| **Disable 2FA** | Turn off 2-step | Confirm → Disable |
| **Select Timezone** | Timezone picker | Update timezone |
| **Select Language** | Language picker | Change language |
| **Dark Mode** | Toggle dark/light | Toggle theme |
| **Save Changes** | Update settings | Save → Success |
| **Cancel Changes** | Revert edits | Reset form |
| **Delete Account** | Permanently delete | Confirm → Delete |

#### 13b. **Team Management** `/settings/team`
```
[Header: "Team Management"]
    ↓
[Current Team Members List]
    ↓
[Invite New Member]
    ↓
[Member Permissions]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **+ Invite Member** | Add teammate | Invite modal |
| **Send Invite** | Send email | Send → Show toast |
| **Resend Invite** (per invite) | Resend email | Resend → Show toast |
| **Cancel Invite** (per invite) | Remove pending | Confirm → Cancel |
| **Change Role** (per member) | Update permissions | Role dropdown |
| **Remove Member** (per member) | Delete from team | Confirm → Remove |
| **Edit Permissions** (per member) | Set granular perms | Permissions modal |
| **View Activity** (per member) | See member logs | Activity log modal |

#### 13c. **Billing & Subscription** `/settings/billing`
```
[Header: "Billing & Subscription"]
    ↓
[Current Plan Card]
    ↓
[Usage Stats]
    ↓
[Billing History Table]
    ↓
[Action Buttons: Upgrade, Change Plan, Cancel]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Upgrade Plan** | Go to pricing | Show upgrade options |
| **Change Plan** | Switch tier | Confirm → Update |
| **Cancel Subscription** | Stop billing | Confirm → Cancel |
| **Update Payment Method** | Edit card | Payment modal |
| **Download Invoice** (per invoice) | Save PDF | Download file |
| **View Receipt** (per invoice) | See details | Receipt modal |
| **Request Refund** | Start refund process | Contact support modal |
| **Promo Code** | Apply discount | Enter code → Apply |
| **Current Usage** | View usage stats | Show details |
| **Pro Tips** | Recommended features | Sidebar tips |

#### 13d. **API Keys** `/settings/api`
```
[Header: "API Keys"]
    ↓
[Generate New Key Button]
    ↓
[Active Keys List]
    ↓
[Key Management Actions]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **+ Generate Key** | Create new API key | Generate → Show key |
| **Copy** (per key) | Copy to clipboard | Copy → Show toast |
| **Regenerate** (per key) | Create new | Confirm → Regenerate |
| **Revoke** (per key) | Disable key | Confirm → Disable |
| **Rename** (per key) | Edit name | Inline edit |
| **Read Documentation** | Go to API docs | External link |
| **View Usage** (per key) | See stats | Usage modal |

---

### 14. **HELP & SUPPORT** `/help/docs`
**Purpose**: Self-service help and support.

```
[Header: "Documentation & Help"]
    ↓
[Search Documentation]
    ↓
[Documentation Categories]
    ↓
[Article List]
    ↓
[Related Articles]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **Search** | Find articles | Show results |
| **Category** (links) | Filter by topic | Show category |
| **View Article** | Read docs | Open article |
| **Helpful?** (Yes/No) | Rate article | Log feedback |
| **Report Issue** | Flag problem | Report modal |
| **Contact Support** | Get help | `/help/support` |

**Contact Support** `/help/support`:
```
[Header: "Contact Support"]
    ↓
[Support Ticket Form]
    ↓
[Priority/Category Selectors]
    ↓
[Submit Ticket Button]
```

#### Buttons:

| Button | Action | Effect |
|--------|--------|--------|
| **File Ticket** | Create support request | Submit → Confirmation |
| **Chat Support** | Live chat | Open chat widget |
| **Schedule Call** | Book support call | Calendar picker |
| **Email Us** | Contact form | Submit → Send email |
| **View Existing Tickets** | See support history | Show tickets list |
| **Attach File** | Upload screenshot | File picker |
| **Preview** | See formatted message | Show preview |

---

## 🧭 NAVIGATION STRUCTURE

### Sidebar Navigation (Always Visible When Logged In)
```
🏠 Dashboard
📝 Content
📤 Publishing
📈 Analytics
🔗 Connectors
🤖 AI Tools
⚙️ Settings
❓ Help
```

### Header Navigation
```
[Logo] [Search] [Notifications] [User Dropdown ▼]
                                    ├─ Profile
                                    ├─ Account Settings
                                    ├─ Logout
                                    └─ Help
```

### Footer Navigation (Public Pages)
```
Platform | Company | Resources | Legal
```

---

## ⚡ QUICK ACTIONS (Always Accessible)

**Keyboard Shortcuts**:
| Shortcut | Action |
|----------|--------|
| `Cmd+Shift+C` | Create new content |
| `Cmd+Shift+S` | Schedule post |
| `Cmd+/` | Search |
| `Cmd+?` | Help/Shortcuts |

**Floating Action Buttons** (Bottom Right):
| Button | Action |
|--------|--------|
| **+ Compose** | `/content/new` |
| **📞 Support** | Chat support |

---

## 🔄 USER FLOWS

### Flow 1: Create & Publish Content
```
Dashboard 
  → Click "New Content" 
  → Compose Page 
  → Write/Edit 
  → Select Platforms 
  → Schedule/Publish 
  → Confirmation
```

### Flow 2: Connect Social Account
```
Dashboard (Connectors Tab)
  → Click "Add Account"
  → Select Platform
  → OAuth Flow
  → Grant Permissions
  → Confirmation
  → Test Connection
```

### Flow 3: Schedule Post Later
```
Dashboard 
  → Click "Schedule Post"
  → Compose Page
  → Write Content
  → Set Publish Time
  → Select Platforms
  → Schedule
  → Confirmation (Added to Publishing Schedule)
```

### Flow 4: View Analytics
```
Dashboard 
  → Click "View Analytics"
  → Analytics Page
  → (Optional) Select Date Range
  → View Charts
  → (Optional) Filter by Platform
  → (Optional) Export Report
```

### Flow 5: Generate AI Content
```
Dashboard 
  → Click "AI Tools" (Sidebar)
  → AI Generator
  → Enter Topic/Style
  → Click "Generate"
  → Review Content
  → Save as Draft / Publish / Edit
```

---

## 📋 IMPLEMENTATION ROADMAP

### Phase 1: Core Navigation (MVP)
- [x] Layout component (Sidebar + Header)
- [ ] React Router setup
- [ ] All pages (stub components)
- [ ] Navigation links working
- **Est. Time**: 2-3 days

### Phase 2: Authentication
- [ ] Login page (functional)
- [ ] Signup page (functional)
- [ ] Password reset
- [ ] OAuth integration (Google, GitHub)
- [ ] Protected routes
- **Est. Time**: 2-3 days

### Phase 3: Core Features
- [ ] Dashboard (functional data loading)
- [ ] Content CRUD
- [ ] Connectors management
- [ ] Publishing schedule
- [ ] Basic analytics
- **Est. Time**: 4-5 days

### Phase 4: AI & Advanced
- [ ] AI content generator
- [ ] Video generator iframe/API
- [ ] Advanced analytics dashboard
- [ ] Team management
- [ ] Billing integration
- **Est. Time**: 3-4 days

### Phase 5: Polish & Optimization
- [ ] Mobile responsiveness
- [ ] Error handling & edge cases
- [ ] Loading states
- [ ] Success/error notifications
- [ ] Performance optimization
- **Est. Time**: 2-3 days

---

## 🎨 COMPONENT STRUCTURE

```
src/
├── components/
│   ├── Layout.tsx          (Header + Sidebar)
│   ├── Navigation.tsx      (Nav links)
│   ├── Sidebar.tsx         (Side menu)
│   ├── Header.tsx          (Top bar)
│   ├── UserMenu.tsx        (Dropdown)
│   ├── ConnectorCard.tsx   (Connector UI)
│   ├── PostCard.tsx        (Content UI)
│   ├── Modal.tsx           (Base modal)
│   └── Forms/             (Input components)
│
├── pages/
│   ├── Dashboard.tsx
│   ├── Content.tsx
│   ├── ContentEditor.tsx
│   ├── Connectors.tsx
│   ├── ConnectorSettings.tsx
│   ├── Publishing.tsx
│   ├── PublishingHistory.tsx
│   ├── Analytics.tsx
│   ├── AIGenerator.tsx
│   ├── Settings.tsx
│   └── Help.tsx
│
├── store/
│   ├── connectors.ts       (Zustand)
│   ├── content.ts          (Zustand)
│   ├── auth.ts             (Zustand)
│   └── ui.ts               (Zustand)
│
├── services/
│   ├── api.ts              (HTTP client)
│   ├── auth.ts             (Auth service)
│   ├── connectors.ts       (Connector API)
│   └── content.ts          (Content API)
│
└── types/
    ├── connectors.ts
    ├── content.ts
    ├── user.ts
    └── api.ts
```

---

## 🎯 BUTTON IMPLEMENTATION CHECKLIST

### Critical Buttons (Must Work First):
- [ ] **Create New Post** (`/content/new`)
- [ ] **Connect Account** (OAuth flow)
- [ ] **Publish Now** (API call)
- [ ] **Schedule Post** (Set time + publish)
- [ ] **View Analytics** (Load chart data)
- [ ] **Logout** (Clear session)
- [ ] **Save Settings** (Update user prefs)

### Secondary Buttons:
- [ ] Edit, Delete, Duplicate
- [ ] Preview, Share
- [ ] Filter, Sort, Search
- [ ] Export, Download
- [ ] Refresh, Reload

### Tertiary Actions:
- [ ] Tooltips on hover
- [ ] Keyboard shortcuts
- [ ] Context menus (right-click)
- [ ] Drag & drop actions

---

## 🔐 PERMISSION LEVELS

### Admin
- Access all pages
- Manage team members
- View all analytics
- Access billing

### Editor
- Create/edit/publish content
- Manage own connectors
- View own analytics
- Cannot access settings/billing

### Viewer
- Read-only access
- View analytics
- Cannot create/edit
- Cannot manage connectors

---

## 🚀 DEPLOYMENT NOTES

**Environment Variables Needed**:
```
VITE_API_BASE_URL=http://localhost:8082
VITE_GOOGLE_OAUTH_CLIENT_ID=xxx
VITE_GITHUB_OAUTH_CLIENT_ID=xxx
VITE_STRIPE_PUBLIC_KEY=xxx
```

**Build Commands**:
```bash
npm run build           # Production build
npm run preview         # Test build locally
make build-docker       # Build Docker image
```

---

## 📞 NEXT STEPS

1. **Approve Blueprint** - Confirm all pages and buttons
2. **Setup React Router** - Install and configure routing
3. **Create Page Stubs** - All pages as empty components
4. **Implement Navigation** - Make nav links work
5. **Build Auth Flow** - Login/signup functionality
6. **Connect Backend** - API integration

---

**Document Version**: 1.0  
**Last Updated**: March 17, 2026  
**Status**: Ready for Implementation
