import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Settings, User, LogOut, Search } from 'lucide-react';
import NotificationDropdown from '../Notifications/NotificationDropdown';
import { notificationManager } from '../../utils/notificationManager';

const TopBar = ({ interventionAlerts }) => {
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [searchValue, setSearchValue] = useState('');

  const user = JSON.parse(localStorage.getItem('user')) || null;

  React.useEffect(() => {
    const update = () => setUnreadCount(notificationManager.getUnreadCount());
    update();
    const interval = setInterval(update, 5000);
    return () => clearInterval(interval);
  }, []);

  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });

  return (
    <header style={{
      position: 'fixed', top: 0, left: '240px', right: 0, zIndex: 30,
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(99,102,241,0.12)',
      boxShadow: '0 2px 20px rgba(99,102,241,0.08)',
    }}>
      <div style={{ padding: '0 1.5rem', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>

        {/* Search Bar */}
        <div style={{ position: 'relative', maxWidth: '340px', width: '100%' }}>
          <Search style={{
            position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)',
            width: '15px', height: '15px', color: '#94a3b8', pointerEvents: 'none',
          }} />
          <input
            type="text"
            placeholder="Search students, analytics..."
            value={searchValue}
            onChange={e => setSearchValue(e.target.value)}
            style={{
              width: '100%', padding: '0.5rem 1rem 0.5rem 2.5rem',
              borderRadius: '0.85rem', border: '1.5px solid #e2e8f0',
              background: '#f8fafc',
              color: '#1e293b', fontSize: '0.85rem', outline: 'none',
              transition: 'all 0.2s ease',
            }}
            onFocus={e => {
              e.target.style.borderColor = '#6366f1';
              e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)';
              e.target.style.background = '#fff';
            }}
            onBlur={e => {
              e.target.style.borderColor = '#e2e8f0';
              e.target.style.boxShadow = 'none';
              e.target.style.background = '#f8fafc';
            }}
          />
        </div>

        {/* Right Side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>

          {/* Date */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.4rem 0.9rem', borderRadius: '0.65rem',
            border: '1.5px solid #e2e8f0', background: '#f8fafc',
            color: '#64748b', fontSize: '0.8rem', fontWeight: 500,
          }} className="hidden sm:flex">
            <span>📅</span>
            <span>{dateStr}</span>
          </div>

          {/* Notification Bell */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
              style={{
                width: '40px', height: '40px', borderRadius: '10px', border: '1.5px solid #e2e8f0',
                cursor: 'pointer', background: '#f8fafc', color: '#64748b',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s ease', position: 'relative',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.color = '#6366f1'; e.currentTarget.style.background = '#eef2ff'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b'; e.currentTarget.style.background = '#f8fafc'; }}
            >
              <Bell style={{ width: '17px', height: '17px' }} />
              {unreadCount > 0 && (
                <span style={{
                  position: 'absolute', top: '-4px', right: '-4px',
                  width: '18px', height: '18px', borderRadius: '50%',
                  background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                  color: 'white', fontSize: '0.65rem', fontWeight: 700,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(239,68,68,0.45)',
                }}>
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
            <NotificationDropdown
              isOpen={showNotifications}
              onClose={() => setShowNotifications(false)}
              onNotificationClick={() => setShowNotifications(false)}
              onUpdate={() => setUnreadCount(notificationManager.getUnreadCount())}
            />
          </div>

          {/* Settings */}
          <button
            onClick={() => navigate('/settings')}
            aria-label="Settings"
            style={{
              width: '40px', height: '40px', borderRadius: '10px', border: '1.5px solid #e2e8f0',
              cursor: 'pointer', background: '#f8fafc', color: '#64748b',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.color = '#6366f1'; e.currentTarget.style.background = '#eef2ff'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.color = '#64748b'; e.currentTarget.style.background = '#f8fafc'; }}
          >
            <Settings style={{ width: '17px', height: '17px' }} />
          </button>

          {/* User Avatar */}
          <div style={{ position: 'relative' }} className="hidden sm:block">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '5px 12px 5px 5px', borderRadius: '10px', cursor: 'pointer',
                border: '1.5px solid #e2e8f0',
                background: '#f8fafc', transition: 'all 0.2s ease',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366f1'; e.currentTarget.style.background = '#eef2ff'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.background = '#f8fafc'; }}
            >
              <div style={{
                width: '30px', height: '30px', borderRadius: '8px',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(99,102,241,0.35)',
              }}>
                <span style={{ color: 'white', fontSize: '0.82rem', fontWeight: 700 }}>
                  {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <span style={{ color: '#374151', fontSize: '0.83rem', fontWeight: 600 }}>
                {user?.name || 'User'}
              </span>
            </button>

            {showUserMenu && (
              <div style={{
                position: 'absolute', right: 0, top: 'calc(100% + 8px)',
                width: '180px', borderRadius: '14px', zIndex: 100,
                background: '#ffffff',
                border: '1.5px solid #e2e8f0',
                boxShadow: '0 12px 32px rgba(99,102,241,0.12), 0 4px 12px rgba(0,0,0,0.08)',
                padding: '6px',
              }}>
                {[
                  { label: 'Profile', icon: User, action: () => { setShowUserMenu(false); navigate('/profile'); } },
                  { label: 'Sign Out', icon: LogOut, action: () => { localStorage.removeItem('token'); localStorage.removeItem('user'); navigate('/signin'); }, danger: true },
                ].map(({ label, icon: Icon, action, danger }) => (
                  <button key={label} onClick={action} style={{
                    display: 'flex', alignItems: 'center', gap: '10px', width: '100%',
                    padding: '8px 12px', borderRadius: '8px', border: 'none', cursor: 'pointer',
                    background: 'transparent', color: danger ? '#ef4444' : '#374151',
                    fontSize: '0.85rem', fontWeight: 500, transition: 'all 0.15s ease', textAlign: 'left',
                  }}
                    onMouseEnter={e => { e.currentTarget.style.background = danger ? '#fef2f2' : '#f8fafc'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                  >
                    <Icon style={{ width: '15px', height: '15px' }} />
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
