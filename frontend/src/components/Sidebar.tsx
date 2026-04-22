import { useState } from 'react'
import { useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query'
import { getSessions, type Session } from '../api'
import { NewSessionModal } from './NewSessionModal'
import { StudyJourneyModal } from './StudyJourneyModal'
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
  const [studyJourneyOpen, setStudyJourneyOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: sessions, isLoading, isError } = useQuery<Session[]>({
    queryKey: ['sessions', userId],
    queryFn: () => getSessions(userId),
    placeholderData: keepPreviousData,
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
        <div className="sidebar-header-actions">
          <button className="btn-study-journey" onClick={() => setStudyJourneyOpen(true)}>
            Study Journey
          </button>
          <button className="btn-new-session" onClick={() => setModalOpen(true)}>
            + New Session
          </button>
        </div>
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

      {studyJourneyOpen && (
        <StudyJourneyModal
          userId={userId}
          onClose={() => setStudyJourneyOpen(false)}
        />
      )}
    </aside>
  )
}
