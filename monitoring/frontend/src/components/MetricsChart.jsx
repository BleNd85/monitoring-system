import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { extractMetricValue, METRIC_CONFIG, formatValue } from '../utils/metrics'
import { useTheme } from '../context/ThemeContext'

const PERCENT_METRICS = ['cpu.load_percent', 'memory.ram_percent', 'memory.swap_percent']

export default function MetricsChart({ data, metricKeys }) {
    const { light } = useTheme()

    if (!metricKeys?.length) return null

    const ramTotal = (() => {
        const last = data[data.length - 1]
        const usage = last?.memory?.ram_usage_mb
        const percent = last?.memory?.ram_percent
        if (usage && percent) return Math.round(usage / (percent / 100))
        return null
    })()

    const chartData = data.map(snapshot => {
        const date = new Date(snapshot.timestamp)
        const point = {
            time: date.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }),
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

    const tooltip = light
        ? {
            bg: '#ffffff',
            border: 'rgba(0,0,0,0.1)',
            label: '#1E1E1E',
            item: '#3A3A3A',
        }
        : {
            bg: '#252525',
            border: '#3A3A3A',
            label: '#f3f4f6',
            item: '#d1d5db',
        }

    return (
        <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 4, right: needsDualAxis ? 0 : 8, bottom: 0, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.12)" />
                <XAxis
                    dataKey="time"
                    tickFormatter={(value) => value.slice(0, 5)}
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
                    width={45}
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
                        width={45}
                        tickFormatter={v => formatValue(v, METRIC_CONFIG[rightKey]?.unit)}
                        domain={getRightDomain()}
                    />
                )}
                <Tooltip
                    content={({ active, payload, label }) => {
                        if (!active || !payload?.length) return null
                        return (
                            <div style={{
                                borderRadius: 8,
                                border: `1px solid ${tooltip.border}`,
                                fontSize: 12,
                                backgroundColor: tooltip.bg,
                                color: tooltip.label,
                                padding: '8px 12px',
                            }}>
                                <div style={{ marginBottom: 6, color: tooltip.label, fontWeight: 500 }}>
                                    {label}
                                </div>
                                {payload.map(entry => {
                                    const cfg = METRIC_CONFIG[entry.dataKey]
                                    return (
                                        <div key={entry.dataKey} style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 6,
                                            marginBottom: 3,
                                            color: tooltip.item,
                                        }}>
                                            <span style={{
                                                width: 8,
                                                height: 8,
                                                borderRadius: '50%',
                                                backgroundColor: entry.stroke,
                                                flexShrink: 0,
                                            }} />
                                            <span>{cfg?.label || entry.dataKey}:</span>
                                            <span style={{ fontWeight: 500, color: tooltip.label }}>
                                                {formatValue(entry.value, cfg?.unit)}
                                            </span>
                                        </div>
                                    )
                                })}
                            </div>
                        )
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
                        stroke={METRIC_CONFIG[key]?.color || '#6B6B6B'}
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                        isAnimationActive={false}
                    />
                ))}
            </LineChart>
        </ResponsiveContainer>
    )
}