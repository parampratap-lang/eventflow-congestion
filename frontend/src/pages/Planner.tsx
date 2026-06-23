import { useEffect, useState } from 'react';
import { api, type ForecastRequest, type ForecastResponse, type ReferenceData, type ResourceRecommendation } from '../api/client';

const demos: { label: string; data: Partial<ForecastRequest> }[] = [
  {
    label: 'Cricket Match',
    data: {
      event_type: 'planned',
      event_cause: 'public_event',
      latitude: 12.9788,
      longitude: 77.5995,
      corridor: 'CBD 2',
      zone: 'Central Zone 2',
      junction: 'QueensStatueCircle',
      police_station: 'Cubbon Park',
      description: 'Cricket match at M Chinnaswamy Stadium',
    },
  },
  {
    label: 'Political Rally',
    data: {
      event_type: 'planned',
      event_cause: 'procession',
      latitude: 12.9716,
      longitude: 77.6412,
      corridor: 'ORR East 1',
      zone: 'East Zone 1',
      junction: 'unknown',
      police_station: 'HSR Layout',
      description: 'Political procession along ORR East',
    },
  },
  {
    label: 'Construction',
    data: {
      event_type: 'planned',
      event_cause: 'construction',
      latitude: 13.04,
      longitude: 77.518,
      corridor: 'Tumkur Road',
      zone: 'North Zone 1',
      junction: 'unknown',
      police_station: 'Peenya',
      description: 'Road widening and lane closure works',
    },
  },
];

const defaultForm: ForecastRequest = {
  event_type: 'planned',
  event_cause: 'public_event',
  latitude: 12.9716,
  longitude: 77.5946,
  corridor: 'Non-corridor',
  zone: 'unknown',
  junction: 'unknown',
  police_station: 'unknown',
  start_datetime: new Date().toISOString().slice(0, 16),
  end_datetime: new Date(Date.now() + 4 * 3600000).toISOString().slice(0, 16),
  description: '',
};

