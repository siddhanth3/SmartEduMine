import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/api';

const SignIn = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const { token, user } = await authService.signIn(formData);
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">

      {/* Animated orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div style={{
          position: 'absolute', top: '-10%', right: '-5%',
          width: '500px', height: '500px',
          background: 'radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%)',
          borderRadius: '50%', animation: 'orb-drift 14s ease-in-out infinite alternate'
        }} />
        <div style={{
          position: 'absolute', bottom: '-10%', left: '-5%',
          width: '450px', height: '450px',
          background: 'radial-gradient(circle, rgba(20,184,166,0.14) 0%, transparent 70%)',
          borderRadius: '50%', animation: 'orb-drift 18s ease-in-out infinite alternate-reverse'
        }} />
        <div style={{
          position: 'absolute', top: '40%', left: '40%',
          width: '300px', height: '300px',
          background: 'radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)',
          borderRadius: '50%', animation: 'orb-drift 22s ease-in-out infinite alternate'
        }} />

        {/* Grid overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'linear-gradient(rgba(148,163,184,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.03) 1px, transparent 1px)',
          backgroundSize: '40px 40px'
        }} />
      </div>

      {/* Card */}
      <div className="relative z-10 w-full max-w-md mx-4 fade-in-up" style={{
        background: 'rgba(10, 15, 28, 0.85)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        border: '1px solid rgba(99, 102, 241, 0.20)',
        borderRadius: '1.5rem',
        padding: '2.5rem',
        boxShadow: '0 24px 80px rgba(0,0,0,0.6), 0 0 60px rgba(99,102,241,0.10), inset 0 1px 0 rgba(255,255,255,0.06)'
      }}>

        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div style={{
            width: '48px', height: '48px',
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            borderRadius: '14px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 24px rgba(99,102,241,0.5)',
            padding: '8px'
          }}>
            <img src="/logo.png" alt="SmartEduMine" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </div>
          <div>
            <span style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #14b8a6)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              fontWeight: 800, fontSize: '1.5rem', letterSpacing: '-0.02em'
            }}>SmartEdu</span>
            <span style={{ color: '#f1f5f9', fontWeight: 800, fontSize: '1.5rem', letterSpacing: '-0.02em' }}>Mine</span>
          </div>
        </div>

        <h2 style={{ color: '#f1f5f9', fontWeight: 700, fontSize: '1.5rem', textAlign: 'center', marginBottom: '4px' }}>
          Welcome back
        </h2>
        <p style={{ color: '#64748b', textAlign: 'center', marginBottom: '2rem', fontSize: '0.9rem' }}>
          Sign in to your SmartEduMine account
        </p>

        {error && (
          <div style={{
            background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.25)',
            color: '#f87171', padding: '0.75rem 1rem', borderRadius: '0.75rem',
            marginBottom: '1.25rem', fontSize: '0.875rem',
            boxShadow: '0 0 12px rgba(239,68,68,0.10)'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Email Address
            </label>
            <input
              type="email" id="email" name="email" required
              style={{
                width: '100%', padding: '0.75rem 1rem', borderRadius: '0.75rem',
                background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(148,163,184,0.12)',
                color: '#f1f5f9', outline: 'none', fontSize: '0.9rem',
                transition: 'all 0.25s ease'
              }}
              placeholder="you@institution.edu"
              value={formData.email}
              onChange={handleChange}
              onFocus={e => { e.target.style.borderColor = 'rgba(99,102,241,0.5)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)'; }}
              onBlur={e => { e.target.style.borderColor = 'rgba(148,163,184,0.12)'; e.target.style.boxShadow = 'none'; }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', color: '#94a3b8', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Password
            </label>
            <input
              type="password" id="password" name="password" required
              style={{
                width: '100%', padding: '0.75rem 1rem', borderRadius: '0.75rem',
                background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(148,163,184,0.12)',
                color: '#f1f5f9', outline: 'none', fontSize: '0.9rem',
                transition: 'all 0.25s ease'
              }}
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              onFocus={e => { e.target.style.borderColor = 'rgba(99,102,241,0.5)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)'; }}
              onBlur={e => { e.target.style.borderColor = 'rgba(148,163,184,0.12)'; e.target.style.boxShadow = 'none'; }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input type="checkbox" style={{ accentColor: '#6366f1' }} />
              <span style={{ color: '#64748b', fontSize: '0.85rem' }}>Remember me</span>
            </label>
            <a href="#" style={{ color: '#6366f1', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 500 }}>
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%', padding: '0.875rem',
              background: isLoading ? 'rgba(99,102,241,0.5)' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              color: 'white', border: 'none', borderRadius: '0.75rem',
              fontWeight: 700, fontSize: '0.95rem', cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.25s ease',
              boxShadow: '0 4px 20px rgba(99,102,241,0.4)',
              letterSpacing: '0.01em'
            }}
            onMouseEnter={e => { if (!isLoading) { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 8px 30px rgba(99,102,241,0.6)'; } }}
            onMouseLeave={e => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 4px 20px rgba(99,102,241,0.4)'; }}
          >
            {isLoading ? 'Signing in...' : 'Sign In →'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.75rem', color: '#64748b', fontSize: '0.875rem' }}>
          Don't have an account?{' '}
          <a href="/signup" style={{ color: '#6366f1', fontWeight: 600, textDecoration: 'none' }}>
            Create one
          </a>
        </p>
      </div>
    </div>
  );
};

export default SignIn;