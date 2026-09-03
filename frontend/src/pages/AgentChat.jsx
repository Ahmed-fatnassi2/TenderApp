

import { useState, useRef, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/AgentChat.css';

function AgentChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState('default');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input, 
          thread_id: threadId 
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Error: ${data.error}` 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: ${error.message}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="agent-chat-container">
      <div className="chat-header">
        <h2>🤖 Tender Assistant</h2>
        <p>Ask me anything about government tenders</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>👋 Hello! I'm your tender assistant. I can help you:</p>
            <ul>
              <li>🔍 Find tenders by description</li>
              <li>📊 Analyze tender requirements</li>
              <li>💡 Get insights about opportunities</li>
              <li>📋 Get detailed tender information</li>
            </ul>
            <p>Try asking: "Find construction tenders in Tunis"</p>
          </div>
        )}
        
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'assistant' && <span className="avatar">🤖</span>}
              {msg.role === 'user' && <span className="avatar">👤</span>}
              <div className="message-text">{msg.content}</div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <span className="avatar">🤖</span>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about tenders..."
          rows={2}
          disabled={loading}
        />
        <button 
          onClick={sendMessage} 
          disabled={loading || !input.trim()}
          className="send-button"
        >
          {loading ? '⏳' : '📤'}
        </button>
      </div>
    </div>
  );
}

export default AgentChat;