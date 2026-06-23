import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import type { EventSummary } from '../api/client';
import 'leaflet/dist/leaflet.css';

const BANGALORE_CENTER: [number, number] = [12.9716, 77.5946];

function FitBounds({ events }: { events: EventSummary[] }) {
  const map = useMap();
  useEffect(() => {
    if (!events.length) return;
    const lats = events.map((e) => e.latitude);
    const lngs = events.map((e) => e.longitude);
    map.fitBounds([
      [Math.min(...lats), Math.min(...lngs)],
      [Math.max(...lats), Math.max(...lngs)],
    ]);
  }, [events, map]);
  return null;
}

const colorByType = (type: string) => (type === 'planned' ? '#22d3ee' : '#f97316');

export default function EventMap({
  events,
  selectedId,
  onSelect,
  height = '520px',
}: {
  events: EventSummary[];
  selectedId?: string;
  onSelect?: (e: EventSummary) => void;
  height?: string;
}) {
  return (
    <div style={{ height }} className="overflow-hidden rounded-xl border border-slate-700">
      <MapContainer center={BANGALORE_CENTER} zoom={11} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        <FitBounds events={events} />
        {events.map((e) => (
          <CircleMarker
            key={e.id}
            center={[e.latitude, e.longitude]}
            radius={selectedId === e.id ? 10 : 6}
            pathOptions={{
              color: colorByType(e.event_type),
              fillColor: colorByType(e.event_type),
              fillOpacity: 0.8,
              weight: selectedId === e.id ? 3 : 1,
            }}
            eventHandlers={{ click: () => onSelect?.(e) }}
          >
            <Popup>
              <div className="text-sm text-slate-900">
                <strong>{e.event_cause}</strong>
                <p>{e.corridor}</p>
                <p>{e.status}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
