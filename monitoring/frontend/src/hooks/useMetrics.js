import { useEffect, useRef, useState } from "react"
import { subscribeLatest } from "../utils/metrics/latestRegistry"
import { fetchRange } from "../utils/metrics/rangeCache"

const POLL_MS = Number(import.meta.env.VITE_POLL_INTERVAL || 10) * 1000

export function useLatestMetrics(agentId) {
    const [state, setState] = useState({ data: null, error: null })

    useEffect(() => {
        if (!agentId) return
        return subscribeLatest(agentId, (data, error) => setState({ data, error }))
    }, [agentId])

    return state
}

export function useRangeMetrics(agentId, hours = 1) {
    const maxPoints = Math.ceil((hours * 3600) / (POLL_MS / 1000))
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)
    const dataRef = useRef([])
    const keyRef = useRef(null)

    useEffect(() => {
        if (!agentId) return

        const key = `${agentId}_${hours}`
        keyRef.current = key
        dataRef.current = []
        let alive = true

        fetchRange(agentId, hours)
            .then(normalized => {
                if (!alive || keyRef.current !== key) return
                dataRef.current = normalized
                setData(normalized)
                setLoading(false)
            })
            .catch(e => {
                console.error(e)
                if (alive && keyRef.current === key) setLoading(false)
            })

        return () => { alive = false }
    }, [agentId, hours])

    useEffect(() => {
        if (!agentId) return

        return subscribeLatest(agentId, latest => {
            if (!latest) return
            const updated = [...dataRef.current, latest]
            const trimmed = updated.length > maxPoints
                ? updated.slice(-maxPoints)
                : updated
            dataRef.current = trimmed
            setData(trimmed)
        })
    }, [agentId, maxPoints])

    return { data, loading }
}