/**
 * Register Page
 */
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { TrendingUp, Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react';
import '../Login/Login.css';

function Register() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            await register({
                name: formData.name,
                email: formData.email,
                password: formData.password
            });
            setSuccess(true);
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create account. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-background">
                <div className="gradient-orb orb-1"></div>
                <div className="gradient-orb orb-2"></div>
                <div className="gradient-orb orb-3"></div>
            </div>

            <div className="auth-container">
                <div className="auth-card glass">
                    <div className="auth-header">
                        <div className="auth-logo">
                            <TrendingUp className="logo-icon" />
                            <span className="logo-text">ForecastAI</span>
                        </div>
                        <h1>Create Account</h1>
                        <p>Get started with AI-powered forecasting</p>
                    </div>

                    {error && (
                        <div className="auth-error">
                            <AlertCircle size={18} />
                            <span>{error}</span>
                        </div>
                    )}

                    {success && (
                        <div className="alert alert-success">
                            <CheckCircle size={18} />
                            <span>Account created! Redirecting to login...</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label className="form-label">Full Name</label>
                            <div className="input-with-icon">
                                <User className="input-icon" />
                                <input
                                    type="text"
                                    name="name"
                                    className="form-input"
                                    placeholder="Enter your name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Email</label>
                            <div className="input-with-icon">
                                <Mail className="input-icon" />
                                <input
                                    type="email"
                                    name="email"
                                    className="form-input"
                                    placeholder="Enter your email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <div className="input-with-icon">
                                <Lock className="input-icon" />
                                <input
                                    type="password"
                                    name="password"
                                    className="form-input"
                                    placeholder="Create a password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Confirm Password</label>
                            <div className="input-with-icon">
                                <Lock className="input-icon" />
                                <input
                                    type="password"
                                    name="confirmPassword"
                                    className="form-input"
                                    placeholder="Confirm your password"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>

                        <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading || success}>
                            {loading ? (
                                <>
                                    <span className="loading-spinner"></span>
                                    Creating Account...
                                </>
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>

                    <div className="auth-footer">
                        <p>Already have an account? <Link to="/login">Sign in</Link></p>
                    </div>
                </div>

                <div className="auth-features">
                    <h2>AI-Powered Demand Forecasting</h2>
                    <ul>
                        <li>📊 Accurate sales predictions using ML</li>
                        <li>🔔 Real-time stockout alerts</li>
                        <li>📦 Automated purchase order generation</li>
                        <li>📈 Interactive forecast visualizations</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default Register;
