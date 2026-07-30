import { useState, useEffect, useRef, useCallback } from 'react'
import ChatWindow from './components/ChatWindow'
import Sidebar from './components/Sidebar'
import { chatAPI, sessionAPI } from './services/api'
import './styles/App.css'

function App() {
  const [sessions, setSessions] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      const res = await sessionAPI.list()
      setSessions(res.sessions || [])
    } catch (err) {
      console.error('加载会话失败:', err)
    }
  }, [])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  // 创建新会话
  const handleNewSession = async () => {
    try {
      const res = await sessionAPI.create({ title: '新对话' })
      setCurrentSession(res)
      setMessages([])
      await loadSessions()
    } catch (err) {
      console.error('创建会话失败:', err)
    }
  }

  // 选择会话
  const handleSelectSession = async (session) => {
    setCurrentSession(session)
    try {
      const res = await chatAPI.history(session.id)
      setMessages(res.messages || [])
    } catch (err) {
      console.error('加载历史失败:', err)
    }
  }

  // 发送消息
  const handleSendMessage = async (content) => {
    if (!content.trim() || isLoading) return

    // 如果没有会话，先创建
    let session = currentSession
    if (!session) {
      session = await sessionAPI.create({ title: content.slice(0, 30) })
      setCurrentSession(session)
      await loadSessions()
    }

    // 添加用户消息到界面
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const res = await chatAPI.send({
        session_id: session.id,
        message: content,
      })

      // 添加助手回复
      const assistantMessage = {
        id: res.id,
        role: 'assistant',
        content: res.content,
        intent: res.intent,
        confidence: res.confidence,
        created_at: res.created_at,
      }
      setMessages((prev) => [...prev, assistantMessage])
      await loadSessions() // 刷新会话列表（更新消息数）
    } catch (err) {
      console.error('发送消息失败:', err)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: '抱歉，发生了错误，请稍后再试。',
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // 删除会话
  const handleDeleteSession = async (sessionId) => {
    try {
      await sessionAPI.delete(sessionId)
      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
        setMessages([])
      }
      await loadSessions()
    } catch (err) {
      console.error('删除会话失败:', err)
    }
  }

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        currentSession={currentSession}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      <ChatWindow
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        currentSession={currentSession}
      />
    </div>
  )
}

export default App
