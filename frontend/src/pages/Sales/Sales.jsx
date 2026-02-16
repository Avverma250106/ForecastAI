/**
 * Sales Page - Sales history and data import
 */
import { useState, useEffect } from 'react';
import {
    BarChart3,
    Upload,
    Plus,
    Calendar,
    TrendingUp,
    DollarSign,
    Package,
    X,
    Save
} from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import { salesAPI, productsAPI } from '../../services/api';
import './Sales.css';

function Sales() {
    const [sales, setSales] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [showImportModal, setShowImportModal] = useState(false);
    const [formData, setFormData] = useState({
        product_id: '',
        quantity: '',
        unit_price: '',
        sale_date: new Date().toISOString().split('T')[0]
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [salesRes, productsRes] = await Promise.all([
                salesAPI.getAll().catch(() => ({ data: [] })),
                productsAPI.getAll().catch(() => ({ data: [] }))
            ]);
            setSales(salesRes.data || []);
            setProducts(productsRes.data || []);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = () => {
        setFormData({
            product_id: '',
            quantity: '',
            unit_price: '',
            sale_date: new Date().toISOString().split('T')[0]
        });
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                product_id: parseInt(formData.product_id),
                quantity: parseInt(formData.quantity),
                unit_price: parseFloat(formData.unit_price),
                sale_date: formData.sale_date
            };
            await salesAPI.create(payload);
            handleCloseModal();
            fetchData();
        } catch (error) {
            console.error('Failed to create sale:', error);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            await salesAPI.importCSV(formData);
            setShowImportModal(false);
            fetchData();
        } catch (error) {
            console.error('Failed to import file:', error);
        }
    };

    const handleProductChange = (productId) => {
        const product = products.find(p => p.id === parseInt(productId));
        setFormData({
            ...formData,
            product_id: productId,
            unit_price: product?.selling_price || ''
        });
    };

    // Demo data
    const displaySales = sales.length > 0 ? sales : [
        { id: 1, product_name: 'Widget Pro X', quantity: 25, unit_price: 29.99, total_revenue: 749.75, sale_date: '2024-01-30' },
        { id: 2, product_name: 'Gadget Plus', quantity: 12, unit_price: 49.99, total_revenue: 599.88, sale_date: '2024-01-30' },
        { id: 3, product_name: 'Basic Widget', quantity: 50, unit_price: 12.99, total_revenue: 649.50, sale_date: '2024-01-29' },
        { id: 4, product_name: 'Premium Gadget', quantity: 5, unit_price: 149.99, total_revenue: 749.95, sale_date: '2024-01-29' },
        { id: 5, product_name: 'Starter Kit', quantity: 15, unit_price: 79.99, total_revenue: 1199.85, sale_date: '2024-01-28' },
        { id: 6, product_name: 'Widget Pro X', quantity: 30, unit_price: 29.99, total_revenue: 899.70, sale_date: '2024-01-28' },
    ];

    const displayProducts = products.length > 0 ? products : [
        { id: 1, name: 'Widget Pro X', selling_price: 29.99 },
        { id: 2, name: 'Gadget Plus', selling_price: 49.99 },
        { id: 3, name: 'Basic Widget', selling_price: 12.99 },
    ];

    // Calculate stats
    const totalRevenue = displaySales.reduce((sum, s) => sum + (s.total_revenue || 0), 0);
    const totalQuantity = displaySales.reduce((sum, s) => sum + (s.quantity || 0), 0);
    const avgOrderValue = displaySales.length > 0 ? totalRevenue / displaySales.length : 0;

    // Chart data - aggregate by date
    const chartData = Object.values(
        displaySales.reduce((acc, sale) => {
            const date = sale.sale_date;
            if (!acc[date]) {
                acc[date] = { date, revenue: 0, quantity: 0 };
            }
            acc[date].revenue += sale.total_revenue || 0;
            acc[date].quantity += sale.quantity || 0;
            return acc;
        }, {})
    ).sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-7);

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="custom-tooltip">
                <div className="tooltip-date">
                    {new Date(label).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="tooltip-revenue">
                    ${payload[0].value.toLocaleString()}
                </div>
            </div>
        );
    }
    return null;
};


    return (
        <div className="sales-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Sales</h1>
                    <p className="page-subtitle">Sales history and data import</p>
                </div>
                <div className="page-actions">
                    <button className="btn btn-secondary" onClick={() => setShowImportModal(true)}>
                        <Upload size={18} />
                        Import CSV
                    </button>
                    <button className="btn btn-primary" onClick={handleOpenModal}>
                        <Plus size={18} />
                        Add Sale
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon success">
                        <DollarSign size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Total Revenue: </span>
                        <span className="stat-value">${totalRevenue.toLocaleString()}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon primary">
                        <Package size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Items Sold: </span>
                        <span className="stat-value">{totalQuantity.toLocaleString()}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon info">
                        <TrendingUp size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Average Order Value: </span>
                        <span className="stat-value">${avgOrderValue.toFixed(2)}</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon warning">
                        <Calendar size={24} />
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Total Orders: </span>
                        <span className="stat-value">{displaySales.length}</span>
                    </div>
                </div>
            </div>

            {/* Sales Chart */}
            <div className="content-card mb-lg">
                <div className="content-card-header">
                    <h3 className="content-card-title">
                        <BarChart3 size={18} /> Daily Revenue
                    </h3>
                </div>
                <div className="content-card-body">
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#64748b"
                                    fontSize={12}
                                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                />
                                <YAxis stroke="#64748b" fontSize={12} />
                                <Tooltip content={<CustomTooltip />} cursor = {{fill : 'transparent'}} />
                                <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} activeBar = {false} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Sales Table */}
            <div className="content-card">
                <div className="content-card-header">
                    <h3 className="content-card-title">Recent Sales</h3>
                </div>
                <div className="content-card-body">
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Product</th>
                                    <th>Quantity</th>
                                    <th>Unit Price</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {displaySales.slice(0, 20).map((sale) => (
                                    <tr key={sale.id}>
                                        <td>{new Date(sale.sale_date).toLocaleDateString()}</td>
                                        <td>{sale.product_name}</td>
                                        <td>{sale.quantity}</td>
                                        <td>${sale.unit_price?.toFixed(2)}</td>
                                        <td><strong>${sale.total_revenue?.toFixed(2)}</strong></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Add Sale Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Add Sale</h2>
                            <button className="btn btn-ghost btn-sm" onClick={handleCloseModal}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="modal-body">
                            <div className="form-group">
                                <label className="form-label">Product *</label>
                                <select
                                    className="form-select"
                                    value={formData.product_id}
                                    onChange={(e) => handleProductChange(e.target.value)}
                                    required
                                >
                                    <option value="">Select Product</option>
                                    {displayProducts.map((p) => (
                                        <option key={p.id} value={p.id}>{p.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label className="form-label">Quantity *</label>
                                    <input
                                        type="number"
                                        min="1"
                                        className="form-input"
                                        value={formData.quantity}
                                        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Unit Price ($) *</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        className="form-input"
                                        value={formData.unit_price}
                                        onChange={(e) => setFormData({ ...formData, unit_price: e.target.value })}
                                        required
                                    />
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Sale Date *</label>
                                <input
                                    type="date"
                                    className="form-input"
                                    value={formData.sale_date}
                                    onChange={(e) => setFormData({ ...formData, sale_date: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    <Save size={18} />
                                    Add Sale
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Import Modal */}
            {showImportModal && (
                <div className="modal-overlay" onClick={() => setShowImportModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Import Sales Data</h2>
                            <button className="btn btn-ghost btn-sm" onClick={() => setShowImportModal(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="import-dropzone">
                                <Upload size={48} />
                                <p>Drop your CSV file here or click to browse</p>
                                <input
                                    type="file"
                                    accept=".csv"
                                    onChange={handleFileUpload}
                                    className="file-input"
                                />
                            </div>
                            <p className="import-note">
                                CSV should include columns: product_id, quantity, unit_price, sale_date
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Sales;
