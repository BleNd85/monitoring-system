import { useCallback, useEffect, useState } from "react"
import { getIncidentsByAgentId } from "../api/alerter"

export function useIncidents(agentId, limit = 50) {
    const [incidents, setIncidents] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetch = useCallback(async () => {
        if (!agentId) return

        setLoading(true)

        try {
            const data = await getIncidentsByAgentId(agentId, limit)

            setIncidents(Array.isArray(data) ? data : [])
        }
        catch (e) {
            setError(e)
            console.error(e)
        }
        finally {
            setLoading(false)
        }
    }, [agentId, limit])

    useEffect(() => {
        if (!agentId) return

        const timeoutId = setTimeout(fetch, 0)

        return () => clearTimeout(timeoutId)
    }, [fetch, agentId])

    return {
        incidents,
        loading,
        error,
        refresh: fetch
    }
}