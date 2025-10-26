/**
 * API client for the Collaborative Worldbuilding backend.
 *
 * Reconstructed from call-site usage + backend URL routes (collab/urls.py).
 *
 * Configuration:
 *   - VITE_API_BASE_URL controls the base URL.
 *     Dev default:  /api/v1   (vite proxies /api -> http://localhost:8000)
 *     Prod default: /api/v1   (frontend nginx proxies /api -> backend Cloud Run)
 *
 * Auth: stores access/refresh tokens in localStorage; an axios response
 * interceptor transparently refreshes the access token on 401 once per
 * request before retrying.
 *
 * List methods (worldsAPI.list, contentAPI.list, tagsAPI.list) return the
 * unwrapped .results array from DRF pagination, because every call site
 * treats them as plain arrays. If a future caller needs pagination metadata
 * (count/next/previous), call the axios instance (default export) directly.
 */
import axios from 'axios'
import type {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
import type {
  AuthTokens,
  Content,
  ContentType,
  CreateContentData,
  CreateWorldData,
  LoginCredentials,
  PaginatedResponse,
  RegisterData,
  Tag,
  User,
  UserProfile,
  World,
} from '@/types'

// ---------------------------------------------------------------------------
// Constants & helpers
// ---------------------------------------------------------------------------

const BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || '/api/v1'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

// Map singular ContentType (UI) to plural URL segment (backend).
const CONTENT_PLURAL: Record<ContentType, string> = {
  page: 'pages',
  essay: 'essays',
  character: 'characters',
  story: 'stories',
  image: 'images',
}

const pluralFor = (t: ContentType): string => CONTENT_PLURAL[t]

const unwrap = <T,>(data: PaginatedResponse<T> | T[]): T[] =>
  Array.isArray(data) ? data : data.results

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  // 30s is generous; image uploads can be slow.
  timeout: 30000,
})

// Attach Bearer token on every request.
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Single-flight refresh: if multiple requests 401 simultaneously, all wait
// on the same refresh promise instead of triggering a refresh storm.
let refreshInFlight: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  if (refreshInFlight) return refreshInFlight

  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
  if (!refresh) return null

  refreshInFlight = (async () => {
    try {
      const resp = await axios.post<{ access: string; refresh?: string }>(
        `${BASE_URL}/auth/refresh/`,
        { refresh },
      )
      const { access, refresh: newRefresh } = resp.data
      localStorage.setItem(ACCESS_TOKEN_KEY, access)
      if (newRefresh) localStorage.setItem(REFRESH_TOKEN_KEY, newRefresh)
      return access
    } catch {
      // Refresh failed - clear tokens; caller will surface auth error.
      localStorage.removeItem(ACCESS_TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      return null
    } finally {
      refreshInFlight = null
    }
  })()

  return refreshInFlight
}

// Response interceptor: on 401, try once to refresh and replay the request.
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retried?: boolean })
      | undefined

    if (
      error.response?.status === 401 &&
      original &&
      !original._retried &&
      // Don't try to refresh if the failing request IS the refresh.
      !original.url?.includes('/auth/refresh/')
    ) {
      original._retried = true
      const newAccess = await refreshAccessToken()
      if (newAccess) {
        original.headers = original.headers ?? {}
        ;(original.headers as Record<string, string>).Authorization =
          `Bearer ${newAccess}`
        return api.request(original)
      }
    }
    return Promise.reject(error)
  },
)

// ---------------------------------------------------------------------------
// Response types not in @/types
// ---------------------------------------------------------------------------

export interface LoginResponse {
  access: string
  refresh: string
  user: User & { profile: UserProfile }
}

export interface RegisterResponse {
  user: User & { profile: UserProfile }
  // Some backends auto-login; some don't. Both cases handled by AuthContext.
  tokens?: AuthTokens
  message?: string
}

export interface ProfileResponse {
  user: User
  profile: UserProfile
}

export interface RefreshResponse {
  access: string
  refresh?: string
}

export interface AddLinksItem {
  content_type: ContentType
  content_id: number
}

