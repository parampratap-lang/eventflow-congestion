import { NavLink, Outlet } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/explorer', label: 'Event Explorer' },
  { to: '/planner', label: 'Event Planner' },
  { to: '/insights', label: 'Learning Insights' },
];

export default function Layout() {
  return (
    <div className="min-h-screen text-slate-100">
      <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur sticky top-0 z-50">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">Bangalore Traffic Ops</p>
            <h1 className="text-xl font-bold">EventFlow</h1>
          </div>
          <nav className="flex gap-2">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === '/'}
                className={({ isActive }) =>
                  `btn btn-ghost ${isActive ? 'border-cyan-500 text-cyan-300' : ''}`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
