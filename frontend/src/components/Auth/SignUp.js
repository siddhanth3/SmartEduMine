import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/api';

const inputStyle = {
  width: '100%', padding: '0.75rem 1rem', borderRadius: '0.75rem',
  background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(148,163,184,0.12)',
  color: '#f1f5f9', outline: 'none', fontSize: '0.875rem', transition: 'all 0.25s ease'
};

const labelStyle = {
  display: 'block', color: '#94a3b8', fontSize: '0.78rem', fontWeight: 600,
  marginBottom: '0.45rem', letterSpacing: '0.04em', textTransform: 'uppercase'
};

const SignUp = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', confirmPassword: '', role: 'teacher',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleFocus = (e) => { e.target.style.borderColor = 'rgba(99,102,241,0.5)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)'; };
  const handleBlur = (e) => { e.target.style.borderColor = 'rgba(148,163,184,0.12)'; e.target.style.boxShadow = 'none'; };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (formData.password !== formData.confirmPassword) { setError('Passwords do not match'); return; }
    setIsLoading(true);
    try {
      const { token, user } = await authService.signUp(formData);
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Registration failed');
    } finally { setIsLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden py-12 px-4">
      {/* Animated orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div style={{ position: 'absolute', top: '-5%', right: '-5%', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)', borderRadius: '50%', animation: 'orb-drift 16s ease-in-out infinite alternate' }} />
        <div style={{ position: 'absolute', bottom: '-10%', left: '-5%', width: '450px', height: '450px', background: 'radial-gradient(circle, rgba(20,184,166,0.12) 0%, transparent 70%)', borderRadius: '50%', animation: 'orb-drift 20s ease-in-out infinite alternate-reverse' }} />
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(148,163,184,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.03) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
      </div>

      <div className="relative z-10 w-full max-w-md fade-in-up" style={{
        background: 'rgba(10,15,28,0.88)', backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)',
        border: '1px solid rgba(99,102,241,0.18)', borderRadius: '1.5rem', padding: '2.25rem',
        boxShadow: '0 24px 80px rgba(0,0,0,0.6), 0 0 60px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.05)'
      }}>

        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '1.75rem' }}>
          <div style={{ width: '44px', height: '44px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(99,102,241,0.45)', padding: '7px' }}>
            <img src="/logo.png" alt="SmartEduMine" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </div>
          <div>
            <span style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6, #14b8a6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontWeight: 800, fontSize: '1.4rem' }}>SmartEdu</span>
            <span style={{ color: '#f1f5f9', fontWeight: 800, fontSize: '1.4rem' }}>Mine</span>
          </div>
        </div>

        <h2 style={{ color: '#f1f5f9', fontWeight: 700, fontSize: '1.4rem', textAlign: 'center', marginBottom: '4px' }}>Create Account</h2>
        <p style={{ color: '#64748b', textAlign: 'center', marginBottom: '1.75rem', fontSize: '0.875rem' }}>Join SmartEduMine and protect your students</p>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.25)', color: '#f87171', padding: '0.65rem 1rem', borderRadius: '0.75rem', marginBottom: '1rem', fontSize: '0.85rem', boxShadow: '0 0 12px rgba(239,68,68,0.08)' }}>{error}</div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {[
            { id: 'name', label: 'Full Name', type: 'text', ph: 'Dr. Jane Smith' },
            { id: 'email', label: 'Email Address', type: 'email', ph: 'you@institution.edu' },
          ].map(({ id, label, type, ph }) => (
            <div key={id}>
              <label htmlFor={id} style={labelStyle}>{label}</label>
              <input id={id} name={id} type={type} required placeholder={ph}
                value={formData[id]} onChange={handleChange} onFocus={handleFocus} onBlur={handleBlur} style={inputStyle} />
            </div>
          ))}

          <div>
            <label htmlFor="role" style={labelStyle}>Role</label>
            <select id="role" name="role" value={formData.role} onChange={handleChange} onFocus={handleFocus} onBlur={handleBlur}
              style={{ ...inputStyle, appearance: 'none', cursor: 'pointer', backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")", backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center', paddingRight: '2.5rem' }}>
              <option value="teacher">Teacher / Educator</option>
              <option value="admin">Administrator</option>
              <option value="counselor">Academic Counselor</option>
            </select>
          </div>

          {[
            { id: 'password', label: 'Password', ph: 'Create a strong password' },
            { id: 'confirmPassword', label: 'Confirm Password', ph: 'Repeat your password' },
          ].map(({ id, label, ph }) => (
            <div key={id}>
              <label htmlFor={id} style={labelStyle}>{label}</label>
              <input id={id} name={id} type="password" required placeholder={ph}
                value={formData[id]} onChange={handleChange} onFocus={handleFocus} onBlur={handleBlur} style={inputStyle} />
            </div>
          ))}

          <button type="submit" disabled={isLoading} style={{
            width: '100%', padding: '0.875rem',
            background: isLoading ? 'rgba(99,102,241,0.5)' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            color: 'white', border: 'none', borderRadius: '0.75rem',
            fontWeight: 700, fontSize: '0.95rem', cursor: isLoading ? 'not-allowed' : 'pointer',
            transition: 'all 0.25s ease', boxShadow: '0 4px 20px rgba(99,102,241,0.4)', marginTop: '0.5rem'
          }}
            onMouseEnter={e => { if (!isLoading) { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 8px 30px rgba(99,102,241,0.6)'; } }}
            onMouseLeave={e => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 4px 20px rgba(99,102,241,0.4)'; }}
          >
            {isLoading ? 'Creating account...' : 'Create Account →'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', color: '#64748b', fontSize: '0.875rem' }}>
          Already have an account?{' '}
          <a href="/signin" style={{ color: '#6366f1', fontWeight: 600, textDecoration: 'none' }}>Sign in</a>
        </p>
      </div>
    </div>
  );
};

export default SignUp;