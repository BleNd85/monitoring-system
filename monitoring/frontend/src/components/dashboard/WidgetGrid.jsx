import { Plus } from 'lucide-react'
import MetricWidget from '../MetricWidget'

export default function WidgetGrid({ agentId, widgets, onAdd, onRemove, onChangeMetrics, onToggleWide }) {
    return (
        <>
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Metric Charts</h2>
                <button
                    onClick={onAdd}
                    className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg bg-orange-500 hover:bg-orange-600 text-white transition-colors"
                >
                    <Plus size={14} /> Add Chart
                </button>
            </div>

            {widgets.length === 0 ? (
                <div className="text-center py-12 text-gray-400 text-sm">
                    No charts yet. Click "Add Chart" to create one.
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-1 gap-4 mb-6">
                    {widgets.map(w => (
                        <MetricWidget
                            key={w.id}
                            agentId={agentId}
                            widgetId={w.id}
                            metricKeys={w.metricKeys}
                            onRemove={onRemove}
                            onChangeMetrics={onChangeMetrics}
                            wide={w.wide}
                            onToggleWide={onToggleWide}
                        />
                    ))}
                </div>
            )}
        </>
    )
}