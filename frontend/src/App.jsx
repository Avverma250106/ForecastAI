/**
 * AI Demand Forecasting Platform - Main Application
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import Products from './pages/Products/Products';
import Forecasts from './pages/Forecasts/Forecasts';
import Alerts from './pages/Alerts/Alerts';
import PurchaseOrders from './pages/PurchaseOrders/PurchaseOrders';
import Suppliers from './pages/Suppliers/Suppliers';
import Sales from './pages/Sales/Sales';
import './index.css';

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Auth Route wrapper (redirect if already logged in)
function AuthRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/login" element={
        <AuthRoute>
          <Login />
        </AuthRoute>
      } />
      <Route path="/register" element={
        <AuthRoute>
          <Register />
        </AuthRoute>
      } />

      {/* Protected Routes */}
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/forecasts" element={<Forecasts />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/purchase-orders" element={<PurchaseOrders />} />
        <Route path="/suppliers" element={<Suppliers />} />
        <Route path="/sales" element={<Sales />} />
      </Route>

      {/* Catch all - redirect to dashboard */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
