import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';
import ChatMessage from './components/ChatMessage';

function App() {
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  const API_URL = 'http://localhost:8000';

  // Tự động cuộn xuống tin nhắn mới nhất
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Tải cuộc trò chuyện từ localStorage khi khởi động
  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      const parsedConversations = JSON.parse(savedConversations);
      setConversations(parsedConversations);

      // Tải cuộc trò chuyện hoạt động cuối cùng nếu có
      const activeId = localStorage.getItem('activeConversationId');
      if (activeId && parsedConversations.find(conv => conv.id === activeId)) {
        setActiveConversationId(activeId);
        const activeConversation = parsedConversations.find(conv => conv.id === activeId);
        if (activeConversation && activeConversation.messages) {
          setMessages(activeConversation.messages);
        }
      } else if (parsedConversations.length > 0) {
        // Nếu không có activeId, mặc định chọn cuộc trò chuyện đầu tiên
        setActiveConversationId(parsedConversations[0].id);
        setMessages(parsedConversations[0].messages || []);
      }
    } else {
      // Tạo cuộc trò chuyện mới nếu không có
      createNewConversation();
    }
  }, []);

  // Lưu cuộc trò chuyện vào localStorage khi thay đổi
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations));
    }
    if (activeConversationId) {
      localStorage.setItem('activeConversationId', activeConversationId);
    }
  }, [conversations, activeConversationId]);

  // Cập nhật tin nhắn cho cuộc trò chuyện hiện tại
  useEffect(() => {
    if (activeConversationId && messages.length > 0) {
      const updatedConversations = conversations.map(conv => {
        if (conv.id === activeConversationId) {
          // Cập nhật tên cuộc trò chuyện dựa trên tin nhắn đầu tiên của người dùng nếu chưa có
          let updatedTitle = conv.title;
          if (updatedTitle === "Cuộc trò chuyện mới" && messages.length >= 2) {
            const firstUserMessage = messages.find(m => m.role === 'user');
            if (firstUserMessage) {
              updatedTitle = firstUserMessage.content.slice(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '');
            }
          }
          return {
            ...conv,
            messages: messages,
            title: updatedTitle
          };
        }
        return conv;
      });
      setConversations(updatedConversations);
    }
  }, [messages, activeConversationId]);

  // Tạo cuộc trò chuyện mới
  const createNewConversation = () => {
    const today = new Date();
    const formattedDate = `${today.getDate()}/${today.getMonth() + 1}/${today.getFullYear()}`;

    const newConversation = {
      id: Date.now().toString(),
      title: "Cuộc trò chuyện mới",
      createdAt: formattedDate,
      messages: []
    };

    setConversations(prev => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
    setMessages([]);

    // Thêm tin nhắn chào mừng từ bot
    const welcomeMessage = {
      role: 'assistant',
      content: 'Xin chào! Tôi là trợ lý hỗ trợ tinh thần của bạn. Bạn đang cảm thấy thế nào hôm nay?'
    };
    setMessages([welcomeMessage]);
  };

  // Xóa cuộc trò chuyện
  const deleteConversation = (e, conversationId) => {
    e.stopPropagation(); // Ngăn chặn sự kiện click lan sang item cha

    const updatedConversations = conversations.filter(
      conv => conv.id !== conversationId
    );

    setConversations(updatedConversations);

    // Nếu xóa cuộc trò chuyện đang hoạt động
    if (conversationId === activeConversationId) {
      if (updatedConversations.length > 0) {
        // Chuyển sang cuộc trò chuyện đầu tiên
        setActiveConversationId(updatedConversations[0].id);
        setMessages(updatedConversations[0].messages || []);
      } else {
        // Nếu không còn cuộc trò chuyện nào, tạo mới
        createNewConversation();
      }
    }
  };

  // Chọn cuộc trò chuyện
  const selectConversation = (conversationId) => {
    if (conversationId === activeConversationId) return;

    const selectedConversation = conversations.find(c => c.id === conversationId);
    if (selectedConversation) {
      setActiveConversationId(conversationId);
      setMessages(selectedConversation.messages || []);
    }
  };

  // Gửi tin nhắn
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (input.trim() === '' || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Gửi tin nhắn tới API
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: userMessage.content,
        history: messages
      });

      // Thêm phản hồi từ bot
      const botMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? '' : 'closed'}`}>
        <button className="new-chat-button" onClick={createNewConversation}>
          + Tạo hội thoại mới
        </button>
        <div className="conversations-list">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`conversation-item ${conversation.id === activeConversationId ? 'active' : ''}`}
              onClick={() => selectConversation(conversation.id)}
            >
              <div className="conversation-info">
                <div className="conversation-title">{conversation.title}</div>
                <div className="conversation-date">{conversation.createdAt}</div>
              </div>
              <button
                className="delete-conversation-button"
                onClick={(e) => deleteConversation(e, conversation.id)}
                aria-label="Xóa cuộc trò chuyện"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-area">
        {/* Header */}
        <div className="chat-header">
          <button className="toggle-sidebar-button" onClick={toggleSidebar}>
            {isSidebarOpen ? '«' : '»'}
          </button>
          <h1 className="chat-title">Tram Chatbot</h1>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          {isLoading && (
            <div className="message bot-message">
              <div className="message-container">
                <div className="avatar bot-avatar">T</div>
                <div className="message-content loading">
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form className="chat-input-form" onSubmit={handleSendMessage}>
          <div className="chat-input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhập tin nhắn..."
              disabled={isLoading}
              className="chat-input"
            />
            <button
              type="submit"
              disabled={isLoading || input.trim() === ''}
              className="send-button"
            >
              Gửi
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;