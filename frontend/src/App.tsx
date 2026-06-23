import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Explorer from './pages/Explorer';
import Planner from './pages/Planner';
import Insights from './pages/Insights';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/planner" element={<Planner />} />
          <Route path="/insights" element={<Insights />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
