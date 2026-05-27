import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, AlertTriangle, LayoutGrid, RefreshCw } from 'lucide-react'
import { useLatestMetrics } from '../hooks/useMetrics'
import { useIncidents } from '../hooks/useIncidents'
import MetricWidget from '../components/MetricWidget'
import ContainersTable from '../components/ContainersTable'
import IncidentList from '../components/incidents/IncidentList'
import { formatValue } from '../utils/metrics'

const STORAGE_KEY = id => `widgets_${id}`

const DEFAULT_WIDGETS = [
    { id: '1', metricKeys: ['cpu.load_percent'] },
    { id: '2', metricKeys: ['memory.ram_percent'] },
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

    const addWidget = () => {
        setWidgets(w => [...w, { id: Date.now().toString(), metricKeys: [] }])
    }

    const removeWidget = (id) => {
        setWidgets(w => w.filter(widget => widget.id !== id))
    }

    const changeMetrics = (id, keys) => {
        setWidgets(w => w.map(widget => widget.id === id ? { ...widget, metricKeys: keys } : widget))
    }

    const unresolvedCount = incidents.filter(i => !i.resolved_at).length

    const stats = [
        { label: 'CPU', value: formatValue(latest?.cpu?.load_percent, '%') },
        { label: 'RAM', value: formatValue(latest?.memory?.ram_percent, '%') },
        { label: 'Swap', value: formatValue(latest?.memory?.swap_percent, '%') },
        { label: 'Load 1m', value: latest?.cpu?.load_avg_1m?.toFixed(2) ?? '—' },
    ]

    return (
        <div className="max-w-6xl mx-auto px-6 py-8">

            {/* Header */}
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

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
                {stats.map(s => (
                    <div
                        key={s.label}
                        className="rounded-xl p-4 border bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700"
                    >
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">{s.label}</div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</div>
                    </div>
                ))}
            </div>

            {/* Tabs */}
            <div className="flex items-center gap-1 mb-5">
                <button
                    onClick={() => setTab('charts')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === 'charts'
                        ? 'bg-orange-500 text-white'
                        : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
                        }`}
                >
                    <LayoutGrid size={15} />
                    Charts
                </button>
                <button
                    onClick={() => setTab('incidents')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === 'incidents'
                        ? 'bg-orange-500 text-white'
                        : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
                        }`}
                >
                    <AlertTriangle size={15} />
                    Incidents
                    {unresolvedCount > 0 && (
                        <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-red-500 text-white font-bold">
                            {unresolvedCount}
                        </span>
                    )}
                </button>
            </div>

            {/* Charts tab */}
            {tab === 'charts' && (
                <>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Metric Charts</h2>
                        <button
                            onClick={addWidget}
                            className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg bg-orange-500 hover:bg-orange-600 text-white transition-colors"
                        >
                            <Plus size={14} /> Add Chart
                        </button>
                    </div>

                    {widgets.length === 0 ? (
                        <div className="text-center py-12 text-gray-400 text-sm">
                            No charts yet. Click "Add Chart" to create one.
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                            {widgets.map(w => (
                                <MetricWidget
                                    key={w.id}
                                    agentId={agentId}
                                    widgetId={w.id}
                                    metricKeys={w.metricKeys}
                                    onRemove={removeWidget}
                                    onChangeMetrics={changeMetrics}
                                />
                            ))}
                        </div>
                    )}

                    <div className="rounded-xl border p-5 bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700">
                        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Containers</h2>
                        <ContainersTable containers={latest?.containers || []} />
                    </div>
                </>
            )}

            {/* Incidents tab */}
            {tab === 'incidents' && (
                <div className="rounded-xl border p-5 bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                            Incidents
                            {incidents.length > 0 && (
                                <span className="ml-2 text-xs text-gray-400">({incidents.length} total)</span>
                            )}
                        </h2>
                        <button
                            onClick={refreshIncidents}
                            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
                        >
                            <RefreshCw size={13} />
                            Refresh
                        </button>
                    </div>

                    {incidentsLoading ? (
                        <div className="text-center text-gray-400 py-8 text-sm">Loading...</div>
                    ) : (
                        <IncidentList incidents={incidents} onRefresh={refreshIncidents} />
                    )}
                </div>
            )}
        </div>
    )
}