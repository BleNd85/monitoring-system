export const METRIC_CONFIG = {
    'cpu.load_percent': { label: 'CPU', unit: '%', color: '#FF6C37' },
    'cpu.load_avg_1m': { label: 'Load Avg 1m', unit: '', color: '#FF9500' },
    'cpu.load_avg_5m': { label: 'Load Avg 5m', unit: '', color: '#FFCC00' },
    'cpu.load_avg_15m': { label: 'Load Avg 15m', unit: '', color: '#34C759' },
    'memory.ram_percent': { label: 'RAM', unit: '%', color: '#007AFF' },
    'memory.ram_usage_mb': { label: 'RAM MiB', unit: 'MiB', color: '#5856D6' },
    'memory.swap_percent': { label: 'Swap %', unit: '%', color: '#AF52DE' },
    'memory.swap_usage_mb': { label: 'Swap MiB', unit: 'MiB', color: '#FF2D55' },
    'disk.read_bytes': { label: 'Disk Read', unit: 'B', color: '#00C7BE' },
    'disk.write_bytes': { label: 'Disk Write', unit: 'B', color: '#30B0C7' },
    'network.sent_bytes': { label: 'Net Sent', unit: 'B', color: '#32ADE6' },
    'network.received_bytes': { label: 'Net Recv', unit: 'B', color: '#64D2FF' },
}

export function extractMetricValue(snapshot, metricKey) {
    const [group, field] = metricKey.split('.')
    return snapshot?.[group]?.[field] ?? null
}

export function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KiB', 'MiB', 'GiB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

export function formatValue(value, unit) {
    if (value === null || value === undefined) return '—'
    if (unit === 'B') return formatBytes(value)
    if (unit === '%') return `${Number(value).toFixed(1)}%`
    if (unit === 'MiB') return `${Number(value).toFixed(0)} MiB`
    return Number(value).toFixed(2)
}