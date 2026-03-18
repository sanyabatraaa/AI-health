// src/components/ChatPopup.jsx
import React from 'react';
import Chatbot from './Chatbot';

const ChatPopup = ({ onClose }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: '#ffffff',
      zIndex: 1001,
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div style={{
        backgroundColor: '#007bff',
        color: 'white',
        padding: '15px',
        fontWeight: 'bold',
        fontSize: '18px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        ZeeCare Assistant
        <button onClick={onClose} style={{
          background: 'transparent',
          border: 'none',
          color: 'white',
          fontSize: '20px',
          cursor: 'pointer',
        }}>✖</button>
      </div>

      <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
        <Chatbot />
      </div>
    </div>
  );
};

export default ChatPopup;
