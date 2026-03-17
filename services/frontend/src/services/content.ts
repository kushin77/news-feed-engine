// TODO: Import when making real API calls
// import { createAPIClient } from './api'
// const apiClient = createAPIClient()

/**
 * Content API service
 *
 * Handles all content creation and management API calls.
 * TODO: Backend endpoints (not yet implemented)
 */

export interface CreateContentRequest {
  title: string
  content: string
  mediaUrls?: string[]
  scheduledAt?: Date
  platforms?: string[]
}

export interface PublishContentRequest {
  contentId: string
  platforms: string[]
  scheduledAt?: Date
}

/**
 * Create new content
 * @param request Content creation request
 * @returns Created content with ID
 * @throws Error if creation fails
 *
 * Endpoint: POST /api/v1/content
 * TODO: Implement backend endpoint
 */
export async function createContent(request: CreateContentRequest): Promise<{ id: string; status: string }> {
  try {
    // TODO: Replace with actual API call
    // const response = await apiClient.post<{ id: string; status: string }>('/content', request)
    // return response.data

    console.log('[API] POST /api/v1/content', request)
    await new Promise((resolve) => setTimeout(resolve, 500))

    return {
      id: `content_${Date.now()}`,
      status: 'draft',
    }
  } catch (error) {
    console.error('Failed to create content:', error)
    throw error
  }
}

/**
 * Publish content to platforms
 * @param request Publish request
 * @returns Publication job status
 * @throws Error if publishing fails
 *
 * Endpoint: POST /api/v1/content/{id}/publish
 * TODO: Implement backend endpoint
 */
export async function publishContent(request: PublishContentRequest): Promise<{ jobId: string; status: string }> {
  try {
    // TODO: Replace with actual API call
    // const response = await apiClient.post<{ job_id: string; status: string }>(
    //   `/content/${request.contentId}/publish`,
    //   { platforms: request.platforms, scheduled_at: request.scheduledAt }
    // )
    // return { jobId: response.data.job_id, status: response.data.status }

    console.log('[API] POST /api/v1/content/:id/publish', request)
    await new Promise((resolve) => setTimeout(resolve, 800))

    return {
      jobId: `job_${Date.now()}`,
      status: request.scheduledAt ? 'scheduled' : 'published',
    }
  } catch (error) {
    console.error('Failed to publish content:', error)
    throw error
  }
}

/**
 * Schedule content for later publishing
 * @param contentId Content ID
 * @param platforms Platforms to publish to
 * @param scheduledAt Scheduled publish time
 * @returns Scheduled content info
 * @throws Error if scheduling fails
 *
 * Endpoint: POST /api/v1/content/{id}/schedule
 * TODO: Implement backend endpoint
 */
export async function scheduleContent(
  contentId: string,
  platforms: string[],
  scheduledAt: Date,
): Promise<{ contentId: string; scheduledAt: Date; platforms: string[] }> {
  try {
    // TODO: Replace with actual API call
    // await apiClient.post(`/content/${contentId}/schedule`, {
    //   platforms,
    //   scheduled_at: scheduledAt.toISOString()
    // })

    console.log('[API] POST /api/v1/content/:id/schedule', { contentId, platforms, scheduledAt })
    await new Promise((resolve) => setTimeout(resolve, 600))

    return { contentId, scheduledAt, platforms }
  } catch (error) {
    console.error('Failed to schedule content:', error)
    throw error
  }
}

/**
 * Get content details
 * @param contentId Content ID
 * @returns Content details
 * @throws Error if request fails
 *
 * Endpoint: GET /api/v1/content/{id}
 * TODO: Implement backend endpoint
 */
export async function getContent(contentId: string): Promise<{ id: string; title: string; status: string }> {
  try {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`/content/${contentId}`)
    // return response.data

    console.log(`[API] GET /api/v1/content/${contentId}`)

    return {
      id: contentId,
      title: 'Sample Content',
      status: 'draft',
    }
  } catch (error) {
    console.error(`Failed to get content ${contentId}:`, error)
    throw error
  }
}

/**
 * List content
 * @param limit Number of items
 * @param offset Pagination offset
 * @returns Array of content items
 * @throws Error if request fails
 *
 * Endpoint: GET /api/v1/content
 * TODO: Implement backend endpoint
 */
export async function listContent(limit = 20, offset = 0): Promise<Array<{ id: string; title: string; status: string }>> {
  try {
    // TODO: Replace with actual API call
    // const response = await apiClient.get(`/content?limit=${limit}&offset=${offset}`)
    // return response.data.items

    console.log(`[API] GET /api/v1/content?limit=${limit}&offset=${offset}`)

    return []
  } catch (error) {
    console.error('Failed to list content:', error)
    throw error
  }
}

/**
 * Delete content
 * @param contentId Content ID
 * @throws Error if deletion fails
 *
 * Endpoint: DELETE /api/v1/content/{id}
 * TODO: Implement backend endpoint
 */
export async function deleteContent(contentId: string): Promise<void> {
  try {
    // TODO: Replace with actual API call
    // await apiClient.delete(`/content/${contentId}`)

    console.log(`[API] DELETE /api/v1/content/${contentId}`)
    await new Promise((resolve) => setTimeout(resolve, 400))
  } catch (error) {
    console.error(`Failed to delete content ${contentId}:`, error)
    throw error
  }
}
