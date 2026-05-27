import { RefreshCw } from 'lucide-react'
import IncidentList from '../incidents/IncidentList'

export default function IncidentsPanel({ incidents, loading, onRefresh }) {
    return (
        <div className="rounded-xl border p-5 bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    Incidents
                    {incidents.length > 0 && (
                        <span className="ml-2 text-xs text-gray-400">({incidents.length} total)</span>
                    )}
                </h2>
                <button
                    onClick={onRefresh}
                    className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                    <RefreshCw size={13} /> Refresh
                </button>
            </div>
            {loading ? (
                <div className="text-center text-gray-400 py-8 text-sm">Loading...</div>
            ) : (
                <IncidentList incidents={incidents} onRefresh={onRefresh} />
            )}
        </div>
    )
}