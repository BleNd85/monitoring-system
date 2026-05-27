export default function StatCard({ label, value }) {
    return (
        <div className="rounded-xl p-4 border bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">{label}</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
        </div>
    )
}