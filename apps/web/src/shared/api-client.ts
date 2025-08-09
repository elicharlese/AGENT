/* Minimal shared API client for Phase 1
 * Uses VITE_API_URL when provided, otherwise falls back to same-origin.
 */
import { z } from 'zod';

// Zod schema for /health response
export const HealthSchema = z.object({
  status: z.string().optional(),
});
export type HealthOk = z.infer<typeof HealthSchema>;
export type HealthErr = { error: string };

// Zod schema for /query request
export const QueryRequestSchema = z.object({
  query: z.string(),
  domain: z.string().optional(),
  app: z.string().optional(),
});

// Zod schema for /query response
export const QueryResponseSchema = z.object({
  success: z.boolean(),
  result: z.object({
    answer: z.string(),
    domain: z.string().optional(),
    confidence: z.number().optional(),
    timestamp: z.string().optional(),
    cached: z.boolean().optional(),
  }).optional(),
  error: z.string().optional(),
});

export type QueryRequest = z.infer<typeof QueryRequestSchema>;
export type QueryResponse = z.infer<typeof QueryResponseSchema>;

const baseFromEnv = (import.meta as any).env?.VITE_API_URL
  ? String((import.meta as any).env.VITE_API_URL).replace(/\/+$/, '')
  : '';

function healthUrl(base: string) {
  return `${base || ''}/health`;
}

function queryUrl(base: string) {
  return `${base || ''}/query`;
}

async function fetchJson(url: string): Promise<unknown> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

async function fetchHealth(): Promise<HealthOk | HealthErr> {
  const url = healthUrl(baseFromEnv);
  try {
    const data = (await fetchJson(url)) as unknown;
    const parsed = HealthSchema.safeParse(data);
    if (parsed.success) {
      return parsed.data;
    }
    if (import.meta && (import.meta as any).env?.DEV) {
      // eslint-disable-next-line no-console
      console.warn('HealthSchema validation failed:', parsed.error?.issues);
    }
    return { error: 'Invalid health response' };
  } catch (e: any) {
    return { error: e?.message ?? 'Network error' };
  }
}

async function sendMessage(request: QueryRequest): Promise<QueryResponse> {
  const url = queryUrl(baseFromEnv);
  try {
    // Validate request
    const validatedRequest = QueryRequestSchema.parse(request);
    
    // Send request
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(validatedRequest),
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    // Parse response
    const data = await res.json();
    const parsed = QueryResponseSchema.safeParse(data);
    
    if (parsed.success) {
      return parsed.data;
    }
    
    if (import.meta && (import.meta as any).env?.DEV) {
      // eslint-disable-next-line no-console
      console.warn('QueryResponseSchema validation failed:', parsed.error?.issues);
    }
    
    return { success: false, error: 'Invalid response format' };
  } catch (e: any) {
    return { success: false, error: e?.message ?? 'Network error' };
  }
}

export const apiClient = {
  baseUrl: baseFromEnv,
  fetchHealth,
  sendMessage,
 };