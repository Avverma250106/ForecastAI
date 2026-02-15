/**
 * Products Page - Product Management
 */
import { useState, useEffect } from 'react';
import {
    Package,
    Plus,
    Search,
    Edit2,
    Trash2,
    AlertTriangle,
    X,
    Save
} from 'lucide-react';
import { productsAPI, suppliersAPI } from '../../services/api';
import './Products.css';

function Products() {
    const [products, setProducts] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: '',
    supplier_id: '',
    unit_cost: '',
    unit_price: '',
    reorder_point: '',
    safety_stock: ''
});


    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [productsRes, suppliersRes] = await Promise.all([
                productsAPI.getAll().catch(() => ({ data: [] })),
                suppliersAPI.getAll().catch(() => ({ data: [] }))
            ]);
            setProducts(productsRes.data || []);
            setSuppliers(suppliersRes.data || []);
        } catch (error) {
            console.error('Failed to fetch products:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (product = null) => {
        if (product) {
            setEditingProduct(product);
            setFormData({
                name: product.name,
                sku: product.sku,
                category: product.category || '',
                supplier_id: product.supplier_id || '',
                unit_cost: product.unit_cost || '',
                unit_price: product.unit_price || '',
                reorder_point: product.reorder_point || '',
                safety_stock: product.safety_stock || ''
            });
        } else {
            setEditingProduct(null);
            setFormData({
                name: '',
                sku: '',
                category: '',
                supplier_id: '',
                unit_cost: '',
                selling_price: '',
                reorder_point: '',
                lead_time_days: ''
            });
        }
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingProduct(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                unit_cost: parseFloat(formData.unit_cost) || 0,
                unit_price: parseFloat(formData.unit_price) || 0,
                reorder_point: parseInt(formData.reorder_point) || 10,
                safety_stock: parseInt(formData.safety_stock) || 5,
                supplier_id: formData.supplier_id ? parseInt(formData.supplier_id) : null
            };


            if (editingProduct) {
                await productsAPI.update(editingProduct.id, payload);
            } else {
                await productsAPI.create(payload);
            }

            handleCloseModal();
            fetchData();
        } catch (error) {
            console.error('Failed to save product:', error);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this product?')) {
            try {
                await productsAPI.delete(id);
                fetchData();
            } catch (error) {
                console.error('Failed to delete product:', error);
            }
        }
    };

    const filteredProducts = products.filter(product =>
        product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.sku?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.category?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Demo data if empty
    const displayProducts = filteredProducts;
    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div className="products-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Products</h1>
                    <p className="page-subtitle">Manage your product catalog</p>
                </div>
                <div className="page-actions">
                    <button className="btn btn-primary" onClick={() => handleOpenModal()}>
                        <Plus size={18} />
                        Add Product
                    </button>
                </div>
            </div>

            {/* Search & Filters */}
            <div className="filters-bar">
                <div className="search-box">
                    <Search className="search-icon" />
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search products..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Products Table */}
            <div className="content-card">
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>SKU</th>
                                <th>Category</th>
                                <th>Cost</th>
                                <th>Price</th>
                                <th>Stock</th>
                                <th>Reorder Point</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {displayProducts.map((product) => (
                                <tr key={product.id}>
                                    <td>
                                        <div className="product-cell">
                                            <div className="product-icon">
                                                <Package size={18} />
                                            </div>
                                            <span className="product-name">{product.name}</span>
                                        </div>
                                    </td>
                                    <td><code>{product.sku}</code></td>
                                    <td>{product.category || '-'}</td>
                                    <td>${product.unit_cost?.toFixed(2)}</td>
                                    <td>${product.unit_price?.toFixed(2)}</td>
                                    <td>
                                        <span className={`stock-badge ${(product.current_stock || 0) <= (product.reorder_point || 0)
                                                ? 'low'
                                                : 'normal'
                                            }`}>
                                            {product.current_stock || 0}
                                            {(product.current_stock || 0) <= (product.reorder_point || 0) && (
                                                <AlertTriangle size={12} />
                                            )}
                                        </span>
                                    </td>
                                    <td>{product.reorder_point}</td>
                                    <td>
                                        <div className="action-buttons">
                                            <button
                                                className="btn btn-ghost btn-sm"
                                                onClick={() => handleOpenModal(product)}
                                                title="Edit"
                                            >
                                                <Edit2 size={16} />
                                            </button>
                                            <button
                                                className="btn btn-ghost btn-sm text-danger"
                                                onClick={() => handleDelete(product.id)}
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

            {/* Add/Edit Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{editingProduct ? 'Edit Product' : 'Add New Product'}</h2>
                            <button className="btn btn-ghost btn-sm" onClick={handleCloseModal}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="modal-body">
                            <div className="form-grid">
                                <div className="form-group">
                                    <label className="form-label">Product Name *</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">SKU *</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.sku}
                                        onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Category</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={formData.category}
                                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Supplier</label>
                                    <select
                                        className="form-select"
                                        value={formData.supplier_id}
                                        onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                                    >
                                        <option value="">Select Supplier</option>
                                        {suppliers.map((s) => (
                                            <option key={s.id} value={s.id}>{s.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Unit Cost ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        className="form-input"
                                        value={formData.unit_cost}
                                        onChange={(e) => setFormData({ ...formData, unit_cost: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Selling Price ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        className="form-input"
                                        value={formData.selling_price}
                                        onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Reorder Point</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        value={formData.reorder_point}
                                        onChange={(e) => setFormData({ ...formData, reorder_point: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Lead Time (days)</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        value={formData.lead_time_days}
                                        onChange={(e) => setFormData({ ...formData, lead_time_days: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    <Save size={18} />
                                    {editingProduct ? 'Update' : 'Create'} Product
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Products;
