import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    LayoutDashboard, Users, TrendingUp, AlertTriangle,
    LogOut, Bell, ChevronRight, GraduationCap, X, Menu
} from 'lucide-react';
import { notificationManager } from '../../utils/notificationManager';

const NAV_ITEMS = [
    { key: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { key: 'students', label: 'Students', icon: Users },
    { key: 'analytics', label: 'Analytics', icon: TrendingUp },
    { key: 'predictions', label: 'Predictions', icon: AlertTriangle },
];

const Sidebar = ({ selectedTab, onTabChange }) => {
    const navigate = useNavigate();
    const [mobileOpen, setMobileOpen] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);

    React.useEffect(() => {
        const update = () => setUnreadCount(notificationManager.getUnreadCount());
        update();
        const t = setInterval(update, 5000);
        return () => clearInterval(t);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/signin');
    };

    const SidebarContent = () => (
        <div style={{
            display: 'flex', flexDirection: 'column', height: '100%',
            padding: '1.25rem 0.75rem',
        }}>
            {/* Logo */}
            <div
                onClick={() => { onTabChange('overview'); setMobileOpen(false); }}
                style={{
                    display: 'flex', alignItems: 'center', gap: '0.65rem',
                    cursor: 'pointer', padding: '0.4rem 0.75rem', marginBottom: '2rem',
                }}
            >
                <div style={{
                    width: '38px', height: '38px', flexShrink: 0,
                    background: 'rgba(255,255,255,0.2)',
                    borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 0 18px rgba(255,255,255,0.3)',
                }}>
                    <GraduationCap style={{ width: '22px', height: '22px', color: 'white' }} />
                </div>
                <div style={{ lineHeight: 1.1 }}>
                    <span style={{
                        color: 'white',
                        fontWeight: 800, fontSize: '1.05rem', letterSpacing: '-0.02em',
                    }}>SmartEdu</span>
                    <span style={{ color: 'rgba(255,255,255,0.75)', fontWeight: 800, fontSize: '1.05rem', letterSpacing: '-0.02em' }}>Mine</span>
                </div>
            </div>

            {/* Main Navigation */}
            <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {NAV_ITEMS.map(({ key, label, icon: Icon }) => {
                    const active = selectedTab === key;
                    return (
                        <button
                            key={key}
                            onClick={() => { onTabChange(key); setMobileOpen(false); }}
                            style={{
                                display: 'flex', alignItems: 'center', gap: '0.75rem',
                                width: '100%', padding: '0.65rem 0.85rem',
                                borderRadius: '0.75rem', border: 'none', cursor: 'pointer',
                                fontSize: '0.875rem', fontWeight: active ? 600 : 500,
                                transition: 'all 0.2s ease',
                                background: active
                                    ? 'rgba(255,255,255,0.2)'
                                    : 'transparent',
                                color: active ? '#ffffff' : 'rgba(255,255,255,0.6)',
                                boxShadow: active ? '0 2px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2)' : 'none',
                                borderLeft: active ? '3px solid rgba(255,255,255,0.9)' : '3px solid transparent',
                                textAlign: 'left',
                                position: 'relative',
                            }}
                            onMouseEnter={e => {
                                if (!active) {
                                    e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                                    e.currentTarget.style.color = 'rgba(255,255,255,0.85)';
                                }
                            }}
                            onMouseLeave={e => {
                                if (!active) {
                                    e.currentTarget.style.background = 'transparent';
                                    e.currentTarget.style.color = 'rgba(255,255,255,0.6)';
                                }
                            }}
                        >
                            <Icon style={{ width: '17px', height: '17px', flexShrink: 0 }} />
                            <span style={{ flex: 1 }}>{label}</span>
                            {active && (
                                <ChevronRight style={{ width: '14px', height: '14px', opacity: 0.6 }} />
                            )}
                        </button>
                    );
                })}
            </nav>

            {/* Support Section */}
            <div style={{ marginTop: 'auto' }}>
                <div style={{
                    fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.08em',
                    color: 'rgba(255,255,255,0.45)', textTransform: 'uppercase', padding: '0 0.85rem',
                    marginBottom: '0.5rem',
                }}>Support</div>

                {/* Notifications */}
                <button
                    onClick={() => navigate('/dashboard')}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                        width: '100%', padding: '0.65rem 0.85rem',
                        borderRadius: '0.75rem', border: 'none', cursor: 'pointer',
                        fontSize: '0.875rem', fontWeight: 500, transition: 'all 0.2s ease',
                        background: 'transparent', color: 'rgba(255,255,255,0.6)',
                        borderLeft: '3px solid transparent', textAlign: 'left',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; e.currentTarget.style.color = 'white'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(255,255,255,0.6)'; }}
                >
                    <Bell style={{ width: '17px', height: '17px', flexShrink: 0 }} />
                    <span style={{ flex: 1 }}>Notifications</span>
                    {unreadCount > 0 && (
                        <span style={{
                            background: 'rgba(255,255,255,0.9)',
                            color: '#6366f1', fontSize: '0.65rem', fontWeight: 700,
                            padding: '2px 7px', borderRadius: '9999px',
                        }}>{unreadCount > 9 ? '9+' : unreadCount}</span>
                    )}
                </button>

                {/* Divider */}
                <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)', margin: '0.5rem 0.85rem' }} />

                {/* Logout */}
                <button
                    onClick={handleLogout}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '0.75rem',
                        width: '100%', padding: '0.65rem 0.85rem',
                        borderRadius: '0.75rem', border: 'none', cursor: 'pointer',
                        fontSize: '0.875rem', fontWeight: 500, transition: 'all 0.2s ease',
                        background: 'transparent', color: 'rgba(255,255,255,0.6)',
                        borderLeft: '3px solid transparent', textAlign: 'left',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = 'white'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'rgba(255,255,255,0.6)'; }}
                >
                    <LogOut style={{ width: '17px', height: '17px', flexShrink: 0 }} />
                    <span>Logout</span>
                </button>
            </div>
        </div>
    );

    const SIDEBAR_WIDTH = 240;

    return (
        <>
            {/* Desktop Sidebar */}
            <aside style={{
                position: 'fixed', top: 0, left: 0, bottom: 0,
                width: `${SIDEBAR_WIDTH}px`, zIndex: 40,
                background: 'linear-gradient(160deg, #4f46e5 0%, #6366f1 40%, #7c3aed 100%)',
                backdropFilter: 'blur(20px)',
                borderRight: '1px solid rgba(255,255,255,0.1)',
                boxShadow: '4px 0 30px rgba(0,0,0,0.4)',
                display: 'flex', flexDirection: 'column',
            }} className="hidden md:flex">
                {/* Subtle top accent */}
                <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0, height: '2px',
                    background: 'rgba(255,255,255,0.3)',
                }} />
                <SidebarContent />
            </aside>

            {/* Mobile Hamburger */}
            <button
                onClick={() => setMobileOpen(true)}
                className="md:hidden"
                style={{
                    position: 'fixed', top: '12px', left: '12px', zIndex: 60,
                    width: '40px', height: '40px', borderRadius: '10px', border: 'none',
                    background: 'rgba(255,255,255,0.15)', color: '#ffffff',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', boxShadow: '0 0 12px rgba(255,255,255,0.2)',
                }}
                aria-label="Open sidebar"
            >
                <Menu style={{ width: '20px', height: '20px' }} />
            </button>

            {/* Mobile Overlay */}
            {mobileOpen && (
                <div
                    style={{
                        position: 'fixed', inset: 0, zIndex: 50,
                        background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
                    }}
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Mobile Sidebar */}
            <aside style={{
                position: 'fixed', top: 0, left: mobileOpen ? 0 : '-100%', bottom: 0,
                width: `${SIDEBAR_WIDTH}px`, zIndex: 55,
                background: 'linear-gradient(160deg, #4f46e5 0%, #6366f1 40%, #7c3aed 100%)',
                borderRight: '1px solid rgba(255,255,255,0.1)',
                boxShadow: '4px 0 30px rgba(0,0,0,0.5)',
                transition: 'left 0.3s cubic-bezier(0.4,0,0.2,1)',
                display: 'flex', flexDirection: 'column',
            }} className="md:hidden">
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '2px', background: 'rgba(255,255,255,0.3)' }} />
                <button
                    onClick={() => setMobileOpen(false)}
                    style={{
                        position: 'absolute', top: '12px', right: '12px',
                        width: '30px', height: '30px', borderRadius: '8px', border: 'none',
                        background: 'rgba(148,163,184,0.1)', color: '#94a3b8',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
                    }}
                    aria-label="Close sidebar"
                >
                    <X style={{ width: '16px', height: '16px' }} />
                </button>
                <SidebarContent />
            </aside>
        </>
    );
};

export default Sidebar;
