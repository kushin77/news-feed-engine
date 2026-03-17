# 🚀 Frontend Implementation Roadmap - Quick Start

**Status**: Ready to Build  
**Priority**: Get all pages + routing working first  
**Estimated Time for MVP**: 1 week

---

## Step 1: Setup React Router (Today - 2 hours)

### Install Router
```bash
cd services/frontend
npm install react-router-dom
```

### Update `src/main.tsx`
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

### Update `src/App.tsx`
```tsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from '@components/Layout'

// Public Pages
import LandingPage from '@pages/Landing'
import LoginPage from '@pages/auth/Login'
import SignupPage from '@pages/auth/Signup'

// Protected Pages
import Dashboard from '@pages/Dashboard'
import Content from '@pages/Content'
import ContentEditor from '@pages/ContentEditor'
import Connectors from '@pages/Connectors'
import Publishing from '@pages/Publishing'
import Analytics from '@pages/Analytics'
import Settings from '@pages/Settings'
import Help from '@pages/Help'

export function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/signup" element={<SignupPage />} />

      {/* Protected Routes (Require Auth) */}
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/content" element={<Content />} />
        <Route path="/content/new" element={<ContentEditor />} />
        <Route path="/content/:id" element={<ContentEditor />} />
        <Route path="/connectors" element={<Connectors />} />
        <Route path="/connectors/:id" element={<Connectors />} />
        <Route path="/publishing" element={<Publishing />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings/:section" element={<Settings />} />
        <Route path="/help/:section" element={<Help />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
```

---

## Step 2: Create Page Components (Day 1-2 - 4 hours)

### Create folder structure:
```bash
mkdir -p src/pages/{auth,settings}

# Create stub files
touch src/pages/Landing.tsx
touch src/pages/auth/Login.tsx
touch src/pages/auth/Signup.tsx
touch src/pages/Dashboard.tsx
touch src/pages/Content.tsx
touch src/pages/ContentEditor.tsx
touch src/pages/Connectors.tsx
touch src/pages/Publishing.tsx
touch src/pages/Analytics.tsx
touch src/pages/Settings.tsx
touch src/pages/Help.tsx
```

### Example Stub (each page):
```tsx
// src/pages/Content.tsx
export default function Content() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Content Library</h1>
      <p className="text-slate-400">Your posts manage page will go here</p>
      
      <button className="px-4 py-2 bg-purple-500 text-white rounded">
        + New Content
      </button>
    </div>
  )
}
```

---

## Step 3: Update Navigation Links (Day 1 - 1 hour)

### Update `src/components/Layout.tsx`
```tsx
import { Link, useLocation } from 'react-router-dom'

export function Layout({ children }) {
  const location = useLocation()
  
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: '📊' },
    { label: 'Content', path: '/content', icon: '📝' },
    { label: 'Publishing', path: '/publishing', icon: '📤' },
    { label: 'Analytics', path: '/analytics', icon: '📈' },
    { label: 'Connectors', path: '/connectors', icon: '🔗' },
    { label: 'Settings', path: '/settings/account', icon: '⚙️' },
    { label: 'Help', path: '/help/docs', icon: '❓' },
  ]

  return (
    <div className="flex min-h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6">
        <h2 className="text-xl font-bold text-white mb-8">The Feed</h2>
        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-2 rounded transition ${
                location.pathname.startsWith(item.path)
                  ? 'bg-purple-500 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1">
        {/* Header */}
        <header className="sticky top-0 z-30 bg-slate-900/95 border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-white">The Feed</h1>
            <button className="px-4 py-2 text-slate-300 hover:bg-slate-800 rounded">
              👤 Profile
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
```

---

## Step 4: Add Connect Button Functionality (Day 2 - 2 hours)

