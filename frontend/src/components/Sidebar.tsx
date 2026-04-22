import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getSessions, type Session } from '../api'
import { NewSessionModal } from './NewSessionModal'
import './Sidebar.css'

interface Props {
  userId: number
  activeSessionId: number | null
  onSelectSession: (id: number) => void
}

const MODE_LABELS: Record<string, string> = {
  structured_learning: 'Structured',
  scene_advice: 'Scene Advice',
}

export function Sidebar({ userId, activeSessionId, onSelectSession }: Props) {
  const [modalOpen, setModalOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: sessions, isLoading, isError } = useQuery<Session[]>({
    queryKey: ['sessions', userId],
    queryFn: () => getSessions(userId),
  })

  function handleSessionCreated(session: Session) {
    queryClient.invalidateQueries({ queryKey: ['sessions', userId] })
    onSelectSession(session.id)
    setModalOpen(false)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-title">Photography Tutor</span>
        <button className="btn-new-session" onClick={() => setModalOpen(true)}>
          + New session
        </button>
      </div>

      <div className="sidebar-list">
        {isLoading && <p className="sidebar-state">Loading…</p>}
        {isError && <p className="sidebar-state sidebar-error">Failed to load sessions</p>}
        {!isLoading && !isError && sessions?.length === 0 && (
          <p className="sidebar-state">No sessions yet</p>
        )}
        {sessions?.map((s) => (
          <button
            key={s.id}
            className={`session-row ${s.id === activeSessionId ? 'session-row--active' : ''}`}
            onClick={() => onSelectSession(s.id)}
          >
            <div className="session-row-top">
              <span className="mode-badge">{MODE_LABELS[s.mode] ?? s.mode}</span>
              <span className="equipment-label">{s.equipment_type}</span>
            </div>
            <div className="session-row-topic">
              {s.last_topic ?? 'New session'}
            </div>
          </button>
        ))}
      </div>

      {modalOpen && (
        <NewSessionModal
          userId={userId}
          onCreated={handleSessionCreated}
          onClose={() => setModalOpen(false)}
        />
      )}
    </aside>
  )
}
