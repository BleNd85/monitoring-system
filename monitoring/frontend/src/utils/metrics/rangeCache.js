import { getRangeMetricsByAgentId } from "../../api/collector"

const cache = new Map()
const FRESH_MS = 5000

export async function fetchRange(agentId, hours) {
    const key = `${agentId}_${hours}`
    const cached = cache.get(key)

    if (cached) {
        if (cached.promise) return cached.promise
        if (Date.now() - cached.ts < FRESH_MS) return cached.data
    }

    const promise = (async () => {
        const end = new Date()
        const start = new Date(end - hours * 3600 * 1000)
        const result = await getRangeMetricsByAgentId(agentId, start, end)
        const normalized = Array.isArray(result) ? result : []
        cache.set(key, { data: normalized, ts: Date.now(), promise: null })
        return normalized
    })()

    cache.set(key, { promise, data: cached?.data ?? [], ts: 0 })
    return promise
}