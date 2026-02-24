import React, { useMemo } from 'react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
    PieChart, Pie, Cell, Tooltip
} from 'recharts';
import {
    AlertTriangle, Users, Bell, Calendar, Plus, Download, Upload,
    FileText, ChevronRight, Activity, TrendingUp, TrendingDown
} from 'lucide-react';

/* ─── Colour palette ──────────────────────────────────────── */


/* ─── Gradient stat card ──────────────────────────────────── */
const GradientStatCard = ({ title, value, subtitle, icon: Icon, gradient, shadowColor, trend, trendUp, onClick }) => (
    <div
        onClick={onClick}
        style={{
            background: gradient,
            borderRadius: '1.25rem',
            padding: '1.4rem 1.5rem',
            cursor: onClick ? 'pointer' : 'default',
            transition: 'all 0.25s ease',
            boxShadow: `0 8px 28px ${shadowColor}`,
            position: 'relative', overflow: 'hidden',
            color: 'white',
        }}
        onMouseEnter={e => { if (onClick) { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = `0 18px 40px ${shadowColor}`; } }}
        onMouseLeave={e => { if (onClick) { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 8px 28px ${shadowColor}`; } }}
    >
        {/* Decorative circles */}
        <div style={{ position: 'absolute', top: '-20px', right: '-20px', width: '100px', height: '100px', borderRadius: '50%', background: 'rgba(255,255,255,0.12)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: '-30px', right: '30px', width: '70px', height: '70px', borderRadius: '50%', background: 'rgba(255,255,255,0.08)', pointerEvents: 'none' }} />

        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{
                width: '48px', height: '48px', borderRadius: '14px',
                background: 'rgba(255,255,255,0.22)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }}>
                <Icon style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            {trend !== undefined && (
                <div style={{
                    display: 'flex', alignItems: 'center', gap: '3px',
                    background: 'rgba(255,255,255,0.2)', borderRadius: '9999px',
                    padding: '3px 10px', fontSize: '0.72rem', fontWeight: 700, color: 'white',
                }}>
                    {trendUp ? <TrendingUp style={{ width: '11px', height: '11px' }} /> : <TrendingDown style={{ width: '11px', height: '11px' }} />}
                    {trend}
                </div>
            )}
        </div>

        <div style={{ fontSize: '2.1rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1, marginBottom: '4px' }}>
            {value}
        </div>
        <div style={{ fontSize: '0.82rem', fontWeight: 600, opacity: 0.85 }}>{title}</div>
        {subtitle && <div style={{ fontSize: '0.72rem', opacity: 0.65, marginTop: '2px' }}>{subtitle}</div>}
    </div>
);

/* ─── Chart tooltip ───────────────────────────────────────── */
const ChartTooltip = ({ active, payload, label }) => {
    if (active && payload?.length) {
        return (
            <div style={{
                background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: '0.85rem',
                padding: '0.75rem 1rem', boxShadow: '0 8px 24px rgba(99,102,241,0.12)', fontSize: '0.8rem',
            }}>
                <div style={{ color: '#64748b', marginBottom: '0.4rem', fontWeight: 600 }}>{label}</div>
                {payload.map((p, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: p.color, display: 'inline-block' }} />
                        <span style={{ color: '#94a3b8' }}>{p.name}:</span>
                        <span style={{ color: '#1e293b', fontWeight: 700 }}>{p.value?.toFixed(1)}%</span>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

/* ─── Pie tooltip ─────────────────────────────────────────── */
const PieTooltip = ({ active, payload }) => {
    if (active && payload?.length) {
        return (
            <div style={{
                background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: '0.65rem',
                padding: '0.55rem 0.85rem', fontSize: '0.78rem', boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
            }}>
                <span style={{ color: payload[0].payload.color, fontWeight: 700 }}>{payload[0].name}</span>
                <span style={{ color: '#64748b', marginLeft: '6px' }}>{payload[0].value} students</span>
            </div>
        );
    }
    return null;
};

/* ─── Light card wrapper ──────────────────────────────────── */
const LightCard = ({ children, style = {} }) => (
    <div style={{
        background: '#ffffff', borderRadius: '1.25rem',
        border: '1.5px solid #f1f5f9',
        boxShadow: '0 2px 16px rgba(99,102,241,0.06)',
        ...style,
    }}>{children}</div>
);

/* ─── Activity item ───────────────────────────────────────── */
const ActivityItem = ({ name, action, color }) => (
    <div style={{
        display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.6rem 0.75rem',
        borderRadius: '0.75rem', transition: 'background 0.15s ease', cursor: 'pointer',
    }}
        onMouseEnter={e => e.currentTarget.style.background = '#f8fafc'}
        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
        <div style={{
            width: '36px', height: '36px', borderRadius: '50%', flexShrink: 0,
            background: `linear-gradient(135deg, ${color}33, ${color}18)`,
            border: `2px solid ${color}40`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.75rem', fontWeight: 700, color: color,
        }}>
            {name?.charAt(0)?.toUpperCase() || '?'}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#1e293b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{name}</div>
            <div style={{ fontSize: '0.71rem', color: '#94a3b8', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{action}</div>
        </div>
        <ChevronRight style={{ width: '14px', height: '14px', color: '#cbd5e1', flexShrink: 0 }} />
    </div>
);

/* ════════════════════════════════════════════════════════════
   Main Component
   ════════════════════════════════════════════════════════════ */
const OverviewTab = ({
    students,
    totalStudents,
    highRiskStudents,
    avgAttendance,
    interventionAlerts,
    monthlyTrendData,
    riskDistribution,
    onTabChange,
    onAddStudent,
    onImportCSV,
    onExport,
    onDownloadTemplate,
    onGenerateHighRiskNotifications,
    onStudentClick,
}) => {

    /* Activity feed */
    const recentActivity = useMemo(() => {
        const highRisk = students.filter(s => s.riskScore >= 0.5).slice(0, 3)
            .map(s => ({ name: s.name, action: `Flagged — ${s.status} (${(s.riskScore * 100).toFixed(0)}%)`, color: '#ef4444', key: s.id + 'r' }));
        const recent = students.filter(s => s.lastActivity === 'Just added' || s.lastActivity === 'Imported').slice(0, 3)
            .map(s => ({ name: s.name, action: s.lastActivity === 'Just added' ? 'Added to system' : 'Imported via CSV', color: '#6366f1', key: s.id + 'a' }));
        const all = [...highRisk, ...recent].slice(0, 6);
        if (all.length === 0) return [
            { name: 'System', action: 'Dashboard is ready', color: '#14b8a6', key: 'sys1' },
            { name: 'Admin', action: 'Import students to see activity', color: '#6366f1', key: 'sys2' },
        ];
        return all;
    }, [students]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

            {/* ── Page Header ──────────────────────────────────── */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.55rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
                        Student Analytics Dashboard
                    </h1>
                    <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '0.2rem' }}>
                        Welcome! Here's an overview of student performance and dropout risk analytics.
                    </p>
                </div>
                <button
                    onClick={onAddStudent}
                    style={{
                        display: 'flex', alignItems: 'center', gap: '6px',
                        padding: '0.6rem 1.2rem', borderRadius: '0.75rem', border: 'none',
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        color: 'white', fontSize: '0.875rem', fontWeight: 700,
                        cursor: 'pointer', boxShadow: '0 4px 18px rgba(99,102,241,0.35)',
                        transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 28px rgba(99,102,241,0.5)'; }}
                    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 18px rgba(99,102,241,0.35)'; }}
                >
                    <Plus style={{ width: '16px', height: '16px' }} />
                    Add Student
                </button>
            </div>

            {/* ── Colorful Stat Cards ───────────────────────────── */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem' }}>
                <GradientStatCard
                    title="Total Students"
                    value={totalStudents}
                    subtitle="Active enrollments"
                    icon={Users}
                    gradient="linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
                    shadowColor="rgba(99,102,241,0.3)"
                    trend={`${students.filter(s => s.lastActivity === 'Just added').length} new`}
                    trendUp={true}
                    onClick={() => onTabChange('students')}
                />
                <GradientStatCard
                    title="High Risk"
                    value={highRiskStudents}
                    subtitle="Require immediate attention"
                    icon={AlertTriangle}
                    gradient="linear-gradient(135deg, #f43f5e 0%, #ef4444 100%)"
                    shadowColor="rgba(244,63,94,0.3)"
                    trend={`${((highRiskStudents / (totalStudents || 1)) * 100).toFixed(0)}% of total`}
                    trendUp={highRiskStudents === 0}
                    onClick={() => onTabChange('predictions')}
                />
                <GradientStatCard
                    title="Avg Attendance"
                    value={`${avgAttendance}%`}
                    subtitle="Across all students"
                    icon={Calendar}
                    gradient="linear-gradient(135deg, #06b6d4 0%, #14b8a6 100%)"
                    shadowColor="rgba(6,182,212,0.3)"
                    trend={avgAttendance < 75 ? 'Below target' : 'On Track ✓'}
                    trendUp={avgAttendance >= 75}
                />
                <GradientStatCard
                    title="Alerts"
                    value={interventionAlerts}
                    subtitle="Active notifications"
                    icon={Bell}
                    gradient="linear-gradient(135deg, #f59e0b 0%, #f97316 100%)"
                    shadowColor="rgba(245,158,11,0.3)"
                    trend={interventionAlerts > 0 ? 'Action needed' : 'All clear'}
                    trendUp={interventionAlerts === 0}
                />
            </div>

            {/* ── Chart + Activity Feed Row ─────────────────────── */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '1rem', alignItems: 'start' }}>

                {/* Trend Area Chart */}
                <LightCard style={{ padding: '1.4rem 1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                        <div>
                            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>Dropout Risk Trends</h3>
                            <p style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '2px' }}>Predicted vs actual over 6 months</p>
                        </div>
                        <select
                            defaultValue="6months"
                            style={{
                                padding: '0.35rem 0.85rem', borderRadius: '0.65rem',
                                background: '#f8fafc', border: '1.5px solid #e2e8f0',
                                color: '#64748b', fontSize: '0.8rem', cursor: 'pointer', outline: 'none',
                                transition: 'border-color 0.2s',
                            }}
                        >
                            <option value="6months">Last 6 months</option>
                            <option value="3months">Last 3 months</option>
                        </select>
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                        <AreaChart data={monthlyTrendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                            <defs>
                                <linearGradient id="gPredicted" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.02} />
                                </linearGradient>
                                <linearGradient id="gActual" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.25} />
                                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.02} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                            <XAxis dataKey="month" stroke="#cbd5e1" fontSize={11} tickLine={false} axisLine={false} />
                            <YAxis stroke="#cbd5e1" fontSize={11} tickLine={false} axisLine={false} />
                            <Tooltip content={<ChartTooltip />} />
                            <Area type="monotone" dataKey="predictions" name="Predicted" stroke="#6366f1" strokeWidth={2.5} fill="url(#gPredicted)" dot={false} isAnimationActive={false} />
                            <Area type="monotone" dataKey="dropoutRate" name="Actual" stroke="#14b8a6" strokeWidth={2.5} fill="url(#gActual)" dot={false} isAnimationActive={false} />
                        </AreaChart>
                    </ResponsiveContainer>
                    <div style={{ display: 'flex', gap: '1.25rem', justifyContent: 'center', marginTop: '0.6rem' }}>
                        {[{ label: 'Predicted', color: '#6366f1' }, { label: 'Actual', color: '#14b8a6' }].map(l => (
                            <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <div style={{ width: '24px', height: '3px', borderRadius: '9999px', background: l.color }} />
                                <span style={{ fontSize: '0.73rem', color: '#94a3b8' }}>{l.label}</span>
                            </div>
                        ))}
                    </div>
                </LightCard>

                {/* Activity Feed */}
                <LightCard style={{ padding: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
                        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a' }}>Recent Activity</h3>
                        <Activity style={{ width: '16px', height: '16px', color: '#cbd5e1' }} />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        {recentActivity.map(item => (
                            <ActivityItem key={item.key} name={item.name} action={item.action} color={item.color} />
                        ))}
                    </div>
                </LightCard>
            </div>

            {/* ── Bottom Row ────────────────────────────────────── */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>

                {/* Risk Distribution */}
                <LightCard style={{ padding: '1.25rem 1.5rem' }}>
                    <div style={{ marginBottom: '0.75rem' }}>
                        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a' }}>Risk Distribution</h3>
                        <p style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '2px' }}>Breakdown by risk level</p>
                    </div>

                    {totalStudents === 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2.5rem 0', color: '#cbd5e1' }}>
                            <Users style={{ width: '36px', height: '36px', marginBottom: '0.75rem' }} />
                            <p style={{ fontSize: '0.82rem' }}>No student data yet</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <ResponsiveContainer width={160} height={160}>
                                <PieChart>
                                    <Pie data={riskDistribution} cx="50%" cy="50%" innerRadius={45} outerRadius={72} dataKey="value" isAnimationActive={false} strokeWidth={0}>
                                        {riskDistribution.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                                    </Pie>
                                    <Tooltip content={<PieTooltip />} />
                                </PieChart>
                            </ResponsiveContainer>
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                                {riskDistribution.map((item, i) => (
                                    <div key={i}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                                            <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: item.color, display: 'inline-block' }} />
                                                {item.name}
                                            </span>
                                            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: item.color }}>{item.value}</span>
                                        </div>
                                        <div style={{ height: '5px', borderRadius: '9999px', background: '#f1f5f9' }}>
                                            <div style={{
                                                height: '100%', borderRadius: '9999px',
                                                background: `linear-gradient(90deg, ${item.color}cc, ${item.color})`,
                                                width: `${totalStudents > 0 ? (item.value / totalStudents) * 100 : 0}%`,
                                                transition: 'width 0.6s ease',
                                            }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </LightCard>

                {/* Quick Actions */}
                <LightCard style={{ padding: '1.25rem 1.5rem' }}>
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Quick Actions</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                        {[
                            { label: 'Import CSV', icon: Upload, gradient: 'linear-gradient(135deg, #6366f1, #8b5cf6)', shadow: 'rgba(99,102,241,0.25)', action: onImportCSV },
                            { label: 'Export CSV', icon: Download, gradient: 'linear-gradient(135deg, #14b8a6, #06b6d4)', shadow: 'rgba(20,184,166,0.25)', action: onExport },
                            { label: 'Template', icon: FileText, gradient: 'linear-gradient(135deg, #8b5cf6, #a855f7)', shadow: 'rgba(139,92,246,0.25)', action: onDownloadTemplate },
                            { label: 'Send Alerts', icon: Bell, gradient: 'linear-gradient(135deg, #f59e0b, #f97316)', shadow: 'rgba(245,158,11,0.25)', action: onGenerateHighRiskNotifications },
                        ].map(({ label, icon: Icon, gradient, shadow, action }) => (
                            <button
                                key={label}
                                onClick={action}
                                style={{
                                    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                                    gap: '0.5rem', padding: '1rem 0.5rem',
                                    borderRadius: '0.85rem', border: 'none', cursor: 'pointer',
                                    background: gradient, color: 'white',
                                    fontSize: '0.78rem', fontWeight: 700,
                                    boxShadow: `0 4px 14px ${shadow}`,
                                    transition: 'all 0.2s ease',
                                }}
                                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = `0 10px 24px ${shadow}`; }}
                                onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 4px 14px ${shadow}`; }}
                            >
                                <div style={{
                                    width: '38px', height: '38px', borderRadius: '10px',
                                    background: 'rgba(255,255,255,0.2)',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                }}>
                                    <Icon style={{ width: '18px', height: '18px', color: 'white' }} />
                                </div>
                                {label}
                            </button>
                        ))}
                    </div>
                </LightCard>
            </div>

            {/* ── High Risk Alert Table ─────────────────────────── */}
            {highRiskStudents > 0 && (
                <LightCard style={{ padding: '1.25rem 1.5rem', border: '1.5px solid #fecaca' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <div style={{
                                width: '38px', height: '38px', borderRadius: '10px',
                                background: 'linear-gradient(135deg, #fef2f2, #fee2e2)',
                                border: '1.5px solid #fecaca',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                <AlertTriangle style={{ width: '18px', height: '18px', color: '#ef4444' }} />
                            </div>
                            <div>
                                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0f172a' }}>High Risk Students</h3>
                                <p style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{highRiskStudents} students require immediate attention</p>
                            </div>
                        </div>
                        <button
                            onClick={onGenerateHighRiskNotifications}
                            style={{
                                display: 'flex', alignItems: 'center', gap: '6px',
                                padding: '0.45rem 1rem', borderRadius: '0.65rem', border: 'none',
                                background: 'linear-gradient(135deg, #ef4444, #f43f5e)',
                                color: 'white', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
                                boxShadow: '0 4px 14px rgba(239,68,68,0.3)',
                                transition: 'all 0.2s ease',
                            }}
                            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(239,68,68,0.4)'; }}
                            onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 14px rgba(239,68,68,0.3)'; }}
                        >
                            <Bell style={{ width: '14px', height: '14px' }} />
                            Send Alerts
                        </button>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1.5px solid #f1f5f9' }}>
                                    {['Student', 'Attendance', 'Grade', 'Risk Score', 'Status', ''].map(h => (
                                        <th key={h} style={{
                                            paddingBottom: '0.65rem', textAlign: 'left',
                                            fontSize: '0.7rem', fontWeight: 700, color: '#94a3b8',
                                            textTransform: 'uppercase', letterSpacing: '0.06em',
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {students.filter(s => s.riskScore >= 0.5).slice(0, 5).map(student => (
                                    <tr
                                        key={student.id}
                                        onClick={() => onStudentClick(student)}
                                        style={{ cursor: 'pointer', transition: 'background 0.15s ease' }}
                                        onMouseEnter={e => e.currentTarget.style.background = '#fff5f5'}
                                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                                    >
                                        <td style={{ padding: '0.7rem 0' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                                <div style={{
                                                    width: '30px', height: '30px', borderRadius: '50%', flexShrink: 0,
                                                    background: 'linear-gradient(135deg, #fecaca, #fca5a5)',
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontSize: '0.72rem', fontWeight: 700, color: '#ef4444',
                                                }}>{student.name?.charAt(0)}</div>
                                                <div>
                                                    <div style={{ fontSize: '0.83rem', fontWeight: 700, color: '#0f172a' }}>{student.name}</div>
                                                    <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{student.id}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ padding: '0.7rem 0', fontSize: '0.83rem', color: '#64748b' }}>{student.attendance}%</td>
                                        <td style={{ padding: '0.7rem 0', fontSize: '0.83rem', color: '#64748b' }}>{student.avgGrade}%</td>
                                        <td style={{ padding: '0.7rem 0' }}>
                                            <span style={{ fontSize: '0.83rem', fontWeight: 800, color: '#ef4444' }}>
                                                {(student.riskScore * 100).toFixed(0)}%
                                            </span>
                                        </td>
                                        <td style={{ padding: '0.7rem 0' }}>
                                            <span style={{
                                                padding: '0.2rem 0.7rem', borderRadius: '9999px',
                                                fontSize: '0.68rem', fontWeight: 700,
                                                background: '#fef2f2', color: '#ef4444',
                                                border: '1.5px solid #fecaca',
                                            }}>High Risk</span>
                                        </td>
                                        <td style={{ padding: '0.7rem 0' }}>
                                            <ChevronRight style={{ width: '14px', height: '14px', color: '#d1d5db' }} />
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </LightCard>
            )}
        </div>
    );
};

export default OverviewTab;
