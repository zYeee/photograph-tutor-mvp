import { useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { SessionView } from './components/SessionView'
import './App.css'

const USER_ID = Number(localStorage.getItem('userId') ?? '1')

export default function App() {
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null)

  return (
    <div className="app-layout">
      <Sidebar
        userId={USER_ID}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
      />
      <main className="app-main">
        <SessionView
          sessionId={activeSessionId}
          userId={USER_ID}
          onSessionClosed={() => setActiveSessionId(null)}
        />
      </main>
    </div>
  )
}
