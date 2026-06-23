import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from 'recharts';
import { api, type DashboardStats } from '../api/client';

const COLORS = ['#22d3ee', '#f97316', '#a78bfa', '#34d399', '#f472b6'];

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.stats().then(setStats).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!stats) return <p className="text-slate-400">Loading dashboard...</p>;

  const kpis = [
    { label: 'Total Events', value: stats.total_events.toLocaleString() },
    { label: 'Planned Events', value: stats.planned_events.toLocaleString() },
    { label: 'Active Now', value: stats.active_events.toLocaleString() },
    { label: 'Median Resolution', value: `${stats.avg_resolution_minutes} min` },
  ];

  const pieData = [
    { name: 'Planned', value: stats.planned_vs_unplanned.planned },
    { name: 'Unplanned', value: stats.planned_vs_unplanned.unplanned },
  ];

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-2xl font-semibold">Operations Dashboard</h2>
        <p className="text-slate-400">
          Historical Astram traffic events powering forecast and deployment recommendations.
        </p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((k) => (
          <div key={k.label} className="card">
            <p className="text-sm text-slate-400">{k.label}</p>
            <p className="mt-1 text-3xl font-bold text-cyan-300">{k.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <h3 className="mb-4 font-semibold">Top Corridors by Incident Volume</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.top_corridors}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="corridor" tick={{ fill: '#94a3b8', fontSize: 11 }} angle={-20} textAnchor="end" height={70} />
                <YAxis tick={{ fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                <Bar dataKey="count" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 className="mb-4 font-semibold">Planned vs Unplanned</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="mb-3 font-semibold">Top Event Causes</h3>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {stats.cause_breakdown.map((c) => (
            <div key={c.cause} className="flex items-center justify-between rounded-lg bg-slate-800/60 px-3 py-2">
              <span>{c.cause}</span>
              <span className="badge bg-cyan-500/20 text-cyan-300">{c.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
