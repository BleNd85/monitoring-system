import { LayoutGrid, AlertTriangle } from 'lucide-react'

export default function DashboardTabs({ tab, setTab, unresolvedCount }) {
    return (
        <div className="flex items-center gap-1 mb-5">
            <button
                onClick={() => setTab('charts')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === 'charts' ? 'bg-orange-500 text-white' : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}`}
            >
                <LayoutGrid size={15} /> Charts
            </button>
            <button
                onClick={() => setTab('incidents')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === 'incidents' ? 'bg-orange-500 text-white' : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}`}
            >
                <AlertTriangle size={15} /> Incidents
                {unresolvedCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-red-500 text-white font-bold">
                        {unresolvedCount}
                    </span>
                )}
            </button>
        </div>
    )
}