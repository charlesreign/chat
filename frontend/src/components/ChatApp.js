import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatList from './ChatList';
import ChatWindow from './ChatWindow';
import './ChatApp.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

function ChatApp({ user, onLogout }) {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
    fetchChats();
  });

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchChats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/chats/user/${user.user_id}`);
      setChats(response.data || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching chats:', error);
      setLoading(false);
    }
  };

  const handleCreateChat = async (chatType, selectedUserIds) => {
    try {
      const chatName = chatType === 'group' 
        ? prompt('Enter group chat name:')
        : null;

      if (chatType === 'group' && !chatName) return;

      // For one-on-one chats, check if chat already exists
      if (chatType === 'one_to_one' && selectedUserIds.length === 1) {
        const otherUserId = selectedUserIds[0];
        const existingChat = chats.find(chat => 
          chat.chat_type === 'one_to_one' && 
          chat.members.includes(otherUserId)
        );
        
        if (existingChat) {
          // Use existing chat instead
          setSelectedChat(existingChat);
          return;
        }
      }

      const response = await axios.post(`${API_URL}/api/chats/`, {
        name: chatName,
        chat_type: chatType === 'group' ? 'group' : 'one_to_one',
        member_ids: [user.user_id, ...selectedUserIds]
      });

      setChats([...chats, response.data]);
      setSelectedChat(response.data);
    } catch (error) {
      console.error('Error creating chat:', error);
      alert('Failed to create chat');
    }
  };

  return (
    <div className="chat-app">
      <div className="chat-header">
        <h1>Chat Application</h1>
        <div className="user-info">
          <span>Welcome, {user.username}</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </div>

      <div className="chat-main">
        <ChatList
          chats={chats}
          selectedChat={selectedChat}
          onSelectChat={setSelectedChat}
          onCreateChat={handleCreateChat}
          users={users}
          currentUserId={user.user_id}
        />

        {selectedChat ? (
          <ChatWindow
            chat={selectedChat}
            user={user}
            wsUrl={`${WS_URL}/api/chats/ws/${selectedChat.id}/${user.user_id}`}
          />
        ) : (
          <div className="no-chat-selected">
            <p>Select or create a chat to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatApp;
