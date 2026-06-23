import { useEffect, useState } from 'react';
import EventMap from '../components/EventMap';
import { api, type EventSummary } from '../api/client';

export default function Explorer() {
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [selected, setSelected] = useState<EventSummary | null>(null);
  const [similar, setSimilar] = useState<EventSummary[]>([]);
  const [filters, setFilters] = useState({ event_type: '', event_cause: '', corridor: '', status: '' });
  const [ref, setRef] = useState<{ corridors: string[]; causes: string[] }>({ corridors: [], causes: [] });

  useEffect(() => {
    api.reference().then((r) => setRef({ corridors: r.corridors, causes: r.causes }));
  }, []);

  useEffect(() => {
    const params: Record<string, string | number> = { page: 1, page_size: 300 };
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params[k] = v;
    });
    api.events(params).then((r) => {
      setEvents(r.items);
      setSelected(null);
      setSimilar([]);
    });
  }, [filters]);

  const onSelect = async (e: EventSummary) => {
    setSelected(e);
    const detail = await api.event(e.id);
    setSimilar(detail.similar_events || []);
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold">Event Explorer</h2>
        <p className="text-slate-400">Map historical planned and unplanned congestion events across Bangalore.</p>
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        {(['event_type', 'event_cause', 'corridor', 'status'] as const).map((key) => (
          <select
            key={key}
            className="rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm"
            value={filters[key]}
            onChange={(e) => setFilters((f) => ({ ...f, [key]: e.target.value }))}
          >
            <option value="">{key.replace('_', ' ')} (all)</option>
            {(key === 'event_type'
              ? ['planned', 'unplanned']
              : key === 'status'
                ? ['active', 'closed', 'resolved']
                : key === 'corridor'
                  ? ref.corridors
                  : ref.causes
            ).map((v) => (
              <option key={v} value={v}>
                {v}
              </option>
            ))}
          </select>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <EventMap events={events} selectedId={selected?.id} onSelect={onSelect} />
        </div>
        <div className="card space-y-3">
          <h3 className="font-semibold">Event Detail</h3>
          {!selected && <p className="text-sm text-slate-400">Click a map marker to inspect an event.</p>}
          {selected && (
            <>
              <div className="space-y-1 text-sm">
                <p><span className="text-slate-400">ID:</span> {selected.id}</p>
                <p><span className="text-slate-400">Type:</span> {selected.event_type}</p>
                <p><span className="text-slate-400">Cause:</span> {selected.event_cause}</p>
                <p><span className="text-slate-400">Corridor:</span> {selected.corridor}</p>
                <p><span className="text-slate-400">Status:</span> {selected.status}</p>
                <p><span className="text-slate-400">Priority:</span> {selected.priority}</p>
                {selected.description && <p className="text-slate-300">{selected.description}</p>}
              </div>
              {similar.length > 0 && (
                <div>
                  <h4 className="mb-2 text-sm font-medium text-cyan-300">Similar Historical Events</h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {similar.map((s) => (
                      <li key={s.id} className="rounded bg-slate-800/70 p-2">
                        {s.event_cause} · {s.corridor} · {s.status}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
