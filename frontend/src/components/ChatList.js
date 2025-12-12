import React, { useState } from 'react';
import './ChatList.css';

function ChatList({ chats, selectedChat, onSelectChat, onCreateChat, users, currentUserId }) {
  const [showCreateMenu, setShowCreateMenu] = useState(false);
  const [selectedUserIds, setSelectedUserIds] = useState([]);

  const availableUsers = users.filter(u => u.id !== currentUserId);

  const handleUserSelect = (userId) => {
    if (selectedUserIds.includes(userId)) {
      setSelectedUserIds(selectedUserIds.filter(id => id !== userId));
    } else {
      setSelectedUserIds([...selectedUserIds, userId]);
    }
  };

  const handleCreateOneToOne = () => {
    if (selectedUserIds.length === 1) {
      onCreateChat('one_to_one', selectedUserIds);
      setSelectedUserIds([]);
      setShowCreateMenu(false);
    }
  };

  const handleCreateGroup = () => {
    if (selectedUserIds.length >= 1) {
      onCreateChat('group', selectedUserIds);
      setSelectedUserIds([]);
      setShowCreateMenu(false);
    }
  };

  return (
    <div className="chat-list">
      <div className="chat-list-header">
        <h2>Chats</h2>
        <button
          onClick={() => setShowCreateMenu(!showCreateMenu)}
          className="create-chat-btn"
        >
          + New Chat
        </button>
      </div>

      {showCreateMenu && (
        <div className="create-menu">
          <h3>Create New Chat</h3>
          <div className="user-selection">
            {availableUsers.map(user => (
              <label key={user.id} className="user-checkbox">
                <input
                  type="checkbox"
                  checked={selectedUserIds.includes(user.id)}
                  onChange={() => handleUserSelect(user.id)}
                />
                <span>{user.username}</span>
              </label>
            ))}
          </div>

          <div className="create-menu-buttons">
            {selectedUserIds.length === 1 && (
              <button onClick={handleCreateOneToOne} className="btn-primary">
                Start 1-on-1 Chat
              </button>
            )}
            {selectedUserIds.length >= 1 && (
              <button onClick={handleCreateGroup} className="btn-primary">
                Create Group Chat
              </button>
            )}
            <button
              onClick={() => {
                setShowCreateMenu(false);
                setSelectedUserIds([]);
              }}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="chat-items">
        {chats.length === 0 ? (
          <p className="no-chats">No chats yet. Create one to get started!</p>
        ) : (
          chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${selectedChat?.id === chat.id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat)}
            >
              <div className="chat-item-info">
                <h4>{chat.name || `Chat #${chat.id}`}</h4>
                <p className="chat-type">{chat.chat_type === 'one_to_one' ? '1-on-1' : 'Group'}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ChatList;
