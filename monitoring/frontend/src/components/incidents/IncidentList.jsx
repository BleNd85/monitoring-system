import { useState } from 'react'
import IncidentRow from './IncidentRow'
import IncidentDetail from './IncidentDetail'

export default function IncidentList({ incidents, onRefresh }) {
  const [selected, setSelected] = useState(null)

  if (!incidents.length) return (
    <div className="text-sm text-gray-400 text-center py-8">No incidents detected</div>
  )

  return (
    <>
      <div className="flex flex-col gap-2">
        {incidents.map(inc => (
          <IncidentRow key={inc.id} incident={inc} onClick={setSelected} />
        ))}
      </div>

      {selected && (
        <IncidentDetail
          incident={selected}
          onClose={() => setSelected(null)}
          onResolved={onRefresh}
        />
      )}
    </>
  )
}