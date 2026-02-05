/**
 * Sidebar Navigation Component
 */
import { NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Package,
    TrendingUp,
    AlertTriangle,
    ShoppingCart,
    Users,
    FileText,
    Settings,
    LogOut,
    BarChart3
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import './Sidebar.css';

function Sidebar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/products', icon: Package, label: 'Products' },
        { path: '/forecasts', icon: TrendingUp, label: 'Forecasts' },
        { path: '/alerts', icon: AlertTriangle, label: 'Alerts' },
        { path: '/purchase-orders', icon: ShoppingCart, label: 'Purchase Orders' },
        { path: '/suppliers', icon: Users, label: 'Suppliers' },
        { path: '/sales', icon: BarChart3, label: 'Sales' },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo">
                    <TrendingUp className="logo-icon" />
                    <span className="logo-text">ForecastAI</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <ul className="nav-list">
                    {navItems.map((item) => (
                        <li key={item.path}>
                            <NavLink
                                to={item.path}
                                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                            >
                                <item.icon className="nav-icon" />
                                <span>{item.label}</span>
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>

            <div className="sidebar-footer">
                <div className="user-info">
                    <div className="user-avatar">
                        {user?.name?.[0] || 'U'}
                    </div>
                    <div className="user-details">
                        <span className="user-name">{user?.name || 'User'}</span>
                        <span className="user-email">{user?.email || ''}</span>
                    </div>
                </div>
                <button className="logout-btn" onClick={handleLogout} title="Logout">
                    <LogOut size={18} />
                </button>
            </div>
        </aside>
    );
}

export default Sidebar;
