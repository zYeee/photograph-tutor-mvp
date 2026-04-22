import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getTopics, getUserProgress, getUser, type Topic } from '../api'
import './StudyJourneyModal.css'

interface Props {
  userId: number
  onClose: () => void
}

const LEVELS: { key: string; label: string }[] = [
  { key: 'beginner', label: 'Beginner' },
  { key: 'intermediate', label: 'Intermediate' },
  { key: 'advanced', label: 'Advanced' },
]

function flattenLeaves(topics: Topic[]): Topic[] {
  const leaves: Topic[] = []
  for (const t of topics) {
    if (t.children && t.children.length > 0) {
      leaves.push(...flattenLeaves(t.children))
    } else if (t.level) {
      leaves.push(t)
    }
  }
  return leaves
}

export function StudyJourneyModal({ userId, onClose }: Props) {
  const overlayRef = useRef<HTMLDivElement>(null)

  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => getUser(userId),
  })

  const { data: topics, isLoading: topicsLoading, isError: topicsError } = useQuery({
    queryKey: ['topics'],
    queryFn: getTopics,
  })

  const { data: progress, isLoading: progressLoading, isError: progressError } = useQuery({
    queryKey: ['progress', userId],
    queryFn: () => getUserProgress(userId),
  })

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  function handleOverlayClick(e: React.MouseEvent) {
    if (e.target === overlayRef.current) onClose()
  }

  const isLoading = topicsLoading || progressLoading
  const isError = topicsError || progressError

  const progressBySlug = new Map(
    (progress ?? []).map((p) => [p.slug, p.status])
  )

  const leafTopics = topics ? flattenLeaves(topics) : []

  function topicBadge(slug: string) {
    const status = progressBySlug.get(slug)
    if (status === 'completed') return <span className="sj-badge sj-badge--done">✅ Done</span>
    if (status === 'in_progress') return <span className="sj-badge sj-badge--progress">⏳ In Progress</span>
    return null
  }

  return (
    <div className="sj-overlay" ref={overlayRef} onClick={handleOverlayClick}>
      <div className="sj-modal" role="dialog" aria-modal="true" aria-label="Study Journey">
        <div className="sj-header">
          <h2 className="sj-title">Study Journey</h2>
          <button className="sj-close" onClick={onClose} aria-label="Close">×</button>
        </div>

        <div className="sj-body">
          {user && (
            <p className="sj-greeting">
              Hi {user.display_name}, this is your study journey ;-)
            </p>
          )}
          {isLoading && <p className="sj-state">Loading topics…</p>}
          {isError && <p className="sj-state sj-error">Failed to load topics. Please try again.</p>}

          {!isLoading && !isError && LEVELS.map(({ key, label }) => {
            const levelTopics = leafTopics.filter((t) => t.level === key)
            return (
              <section key={key} className="sj-section">
                <h3 className="sj-level-heading">{label}</h3>
                {levelTopics.length === 0 ? (
                  <p className="sj-empty">No topics</p>
                ) : (
                  <ul className="sj-topic-list">
                    {levelTopics.map((t) => (
                      <li key={t.slug} className="sj-topic-row">
                        <span className="sj-topic-title">{t.title}</span>
                        {topicBadge(t.slug)}
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            )
          })}
        </div>
      </div>
    </div>
  )
}
