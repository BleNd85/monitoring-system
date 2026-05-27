import { Link } from 'react-router-dom'
import { Server, Circle } from 'lucide-react'

export default function AgentCard({ agent }) {
    return (
        <Link
            to={`/agents/${agent.agent_id}`}
            className="block p-5 rounded-xl border transition-all bg-white border-gray-200 hover:border-orange-400 hover:shadow-md dark:bg-gray-800 dark:border-gray-700 dark:hover:border-orange-500"
        >
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-50 dark:bg-orange-500/10">
                    <Server size={20} className="text-orange-500" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="font-semibold text-gray-900 dark:text-white truncate">{agent.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{agent.agent_id}</div>
                </div>
                <Circle size={10} className="fill-green-500 text-green-500 shrink-0" />
                <div className="mt-3 text-xs text-gray-400 dark:text-gray-500 truncate">{agent.url}</div>
            </div>
        </Link>
    )
}