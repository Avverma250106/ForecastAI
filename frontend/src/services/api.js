/**
 * API Service - Backend Communication Layer
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor - handle errors (don't auto-redirect, let components handle it)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Just log the error, don't auto-redirect
        if (error.response?.status === 401) {
            console.warn('API 401:', error.config?.url);
        }
        return Promise.reject(error);
    }
);

// ============ AUTH ============
export const authAPI = {
    login: (email, password) =>
        api.post('/auth/login', new URLSearchParams({ username: email, password }), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        }),
    register: (userData) => api.post('/auth/register', userData),
    getProfile: () => api.get('/auth/me'),
};

// ============ DASHBOARD ============
export const dashboardAPI = {
    getStats: () => api.get('/dashboard/stats'),
    getAlerts: (limit = 5) => api.get(`/dashboard/alerts?limit=${limit}`),
    getTopProducts: (limit = 5) => api.get(`/dashboard/top-products?limit=${limit}`),
    getRecentSales: (limit = 10) => api.get(`/dashboard/recent-sales?limit=${limit}`),
    getSalesChart: (days = 30) => api.get(`/dashboard/sales-chart?days=${days}`),
    getInventoryHealth: () => api.get('/dashboard/inventory-health'),
};

// ============ PRODUCTS ============
export const productsAPI = {
    getAll: (skip = 0, limit = 100) => api.get(`/products?skip=${skip}&limit=${limit}`),
    getById: (id) => api.get(`/products/${id}`),
    create: (product) => api.post('/products', product),
    update: (id, product) => api.put(`/products/${id}`, product),
    delete: (id) => api.delete(`/products/${id}`),
    getLowStock: () => api.get('/products/low-stock'),
};

// ============ SUPPLIERS ============
export const suppliersAPI = {
    getAll: (skip = 0, limit = 100) => api.get(`/suppliers?skip=${skip}&limit=${limit}`),
    getById: (id) => api.get(`/suppliers/${id}`),
    create: (supplier) => api.post('/suppliers', supplier),
    update: (id, supplier) => api.put(`/suppliers/${id}`, supplier),
    delete: (id) => api.delete(`/suppliers/${id}`),
};

// ============ SALES ============
export const salesAPI = {
    getAll: (skip = 0, limit = 100) => api.get(`/sales?skip=${skip}&limit=${limit}`),
    getById: (id) => api.get(`/sales/${id}`),
    create: (sale) => api.post('/sales', sale),
    bulkCreate: (sales) => api.post('/sales/bulk', sales),
    importCSV: (formData) => api.post('/sales/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    getByProduct: (productId, startDate, endDate) => {
        let url = `/sales/product/${productId}`;
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (params.toString()) url += `?${params.toString()}`;
        return api.get(url);
    },
};

// ============ INVENTORY ============
export const inventoryAPI = {
    getAll: (skip = 0, limit = 100) => api.get(`/inventory?skip=${skip}&limit=${limit}`),
    getByProduct: (productId) => api.get(`/inventory/product/${productId}`),
    update: (productId, data) => api.put(`/inventory/product/${productId}`, data),
    adjustStock: (productId, adjustment, reason) =>
        api.post(`/inventory/product/${productId}/adjust`, { adjustment, reason }),
    getLowStock: () => api.get('/inventory/low-stock'),
};

// ============ FORECASTS ============
export const forecastsAPI = {
    getByProduct: (productId, horizon = 30) =>
        api.get(`/forecasts/product/${productId}?horizon_days=${horizon}`),
    generateForProduct: (productId, horizon = 30) =>
        api.post(`/forecasts/generate/${productId}?horizon_days=${horizon}`),
    generateForAll: (horizon = 30) =>
        api.post(`/forecasts/generate-all?horizon_days=${horizon}`),
};

// ============ ALERTS ============
export const alertsAPI = {
    getAll: (status, limit = 50) => {
        let url = `/alerts?limit=${limit}`;
        if (status) url += `&status=${status}`;
        return api.get(url);
    },
    getById: (id) => api.get(`/alerts/${id}`),
    acknowledge: (id) => api.put(`/alerts/${id}/acknowledge`),
    dismiss: (id) => api.put(`/alerts/${id}/dismiss`),
    getCritical: () => api.get('/alerts/critical'),
    generateAlerts: () => api.post('/alerts/generate'),
};

// ============ PURCHASE ORDERS ============
export const purchaseOrdersAPI = {
    getAll: (skip = 0, limit = 100) => api.get(`/purchase-orders?skip=${skip}&limit=${limit}`),
    getById: (id) => api.get(`/purchase-orders/${id}`),
    create: (order) => api.post('/purchase-orders', order),
    update: (id, order) => api.put(`/purchase-orders/${id}`, order),
    updateStatus: (id, status) => api.put(`/purchase-orders/${id}/status`, { status }),
    delete: (id) => api.delete(`/purchase-orders/${id}`),
    generatePDF: (id) => api.get(`/purchase-orders/${id}/pdf`, { responseType: 'blob' }),
    generateFromRecommendations: () => api.post('/purchase-orders/generate-from-recommendations'),
};

export default api;
