import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || '';

export const LeadGenChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [chatStage, setChatStage] = useState('greeting'); // greeting, identify, capture_name, capture_email, complete
  const [userType, setUserType] = useState(''); // renter or property_manager
  const [leadData, setLeadData] = useState({ name: '', email: '', type: '' });
  const [isTyping, setIsTyping] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);

  useEffect(() => {
    // Generate session ID
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substring(7)}`);
    
    // Show initial greeting after 3 seconds
    setTimeout(() => {
      addBotMessage("👋 Hi! I'm here to help you find your perfect no-fee apartment or list your property. Are you looking to rent an apartment or do you manage properties?");
    }, 3000);
  }, []);

  const addBotMessage = (text) => {
    setMessages(prev => [...prev, { type: 'bot', text, timestamp: new Date() }]);
  };

  const addUserMessage = (text) => {
    setMessages(prev => [...prev, { type: 'user', text, timestamp: new Date() }]);
  };

  const handleQuickReply = async (reply, value) => {
    addUserMessage(reply);
    setHasInteracted(true);

    if (chatStage === 'greeting') {
      setUserType(value);
      setChatStage('capture_name');
      
      if (value === 'renter') {
        setTimeout(() => {
          addBotMessage("Great! I'd love to help you find the perfect apartment. What's your name?");
        }, 500);
      } else if (value === 'property_manager') {
        setTimeout(() => {
          addBotMessage("Excellent! We'd love to help you list your properties on NoFeePlaces. What's your name?");
        }, 500);
      }
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMsg = inputMessage;
    addUserMessage(userMsg);
    setInputMessage('');
    setHasInteracted(true);
    setIsTyping(true);

    try {
      if (chatStage === 'capture_name') {
        // Capture name
        setLeadData(prev => ({ ...prev, name: userMsg, type: userType }));
        setChatStage('capture_email');
        
        setTimeout(() => {
          addBotMessage(`Nice to meet you, ${userMsg}! Could you share your email address so I can send you personalized recommendations?`);
          setIsTyping(false);
        }, 800);
        
      } else if (chatStage === 'capture_email') {
        // Validate and capture email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailRegex.test(userMsg)) {
          setTimeout(() => {
            addBotMessage("That doesn't look like a valid email address. Could you please try again?");
            setIsTyping(false);
          }, 500);
          return;
        }

        const finalLeadData = {
          name: leadData.name,
          email: userMsg,
          type: userType,
          session_id: sessionId,
          source: 'chatbot',
          page: window.location.pathname
        };

        // Submit lead to backend
        try {
          await axios.post(`${API}/api/leads/capture`, finalLeadData);
          
          setChatStage('complete');
          setLeadData(prev => ({ ...prev, email: userMsg }));
          
          setTimeout(() => {
            if (userType === 'renter') {
              addBotMessage(`Awesome! ✅ I've saved your info. Check your email at ${userMsg} - I've sent you our latest listings! Feel free to browse apartments on our site or ask me anything about finding your perfect place in NYC.`);
            } else {
              addBotMessage(`Perfect! ✅ Your information has been saved. We'll reach out to ${userMsg} within 24 hours to discuss listing your properties. In the meantime, feel free to explore our platform!`);
            }
            setIsTyping(false);
          }, 1000);
          
        } catch (error) {
          console.error('Error submitting lead:', error);
          setTimeout(() => {
            addBotMessage("Oops! There was an issue saving your information. Please try contacting us at placesfirm@gmail.com");
            setIsTyping(false);
          }, 500);
        }
        
      } else if (chatStage === 'complete') {
        // Continue normal chat after lead capture
        try {
          const response = await axios.post(`${API}/api/chat`, {
            message: userMsg,
            session_id: sessionId
          });
          
          setTimeout(() => {
            addBotMessage(response.data.response);
            setIsTyping(false);
          }, 800);
          
        } catch (error) {
          console.error('Error getting chat response:', error);
          setTimeout(() => {
            addBotMessage("I'm having trouble connecting. Please try again or email us at placesfirm@gmail.com");
            setIsTyping(false);
          }, 500);
        }
      }
      
    } catch (error) {
      console.error('Error:', error);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-full p-4 shadow-2xl hover:shadow-3xl transition-all duration-300 z-50 animate-bounce"
          aria-label="Open chat"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          {!hasInteracted && (
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
          )}
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-2xl">
                🏠
              </div>
              <div>
                <h3 className="font-bold">NoFeeBot</h3>
                <p className="text-xs text-purple-100">Your Apartment Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20 rounded-full p-1 transition"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                    msg.type === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-gray-800 shadow-sm border border-gray-200'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                </div>
              </div>
            ))}

            {/* Quick Reply Buttons */}
            {chatStage === 'greeting' && messages.length > 0 && (
              <div className="flex flex-col gap-2 mt-4">
                <button
                  onClick={() => handleQuickReply("I'm looking to rent 🏠", 'renter')}
                  className="bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-50 rounded-xl px-4 py-3 font-medium transition-all"
                >
                  I'm looking to rent 🏠
                </button>
                <button
                  onClick={() => handleQuickReply("I manage properties 🏢", 'property_manager')}
                  className="bg-white border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 rounded-xl px-4 py-3 font-medium transition-all"
                >
                  I manage properties 🏢
                </button>
              </div>
            )}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-200">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                disabled={chatStage === 'greeting'}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || chatStage === 'greeting'}
                className="bg-purple-600 text-white rounded-xl px-4 py-3 hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default LeadGenChatbot;
