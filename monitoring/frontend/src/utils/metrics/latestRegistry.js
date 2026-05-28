import { getLatestMetricsByAgentId } from "../../api/collector"

const POLL_MS = Number(import.meta.env.VITE_POLL_INTERVAL || 10) * 1000

const registry = new Map()

function getOrCreateEntry(agentId) {
    if (!registry.has(agentId)) {
        registry.set(agentId, {
            data: null,
            error: null,
            listeners: new Set(),
            intervalId: null,
            timeoutId: null,
        })
    }
    return registry.get(agentId)
}

async function poll(agentId) {
    const entry = registry.get(agentId)
    if (!entry) return
    try {
        entry.data = await getLatestMetricsByAgentId(agentId)
        entry.error = null
    } catch (e) {
        entry.error = e
    }
    entry.listeners.forEach(fn => fn(entry.data, entry.error))
}

export function subscribeLatest(agentId, listener) {
    const entry = getOrCreateEntry(agentId)
    entry.listeners.add(listener)

    if (entry.listeners.size === 1) {
        entry.timeoutId = setTimeout(() => poll(agentId), 0)
        entry.intervalId = setInterval(() => poll(agentId), POLL_MS)
    } else if (entry.data !== null) {
        listener(entry.data, entry.error)
    }

    return () => {
        entry.listeners.delete(listener)
        if (entry.listeners.size === 0) {
            clearTimeout(entry.timeoutId)
            clearInterval(entry.intervalId)
            registry.delete(agentId)
        }
    }
}