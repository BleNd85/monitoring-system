import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { extractMetricValue, METRIC_CONFIG, formatValue } from '../utils/metrics'

const PERCENT_METRICS = ['cpu.load_percent', 'memory.ram_percent', 'memory.swap_percent']
const MAX_POINTS = 200

export default function MetricsChart({ data, metricKeys }) {
    if (!metricKeys?.length) return null

    const ramTotal = (() => {
        const last = data[data.length - 1]
        const usage = last?.memory?.ram_usage_mb
        const percent = last?.memory?.ram_percent
        if (usage && percent) return Math.round(usage / (percent / 100))
        return null
    })()

    const sliced = data.length > MAX_POINTS
        ? data.filter((_, i) => i % Math.ceil(data.length / MAX_POINTS) === 0)
        : data

    const chartData = sliced.map(snapshot => {
        const point = {
            time: new Date(snapshot.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            })
        }
        metricKeys.forEach(key => {
            point[key] = extractMetricValue(snapshot, key)
        })
        return point
    })

    const hasPercent = metricKeys.some(k => PERCENT_METRICS.includes(k))
    const hasAbsolute = metricKeys.some(k => !PERCENT_METRICS.includes(k))
    const needsDualAxis = hasPercent && hasAbsolute

    const leftKey = metricKeys.find(k => PERCENT_METRICS.includes(k)) || metricKeys[0]
    const rightKey = metricKeys.find(k => !PERCENT_METRICS.includes(k))

    const getRightDomain = () => {
        if (!rightKey) return ['auto', 'auto']
        if (PERCENT_METRICS.includes(rightKey)) return [0, 100]
        if (rightKey === 'memory.ram_usage_mb' && ramTotal) return [0, ramTotal]
        return ['auto', 'auto']
    }

    const getLeftDomain = () => {
        if (PERCENT_METRICS.includes(leftKey)) return [0, 100]
        if (leftKey === 'memory.ram_usage_mb' && ramTotal) return [0, ramTotal]
        return ['auto', 'auto']
    }

    return (
        <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 4, right: needsDualAxis ? 56 : 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.12)" />
                <XAxis
                    dataKey="time"
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    interval="preserveStartEnd"
                    stroke="rgba(128,128,128,0.2)"
                />
                <YAxis
                    yAxisId="left"
                    tick={{ fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    width={52}
                    tickFormatter={v => formatValue(v, METRIC_CONFIG[leftKey]?.unit)}
                    domain={getLeftDomain()}
                />
                {needsDualAxis && rightKey && (
                    <YAxis
                        yAxisId="right"
                        orientation="right"
                        tick={{ fontSize: 10 }}
                        tickLine={false}
                        axisLine={false}
                        width={56}
                        tickFormatter={v => formatValue(v, METRIC_CONFIG[rightKey]?.unit)}
                        domain={getRightDomain()}
                    />
                )}
                <Tooltip
                    contentStyle={{ borderRadius: 8, border: '1px solid rgba(128,128,128,0.2)', fontSize: 12 }}
                    formatter={(v, name) => {
                        const cfg = METRIC_CONFIG[name]
                        return [formatValue(v, cfg?.unit), cfg?.label || name]
                    }}
                />
                {metricKeys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
                {metricKeys.map(key => (
                    <Line
                        key={key}
                        yAxisId={needsDualAxis && !PERCENT_METRICS.includes(key) ? 'right' : 'left'}
                        type="monotone"
                        dataKey={key}
                        name={key}
                        stroke={METRIC_CONFIG[key]?.color || '#888'}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                        isAnimationActive={true}
                    />
                ))}
            </LineChart>
        </ResponsiveContainer>
    )
}