### Update `src/components/ConnectorCard.tsx`
```tsx
import { useState } from 'react'

export function ConnectorCard({ connector, onConnect, onDisconnect }) {
  const [isLoading, setIsLoading] = useState(false)

  const handleConnect = async () => {
    setIsLoading(true)
    try {
      // Simulated OAuth flow
      console.log(`Connecting to ${connector.platform}...`)
      // In real app: const result = await loginWithOAuth(connector.platform)
      
      onConnect(connector.id)
      alert(`Connected to ${connector.name}!`)
    } catch (error) {
      alert(`Failed to connect: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisconnect = async () => {
    if (confirm(`Disconnect from ${connector.name}?`)) {
      onDisconnect(connector.id)
      alert(`Disconnected from ${connector.name}`)
    }
  }

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-white">{connector.name}</h3>
          <p className="text-sm text-slate-400">
            Status: <span className={connector.status === 'connected' ? 'text-green-500' : 'text-slate-500'}>
              {connector.status}
            </span>
          </p>
        </div>
        <span className="text-3xl">{connector.icon}</span>
      </div>

      {connector.status === 'connected' && (
        <div className="mb-4 text-sm text-slate-300">
          Connected as: <strong>{connector.handle}</strong>
        </div>
      )}

      <div className="flex gap-2">
        {connector.status === 'connected' ? (
          <>
            <button
              onClick={handleDisconnect}
              className="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm"
            >
              Disconnect
            </button>
            <button
              onClick={() => console.log('Settings for ', connector.name)}
              className="flex-1 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm"
            >
              Settings
            </button>
          </>
        ) : (
          <button
            onClick={handleConnect}
            disabled={isLoading}
            className="w-full px-3 py-2 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white rounded text-sm"
          >
            {isLoading ? 'Connecting...' : 'Connect'}
          </button>
        )}
      </div>
    </div>
  )
}
```

---

## Step 5: Test Everything (Day 2 - 1 hour)

### Run dev server
```bash
npm run dev
```

### Test routes:
- ✅ `/` - Landing page
- ✅ `/dashboard` - Dashboard
- ✅ `/content` - Content page
- ✅ `/connectors` - Connectors page
- ✅ Sidebar navigation working
- ✅ Active route highlighting

---

## Week 2: Core Features

### Day 1-2: Authentication
- [ ] Login form with validation
- [ ] Signup form
- [ ] Password reset flow
- [ ] Protected routes (redirect if not authenticated)

### Day 3-4: Content Management
- [ ] Create post form
- [ ] Edit post form
- [ ] List view with search/filter
- [ ] Delete confirmation

### Day 5: Publishing & Analytics
- [ ] Schedule picker
- [ ] Analytics charts
- [ ] Export functionality

---

## CRITICAL FILES TO UPDATE NOW

1. **`src/main.tsx`** - Add BrowserRouter
2. **`src/App.tsx`** - Add Routes/routing logic
3. **`src/components/Layout.tsx`** - Fix navigation links
4. **Create all `src/pages/*.tsx`** - Stub components

---

## TESTING CHECKLIST

After implementing, verify:
- [ ] All nav links work (click to navigate)
- [ ] Active nav item highlights
- [ ] Page title changes
- [ ] URL updates in browser
- [ ] Back button works
- [ ] Direct URL access works (`/content` → Content page)
- [ ] 404 page shows for invalid routes
- [ ] No console errors

---

## BRANCH STRATEGY

**Current**: `feat/110-modern-frontend-react-ts`

**Sub-tasks**:
1. `feat/110-routing` - Add React Router
2. `feat/110-pages` - Create all page stubs
3. `feat/110-auth` - Login/signup
4. `feat/110-content` - Content CRUD
5. `feat/110-connectors` - Connector management
6. `feat/110-polish` - Styling, fixes, deploy

---

## QUICK WINS (Priorities)

1. **Get pages** - Make all routes work
2. **Fix buttons** - Make buttons navigate/function
3. **Add Auth** - Protect routes
4. **Connect backend** - Real data

---

**Next**: Do you want me to start implementing Step 1 (React Router setup)?
