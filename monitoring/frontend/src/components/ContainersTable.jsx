import { Circle } from 'lucide-react'
import { formatValue } from '../utils/metrics'

const STATUS_COLORS = {
    running: 'fill-green-500 text-green-500',
    paused: 'fill-yellow-500 text-yellow-500',
    exited: 'fill-red-500 text-red-500',
}

export default function ContainersTable({ containers = [] }) {
    if (!containers.length) return (
        <div className="text-sm text-gray-400 text-center py-6">No containers detected</div>
    )

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead>
                    <tr className="text-left text-xs text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                        <th className="pb-2 font-medium pr-4">Name</th>
                        <th className="pb-2 font-medium pr-4">Status</th>
                        <th className="pb-2 font-medium pr-4">CPU %</th>
                        <th className="pb-2 font-medium pr-4">RAM</th>
                        <th className="pb-2 font-medium">Limit</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                    {containers.map(c => (
                        <tr key={c.name} className="text-gray-700 dark:text-gray-300">
                            <td className="py-2.5 pr-4 font-mono text-xs truncate max-w-40">{c.name}</td>
                            <td className="py-2.5 pr-4">
                                <div className="flex items-center gap-1.5">
                                    <Circle size={8} className={STATUS_COLORS[c.status] || 'fill-gray-400 text-gray-400'} />
                                    <span className="text-xs">{c.status}</span>
                                </div>
                            </td>
                            <td className="py-2.5 pr-4 text-xs">{c.cpu_load_percent?.toFixed(2)}%</td>
                            <td className="py-2.5 pr-4 text-xs">{formatValue(c.ram_usage_mb, 'MB')}</td>
                            <td className="py-2.5 text-xs text-gray-400">{formatValue(c.ram_limit_mb, 'MB')}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}