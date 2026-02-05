/**
 * Alerts Page - Stock alerts and notifications
 */
import { useState, useEffect } from 'react';
import {
    AlertTriangle,
    Check,
    X,
    RefreshCw,
    Bell,
    ChevronDown,
    Filter
} from 'lucide-react';
import { alertsAPI } from '../../services/api';
import './Alerts.css';

function Alerts() {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchAlerts();
    }, [filter]);

    const fetchAlerts = async () => {
        setLoading(true);
        try {
            const status = filter === 'all' ? null : filter;
            const res = await alertsAPI.getAll(status);
            setAlerts(res.data || []);
        } catch (error) {
            console.error('Failed to fetch alerts:', error);
            // Demo data
            setAlerts(getDemoAlerts());
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateAlerts = async () => {
        setGenerating(true);
        try {
            await alertsAPI.generateAlerts();
            fetchAlerts();
        } catch (error) {
            console.error('Failed to generate alerts:', error);
        } finally {
            setGenerating(false);
        }
    };

    const handleAcknowledge = async (id) => {
        try {
            await alertsAPI.acknowledge(id);
            fetchAlerts();
        } catch (error) {
            console.error('Failed to acknowledge alert:', error);
        }
    };

    const handleDismiss = async (id) => {
        try {
            await alertsAPI.dismiss(id);
            fetchAlerts();
        } catch (error) {
            console.error('Failed to dismiss alert:', error);
        }
    };

    const getDemoAlerts = () => [
        {
            id: 1,
            type: 'STOCKOUT_WARNING',
            severity: 'critical',
            title: 'Stockout imminent',
            message: 'Widget Pro X will run out of stock in 2 days based on current demand.',
            product_name: 'Widget Pro X',
            recommended_action: 'Order 150 units immediately',
            status: 'active',
            created_at: new Date().toISOString()
        },
        {
            id: 2,
            type: 'LOW_STOCK',
            severity: 'warning',
            title: 'Low stock warning',
            message: 'Gadget Plus is below reorder point. Current stock: 15 units.',
            product_name: 'Gadget Plus',
            recommended_action: 'Order 50 units within 3 days',
            status: 'active',
            created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
            id: 3,
            type: 'REORDER_REMINDER',
            severity: 'info',
            title: 'Reorder recommended',
            message: 'Lead time for Basic Widget is approaching. Plan reorder soon.',
            product_name: 'Basic Widget',
            recommended_action: 'Review forecast and plan order',
            status: 'active',
            created_at: new Date(Date.now() - 7200000).toISOString()
        },
        {
            id: 4,
            type: 'OVERSTOCK',
            severity: 'info',
            title: 'Potential overstock',
            message: 'Premium Gadget has more than 90 days of supply based on forecast.',
            product_name: 'Premium Gadget',
            recommended_action: 'Consider promotional pricing',
            status: 'acknowledged',
            created_at: new Date(Date.now() - 86400000).toISOString()
        }
    ];

    const getAlertIcon = (severity) => {
        switch (severity) {
            case 'critical': return <AlertTriangle className="alert-icon critical" />;
            case 'warning': return <AlertTriangle className="alert-icon warning" />;
            default: return <Bell className="alert-icon info" />;
        }
    };

    const getAlertClass = (severity) => {
        switch (severity) {
            case 'critical': return 'alert-card critical';
            case 'warning': return 'alert-card warning';
            default: return 'alert-card info';
        }
    };

    const displayAlerts = alerts.length > 0 ? alerts : getDemoAlerts();
    const filteredAlerts = filter === 'all'
        ? displayAlerts
        : displayAlerts.filter(a => a.status === filter);

    const criticalCount = displayAlerts.filter(a => a.severity === 'critical' && a.status !== 'dismissed').length;
    const warningCount = displayAlerts.filter(a => a.severity === 'warning' && a.status !== 'dismissed').length;
    const infoCount = displayAlerts.filter(a => a.severity === 'info' && a.status !== 'dismissed').length;

    return (
        <div className="alerts-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Alerts</h1>
                    <p className="page-subtitle">Inventory warnings and recommendations</p>
                </div>
                <div className="page-actions">
                    <button
                        className="btn btn-primary"
                        onClick={handleGenerateAlerts}
                        disabled={generating}
                    >
                        {generating ? (
                            <>
                                <RefreshCw size={18} className="spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <RefreshCw size={18} />
                                Refresh Alerts
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Alert Summary */}
            <div className="alert-summary">
                <div className="summary-card critical">
                    <span className="summary-count">{criticalCount}</span>
                    <span className="summary-label">Critical</span>
                </div>
                <div className="summary-card warning">
                    <span className="summary-count">{warningCount}</span>
                    <span className="summary-label">Warnings</span>
                </div>
                <div className="summary-card info">
                    <span className="summary-count">{infoCount}</span>
                    <span className="summary-label">Info</span>
                </div>
            </div>

            {/* Filters */}
            <div className="filters-bar">
                <div className="filter-group">
                    <Filter size={18} />
                    <select
                        className="form-select"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    >
                        <option value="all">All Alerts</option>
                        <option value="active">Active</option>
                        <option value="acknowledged">Acknowledged</option>
                        <option value="dismissed">Dismissed</option>
                    </select>
                </div>
            </div>

            {/* Alerts List */}
            {loading ? (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                </div>
            ) : (
                <div className="alerts-grid">
                    {filteredAlerts.map((alert) => (
                        <div key={alert.id} className={getAlertClass(alert.severity)}>
                            <div className="alert-header">
                                {getAlertIcon(alert.severity)}
                                <div className="alert-title-section">
                                    <h3 className="alert-title">{alert.title}</h3>
                                    <span className="alert-product">{alert.product_name}</span>
                                </div>
                                <span className={`badge badge-${alert.severity === 'critical' ? 'danger' : alert.severity === 'warning' ? 'warning' : 'info'}`}>
                                    {alert.severity}
                                </span>
                            </div>

                            <p className="alert-message">{alert.message}</p>

                            {alert.recommended_action && (
                                <div className="alert-recommendation">
                                    <strong>Recommended:</strong> {alert.recommended_action}
                                </div>
                            )}

                            <div className="alert-footer">
                                <span className="alert-time">
                                    {new Date(alert.created_at).toLocaleString()}
                                </span>
                                <div className="alert-actions">
                                    {alert.status === 'active' && (
                                        <>
                                            <button
                                                className="btn btn-ghost btn-sm"
                                                onClick={() => handleAcknowledge(alert.id)}
                                                title="Acknowledge"
                                            >
                                                <Check size={16} /> Acknowledge
                                            </button>
                                            <button
                                                className="btn btn-ghost btn-sm text-danger"
                                                onClick={() => handleDismiss(alert.id)}
                                                title="Dismiss"
                                            >
                                                <X size={16} /> Dismiss
                                            </button>
                                        </>
                                    )}
                                    {alert.status === 'acknowledged' && (
                                        <span className="status-badge acknowledged">Acknowledged</span>
                                    )}
                                    {alert.status === 'dismissed' && (
                                        <span className="status-badge dismissed">Dismissed</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {filteredAlerts.length === 0 && (
                        <div className="empty-state">
                            <Bell size={48} />
                            <p>No alerts found</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default Alerts;
