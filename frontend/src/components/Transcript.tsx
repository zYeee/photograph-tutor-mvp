import { useEffect, useRef } from 'react'
import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { getMessages, type Message } from '../api'
import './Transcript.css'

interface StreamingPreview {
  text: string
  role: 'user' | 'assistant'
}

interface Props {
  sessionId: number
  isConnected: boolean
  streamingPreviews?: StreamingPreview[]
}

export function Transcript({ sessionId, isConnected, streamingPreviews = [] }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const userScrolledUpRef = useRef(false)

  const { data: messages } = useQuery<Message[]>({
    queryKey: ['messages', sessionId],
    queryFn: () => getMessages(sessionId),
    refetchInterval: isConnected ? 2000 : false,
    placeholderData: keepPreviousData,
  })

  const hasContent = (messages && messages.length > 0) || streamingPreviews.length > 0

  const streamingPreviewsToDisplay = streamingPreviews.filter((preview) => {
    // If a persistent message already ends with or contains this text, skip the preview
    return !messages?.some(
      (m) => m.role === preview.role && m.content.includes(preview.text.trim()),
    )
  })

  // Track whether the user has scrolled away from the bottom
  function handleScroll() {
    const el = containerRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    userScrolledUpRef.current = distanceFromBottom > 80
  }

  // Scroll to bottom whenever messages or streaming text changes, unless user scrolled up
  const streamingText = streamingPreviewsToDisplay.map((s) => s.text).join('')
  useEffect(() => {
    if (!userScrolledUpRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages?.length, streamingText])

  if (!hasContent) {
    return (
      <div className="transcript transcript--empty">
        <p>{isConnected ? 'Listening… start speaking' : 'Connect and start speaking'}</p>
      </div>
    )
  }
  return (
    <div className="transcript" ref={containerRef} onScroll={handleScroll}>
      {messages?.map((msg) => (
        <div key={msg.id} className={`bubble bubble--${msg.role}`}>
          <span className="bubble-role">{msg.role === 'user' ? 'You' : 'Tutor'}</span>
          <p className="bubble-content">{msg.content}</p>
        </div>
      ))}
      {streamingPreviewsToDisplay.map((seg, i) => (
        <div key={`stream-${i}`} className={`bubble bubble--${seg.role} bubble--streaming`}>
          <span className="bubble-role">{seg.role === 'user' ? 'You' : 'Tutor'}</span>
          <p className="bubble-content">{seg.text}<span className="bubble-cursor" /></p>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
