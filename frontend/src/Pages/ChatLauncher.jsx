// src/components/ChatLauncher.jsx
import React, { useState } from 'react';
import ChatPopup from './ChatPopup';

const ChatLauncher = () => {
  const [open, setOpen] = useState(false);

  return (
    <>
      {open && <ChatPopup onClose={() => setOpen(false)} />}
      <button
        onClick={() => setOpen(true)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          backgroundColor: 'blue',
          color: 'white',
          borderRadius: '9999px',
          padding: '10px 20px',
          fontSize: '18px',
          border: 'none',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          zIndex: 1000
        }}
      >
        💬 Chat
      </button>
    </>
  );
};

export default ChatLauncher;
