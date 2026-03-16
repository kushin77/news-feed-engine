/**
 * Social media connector types and interfaces
 */

export type ConnectorStatus = 'connected' | 'disconnected' | 'error' | 'pending'

export type ConnectorPlatform = 'instagram' | 'tiktok' | 'youtube' | 'twitter' | 'facebook' | 'threads'

export interface ConnectorConfig {
  id: string
  platform: ConnectorPlatform
  name: string
  icon: string
  status: ConnectorStatus
  handle?: string
  lastSync?: Date
  followerCount?: number
  error?: string
}

export interface ConnectorCredentials {
  accessToken: string
  refreshToken?: string
  expiresAt?: Date
  scope?: string[]
}

export interface SocialPost {
  id: string
  platform: ConnectorPlatform
  content: string
  mediaUrl?: string
  publishedAt: Date
  engagement: {
    likes: number
    comments: number
    shares: number
    views: number
  }
}

export interface ConnectorCapabilities {
  canPublish: boolean
  canSchedule: boolean
  canAnalytics: boolean
  maxMediaSize: number // MB
  supportedFormats: string[]
}

export const CONNECTOR_CAPABILITIES: Record<ConnectorPlatform, ConnectorCapabilities> = {
  instagram: {
    canPublish: true,
    canSchedule: true,
    canAnalytics: true,
    maxMediaSize: 8,
    supportedFormats: ['jpg', 'png', 'mp4', 'mov'],
  },
  tiktok: {
    canPublish: true,
    canSchedule: false,
    canAnalytics: true,
    maxMediaSize: 287.6,
    supportedFormats: ['mp4', 'mov'],
  },
  youtube: {
    canPublish: true,
    canSchedule: true,
    canAnalytics: true,
    maxMediaSize: 256 * 1024, // 256GB
    supportedFormats: ['mp4', 'mov', 'avi', 'mkv'],
  },
  twitter: {
    canPublish: true,
    canSchedule: true,
    canAnalytics: true,
    maxMediaSize: 15,
    supportedFormats: ['jpg', 'png', 'gif', 'mp4'],
  },
  facebook: {
    canPublish: true,
    canSchedule: true,
    canAnalytics: true,
    maxMediaSize: 4,
    supportedFormats: ['jpg', 'png', 'mp4'],
  },
  threads: {
    canPublish: true,
    canSchedule: false,
    canAnalytics: false,
    maxMediaSize: 8,
    supportedFormats: ['jpg', 'png'],
  },
}
