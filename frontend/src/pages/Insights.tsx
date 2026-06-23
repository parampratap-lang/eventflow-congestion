import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api, type InsightsResponse } from '../api/client';

export default function Insights() {
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.insights().then(setData).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!data) return <p className="text-slate-400">Loading insights...</p>;

  const causeChart = data.cause_duration
    .sort((a, b) => b.median_minutes - a.median_minutes)
    .slice(0, 10);

  const corridorChart = data.corridor_duration
    .filter((c) => c.corridor !== 'Non-corridor')
    .sort((a, b) => b.median_minutes - a.median_minutes)
    .slice(0, 8);

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold">Learning Insights</h2>
        <p className="text-slate-400">
          Post-event analytics from {data.cause_duration.reduce((a, c) => a + c.event_count, 0).toLocaleString()} historical records.
          City median resolution: <strong>{Math.round(data.overall_median_duration)} min</strong>.
        </p>
      </section>

      <div className="card">
        <h3 className="mb-3 font-semibold">Automated Learning Notes</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          {data.learning_notes.map((n) => (
            <li key={n} className="rounded-lg bg-slate-800/60 px-3 py-2">{n}</li>
          ))}
        </ul>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-4 font-semibold">Resolution Time by Cause</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={causeChart} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" tick={{ fill: '#94a3b8' }} />
                <YAxis dataKey="event_cause" type="category" width={120} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                <Bar dataKey="median_minutes" fill="#a78bfa" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="mb-4 font-semibold">Slow Corridors (Median Resolution)</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={corridorChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="corridor" tick={{ fill: '#94a3b8', fontSize: 10 }} angle={-15} textAnchor="end" height={60} />
                <YAxis tick={{ fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                <Bar dataKey="median_minutes" fill="#f97316" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="mb-3 font-semibold">Recurring Junction Hotspots</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-slate-400">
              <tr>
                <th className="py-2">Junction</th>
                <th>Events</th>
                <th>Median Duration</th>
                <th>Avg Impact</th>
              </tr>
            </thead>
            <tbody>
              {data.junction_hotspots.map((j) => (
                <tr key={j.junction} className="border-t border-slate-800">
                  <td className="py-2">{j.junction}</td>
                  <td>{j.event_count}</td>
                  <td>{Math.round(j.median_duration)} min</td>
                  <td>{j.avg_impact.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card text-sm text-slate-300">
        <h3 className="mb-2 font-semibold text-slate-100">Model Performance (validation)</h3>
        <pre className="overflow-x-auto rounded bg-slate-950/70 p-3 text-xs">
          {JSON.stringify(data.training_metrics, null, 2)}
        </pre>
      </div>
    </div>
  );
}
