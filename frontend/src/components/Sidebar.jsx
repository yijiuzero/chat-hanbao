import './Sidebar.css'

function Sidebar({
  sessions,
  currentSession,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  isOpen,
  onToggle,
}) {
  return (
    <>
      {/* 移动端遮罩 */}
      {isOpen && <div className="sidebar-overlay" onClick={onToggle} />}
      
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h3>💬 会话列表</h3>
          <button className="new-chat-btn" onClick={onNewSession} title="新建对话">
            ＋ 新对话
          </button>
        </div>

        <div className="sessions-list">
          {sessions.length === 0 ? (
            <div className="empty-sessions">
              <p>暂无会话</p>
              <p className="hint">点击上方按钮创建新对话</p>
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${
                  currentSession?.id === session.id ? 'active' : ''
                }`}
                onClick={() => onSelectSession(session)}
              >
                <div className="session-content">
                  <div className="session-title">{session.title}</div>
                  <div className="session-meta">
                    <span>{session.message_count || 0} 条消息</span>
                    <span className="session-time">
                      {session.updated_at
                        ? new Date(session.updated_at).toLocaleDateString('zh-CN')
                        : ''}
                    </span>
                  </div>
                </div>
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm('确定要删除这个会话吗？')) {
                      onDeleteSession(session.id)
                    }
                  }}
                  title="删除会话"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <span>🐳 Chat Hanbao v1.0</span>
        </div>
      </div>

      {/* 切换按钮 */}
      <button className="sidebar-toggle" onClick={onToggle}>
        {isOpen ? '◀' : '▶'}
      </button>
    </>
  )
}

export default Sidebar
