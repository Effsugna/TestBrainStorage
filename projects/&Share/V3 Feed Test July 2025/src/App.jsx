// App.jsx

import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [activeStream, setActiveStream] = useState('For You')
  const [menuOpen, setMenuOpen] = useState(false)
  const [streams, setStreams] = useState(['For You', 'Following', 'Photography', 'Design', 'Tech'])
  const [editingIndex, setEditingIndex] = useState(null)
  const inputRef = useRef(null)

  const addStream = () => {
    const newStreams = [...streams, 'New Stream']
    setStreams(newStreams)
    setActiveStream('New Stream')
    setEditingIndex(newStreams.length - 1)
    setMenuOpen(false)
  }

  const removeStream = (indexToRemove) => {
    const streamToRemove = streams[indexToRemove]
    if (streamToRemove === 'For You') return

    const updated = streams.filter((_, i) => i !== indexToRemove)
    setStreams(updated)

    if (activeStream === streamToRemove) setActiveStream('For You')
  }

  useEffect(() => {
    if (editingIndex !== null && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [editingIndex])

  return (
    <div className="app">
      <div className={`side-drawer ${menuOpen ? 'open' : ''}`}>
        <button className="menu-button internal" onClick={() => setMenuOpen(false)}>
          ☰
        </button>
        <button onClick={addStream}>Create Stream</button>
        <button>Edit Streams</button>
      </div>

      <div className="top-bar">
        <button className="menu-button fixed" onClick={() => setMenuOpen(!menuOpen)}>
          ☰
        </button>
        <div className="feed-tabs">
          {streams.map((stream, index) => (
            <div className="tab-wrapper" key={`${stream}-${index}`}>
              {editingIndex === index ? (
                <input
                  ref={inputRef}
                  className={`edit-tab ${activeStream === stream ? 'active' : ''}`}
                  value={stream}
                  onChange={(e) => {
                    const newList = [...streams]
                    newList[index] = e.target.value
                    setStreams(newList)
                  }}
                  onBlur={() => setEditingIndex(null)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === 'Escape') {
                      setEditingIndex(null)
                    }
                  }}
                />
              ) : (
                <button
                  className={activeStream === stream ? 'active' : ''}
                  onClick={() => setActiveStream(stream)}
                >
                  {stream}
                </button>
              )}
              {stream !== 'For You' && (
                <span
                  className="close-btn"
                  onClick={() => removeStream(index)}
                >
                  ×
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="feed-content">
        <h2>{activeStream} Stream</h2>
        <p>Here’s where content for the <strong>{activeStream}</strong> stream would go.</p>
      </div>
    </div>
  )
}

export default App