// ---------------------------------------------------------------------------
// authAPI
// ---------------------------------------------------------------------------

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>('/auth/login/', credentials)
    return data
  },

  async register(payload: RegisterData): Promise<RegisterResponse> {
    const { data } = await api.post<RegisterResponse>(
      '/auth/register/',
      payload,
    )
    return data
  },

  async refresh(refresh: string): Promise<RefreshResponse> {
    const { data } = await api.post<RefreshResponse>('/auth/refresh/', {
      refresh,
    })
    return data
  },

  async logout(refresh?: string): Promise<void> {
    // Fire-and-forget by callers; backend may 200 or 205.
    await api.post('/auth/logout/', refresh ? { refresh } : {})
  },

  async getProfile(): Promise<ProfileResponse> {
    const { data } = await api.get<ProfileResponse>('/auth/profile/')
    return data
  },
}

// ---------------------------------------------------------------------------
// worldsAPI
// ---------------------------------------------------------------------------

export const worldsAPI = {
  async list(params?: {
    search?: string
    creator?: string
    is_public?: boolean
    page?: number
  }): Promise<World[]> {
    const { data } = await api.get<PaginatedResponse<World> | World[]>(
      '/worlds/',
      { params },
    )
    return unwrap<World>(data)
  },

  async get(id: number): Promise<World> {
    const { data } = await api.get<World>(`/worlds/${id}/`)
    return data
  },

  async create(payload: CreateWorldData): Promise<World> {
    const { data } = await api.post<World>('/worlds/', payload)
    return data
  },
}

// ---------------------------------------------------------------------------
// contentAPI (pages, essays, characters, stories, images)
// ---------------------------------------------------------------------------

export interface ContentListParams {
  search?: string
  author?: string
  tags?: string
  ordering?: string
  page?: number
}

export const contentAPI = {
  async list(
    worldId: number,
    contentType: ContentType,
    params?: ContentListParams,
  ): Promise<Content[]> {
    const { data } = await api.get<PaginatedResponse<Content> | Content[]>(
      `/worlds/${worldId}/${pluralFor(contentType)}/`,
      { params },
    )
    return unwrap<Content>(data)
  },

  async get(
    worldId: number,
    contentType: ContentType,
    contentId: number,
  ): Promise<Content> {
    const { data } = await api.get<Content>(
      `/worlds/${worldId}/${pluralFor(contentType)}/${contentId}/`,
    )
    return data
  },

  async create(
    worldId: number,
    contentType: ContentType,
    payload: CreateContentData | FormData,
  ): Promise<Content> {
    const isForm =
      typeof FormData !== 'undefined' && payload instanceof FormData
    const config: AxiosRequestConfig | undefined = isForm
      ? { headers: { 'Content-Type': 'multipart/form-data' } }
      : undefined
    const { data } = await api.post<Content>(
      `/worlds/${worldId}/${pluralFor(contentType)}/`,
      payload,
      config,
    )
    return data
  },

  async addTags(
    worldId: number,
    contentType: ContentType,
    contentId: number,
    tagNames: string[],
  ): Promise<{ added: string[]; skipped?: string[] }> {
    const { data } = await api.post<{ added: string[]; skipped?: string[] }>(
      `/worlds/${worldId}/${pluralFor(contentType)}/${contentId}/add-tags/`,
      { tag_names: tagNames },
    )
    return data
  },

  async addLinks(
    worldId: number,
    contentType: ContentType,
    contentId: number,
    links: AddLinksItem[],
  ): Promise<{ added: number; results: unknown[] }> {
    const { data } = await api.post<{ added: number; results: unknown[] }>(
      `/worlds/${worldId}/${pluralFor(contentType)}/${contentId}/add-links/`,
      { links },
    )
    return data
  },
}

// ---------------------------------------------------------------------------
// tagsAPI
// ---------------------------------------------------------------------------

export const tagsAPI = {
  async list(
    worldId: number,
    params?: { search?: string; ordering?: string },
  ): Promise<Tag[]> {
    const { data } = await api.get<PaginatedResponse<Tag> | Tag[]>(
      `/worlds/${worldId}/tags/`,
      { params },
    )
    return unwrap<Tag>(data)
  },

  // Backend exposes tag-by-name at /worlds/(world_pk)/tags/by-name/(tag_name)/

  // Backend exposes tag-by-name at /worlds/(world_pk)/tags/by-name/(tag_name)/
  async get(worldId: number, tagName: string): Promise<Tag> {
    const { data } = await api.get<Tag>(
      `/worlds/${worldId}/tags/by-name/${encodeURIComponent(tagName)}/`,
    )
    return data
  },
}

// ---------------------------------------------------------------------------
// Default export - escape hatch for callers that need the raw axios instance.
// ---------------------------------------------------------------------------

export default api
