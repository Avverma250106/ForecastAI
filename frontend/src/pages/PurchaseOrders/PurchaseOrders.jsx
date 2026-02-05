/**
 * Purchase Orders Page
 */
import { useState, useEffect } from 'react';
import {
    ShoppingCart,
    Plus,
    Eye,
    Download,
    Edit2,
    Trash2,
    Check,
    X,
    Clock,
    Truck,
    Package,
    Save
} from 'lucide-react';
import { purchaseOrdersAPI, productsAPI, suppliersAPI } from '../../services/api';
import './PurchaseOrders.css';

function PurchaseOrders() {
    const [orders, setOrders] = useState([]);
    const [products, setProducts] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [formData, setFormData] = useState({
        supplier_id: '',
        items: [{ product_id: '', quantity: '', unit_price: '' }]
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [ordersRes, productsRes, suppliersRes] = await Promise.all([
                purchaseOrdersAPI.getAll().catch(() => ({ data: [] })),
                productsAPI.getAll().catch(() => ({ data: [] })),
                suppliersAPI.getAll().catch(() => ({ data: [] }))
            ]);
            setOrders(ordersRes.data || []);
            setProducts(productsRes.data || []);
            setSuppliers(suppliersRes.data || []);
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (order = null) => {
        if (order) {
            setSelectedOrder(order);
            setFormData({
                supplier_id: order.supplier_id || '',
                items: order.items?.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    unit_price: item.unit_price
                })) || [{ product_id: '', quantity: '', unit_price: '' }]
            });
        } else {
            setSelectedOrder(null);
            setFormData({
                supplier_id: '',
                items: [{ product_id: '', quantity: '', unit_price: '' }]
            });
        }
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setSelectedOrder(null);
    };

    const handleAddItem = () => {
        setFormData({
            ...formData,
            items: [...formData.items, { product_id: '', quantity: '', unit_price: '' }]
        });
    };

    const handleRemoveItem = (index) => {
        const newItems = formData.items.filter((_, i) => i !== index);
        setFormData({ ...formData, items: newItems.length ? newItems : [{ product_id: '', quantity: '', unit_price: '' }] });
    };

    const handleItemChange = (index, field, value) => {
        const newItems = [...formData.items];
        newItems[index] = { ...newItems[index], [field]: value };

        // Auto-fill unit price from product
        if (field === 'product_id') {
            const product = products.find(p => p.id === parseInt(value));
            if (product) {
                newItems[index].unit_price = product.unit_cost || '';
            }
        }

        setFormData({ ...formData, items: newItems });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                supplier_id: parseInt(formData.supplier_id),
                items: formData.items.filter(i => i.product_id && i.quantity).map(item => ({
                    product_id: parseInt(item.product_id),
                    quantity: parseInt(item.quantity),
                    unit_price: parseFloat(item.unit_price) || 0
                }))
            };

            if (selectedOrder) {
                await purchaseOrdersAPI.update(selectedOrder.id, payload);
            } else {
                await purchaseOrdersAPI.create(payload);
            }

            handleCloseModal();
            fetchData();
        } catch (error) {
            console.error('Failed to save order:', error);
        }
    };

    const handleUpdateStatus = async (id, status) => {
        try {
            await purchaseOrdersAPI.updateStatus(id, status);
            fetchData();
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    };

    const handleDownloadPDF = async (id) => {
        try {
            const res = await purchaseOrdersAPI.generatePDF(id);
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `PO-${id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Failed to download PDF:', error);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this order?')) {
            try {
                await purchaseOrdersAPI.delete(id);
                fetchData();
            } catch (error) {
                console.error('Failed to delete order:', error);
            }
        }
    };

    const getStatusBadge = (status) => {
        const styles = {
            draft: 'badge-info',
            pending: 'badge-warning',
            approved: 'badge-success',
            sent: 'badge-info',
            received: 'badge-success',
            cancelled: 'badge-danger'
        };
        return styles[status] || 'badge-info';
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'received': return <Check size={14} />;
            case 'sent': return <Truck size={14} />;
            case 'pending': return <Clock size={14} />;
            default: return <Package size={14} />;
        }
    };

    // Demo data
    const displayOrders = orders.length > 0 ? orders : [
        { id: 1, po_number: 'PO-2024-001', supplier_name: 'Acme Supplies', total_amount: 2450.00, status: 'sent', created_at: '2024-01-28', items_count: 3 },
        { id: 2, po_number: 'PO-2024-002', supplier_name: 'Widget Corp', total_amount: 1875.50, status: 'pending', created_at: '2024-01-29', items_count: 2 },
        { id: 3, po_number: 'PO-2024-003', supplier_name: 'Tech Parts Inc', total_amount: 5200.00, status: 'draft', created_at: '2024-01-30', items_count: 5 },
        { id: 4, po_number: 'PO-2024-004', supplier_name: 'Acme Supplies', total_amount: 890.00, status: 'received', created_at: '2024-01-25', items_count: 1 },
    ];

    const displaySuppliers = suppliers.length > 0 ? suppliers : [
        { id: 1, name: 'Acme Supplies' },
        { id: 2, name: 'Widget Corp' },
        { id: 3, name: 'Tech Parts Inc' },
    ];

    const displayProducts = products.length > 0 ? products : [
        { id: 1, name: 'Widget Pro X', unit_cost: 15.00 },
        { id: 2, name: 'Gadget Plus', unit_cost: 25.00 },
        { id: 3, name: 'Basic Widget', unit_cost: 5.00 },
    ];

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div className="po-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Purchase Orders</h1>
                    <p className="page-subtitle">Manage your purchase orders and supplier relationships</p>
                </div>
                <div className="page-actions">
                    <button className="btn btn-primary" onClick={() => handleOpenModal()}>
                        <Plus size={18} />
                        Create Order
                    </button>
                </div>
            </div>

            {/* Orders Table */}
            <div className="content-card">
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>PO Number</th>
                                <th>Supplier</th>
                                <th>Items</th>
                                <th>Total</th>
                                <th>Status</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {displayOrders.map((order) => (
                                <tr key={order.id}>
                                    <td><code>{order.po_number}</code></td>
                                    <td>{order.supplier_name}</td>
                                    <td>{order.items_count || order.items?.length || 0} items</td>
                                    <td><strong>${order.total_amount?.toLocaleString()}</strong></td>
                                    <td>
                                        <span className={`badge ${getStatusBadge(order.status)}`}>
                                            {getStatusIcon(order.status)}
                                            {order.status}
                                        </span>
                                    </td>
                                    <td>{new Date(order.created_at).toLocaleDateString()}</td>
                                    <td>
                                        <div className="action-buttons">
                                            <button
                                                className="btn btn-ghost btn-sm"
                                                onClick={() => handleDownloadPDF(order.id)}
                                                title="Download PDF"
                                            >
                                                <Download size={16} />
                                            </button>
                                            <button
                                                className="btn btn-ghost btn-sm"
                                                onClick={() => handleOpenModal(order)}
                                                title="Edit"
                                            >
                                                <Edit2 size={16} />
                                            </button>
                                            {order.status === 'draft' && (
                                                <button
                                                    className="btn btn-ghost btn-sm text-success"
                                                    onClick={() => handleUpdateStatus(order.id, 'pending')}
                                                    title="Submit"
                                                >
                                                    <Check size={16} />
                                                </button>
                                            )}
                                            <button
                                                className="btn btn-ghost btn-sm text-danger"
                                                onClick={() => handleDelete(order.id)}
                                                title="Delete"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Create/Edit Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{selectedOrder ? 'Edit Purchase Order' : 'Create Purchase Order'}</h2>
                            <button className="btn btn-ghost btn-sm" onClick={handleCloseModal}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="modal-body">
                            <div className="form-group">
                                <label className="form-label">Supplier *</label>
                                <select
                                    className="form-select"
                                    value={formData.supplier_id}
                                    onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                                    required
                                >
                                    <option value="">Select Supplier</option>
                                    {displaySuppliers.map((s) => (
                                        <option key={s.id} value={s.id}>{s.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Order Items</label>
                                <div className="items-table">
                                    <div className="items-header">
                                        <span>Product</span>
                                        <span>Quantity</span>
                                        <span>Unit Price</span>
                                        <span>Total</span>
                                        <span></span>
                                    </div>
                                    {formData.items.map((item, index) => (
                                        <div key={index} className="item-row">
                                            <select
                                                className="form-select"
                                                value={item.product_id}
                                                onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                                            >
                                                <option value="">Select Product</option>
                                                {displayProducts.map((p) => (
                                                    <option key={p.id} value={p.id}>{p.name}</option>
                                                ))}
                                            </select>
                                            <input
                                                type="number"
                                                className="form-input"
                                                placeholder="Qty"
                                                value={item.quantity}
                                                onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                                                min="1"
                                            />
                                            <input
                                                type="number"
                                                step="0.01"
                                                className="form-input"
                                                placeholder="$0.00"
                                                value={item.unit_price}
                                                onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                                            />
                                            <span className="item-total">
                                                ${((parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)).toFixed(2)}
                                            </span>
                                            <button
                                                type="button"
                                                className="btn btn-ghost btn-sm text-danger"
                                                onClick={() => handleRemoveItem(index)}
                                            >
                                                <X size={16} />
                                            </button>
                                        </div>
                                    ))}
                                    <button type="button" className="btn btn-secondary btn-sm" onClick={handleAddItem}>
                                        <Plus size={16} /> Add Item
                                    </button>
                                </div>
                            </div>

                            <div className="order-summary">
                                <strong>Order Total: </strong>
                                <span className="total-amount">
                                    ${formData.items.reduce((sum, item) =>
                                        sum + ((parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)), 0
                                    ).toFixed(2)}
                                </span>
                            </div>

                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    <Save size={18} />
                                    {selectedOrder ? 'Update' : 'Create'} Order
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default PurchaseOrders;
