const API_BASE = import.meta.env.VITE_API_BASE || '';

export interface EventSummary {
  id: string;
  event_type: string;
  event_cause: string;
  latitude: number;
  longitude: number;
  address?: string;
  corridor: string;
  zone: string;
  junction: string;
  police_station: string;
  priority: string;
  status: string;
  requires_road_closure: boolean;
  start_datetime?: string;
  end_datetime?: string;
  description?: string;
  impact_score?: number;
  duration_minutes?: number;
}

export interface ForecastRequest {
  event_type: 'planned' | 'unplanned';
  event_cause: string;
  latitude: number;
  longitude: number;
  corridor: string;
  zone: string;
  junction: string;
  police_station: string;
  start_datetime: string;
  end_datetime?: string;
  description?: string;
}

export interface ForecastResponse {
  impact_score: number;
  impact_tier: string;
  duration_minutes: number;
  closure_probability: number;
  confidence: number;
  similar_event_count: number;
}

export interface ResourceRecommendation {
  manpower_officers: number;
  barricades: number;
  diversions: { corridor: string; reason: string; distance_km: number }[];
  deploy_minutes_before: number;
  deployment_timeline: string[];
  checklist: string[];
  rationale: string;
}

export interface DashboardStats {
  total_events: number;
  planned_events: number;
  unplanned_events: number;
  active_events: number;
  avg_resolution_minutes: number;
  top_corridors: { corridor: string; count: number }[];
  planned_vs_unplanned: { planned: number; unplanned: number };
  cause_breakdown: { cause: string; count: number }[];
}

export interface ReferenceData {
  corridors: string[];
  zones: string[];
  causes: string[];
  junctions: string[];
  event_types: string[];
}

export interface InsightsResponse {
  cause_duration: { event_cause: string; avg_minutes: number; median_minutes: number; event_count: number }[];
  corridor_duration: { corridor: string; avg_minutes: number; median_minutes: number; event_count: number }[];
  zone_stats: { zone: string; total_events: number; planned: number; unplanned: number; avg_duration: number }[];
  junction_hotspots: { junction: string; event_count: number; median_duration: number; avg_impact: number }[];
  training_metrics: Record<string, unknown>;
  overall_median_duration: number;
  learning_notes: string[];
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const api = {
  health: () => get<{ status: string }>('/api/health'),
  stats: () => get<DashboardStats>('/api/stats'),
  reference: () => get<ReferenceData>('/api/reference'),
  events: (params: Record<string, string | number>) => {
    const qs = new URLSearchParams(
      Object.entries(params).map(([k, v]) => [k, String(v)])
    ).toString();
    return get<{ total: number; page: number; page_size: number; items: EventSummary[] }>(
      `/api/events?${qs}`
    );
  },
  event: (id: string) =>
    get<EventSummary & { similar_events: EventSummary[] }>(`/api/events/${id}`),
  forecast: (body: ForecastRequest) => post<ForecastResponse>('/api/forecast', body),
  recommend: (body: { forecast: ForecastRequest; forecast_result?: ForecastResponse }) =>
    post<ResourceRecommendation>('/api/recommend', body),
  insights: () => get<InsightsResponse>('/api/insights'),
};
