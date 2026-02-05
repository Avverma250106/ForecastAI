/**
 * Dashboard Page - Main Overview
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
    Package,
    TrendingUp,
    AlertTriangle,
    DollarSign,
    ShoppingCart,
    ArrowUpRight,
    ArrowDownRight,
    RefreshCw,
    Bell,
    ChevronRight
} from 'lucide-react';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import { dashboardAPI, alertsAPI } from '../../services/api';
import './Dashboard.css';

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [salesChart, setSalesChart] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [topProducts, setTopProducts] = useState([]);
    const [inventoryHealth, setInventoryHealth] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6366f1'];

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [statsRes, salesRes, alertsRes, productsRes, healthRes] = await Promise.all([
                dashboardAPI.getStats().catch(() => ({ data: null })),
                dashboardAPI.getSalesChart(30).catch(() => ({ data: [] })),
                dashboardAPI.getAlerts(5).catch(() => ({ data: [] })),
                dashboardAPI.getTopProducts(5).catch(() => ({ data: [] })),
                dashboardAPI.getInventoryHealth().catch(() => ({ data: null })),
            ]);

            setStats(statsRes.data);
            setSalesChart(salesRes.data || []);
            setAlerts(alertsRes.data || []);
            setTopProducts(productsRes.data || []);
            setInventoryHealth(healthRes.data);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRefresh = async () => {
        setRefreshing(true);
        await fetchDashboardData();
        setRefreshing(false);
    };

    const getAlertColor = (severity) => {
        switch (severity) {
            case 'critical': return 'danger';
            case 'warning': return 'warning';
            default: return 'info';
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    // Mock data for demo if API returns empty
    const defaultStats = {
        total_products: 156,
        total_revenue: 284500,
        active_alerts: 12,
        pending_orders: 8,
        low_stock_items: 23,
        revenue_change: 12.5,
        forecast_accuracy: 94.2
    };

    const displayStats = stats || defaultStats;

    const mockSalesData = salesChart.length > 0 ? salesChart : [
        { date: 'Jan 1', sales: 4200, forecast: 4000 },
        { date: 'Jan 8', sales: 3800, forecast: 4100 },
        { date: 'Jan 15', sales: 5100, forecast: 4800 },
        { date: 'Jan 22', sales: 4600, forecast: 4500 },
        { date: 'Jan 29', sales: 5400, forecast: 5200 },
    ];

    const mockPieData = inventoryHealth || [
        { name: 'Healthy', value: 65, color: '#10b981' },
        { name: 'Low Stock', value: 20, color: '#f59e0b' },
        { name: 'Critical', value: 10, color: '#ef4444' },
        { name: 'Overstock', value: 5, color: '#6366f1' },
    ];

    return (
        <div className="dashboard-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Dashboard</h1>
                    <p className="page-subtitle">Welcome back! Here's your inventory overview</p>
                </div>
                <div className="page-actions">
                    <button className="btn btn-secondary" onClick={handleRefresh} disabled={refreshing}>
                        <RefreshCw size={18} className={refreshing ? 'spin' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon primary">
                        <Package size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Total Products</span>
                        <span className="stat-value">{displayStats.total_products?.toLocaleString()}</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon success">
                        <DollarSign size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Total Revenue</span>
                        <span className="stat-value">${displayStats.total_revenue?.toLocaleString()}</span>
                        <span className={`stat-change ${displayStats.revenue_change >= 0 ? 'positive' : 'negative'}`}>
                            {displayStats.revenue_change >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                            {Math.abs(displayStats.revenue_change || 0)}% from last month
                        </span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon warning">
                        <AlertTriangle size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Active Alerts</span>
                        <span className="stat-value">{displayStats.active_alerts}</span>
                        <span className="stat-change text-muted">
                            {displayStats.low_stock_items} low stock items
                        </span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon info">
                        <TrendingUp size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Forecast Accuracy</span>
                        <span className="stat-value">{displayStats.forecast_accuracy}%</span>
                        <span className="stat-change positive">
                            <ArrowUpRight size={14} />
                            2.3% improvement
                        </span>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="dashboard-grid">
                {/* Sales Trend Chart */}
                <div className="content-card">
                    <div className="content-card-header">
                        <h3 className="content-card-title">Sales vs Forecast</h3>
                        <Link to="/forecasts" className="btn btn-ghost btn-sm">
                            View All <ChevronRight size={16} />
                        </Link>
                    </div>
                    <div className="content-card-body">
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={mockSalesData}>
                                    <defs>
                                        <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                                    <YAxis stroke="#64748b" fontSize={12} />
                                    <Tooltip
                                        contentStyle={{
                                            background: '#1e293b',
                                            border: '1px solid #334155',
                                            borderRadius: '8px',
                                            color: '#f8fafc'
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="sales"
                                        stroke="#6366f1"
                                        fill="url(#salesGradient)"
                                        strokeWidth={2}
                                        name="Actual Sales"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="forecast"
                                        stroke="#10b981"
                                        fill="url(#forecastGradient)"
                                        strokeWidth={2}
                                        strokeDasharray="5 5"
                                        name="Forecast"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Inventory Health */}
                <div className="content-card">
                    <div className="content-card-header">
                        <h3 className="content-card-title">Inventory Health</h3>
                    </div>
                    <div className="content-card-body">
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height={200}>
                                <PieChart>
                                    <Pie
                                        data={mockPieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {mockPieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{
                                            background: '#1e293b',
                                            border: '1px solid #334155',
                                            borderRadius: '8px',
                                            color: '#f8fafc'
                                        }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="pie-legend">
                            {mockPieData.map((item, index) => (
                                <div key={index} className="legend-item">
                                    <span className="legend-dot" style={{ background: item.color || COLORS[index] }}></span>
                                    <span className="legend-label">{item.name}</span>
                                    <span className="legend-value">{item.value}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Recent Alerts */}
                <div className="content-card">
                    <div className="content-card-header">
                        <h3 className="content-card-title">
                            <Bell size={18} /> Recent Alerts
                        </h3>
                        <Link to="/alerts" className="btn btn-ghost btn-sm">
                            View All <ChevronRight size={16} />
                        </Link>
                    </div>
                    <div className="content-card-body">
                        {alerts.length > 0 ? (
                            <div className="alerts-list">
                                {alerts.slice(0, 5).map((alert) => (
                                    <div key={alert.id} className={`alert-item ${getAlertColor(alert.severity)}`}>
                                        <AlertTriangle size={16} />
                                        <div className="alert-content">
                                            <span className="alert-title">{alert.title || alert.message}</span>
                                            <span className="alert-meta">{alert.product_name || 'System Alert'}</span>
                                        </div>
                                        <span className={`badge badge-${getAlertColor(alert.severity)}`}>
                                            {alert.severity || 'info'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="alerts-list">
                                <div className="alert-item warning">
                                    <AlertTriangle size={16} />
                                    <div className="alert-content">
                                        <span className="alert-title">Low stock warning</span>
                                        <span className="alert-meta">Widget Pro X - Only 5 units left</span>
                                    </div>
                                    <span className="badge badge-warning">warning</span>
                                </div>
                                <div className="alert-item danger">
                                    <AlertTriangle size={16} />
                                    <div className="alert-content">
                                        <span className="alert-title">Stockout imminent</span>
                                        <span className="alert-meta">Gadget Plus - 2 days of stock</span>
                                    </div>
                                    <span className="badge badge-danger">critical</span>
                                </div>
                                <div className="alert-item info">
                                    <AlertTriangle size={16} />
                                    <div className="alert-content">
                                        <span className="alert-title">Reorder recommended</span>
                                        <span className="alert-meta">Basic Widget - Lead time approaching</span>
                                    </div>
                                    <span className="badge badge-info">info</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Top Products */}
                <div className="content-card">
                    <div className="content-card-header">
                        <h3 className="content-card-title">Top Selling Products</h3>
                        <Link to="/products" className="btn btn-ghost btn-sm">
                            View All <ChevronRight size={16} />
                        </Link>
                    </div>
                    <div className="content-card-body">
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Sales</th>
                                        <th>Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {topProducts.length > 0 ? topProducts.map((product) => (
                                        <tr key={product.id}>
                                            <td>{product.name}</td>
                                            <td>{product.total_sales?.toLocaleString()}</td>
                                            <td>${product.total_revenue?.toLocaleString()}</td>
                                        </tr>
                                    )) : (
                                        <>
                                            <tr><td>Widget Pro X</td><td>1,234</td><td>$24,680</td></tr>
                                            <tr><td>Gadget Plus</td><td>987</td><td>$19,740</td></tr>
                                            <tr><td>Basic Widget</td><td>856</td><td>$8,560</td></tr>
                                            <tr><td>Premium Gadget</td><td>654</td><td>$32,700</td></tr>
                                            <tr><td>Starter Kit</td><td>543</td><td>$10,860</td></tr>
                                        </>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
