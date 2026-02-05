/**
 * Main Layout Component - Wraps authenticated pages
 */
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Sidebar from '../Sidebar/Sidebar';
import './Layout.css';

function Layout() {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="app-layout">
            <Sidebar />
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}

export default Layout;
