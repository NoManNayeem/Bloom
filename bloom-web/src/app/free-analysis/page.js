'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { FiSend } from 'react-icons/fi';
import { getCookie } from '@/lib/api';

export default function FreeAnalysisPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Fetch conversation history on component mount
  useEffect(() => {
    fetchConversationHistory();
    fetchAnalysisResults();
  }, []);

  const fetchConversationHistory = async () => {
    try {
      const token = getCookie('access_token');
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }
      
      const response = await fetch(`${API_URL}/chat-analysis/history/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversationHistory(data);
        
        // Convert history to message format
        const historyMessages = data.flatMap(conv => [
          { text: conv.agent_message, sender: 'agent' },
          { text: conv.user_message, sender: 'user' }
        ]).filter(msg => msg.text);
        
        setMessages(historyMessages);
        setError(null);
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
      } else {
        setError('Failed to load conversation history.');
      }
    } catch (error) {
      console.error('Error fetching conversation history:', error);
      setError('Network error. Please check your connection.');
    }
  };

  const fetchAnalysisResults = async () => {
    try {
      const token = getCookie('access_token');
      if (!token) return;
      
      const response = await fetch(`${API_URL}/chat-analysis/analysis/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalysisResults(data);
      } else if (response.status === 500) {
        // Handle database schema issues gracefully
        console.warn('Analysis endpoint returned 500, likely due to database schema changes');
        setAnalysisResults([]);
      }
    } catch (error) {
      console.error('Error fetching analysis results:', error);
      // Don't set error state for analysis results as they're secondary
    }
  };

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = input;
      setInput('');
      setIsTyping(true);
      
      // Add user message to UI immediately
      setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
      
      try {
        const token = getCookie('access_token');
        if (!token) {
          setError('Authentication required. Please log in again.');
          setIsTyping(false);
          return;
        }
        
        const response = await fetch(`${API_URL}/chat-analysis/chat/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: userMessage }),
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // Add agent response to UI
          setMessages(prev => [...prev, { text: data.response, sender: 'agent' }]);
          
          // If analysis was triggered, refresh analysis results
          if (data.analysis_triggered) {
            fetchAnalysisResults();
          }
        } else {
          console.error('Failed to send message');
          setMessages(prev => [...prev, { 
            text: 'Sorry, there was an error processing your message.', 
            sender: 'agent' 
          }]);
        }
      } catch (error) {
        console.error('Error sending message:', error);
        setMessages(prev => [...prev, { 
          text: 'Sorry, there was an error connecting to the server.', 
          sender: 'agent' 
        }]);
      } finally {
        setIsTyping(false);
        setError(null);
      }
    }
  };

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-pink-50">
      <div className="relative mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <motion.div
          className="mb-6 flex flex-col gap-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-2xl font-semibold text-gray-900">Free Chat Analysis</h1>
          <p className="mt-1 text-sm text-gray-600">Talk to our agent to get self-analyzed.</p>
        </motion.div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Section */}
          <div className="bg-white p-6 rounded-lg shadow-lg h-[500px] flex flex-col lg:col-span-2">
            <div className="flex-grow overflow-y-auto p-4 space-y-4">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div
                    className={`px-4 py-2 rounded-lg max-w-xs ${
                      msg.sender === 'user'
                        ? 'bg-indigo-600 text-white shadow-lg'
                        : 'bg-gray-200 text-gray-900 shadow-sm'
                    }`}
                  >
                    {msg.sender === 'agent' ? (
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    ) : (
                      msg.text
                    )}
                  </div>
                </motion.div>
              ))}
              {isTyping && (
                <motion.div
                  className="flex justify-start animate-pulse"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  <div className="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg max-w-xs">
                    Agent is typing...
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="flex items-center mt-4 space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-grow p-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Type your response..."
                disabled={isTyping}
              />
              <button
                onClick={handleSend}
                disabled={isTyping || !input.trim()}
                className="ml-2 p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FiSend className="h-6 w-6" />
              </button>
            </div>
          </div>

          {/* Analysis Results Section */}
          <div className="bg-white p-6 rounded-lg shadow-lg h-[500px] overflow-y-auto">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Results</h2>
            
            {analysisResults.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No analysis results yet. Complete conversations will appear here.
              </p>
            ) : (
              <div className="space-y-4">
                {analysisResults.map((analysis, idx) => (
                  <motion.div
                    key={idx}
                    className="bg-gray-50 p-4 rounded-lg border border-gray-200"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.1 }}
                  >
                    <h3 className="font-medium text-gray-800 mb-2">Analysis #{idx + 1}</h3>
                    
                    {analysis.question && (
                      <div className="mb-3">
                        <h4 className="text-sm font-medium text-gray-600 mb-1">Question</h4>
                        <p className="text-sm text-gray-700">{analysis.question}</p>
                      </div>
                    )}
                    
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-green-600 mb-1">Positive Traits</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.positive_traits && Object.entries(analysis.positive_traits).map(([trait, score]) => (
                          <span key={trait} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                            {trait}: {score}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-red-600 mb-1">Negative Traits</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.negative_traits && Object.entries(analysis.negative_traits).map(([trait, score]) => (
                          <span key={trait} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                            {trait}: {score}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-indigo-600 mb-1">Insight</h4>
                      <p className="text-sm text-gray-700 italic">"{analysis.quote}"</p>
                    </div>
                    
                    <p className="text-xs text-gray-500 mt-2">
                      Analyzed on {new Date(analysis.analyzed_at).toLocaleDateString()}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}