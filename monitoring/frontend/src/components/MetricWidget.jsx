import { useState } from 'react'
import { X, Settings, Check } from 'lucide-react'
import MetricChart from './MetricsChart'
import { METRIC_CONFIG, formatValue, extractMetricValue } from '../utils/metrics'
import { useRangeMetrics } from '../hooks/useMetrics'

const PERIODS = [
    { label: '15m', hours: 0.25 },
    { label: '1h', hours: 1 },
    { label: '6h', hours: 6 },
    { label: '24h', hours: 24 },
]

export default function MetricWidget({ agentId, widgetId, metricKeys = [], onRemove, onChangeMetrics }) {
    const [period, setPeriod] = useState(1)
    const [showSettings, setShowSettings] = useState(!metricKeys.length)
    const [selected, setSelected] = useState(new Set(metricKeys))
    const { data, loading } = useRangeMetrics(agentId, period)

    const latest = data[data.length - 1]

    const toggleMetric = (key) => {
        setSelected(prev => {
            const next = new Set(prev)
            next.has(key) ? next.delete(key) : next.add(key)
            return next
        })
    }

    const applyMetrics = () => {
        const keys = [...selected]
        if (!keys.length) return
        onChangeMetrics(widgetId, keys)
        setShowSettings(false)
    }

    return (
        <div className="rounded-xl border p-4 flex flex-col gap-3 bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700">
            <div className="flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-center gap-2 flex-wrap">
                    {metricKeys.map(key => (
                        <span
                            key={key}
                            className="text-xs font-medium px-2 py-0.5 rounded-full bg-orange-50 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400"
                        >
                            {METRIC_CONFIG[key]?.label || key}
                            {latest && (
                                <span className="ml-1 font-bold">
                                    {formatValue(extractMetricValue(latest, key), METRIC_CONFIG[key]?.unit)}
                                </span>
                            )}
                        </span>
                    ))}
                    {!metricKeys.length && (
                        <span className="text-xs text-gray-400">Select metrics</span>
                    )}
                </div>

                <div className="flex items-center gap-1 ml-auto">
                    {PERIODS.map(p => (
                        <button
                            key={p.hours}
                            onClick={() => setPeriod(p.hours)}
                            className={`text-xs px-2 py-1 rounded transition-colors ${period === p.hours
                                ? 'bg-orange-500 text-white'
                                : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
                                }`}
                        >
                            {p.label}
                        </button>
                    ))}
                    <button
                        onClick={() => setShowSettings(s => !s)}
                        className="p-1.5 text-gray-400 hover:text-gray-900 dark:hover:text-white rounded transition-colors"
                    >
                        <Settings size={14} />
                    </button>
                    <button
                        onClick={() => onRemove(widgetId)}
                        className="p-1.5 text-gray-400 hover:text-red-500 rounded transition-colors"
                    >
                        <X size={14} />
                    </button>
                </div>
            </div>

            {showSettings && (
                <div className="border rounded-lg p-3 border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-500 mb-2">Select metrics (multiple allowed):</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
                        {Object.entries(METRIC_CONFIG).map(([key, cfg]) => (
                            <button
                                key={key}
                                onClick={() => toggleMetric(key)}
                                className={`flex items-center gap-1.5 text-xs px-2 py-1.5 rounded-md text-left transition-colors ${selected.has(key)
                                    ? 'bg-orange-500 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                                    }`}
                            >
                                {selected.has(key) && <Check size={10} />}
                                {cfg.label}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={applyMetrics}
                        disabled={!selected.size}
                        className="mt-2 w-full py-1.5 text-xs rounded-md bg-orange-500 hover:bg-orange-600 text-white transition-colors disabled:opacity-40"
                    >
                        Apply
                    </button>
                </div>
            )}

            {metricKeys.length > 0 && !showSettings && (
                <div className="h-44">
                    {loading
                        ? <div className="h-full flex items-center justify-center">
                            <div className="w-8 h-8 rounded-full border-2 border-orange-500/30 border-t-orange-500 animate-spin" />
                        </div>
                        : data.length === 0
                            ? <div className="h-full flex items-center justify-center text-gray-400 text-xs">No data</div>
                            : <MetricChart data={data} metricKeys={metricKeys} />
                    }
                </div>
            )}
        </div>
    )
}