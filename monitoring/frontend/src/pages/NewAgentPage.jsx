import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { registerAgent } from '../api/collector'
import { ArrowLeft } from 'lucide-react'

export default function NewAgentPage() {
    const navigate = useNavigate()
    const [form, setForm] = useState({ url: '', name: '' })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const agent = await registerAgent(form)
            navigate(`/agents/${agent.agent_id}`)
        } catch (e) {
            setError(e.response?.data?.detail || 'Failed to register agent')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-lg mx-auto px-6 py-8">
            <button onClick={() => navigate(-1)}
                className="flex items-center gap-2 text-sm text-gray-500
          hover:text-gray-900 dark:hover:text-white mb-6 transition-colors">
                <ArrowLeft size={16} /> Back
            </button>

            <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                Register Agent
            </h1>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700
            dark:text-gray-300 mb-1.5">
                        Agent URL
                    </label>
                    <input
                        type="url"
                        placeholder="http://192.168.1.100:8200"
                        value={form.url}
                        onChange={e => setForm(f => ({ ...f, url: e.target.value }))}
                        required
                        className="w-full px-3 py-2 rounded-lg border text-sm bg-white border-gray-300 text-gray-900
                        dark:bg-gray-800 dark:border-gray-700 dark:text-white focus:outline-none
                        focus:border-orange-500 transition-colors"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700
            dark:text-gray-300 mb-1.5">
                        Display Name
                    </label>
                    <input
                        type="text"
                        placeholder="Production Server"
                        value={form.name}
                        onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                        required
                        className="w-full px-3 py-2 rounded-lg border text-sm bg-white border-gray-300 text-gray-900
                        dark:bg-gray-800 dark:border-gray-700 dark:text-white focus:outline-none
                        focus:border-orange-500 transition-colors"
                    />
                </div>

                {error && (
                    <div className="text-sm text-red-500 bg-red-50 dark:bg-red-500/10
            rounded-lg px-3 py-2">
                        {error}
                    </div>
                )}

                <button type="submit" disabled={loading}
                    className="w-full py-2 rounded-lg bg-orange-500 hover:bg-orange-600
            text-white font-medium text-sm transition-colors disabled:opacity-50">
                    {loading ? 'Connecting...' : 'Register Agent'}
                </button>
            </form>
        </div>
    )
}