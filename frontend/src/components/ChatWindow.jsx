import { useState, useRef, useEffect } from 'react'
import './ChatWindow.css'

function ChatWindow({ messages, onSendMessage, isLoading, currentSession }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // 聚焦输入框
  useEffect(() => {
    inputRef.current?.focus()
  }, [currentSession])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="chat-window">
      {/* 聊天头部 */}
      <div className="chat-header">
        <div className="header-left">
          <div className="logo">🐳</div>
          <div className="header-info">
            <h2>Chat Hanbao</h2>
            <span className="status">
              <span className="status-dot online"></span>
              在线
            </span>
          </div>
        </div>
        {currentSession && (
          <div className="session-info">
            <span className="session-title">{currentSession.title}</span>
            <span className="message-count">
              {currentSession.message_count || 0} 条消息
            </span>
          </div>
        )}
      </div>

      {/* 消息区域 */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">🐳</div>
            <h3>欢迎来到 Chat Hanbao!</h3>
            <p>我是你的 AI 聊天伙伴，有什么想聊的吗？</p>
            <div className="quick-actions">
              <button onClick={() => onSendMessage('你好！')}>👋 打招呼</button>
              <button onClick={() => onSendMessage('你能做什么？')}>❓ 了解功能</button>
              <button onClick={() => onSendMessage('讲个笑话')}>😄 听笑话</button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🐳'}
                </div>
                <div className="message-content">
                  <div className="message-bubble">
                    {msg.content.split('\n').map((line, i) => (
                      <span key={i}>
                        {line}
                        {i < msg.content.split('\n').length - 1 && <br />}
                      </span>
                    ))}
                  </div>
                  <div className="message-meta">
                    <span className="message-time">
                      {msg.created_at
                        ? new Date(msg.created_at).toLocaleTimeString('zh-CN', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : ''}
                    </span>
                    {msg.intent && msg.intent !== 'chat' && (
                      <span className="message-intent">{msg.intent}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant loading">
                <div className="message-avatar">🐳</div>
                <div className="message-content">
                  <div className="message-bubble">
                    <span className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 输入区域 */}
      <form className="input-area" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatWindow
