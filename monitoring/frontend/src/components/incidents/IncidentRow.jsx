import { AlertTriangle, Clock, CheckCircle } from 'lucide-react'
import {SEVERITY_STYLE} from "../../utils/severity"

export default function IncidentRow({ incident, onClick }) {
  const s = SEVERITY_STYLE[incident.severity] || SEVERITY_STYLE.warning

  return (
    <button
      onClick={() => onClick(incident)}
      className={`w-full text-left p-4 rounded-lg border-l-4 transition-all hover:shadow-sm ${s.border} ${s.bg}`}
    >
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <AlertTriangle size={15} className={s.icon} />
          <span className="font-medium text-sm text-gray-900 dark:text-white capitalize">
            {incident.anomaly_type?.replace(/_/g, ' ')}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s.badge}`}>
            {incident.severity}
          </span>
          {incident.resolved_at && (
            <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400">
              <CheckCircle size={10} />
              resolved
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-400 shrink-0">
          <Clock size={11} />
          {new Date(incident.timestamp).toLocaleString()}
        </div>
      </div>
      {incident.llm_interpretation && (
        <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400 line-clamp-2 text-left">
          {incident.llm_interpretation}
        </p>
      )}
    </button>
  )
}