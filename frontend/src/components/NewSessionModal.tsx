import { useEffect, useRef, useState } from 'react'
import { createSession, type Session } from '../api'
import './NewSessionModal.css'

interface Props {
  userId: number
  onCreated: (session: Session) => void
  onClose: () => void
}

export function NewSessionModal({ userId, onCreated, onClose }: Props) {
  const [mode, setMode] = useState('structured_learning')
  const [userLevel, setUserLevel] = useState('beginner')
  const [equipmentType, setEquipmentType] = useState('dslr')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      const roomName = `room-${userId}-${Date.now()}`
      const session = await createSession({
        user_id: userId,
        livekit_room_name: roomName,
        mode,
        user_level: userLevel,
        equipment_type: equipmentType,
      })
      onCreated(session)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session')
    } finally {
      setSubmitting(false)
    }
  }

  function handleOverlayClick(e: React.MouseEvent) {
    if (e.target === overlayRef.current) onClose()
  }

  return (
    <div className="modal-overlay" ref={overlayRef} onClick={handleOverlayClick}>
      <div className="modal" role="dialog" aria-modal="true" aria-label="New session">
        <h2 className="modal-title">New session</h2>

        <form onSubmit={handleSubmit} className="modal-form">
          <label className="modal-label">
            Mode
            <select value={mode} onChange={(e) => setMode(e.target.value)} className="modal-select">
              <option value="structured_learning">Structured Learning</option>
              <option value="scene_advice">Scene Advice</option>
            </select>
          </label>

          <label className="modal-label">
            Your level
            <select value={userLevel} onChange={(e) => setUserLevel(e.target.value)} className="modal-select">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </label>

          <label className="modal-label">
            Equipment
            <select value={equipmentType} onChange={(e) => setEquipmentType(e.target.value)} className="modal-select">
              <option value="dslr">DSLR</option>
              <option value="mirrorless">Mirrorless</option>
              <option value="smartphone">Smartphone</option>
              <option value="film">Film camera</option>
              <option value="point-and-shoot">Point-and-shoot</option>
            </select>
          </label>


{error && <p className="modal-error">{error}</p>}

          <div className="modal-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-create" disabled={submitting}>
              {submitting ? 'Creating…' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
