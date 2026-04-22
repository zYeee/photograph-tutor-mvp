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
  const bottomRef = useRef<HTMLDivElement>(null)

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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages?.length, streamingPreviewsToDisplay.length])

  if (!hasContent) {
    return (
      <div className="transcript transcript--empty">
        <p>{isConnected ? 'Listening… start speaking' : 'Connect and start speaking'}</p>
      </div>
    )
  }
  return (
    <div className="transcript">
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
