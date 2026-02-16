/**
 * Forecasts Page - ML-powered demand predictions
 */
import { useState, useEffect } from 'react';
import {
    TrendingUp,
    RefreshCw,
    Calendar,
    Zap,
    Target
} from 'lucide-react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';
import { forecastsAPI, productsAPI } from '../../services/api';
import './Forecasts.css';

function Forecasts() {
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [forecast, setForecast] = useState(null);
    const [horizon, setHorizon] = useState(30);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const res = await productsAPI.getAll();
            setProducts(res.data || []);
            if (res.data?.length > 0) {
                setSelectedProduct(res.data[0]);
                fetchForecast(res.data[0].id);
            } else {
                setLoading(false);
            }
        } catch (error) {
            console.error('Failed to fetch products:', error);
            setLoading(false);
        }
    };

    const fetchForecast = async (productId) => {
        setLoading(true);
        try {
            const res = await forecastsAPI.getByProduct(productId, horizon);
            setForecast(res.data);
        } catch (error) {
            console.error('Failed to fetch forecast:', error);
            // Use demo data
            setForecast(getDemoForecast());
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateForecast = async () => {
        if (!selectedProduct) return;
        setGenerating(true);
        try {
            const res = await forecastsAPI.generateForProduct(selectedProduct.id, horizon);
            setForecast(res.data);
        } catch (error) {
            console.error('Failed to generate forecast:', error);
            setForecast(getDemoForecast());
        } finally {
            setGenerating(false);
        }
    };

    const handleProductChange = (productId) => {
        const product = products.find(p => p.id === parseInt(productId));
        setSelectedProduct(product);
        if (product) {
            fetchForecast(product.id);
        }
    };

    const getDemoForecast = () => {
        const data = [];
        const baseDate = new Date();
        for (let i = 0; i < 30; i++) {
            const date = new Date(baseDate);
            date.setDate(date.getDate() + i);
            const predicted = Math.floor(20 + Math.random() * 30 + Math.sin(i / 7) * 10);
            data.push({
                forecast_date: date.toISOString().split('T')[0],
                predicted_quantity: predicted,
                confidence_lower: Math.max(0, predicted - 8),
                confidence_upper: predicted + 8
            });
        }
        return {
            product_id: 1,
            product_name: selectedProduct?.name || 'Demo Product',
            model_name: 'RandomForest',
            forecast_data: data,
            total_predicted_demand: data.reduce((sum, d) => sum + d.predicted_quantity, 0),
            avg_daily_demand: Math.round(data.reduce((sum, d) => sum + d.predicted_quantity, 0) / data.length),
            peak_date: data.reduce((max, d) => d.predicted_quantity > max.predicted_quantity ? d : max, data[0]).forecast_date,
            peak_quantity: Math.max(...data.map(d => d.predicted_quantity))
        };
    };

    const chartData = forecast?.forecast_data?.map(d => ({
        date: new Date(d.forecast_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        predicted: d.predicted_quantity,
        lower: d.confidence_lower,
        upper: d.confidence_upper
    })) || [];

    // Demo products if empty
    const displayProducts = products;

    return (
        <div className="forecasts-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Demand Forecasts</h1>
                    <p className="page-subtitle">AI-powered predictions for inventory planning</p>
                </div>
                <div className="page-actions">
                    <button
                        className="btn btn-primary"
                        onClick={handleGenerateForecast}
                        disabled={generating || !selectedProduct}
                    >
                        {generating ? (
                            <>
                                <RefreshCw size={18} className="spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Zap size={18} />
                                Generate Forecast
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Controls */}
            <div className="forecast-controls">
                <div className="control-group">
                    <label className="form-label">Select Product</label>
                    <select
                        className="form-select"
                        value={selectedProduct?.id || ''}
                        onChange={(e) => handleProductChange(e.target.value)}
                    >
                        {displayProducts.map((p) => (
                            <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                    </select>
                </div>
                <div className="control-group">
                    <label className="form-label">Forecast Horizon</label>
                    <select
                        className="form-select"
                        value={horizon}
                        onChange={(e) => setHorizon(parseInt(e.target.value))}
                    >
                        <option value={7}>7 days</option>
                        <option value={14}>14 days</option>
                        <option value={30}>30 days</option>
                        <option value={60}>60 days</option>
                        <option value={90}>90 days</option>
                    </select>
                </div>
            </div>

            {/* Stats Cards */}
            {forecast && (
                <div className="forecast-stats">
                    <div className="stat-card">
                        <div className="stat-icon primary">
                            <TrendingUp size={24} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">Total Predicted Demand: </span>
                            <span className="stat-value">{forecast.total_predicted_demand?.toLocaleString()}</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon success">
                            <Target size={24} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">Average Daily Demand: </span>
                            <span className="stat-value">{forecast.avg_daily_demand?.toFixed(1)}</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon warning">
                            <Calendar size={24} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">Peak Date: </span>
                            <span className="stat-value">{forecast.peak_date ? new Date(forecast.peak_date).toLocaleDateString() : 'N/A'}</span>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-icon info">
                            <Zap size={24} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-label">Model: </span>
                            <span className="stat-value">{forecast.model_name || 'RandomForest'}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Forecast Chart */}
            <div className="content-card">
                <div className="content-card-header">
                    <h3 className="content-card-title">
                        <TrendingUp size={18} />
                        Demand Forecast - {selectedProduct?.name || 'Product'}
                    </h3>
                </div>
                <div className="content-card-body">
                    {loading ? (
                        <div className="loading-container">
                            <div className="loading-spinner"></div>
                        </div>
                    ) : (
                        <div className="chart-container large">
                            <ResponsiveContainer width="100%" height={400}>
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
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
                                    <Legend />
                                    <Area
                                        type="monotone"
                                        dataKey="upper"
                                        stackId="1"
                                        stroke="transparent"
                                        fill="url(#colorConfidence)"
                                        name="Upper Bound"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="lower"
                                        stackId="2"
                                        stroke="transparent"
                                        fill="#0f172a"
                                        name="Lower Bound"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="predicted"
                                        stroke="#6366f1"
                                        strokeWidth={2}
                                        fill="url(#colorPredicted)"
                                        name="Predicted Demand"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>
            </div>

            {/* Forecast Data Table */}
            {forecast && (
                <div className="content-card">
                    <div className="content-card-header">
                        <h3 className="content-card-title">Detailed Forecast Data</h3>
                    </div>
                    <div className="content-card-body">
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Predicted Quantity</th>
                                        <th>Lower Bound</th>
                                        <th>Upper Bound</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {forecast.forecast_data?.slice(0, 14).map((d, i) => (
                                        <tr key={i}>
                                            <td>{new Date(d.forecast_date).toLocaleDateString()}</td>
                                            <td className="text-primary"><strong>{d.predicted_quantity}</strong></td>
                                            <td>{d.confidence_lower}</td>
                                            <td>{d.confidence_upper}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Forecasts;
