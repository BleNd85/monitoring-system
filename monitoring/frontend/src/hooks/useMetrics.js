import { useCallback, useEffect, useState } from "react"
import { getLatestMetricsByAgentId, getRangeMetricsByAgentId } from "../api/collector"

const POLL_MS = Number(import.meta.env.VITE_POLL_INTERVAL || 10) * 1000

const rangeCache = new Map()

async function fetchRange(agentId, hours) {
    const cacheKey = `${agentId}_${hours}`
    const cached = rangeCache.get(cacheKey)

    if (cached) {
        if (cached.promise) return cached.promise
        if (Date.now() - cached.ts < 5000) return cached.data
    }

    const promise = (async () => {
        const end = new Date()
        const start = new Date(end - hours * 3600 * 1000)
        const result = await getRangeMetricsByAgentId(agentId, start, end)
        const normalized = Array.isArray(result) ? result : []
        rangeCache.set(cacheKey, { data: normalized, ts: Date.now(), promise: null })
        return normalized
    })()

    rangeCache.set(cacheKey, { promise, data: cached?.data || [], ts: 0 })
    return promise
}

export function useLatestMetrics(agentId) {
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    const fetch = useCallback(async () => {
        if (!agentId) return
        try {
            const result = await getLatestMetricsByAgentId(agentId)
            setData(result)
        } catch (e) {
            setError(e)
        }
    }, [agentId])

    useEffect(() => {
        if (!agentId) return
        const timeoutId = setTimeout(fetch, 0)
        const intervalId = setInterval(fetch, POLL_MS)
        return () => {
            clearTimeout(timeoutId)
            clearInterval(intervalId)
        }
    }, [fetch, agentId])

    return { data, error }
}

export function useRangeMetrics(agentId, hours = 1) {
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(true)

    const fetch = useCallback(async (showLoading = false) => {
        if (!agentId) return
        if (showLoading) setLoading(true)
        try {
            const result = await fetchRange(agentId, hours)
            setData(result)
        } catch (e) {
            console.error(e)
        } finally {
            if (showLoading) setLoading(false)
        }
    }, [agentId, hours])

    useEffect(() => {
        if (!agentId) return
        setTimeout(() => fetch(true), 0)
        const id = setInterval(() => fetch(false), POLL_MS)
        return () => clearInterval(id)
    }, [fetch, agentId])

    return { data, loading }
}