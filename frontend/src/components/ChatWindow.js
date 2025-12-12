import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatWindow.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ChatWindow({ chat, user, wsUrl }) {
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState('');
  const [activeUsers, setActiveUsers] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const ws = useRef(null);
  const messagesEndRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Load initial messages when chat is selected
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const response = await axios.get(`${API_URL}${chat.id}/messages`);
        setMessages(response.data || []);
      } catch (error) {
        console.error('Error loading messages:', error);
        setMessages([]);
      }
    };

    if (chat && chat.id) {
      loadMessages();
    }
  }, [chat.id, chat]);

  // WebSocket connection effect
  useEffect(() => {
    const connectWebSocket = () => {
      if (!chat || !chat.id) return;

      try {
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
          console.log('WebSocket connected');
          setConnectionStatus('connected');
          reconnectAttempts.current = 0;
        };

        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === 'message') {
              setMessages(prev => {
                // Avoid duplicate messages
                const messageExists = prev.some(msg => msg.id === data.id);
                if (messageExists) return prev;
                return [...prev, {
                  id: data.id,
                  sender_id: data.sender_id,
                  content: data.content,
                  created_at: data.created_at
                }];
              });
            } else if (data.type === 'user_online' || data.type === 'user_offline') {
              setActiveUsers(data.active_users || []);
            } else if (data.type === 'error') {
              console.error('Server error:', data.message);
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e);
          }
        };

        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('error');
        };

        ws.current.onclose = () => {
          console.log('WebSocket disconnected');
          setConnectionStatus('disconnected');
          
          // Attempt to reconnect with exponential backoff
          if (reconnectAttempts.current < maxReconnectAttempts) {
            reconnectAttempts.current += 1;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
            console.log(`Attempting to reconnect in ${delay}ms...`);
            setTimeout(connectWebSocket, delay);
          } else {
            console.error('Max reconnection attempts reached');
          }
        };
      } catch (error) {
        console.error('Error establishing WebSocket connection:', error);
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close(1000, 'Component unmounted');
      }
    };
  }, [wsUrl, chat.id]);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!messageText.trim()) {
      return;
    }

    if (ws.current?.readyState !== WebSocket.OPEN) {
      alert('WebSocket is not connected. Please wait or try again.');
      return;
    }

    try {
      ws.current.send(JSON.stringify({
        content: messageText.trim()
      }));
      setMessageText('');
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-window-header">
        <div>
          <h3>{chat.name || `Chat #${chat.id}`}</h3>
          <p className="chat-info">{chat.chat_type === 'one_to_one' ? '1-on-1 Chat' : 'Group Chat'}</p>
        </div>
        <div className="active-users">
          <span className={`status-indicator ${connectionStatus}`}></span>
          <span className="active-count">{activeUsers.length} online</span>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="no-messages">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`message ${msg.sender_id === user.user_id ? 'sent' : 'received'}`}
            >
              <div className="message-bubble">
                <p>{msg.content}</p>
                <span className="message-time">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="message-input-form">
        <input
          type="text"
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          placeholder={connectionStatus === 'connected' ? 'Type a message...' : 'Connecting...'}
          className="message-input"
          disabled={connectionStatus !== 'connected'}
        />
        <button 
          type="submit" 
          className="send-btn"
          disabled={connectionStatus !== 'connected' || !messageText.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatWindow;
