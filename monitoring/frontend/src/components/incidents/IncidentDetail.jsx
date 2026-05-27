import { useState } from 'react'
import { X, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { resolveIncidentById } from '../../api/alerter'
import { SEVERITY_STYLE } from "../../utils/severity"

function MetricPill({ label, value }) {
    return (
        <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
            <span className="text-gray-400">{label}:</span>
            <span className="font-mono font-medium">
                {typeof value === 'number' ? value.toFixed(2) : String(value)}
            </span>
        </span>
    )
}

export default function IncidentDetail({ incident, onClose, onResolved }) {
    const [resolving, setResolving] = useState(false)
    const s = SEVERITY_STYLE[incident.severity] || SEVERITY_STYLE.warning

    const handleResolve = async () => {
        setResolving(true)
        try {
            await resolveIncidentById(incident.id)
            onResolved()
            onClose()
        } catch (e) {
            console.error(e)
        } finally {
            setResolving(false)
        }
    }

    return (
        <div
            onClick={onClose}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in"
        >
            <div
                className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white dark:bg-gray-800 shadow-2xl animate-modal-in"
                onClick={e => e.stopPropagation()}
            >

                {/* Header */}
                <div className={`p-5 border-b border-gray-200 dark:border-gray-700 ${s.bg} rounded-t-2xl`}>
                    <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2">
                            <AlertTriangle size={18} className={s.icon} />
                            <div>
                                <h2 className="font-semibold text-gray-900 dark:text-white capitalize">
                                    {incident.anomaly_type?.replace(/_/g, ' ')}
                                </h2>
                                <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                                    <Clock size={10} />
                                    {new Date(incident.timestamp).toLocaleString()}
                                    <span className="mx-1">·</span>
                                    score {incident.deviation_score?.toFixed(2)}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1.5 text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg transition-colors"
                        >
                            <X size={18} />
                        </button>
                    </div>
                </div>

                <div className="p-5 flex flex-col gap-5">

                    {/* LLM interpretation */}
                    {incident.llm_interpretation && (
                        <div>
                            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                                Analysis
                            </h3>
                            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                                {incident.llm_interpretation}
                            </p>
                        </div>
                    )}

                    {/* Affected metrics */}
                    {incident.affected_metrics && Object.keys(incident.affected_metrics).length > 0 && (
                        <div>
                            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                                Affected Metrics
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {Object.entries(incident.affected_metrics).map(([k, v]) => (
                                    <MetricPill key={k} label={k.replace(/_/g, ' ')} value={v} />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Expected vs Actual */}
                    {incident.expected_values && incident.actual_values && (
                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                                    Expected (baseline)
                                </h3>
                                <div className="flex flex-col gap-1.5">
                                    {Object.entries(incident.expected_values).map(([k, v]) => (
                                        <MetricPill key={k} label={k.replace(/_/g, ' ')} value={v} />
                                    ))}
                                </div>
                            </div>
                            <div>
                                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                                    Actual
                                </h3>
                                <div className="flex flex-col gap-1.5">
                                    {Object.entries(incident.actual_values)
                                        .filter(([k]) => k in (incident.expected_values || {}))
                                        .map(([k, v]) => (
                                            <MetricPill key={k} label={k.replace(/_/g, ' ')} value={v} />
                                        ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Resolved at */}
                    {incident.resolved_at && (
                        <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                            <CheckCircle size={15} />
                            Resolved at {new Date(incident.resolved_at).toLocaleString()}
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-3 pt-1">
                        {!incident.resolved_at && (
                            <button
                                onClick={handleResolve}
                                disabled={resolving}
                                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
                            >
                                <CheckCircle size={15} />
                                {resolving ? 'Resolving...' : 'Mark as Resolved'}
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}