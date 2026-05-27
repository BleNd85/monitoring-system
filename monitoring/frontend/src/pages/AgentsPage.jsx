import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { RefreshCw, ServerOff } from 'lucide-react'
import { getAgents } from '../api/collector'
import AgentCard from '../components/AgentCard'

export default function AgentsPage() {
    const [agents, setAgents] = useState([])
    const [loading, setLoading] = useState(true)

    const fetchAgents = useCallback(async () => {
        setLoading(true)
        try {
            const data = await getAgents()
            setAgents(Array.isArray(data) ? data : [])
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        let cancelled = false

        const load = async () => {
            try {
                const data = await getAgents()
                if (!cancelled) setAgents(Array.isArray(data) ? data : [])
            } catch (e) {
                console.error(e)
            } finally {
                if (!cancelled) setLoading(false)
            }
        }

        load()
        return () => { cancelled = true }
    }, [])

    return (
        <div className="max-w-5xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Agents</h1>
                <button
                    onClick={fetchAgents}
                    className="p-2 rounded-lg text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                    <RefreshCw size={16} />
                </button>
            </div>

            {loading ? (
                <div className="h-full flex items-center justify-center">
                    <div className="w-8 h-8 rounded-full border-2 border-orange-500/30 border-t-orange-500 animate-spin" />
                </div>
            ) : agents.length === 0 ? (
                <div className="text-center py-16 flex flex-col items-center gap-4">
                    <ServerOff size={40} className="text-gray-300 dark:text-gray-600" />
                    <p className="text-gray-400">No agents registered yet</p>
                    <Link
                        to="/agents/new"
                        className="px-4 py-2 rounded-md bg-orange-500 hover:bg-orange-600 text-white text-sm font-medium transition-colors"
                    >
                        Add your first agent
                    </Link>
                </div>
            ) : (
                <div className="flex flex-col gap-4">
                    {agents.map(a => <AgentCard key={a.agent_id} agent={a} />)}
                </div>
            )}
        </div>
    )
}