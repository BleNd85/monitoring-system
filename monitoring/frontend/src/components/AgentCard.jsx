import { Link } from 'react-router-dom'
import { Server, Circle, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { deleteAgentById } from '../api/collector'

export default function AgentCard({ agent, onDeleted }) {
    const [deleting, setDeleting] = useState(false)

    const handleDelete = async (e) => {
        e.preventDefault()
        if (!confirm(`Delete agent "${agent.name}"?`)) return
        setDeleting(true)
        try {
            await deleteAgentById(agent.agent_id)
            onDeleted?.(agent.agent_id)
        } catch (err) {
            console.error(err)
        } finally {
            setDeleting(false)
        }
    }

    return (
        <div className="relative flex items-center rounded-xl border transition-all bg-white border-gray-200 hover:border-orange-400 hover:shadow-md dark:bg-gray-800 dark:border-gray-700 dark:hover:border-orange-500">
            <Link
                to={`/agents/${agent.agent_id}`}
                className="flex-1 flex items-center gap-3 p-5 min-w-0"
            >
                <div className="p-2 rounded-lg bg-orange-50 dark:bg-orange-500/10">
                    <Server size={20} className="text-orange-500" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="font-semibold text-gray-900 dark:text-white truncate">{agent.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{agent.agent_id}</div>
                    <div className="mt-1 text-xs text-gray-400 dark:text-gray-500 truncate">{agent.url}</div>
                </div>
                <Circle size={10} className="fill-green-500 text-green-500 shrink-0" />
            </Link>

            <div className="pr-4">
                <button
                    onClick={handleDelete}
                    disabled={deleting}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
                >
                    <Trash2 size={15} />
                    {deleting ? 'Deleting...' : 'Delete'}
                </button>
            </div>
        </div>
    )
}