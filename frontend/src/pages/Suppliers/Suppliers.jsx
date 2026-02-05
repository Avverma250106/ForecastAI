/**
 * Suppliers Page
 */
import { useState, useEffect } from 'react';
import { Users, Plus, Edit2, Trash2, X, Save, Mail, Phone, MapPin } from 'lucide-react';
import { suppliersAPI } from '../../services/api';
import '../Products/Products.css';

function Suppliers() {
    const [suppliers, setSuppliers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingSupplier, setEditingSupplier] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        address: '',
        contact_person: ''
    });

    useEffect(() => {
        fetchSuppliers();
    }, []);

    const fetchSuppliers = async () => {
        try {
            const res = await suppliersAPI.getAll();
            setSuppliers(res.data || []);
        } catch (error) {
            console.error('Failed to fetch suppliers:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (supplier = null) => {
        if (supplier) {
            setEditingSupplier(supplier);
            setFormData({
                name: supplier.name,
                email: supplier.email || '',
                phone: supplier.phone || '',
                address: supplier.address || '',
                contact_person: supplier.contact_person || ''
            });
        } else {
            setEditingSupplier(null);
            setFormData({
                name: '',
                email: '',
                phone: '',
                address: '',
                contact_person: ''
            });
        }
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingSupplier(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingSupplier) {
                await suppliersAPI.update(editingSupplier.id, formData);
            } else {
                await suppliersAPI.create(formData);
            }
            handleCloseModal();
            fetchSuppliers();
        } catch (error) {
            console.error('Failed to save supplier:', error);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this supplier?')) {
            try {
                await suppliersAPI.delete(id);
                fetchSuppliers();
            } catch (error) {
                console.error('Failed to delete supplier:', error);
            }
        }
    };

    // Demo data
    const displaySuppliers = suppliers.length > 0 ? suppliers : [
        { id: 1, name: 'Acme Supplies', email: 'orders@acme.com', phone: '+1 555-0123', address: '123 Main St, City', contact_person: 'John Smith' },
        { id: 2, name: 'Widget Corp', email: 'sales@widgetcorp.com', phone: '+1 555-0456', address: '456 Oak Ave, Town', contact_person: 'Jane Doe' },
        { id: 3, name: 'Tech Parts Inc', email: 'info@techparts.com', phone: '+1 555-0789', address: '789 Tech Blvd, Metro', contact_person: 'Bob Wilson' },
    ];

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div className="suppliers-page fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Suppliers</h1>
                    <p className="page-subtitle">Manage your supplier contacts</p>
                </div>
                <div className="page-actions">
                    <button className="btn btn-primary" onClick={() => handleOpenModal()}>
                        <Plus size={18} />
                        Add Supplier
                    </button>
                </div>
            </div>

            {/* Suppliers Grid */}
            <div className="suppliers-grid">
                {displaySuppliers.map((supplier) => (
                    <div key={supplier.id} className="supplier-card">
                        <div className="supplier-header">
                            <div className="supplier-avatar">
                                <Users size={24} />
                            </div>
                            <div className="supplier-info">
                                <h3>{supplier.name}</h3>
                                {supplier.contact_person && (
                                    <span className="contact-person">{supplier.contact_person}</span>
                                )}
                            </div>
                            <div className="supplier-actions">
                                <button className="btn btn-ghost btn-sm" onClick={() => handleOpenModal(supplier)}>
                                    <Edit2 size={16} />
                                </button>
                                <button className="btn btn-ghost btn-sm text-danger" onClick={() => handleDelete(supplier.id)}>
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                        <div className="supplier-details">
                            {supplier.email && (
                                <div className="detail-item">
                                    <Mail size={14} />
                                    <a href={`mailto:${supplier.email}`}>{supplier.email}</a>
                                </div>
                            )}
                            {supplier.phone && (
                                <div className="detail-item">
                                    <Phone size={14} />
                                    <span>{supplier.phone}</span>
                                </div>
                            )}
                            {supplier.address && (
                                <div className="detail-item">
                                    <MapPin size={14} />
                                    <span>{supplier.address}</span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Add/Edit Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={handleCloseModal}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}</h2>
                            <button className="btn btn-ghost btn-sm" onClick={handleCloseModal}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="modal-body">
                            <div className="form-group">
                                <label className="form-label">Company Name *</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        className="form-input"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Phone</label>
                                    <input
                                        type="tel"
                                        className="form-input"
                                        value={formData.phone}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Contact Person</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.contact_person}
                                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Address</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.address}
                                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                                />
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    <Save size={18} />
                                    {editingSupplier ? 'Update' : 'Create'} Supplier
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Suppliers;
