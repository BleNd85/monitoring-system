import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useLatestMetrics } from '../hooks/useMetrics'
import { useIncidents } from '../hooks/useIncidents'
import ContainersTable from '../components/ContainersTable'
import StatCard from '../components/dashboard/StatCard'
import DashboardTabs from '../components/dashboard/DashboardTabs'
import WidgetGrid from '../components/dashboard/WidgetGrid'
import IncidentsPanel from '../components/dashboard/IncidentsPanel'
import { formatValue } from '../utils/metrics'

const STORAGE_KEY = id => `widgets_${id}`

const DEFAULT_WIDGETS = [
    { id: '1', metricKeys: ['cpu.load_percent'], wide: false },
    { id: '2', metricKeys: ['memory.ram_percent'], wide: false },
]

export default function AgentDashboard() {
    const { agentId } = useParams()
    const navigate = useNavigate()
    const { data: latest } = useLatestMetrics(agentId)
    const { incidents, loading: incidentsLoading, refresh: refreshIncidents } = useIncidents(agentId)
    const [tab, setTab] = useState('charts')

    const [widgets, setWidgets] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY(agentId))) || DEFAULT_WIDGETS
        } catch {
            return DEFAULT_WIDGETS
        }
    })

    useEffect(() => {
        localStorage.setItem(STORAGE_KEY(agentId), JSON.stringify(widgets))
    }, [widgets, agentId])

    const addWidget = useCallback(() => {
        setWidgets(w => [...w, { id: Date.now().toString(), metricKeys: [], wide: false }])
    }, [])

    const removeWidget = useCallback((id) => {
        setWidgets(w => w.filter(widget => widget.id !== id))
    }, [])

    const changeMetrics = useCallback((id, keys) => {
        setWidgets(w => w.map(widget => widget.id === id ? { ...widget, metricKeys: keys } : widget))
    }, [])


    const unresolvedCount = incidents.filter(i => !i.resolved_at).length

    const stats = [
        { label: 'CPU', value: formatValue(latest?.cpu?.load_percent, '%') },
        { label: 'RAM', value: formatValue(latest?.memory?.ram_percent, '%') },
        { label: 'Swap', value: formatValue(latest?.memory?.swap_percent, '%') },
        { label: 'Load 1m', value: latest?.cpu?.load_avg_1m?.toFixed(2) ?? '—' },
    ]

    return (
        <div className="max-w-6xl mx-auto px-6 py-8">
            <div className="flex items-center gap-4 mb-6">
                <button
                    onClick={() => navigate('/')}
                    className="p-2 rounded-lg text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                    <ArrowLeft size={18} />
                </button>
                <div>
                    <h1 className="text-xl font-bold text-gray-900 dark:text-white">{agentId}</h1>
                    <p className="text-xs text-gray-400 mt-0.5">
                        {latest?.timestamp
                            ? `Last update: ${new Date(latest.timestamp).toLocaleTimeString()}`
                            : 'Waiting for data...'}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
                {stats.map(s => <StatCard key={s.label} label={s.label} value={s.value} />)}
            </div>

            <DashboardTabs tab={tab} setTab={setTab} unresolvedCount={unresolvedCount} />

            {tab === 'charts' && (
                <>
                    <WidgetGrid
                        agentId={agentId}
                        widgets={widgets}
                        onAdd={addWidget}
                        onRemove={removeWidget}
                        onChangeMetrics={changeMetrics}
                    />
                    <div className="rounded-xl border p-5 bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700">
                        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Containers</h2>
                        <ContainersTable containers={latest?.containers || []} />
                    </div>
                </>
            )}

            {tab === 'incidents' && (
                <IncidentsPanel
                    incidents={incidents}
                    loading={incidentsLoading}
                    onRefresh={refreshIncidents}
                />
            )}
        </div>
    )
}