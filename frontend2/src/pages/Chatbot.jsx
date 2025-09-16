import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

// Simulated API response data
const initialChatData = {
  user: {
    name: 'John Doe',
    status: 'Online',
    avatar: 'JD',
  },
  sessions: [
    { 
      id: 1, 
      title: 'Contract Summary', 
      date: 'Sep 16, 2025', 
      messages: [
        { id: 1, type: 'assistant', content: 'Here is a summary of the uploaded contract:', timestamp: new Date(Date.now() - 3600000) },
        { id: 2, type: 'user', content: 'What are the key clauses?', timestamp: new Date(Date.now() - 3500000) },
        { id: 3, type: 'assistant', content: 'The key clauses are confidentiality, termination, and payment terms.', timestamp: new Date(Date.now() - 3400000) },
      ]
    },
    { 
      id: 2, 
      title: 'Project Discussion', 
      date: 'Aug 28, 2025',
      messages: [
        { id: 1, type: 'assistant', content: 'Hello! How can I help with your project?', timestamp: new Date(Date.now() - 3600000) },
        { id: 2, type: 'user', content: 'Can you outline the next steps?', timestamp: new Date(Date.now() - 3500000) },
        { id: 3, type: 'assistant', content: 'I recommend we start with a project brief.', timestamp: new Date(Date.now() - 3400000) },
      ]
    },
  ],
  newDocumentResponse: {
    documentName: 'document_to_be_summarized.pdf',
    summary: "The uploaded document outlines a comprehensive project plan, including key milestones, budget allocation, and a timeline. It emphasizes a phased approach with an initial focus on market research and stakeholder alignment before proceeding to development.",
    sessionTitle: "Document Summary - document_to_be_summarized.pdf",
  },
};

const Chatbot = () => {
  const navigate = useNavigate();
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [chatData, setChatData] = useState(initialChatData);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const activeSession = chatData.sessions.find(session => session.id === activeSessionId);
  const messages = activeSession ? activeSession.messages : [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleSidebar = () => setSidebarVisible(!sidebarVisible);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };
    
    setIsLoading(true);

    setTimeout(() => {
      const responses = [
        "I can help with that. Let me explain further...",
        "Based on your question, here's what I recommend...",
        "That's an interesting query. Here's some information...",
        "I understand your question. Let me provide more details...",
      ];
      
      const aiMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date(),
      };
      
      setChatData(prevData => ({
        ...prevData,
        sessions: prevData.sessions.map(session =>
          session.id === activeSessionId
            ? { ...session, messages: [...session.messages, userMessage, aiMessage] }
            : session
        )
      }));

      setIsLoading(false);
    }, 1000);

    setInputMessage('');
  };

  const startNewChat = () => {
    setActiveSessionId(null);
  };

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setIsLoading(true);
      
      const getSummary = () => new Promise(resolve => {
        setTimeout(() => {
          resolve(chatData.newDocumentResponse);
        }, 2000);
      });

      try {
        const response = await getSummary();
        const { documentName, summary, sessionTitle } = response;

        const newSessionId = chatData.sessions.length + 1;
        const newSummaryMessage = {
          id: 1,
          type: 'assistant',
          content: `Here is a summary of the uploaded document:\n\n${summary}`,
          timestamp: new Date(),
          documentName: documentName,
        };
        
        const newSession = {
          id: newSessionId,
          title: sessionTitle,
          date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          messages: [newSummaryMessage],
        };

        setChatData(prevData => ({
          ...prevData,
          sessions: [newSession, ...prevData.sessions],
        }));

        setActiveSessionId(newSessionId);
      } catch (error) {
        console.error("Error processing document:", error);
      } finally {
        setIsLoading(false);
      }
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
            <h3 className="text-sm font-semibold text-foreground/60 px-2 py-3 uppercase">Chat Sessions</h3>
            <div className="space-y-2">
              {chatData.sessions.map(session => (
                <div
                  key={session.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    activeSessionId === session.id ? 'bg-border' : 'hover:bg-border'
                  }`}
                  onClick={() => setActiveSessionId(session.id)}
                >
                  <div className="font-medium">{session.title}</div>
                  <div className="text-xs text-foreground/60">{session.date}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="p-4 border-t border-border">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-white font-semibold">
                {chatData.user.avatar}
              </div>
              <div>
                <div className="font-medium">{chatData.user.name}</div>
                <div className="text-xs text-green-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
                  {chatData.user.status}
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
            
            {isLoading && !messages.length > 0 && (
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