export default function Planner() {
  const [form, setForm] = useState<ForecastRequest>(defaultForm);
  const [ref, setRef] = useState<ReferenceData | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [plan, setPlan] = useState<ResourceRecommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.reference().then(setRef);
  }, []);

  const submit = async () => {
    setLoading(true);
    setError('');
    try {
      const payload = {
        ...form,
        start_datetime: new Date(form.start_datetime).toISOString(),
        end_datetime: form.end_datetime ? new Date(form.end_datetime).toISOString() : undefined,
      };
      const fc = await api.forecast(payload);
      const rec = await api.recommend({ forecast: payload, forecast_result: fc });
      setForecast(fc);
      setPlan(rec);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const applyDemo = (demo: Partial<ForecastRequest>) => {
    setForm((f) => ({ ...f, ...demo }));
    setForecast(null);
    setPlan(null);
  };

  const tierColor: Record<string, string> = {
    Low: 'bg-emerald-500/20 text-emerald-300',
    Medium: 'bg-amber-500/20 text-amber-300',
    High: 'bg-orange-500/20 text-orange-300',
    Critical: 'bg-red-500/20 text-red-300',
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">Event Planner</h2>
          <p className="text-slate-400">Forecast congestion impact and generate deployment recommendations.</p>
        </div>
        <div className="flex gap-2">
          {demos.map((d) => (
            <button key={d.label} className="btn btn-ghost" onClick={() => applyDemo(d.data)}>
              {d.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card space-y-3">
          <h3 className="font-semibold">Event Details</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm">
              Type
              <select className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.event_type} onChange={(e) => setForm({ ...form, event_type: e.target.value as 'planned' | 'unplanned' })}>
                <option value="planned">planned</option>
                <option value="unplanned">unplanned</option>
              </select>
            </label>
            <label className="text-sm">
              Cause
              <select className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.event_cause} onChange={(e) => setForm({ ...form, event_cause: e.target.value })}>
                {(ref?.causes || []).map((c) => <option key={c}>{c}</option>)}
              </select>
            </label>
            <label className="text-sm">
              Corridor
              <select className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.corridor} onChange={(e) => setForm({ ...form, corridor: e.target.value })}>
                {(ref?.corridors || []).map((c) => <option key={c}>{c}</option>)}
              </select>
            </label>
            <label className="text-sm">
              Zone
              <input className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.zone} onChange={(e) => setForm({ ...form, zone: e.target.value })} />
            </label>
            <label className="text-sm">
              Latitude
              <input type="number" step="0.0001" className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.latitude} onChange={(e) => setForm({ ...form, latitude: Number(e.target.value) })} />
            </label>
            <label className="text-sm">
              Longitude
              <input type="number" step="0.0001" className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.longitude} onChange={(e) => setForm({ ...form, longitude: Number(e.target.value) })} />
            </label>
            <label className="text-sm">
              Start
              <input type="datetime-local" className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.start_datetime} onChange={(e) => setForm({ ...form, start_datetime: e.target.value })} />
            </label>
            <label className="text-sm">
              End
              <input type="datetime-local" className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" value={form.end_datetime || ''} onChange={(e) => setForm({ ...form, end_datetime: e.target.value })} />
            </label>
          </div>
          <label className="block text-sm">
            Description
            <textarea className="mt-1 w-full rounded border border-slate-600 bg-slate-900 px-2 py-2" rows={3} value={form.description || ''} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <button className="btn btn-primary" onClick={submit} disabled={loading}>
            {loading ? 'Analyzing...' : 'Generate Forecast & Plan'}
          </button>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>

        <div className="space-y-4">
          <div className="card">
            <h3 className="mb-3 font-semibold">Impact Forecast</h3>
            {!forecast && <p className="text-sm text-slate-400">Submit an event to see predicted impact.</p>}
            {forecast && (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className={`badge ${tierColor[forecast.impact_tier] || ''}`}>{forecast.impact_tier}</span>
                  <span className="text-3xl font-bold text-cyan-300">{forecast.impact_score}</span>
                  <span className="text-slate-400">/ 100</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p>Duration: <strong>{Math.round(forecast.duration_minutes)} min</strong></p>
                  <p>Closure risk: <strong>{(forecast.closure_probability * 100).toFixed(0)}%</strong></p>
                  <p>Confidence: <strong>{(forecast.confidence * 100).toFixed(0)}%</strong></p>
                  <p>Similar events: <strong>{forecast.similar_event_count}</strong></p>
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <h3 className="mb-3 font-semibold">Resource Deployment Plan</h3>
            {!plan && <p className="text-sm text-slate-400">Recommendations appear after forecast.</p>}
            {plan && (
              <div className="space-y-3 text-sm">
                <p>{plan.rationale}</p>
                <div className="grid grid-cols-3 gap-2">
                  <div className="rounded bg-slate-800/70 p-3 text-center">
                    <p className="text-2xl font-bold text-cyan-300">{plan.manpower_officers}</p>
                    <p className="text-xs text-slate-400">Officers</p>
                  </div>
                  <div className="rounded bg-slate-800/70 p-3 text-center">
                    <p className="text-2xl font-bold text-cyan-300">{plan.barricades}</p>
                    <p className="text-xs text-slate-400">Barricades</p>
                  </div>
                  <div className="rounded bg-slate-800/70 p-3 text-center">
                    <p className="text-2xl font-bold text-cyan-300">{plan.deploy_minutes_before}m</p>
                    <p className="text-xs text-slate-400">Deploy Before</p>
                  </div>
                </div>
                <div>
                  <h4 className="mb-1 font-medium text-cyan-300">Diversions</h4>
                  <ul className="space-y-1">
                    {plan.diversions.map((d) => (
                      <li key={d.corridor} className="rounded bg-slate-800/60 p-2">{d.corridor} ({d.distance_km} km) — {d.reason}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="mb-1 font-medium text-cyan-300">Timeline</h4>
                  <ul className="list-disc space-y-1 pl-5 text-slate-300">{plan.deployment_timeline.map((t) => <li key={t}>{t}</li>)}</ul>
                </div>
                <div>
                  <h4 className="mb-1 font-medium text-cyan-300">Ops Checklist</h4>
                  <ul className="list-disc space-y-1 pl-5 text-slate-300">{plan.checklist.map((t) => <li key={t}>{t}</li>)}</ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
