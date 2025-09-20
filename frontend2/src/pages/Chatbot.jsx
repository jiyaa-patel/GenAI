import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { legalApi } from '../utils/api';

// Start with no seed data; hydrate from server
const initialChatData = { user: {}, sessions: [] };

const Chatbot = () => {
  const navigate = useNavigate();
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [chatData, setChatData] = useState(initialChatData);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [activeDocumentId, setActiveDocumentId] = useState(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const displayName = localStorage.getItem('displayName') || localStorage.getItem('email') || 'User';

  const activeSession = chatData.sessions.find(session => session.id === activeSessionId);
  const messages = activeSession ? activeSession.messages : [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessions = async () => {
    try {
      // Check if user is authenticated
      const token = localStorage.getItem('accessToken');
      const userEmail = localStorage.getItem('userEmail');
      console.log('Auth check:', { hasToken: !!token, userEmail });
      
      if (!token || !userEmail) {
        console.log('User not authenticated, skipping session load');
        return;
      }
      
      const sessions = await legalApi.getSessionsWithMessages();
      console.log('Loaded sessions:', sessions); // Debug log
      if (Array.isArray(sessions) && sessions.length) {
        const mapped = sessions.map((s, idx) => ({
          id: s.id,
          title: s.name || `Chat ${idx + 1}`,
          date: new Date(s.last_updated || s.created_at || Date.now()).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          documentId: s.document_id || null,
          messages: (s.messages || []).map((m, i) => ({
            id: i + 1,
            type: m.message_type === 'user' ? 'user' : 'assistant',
            content: m.content,
            timestamp: new Date(m.created_at || Date.now()),
          })),
        }));
        setChatData(prev => ({ ...prev, sessions: mapped }));
        if (!activeSessionId && mapped.length) {
          setActiveSessionId(mapped[0].id);
          setActiveDocumentId(mapped[0].documentId || null);
        }
      } else {
        console.log('No sessions found or empty array');
        setChatData(prev => ({ ...prev, sessions: [] }));
      }
    } catch (e) {
      console.error('Error loading sessions:', e);
      if (e.message.includes('Authentication failed')) {
        console.log('Authentication failed, user needs to log in');
      }
      setChatData(prev => ({ ...prev, sessions: [] }));
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);



  const toggleSidebar = () => setSidebarVisible(!sidebarVisible);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };
    
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // Add user message immediately
    setChatData(prevData => ({
      ...prevData,
      sessions: prevData.sessions.map(session =>
        session.id === activeSessionId
          ? { ...session, messages: [...session.messages, userMessage] }
          : session
      )
    }));

    try {
      // Save user message to database
      if (activeSessionId) {
        await legalApi.saveMessage(activeSessionId, currentInput, 'user');
      }

      const chatId = activeSessionId; // Django ChatSession id
      const apiResponse = await legalApi.askQuestion(currentInput, chatId, activeDocumentId);
      const assistantText = apiResponse?.response || 'No response';

      // Save assistant message to database
      if (activeSessionId) {
        await legalApi.saveMessage(activeSessionId, assistantText, 'assistant');
      }

      const aiMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: assistantText,
        timestamp: new Date(),
      };

      // Add AI response
      setChatData(prevData => ({
        ...prevData,
        sessions: prevData.sessions.map(session =>
          session.id === activeSessionId
            ? { ...session, messages: [...session.messages, aiMessage] }
            : session
        )
      }));
    } catch (err) {
      console.error('askQuestion failed', err);
      // Add error message
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: 'Sorry, there was an error processing your question. Please try again.',
        timestamp: new Date(),
      };
      
      setChatData(prevData => ({
        ...prevData,
        sessions: prevData.sessions.map(session =>
          session.id === activeSessionId
            ? { ...session, messages: [...session.messages, errorMessage] }
            : session
        )
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setActiveSessionId(null);
    setActiveDocumentId(null);
  };

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setIsLoading(true);
    try {
      const res = await legalApi.uploadDocument(file);
      const { chat_id, chat_name, message, success, document_id, initial_summary } = res || {};
      const docName = res?.document_name || file.name;
      const summary = initial_summary?.summary || message || 'Document processed.';

      const newSummaryMessage = {
        id: 1,
        type: 'assistant',
        content: `Here is a summary of the uploaded document:\n\n${summary}`,
        timestamp: new Date(),
        documentName: docName,
      };

      if (!chat_id) {
        // If backend didn’t return a chat id, skip adding a session to avoid invalid id
        setIsLoading(false);
        return;
      }
      const newSession = {
        id: chat_id,
        title: chat_name || `Document Summary - ${docName}`,
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        documentId: document_id || null,
        messages: [newSummaryMessage],
      };

      setChatData(prevData => ({
        ...prevData,
        sessions: [newSession, ...prevData.sessions],
      }));

      setActiveSessionId(newSession.id);
      setActiveDocumentId(document_id || null);
    } catch (error) {
      console.error('Error processing document:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Left sidebar */}
      {sidebarVisible && (
        <div className="w-80 bg-card border-r border-border flex flex-col transition-all duration-300 ease-in-out">
          <div className="p-5 border-b border-border">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-xl font-bold">PactAI Chatbot</h1>
              <div className="flex items-center space-x-2">
                <button
                  onClick={startNewChat}
                  className="bg-primary text-white p-2 rounded-lg transition-colors hover:bg-primary/90"
                  title="New Chat"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
                <button
                  onClick={loadSessions}
                  className="p-2 rounded-lg text-foreground/70 hover:bg-border transition-colors"
                  title="Refresh Sessions"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button
                  onClick={toggleSidebar}
                  className="p-2 rounded-lg text-foreground/70 hover:bg-border transition-colors"
                  title="Hide Sidebar"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-3">
            <h3 className="text-sm font-semibold text-foreground/60 px-2 py-3 uppercase">Chat Sessions ({chatData.sessions.length})</h3>
            <div className="space-y-2">
              {chatData.sessions.length === 0 ? (
                <div className="p-3 text-center text-foreground/60 text-sm">
                  No chat sessions yet.<br/>
                  Upload a document to start chatting!
                </div>
              ) : (
                chatData.sessions.map(session => (
                  <div
                    key={session.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      activeSessionId === session.id ? 'bg-border' : 'hover:bg-border'
                    }`}
                    onClick={() => {
                      setActiveSessionId(session.id);
                      setActiveDocumentId(session.documentId || null);
                    }}
                  >
                    <div className="font-medium truncate">{session.title}</div>
                    <div className="text-xs text-foreground/60">{session.date}</div>
                    <div className="text-xs text-foreground/40">{session.messages?.length || 0} messages</div>
                  </div>
                ))
              )}
            </div>
          </div>
          
          <div className="p-4 border-t border-border">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-white font-semibold">
                {(displayName.split(' ').map(p => p[0]).join('').slice(0,2) || 'U').toUpperCase()}
              </div>
              <div>
                <div className="font-medium">{displayName}</div>
                <div className="text-xs text-green-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                  Online
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Main chat area */}
      <div className={`flex-1 flex flex-col ${sidebarVisible ? '' : 'ml-0'}`}>
        <div className="bg-card border-b border-border p-4 flex justify-between items-center">
          <div className="flex items-center">
            {!sidebarVisible && (
              <button
                onClick={toggleSidebar}
                className="p-2 mr-3 rounded-lg text-foreground/70 hover:bg-border transition-colors"
                title="Show Sidebar"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </button>
            )}
            <h2 className="text-lg font-semibold">
              {activeSession ? activeSession.title : 'New Chat'}
            </h2>
          </div>
          
          {!sidebarVisible && (
            <button
              onClick={startNewChat}
              className="bg-primary hover:bg-primary/90 text-white py-2 px-4 rounded-lg flex items-center transition-colors"
            >
              <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
          )}
        </div>
        
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-6 bg-background relative">
          <div className="max-w-3xl mx-auto space-y-6">
            {!activeSessionId && messages.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="p-6 bg-card rounded-lg shadow-xl text-center max-w-sm">
                  <h2 className="text-2xl font-semibold mb-2">PactAI Chatbot</h2>
                  <p className="text-foreground/80 mb-4">Upload a document to get a summary and ask questions about it.</p>
                  
                  {isLoading ? (
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 rounded-full border-4 border-border border-t-blue-500 animate-spin"></div>
                      <p className="mt-4 text-foreground/80">Processing document...</p>
                    </div>
                  ) : (
                    <label className="inline-flex items-center px-6 py-3 border border-border rounded-lg bg-card cursor-pointer hover:bg-border transition-colors text-foreground">
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M5.5 12.5a.5.5 0 01.5-.5h4.5a.5.5 0 010 1H6a.5.5 0 01-.5-.5zM5.5 8.5a.5.5 0 01.5-.5h7.5a.5.5 0 010 1H6a.5.5 0 01-.5-.5z" />
                        <path fillRule="evenodd" d="M14.5 2.5a.5.5 0 01.5.5v12a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h4.5a2.5 2.5 0 012.5 2.5V8a.5.5 0 01-1 0V5.5a1.5 1.5 0 00-1.5-1.5H5a1 1 0 00-1 1v12a1 1 0 001 1h8a1 1 0 001-1V3a.5.5 0 011 0z" clipRule="evenodd" />
                      </svg>
                      <input type="file" className="hidden" onChange={handleDocumentUpload} />
                      Upload Document
                    </label>
                  )}
                </div>
              </div>
            )}
            
            {activeSession && messages.length > 0 && messages[0].documentName && (
              <div className="text-center text-sm text-foreground/70 mb-4 font-semibold">
                Document: {messages[0].documentName}
              </div>
            )}

            {messages.map(message => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl rounded-lg p-4 ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                      : 'bg-card text-foreground border border-border'
                  }`}
                >
                  <div className="whitespace-pre-line">{message.content}</div>
                  <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-blue-100' : 'text-foreground/60'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-card border border-border rounded-lg p-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-foreground/50 animate-bounce"></div>
                    <div className="w-2 h-2 rounded-full bg-foreground/50 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 rounded-full bg-foreground/50 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        {/* Input area */}
        <div className="bg-card border-t border-border p-4">
          <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex space-x-3">
            <input
              type="text"
              value={inputMessage}
              onChange={e => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors bg-background text-foreground"
              disabled={isLoading || !activeSession}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading || !activeSession}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;