import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import {
  MessageSquare,
  Search,
  Menu,
  ChevronDown,
  Home,
  Mic,
  Plus,
  Settings,
} from "lucide-react";
import { Link } from "react-router-dom"; // If not using React Router, replace with <a>
import { Button } from "../ui/Button";

export default function ChatInterface() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      type: "ai",
      content:
        "Hello! I've analyzed your PDF document. Here's a summary of the key points and I'm ready to answer any questions you have about the content.",
    },
  ]);

  const handleSendMessage = () => {
    if (message.trim()) {
      setMessages([...messages, { type: "user", content: message }]);
      setMessage("");

      // Simulate AI response
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            type: "ai",
            content:
              "I understand your question about the document. Let me provide you with a detailed analysis based on the content...",
          },
        ]);
      }, 1000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-80 bg-dark-charcoal text-white flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Menu className="w-5 h-5" />
            <Search className="w-5 h-5" />
          </div>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <Button className="w-full bg-transparent border border-gray-600 hover:bg-gray-700 text-white flex items-center space-x-2">
            <MessageSquare className="w-4 h-4" />
            <span>New chat</span>
          </Button>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto">
          {/* Gems Section */}
          <div className="px-4 py-2">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Gems</h3>
            <div className="space-y-2">
              <div className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 cursor-pointer">
                <div className="w-2 h-2 bg-digital-lavender rounded-full"></div>
                <span className="text-sm text-gray-300">Storybook</span>
                <Settings className="w-3 h-3 text-gray-500 ml-auto" />
              </div>
              <div className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 cursor-pointer">
                <div className="w-4 h-4 border border-gray-500 rounded flex items-center justify-center">
                  <Plus className="w-2 h-2 text-gray-500" />
                </div>
                <span className="text-sm text-gray-300">Explore Gems</span>
              </div>
            </div>
          </div>

          {/* Recent Section */}
          <div className="px-4 py-2 mt-6">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Recent</h3>
            <div className="space-y-2">
              <div className="p-2 rounded hover:bg-gray-700 cursor-pointer">
                <span className="text-sm text-gray-300">
                  Document Analysis Report
                </span>
              </div>
              <div className="p-2 rounded hover:bg-gray-700 cursor-pointer">
                <span className="text-sm text-gray-300">
                  Research Paper Summary
                </span>
              </div>
              <div className="p-2 rounded hover:bg-gray-700 cursor-pointer">
                <span className="text-sm text-gray-300">
                  Legal Document Review
                </span>
              </div>
              <div className="p-2 rounded hover:bg-gray-700 cursor-pointer">
                <span className="text-sm text-gray-300">
                  Financial Report Analysis
                </span>
              </div>
              <div className="p-2 rounded hover:bg-gray-700 cursor-pointer">
                <span className="text-sm text-gray-300">
                  Technical Manual Summary
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="p-4 border-t border-gray-700">
          <Link to="/">
            <Button className="w-full bg-transparent hover:bg-gray-700 text-white flex items-center space-x-2">
              <Home className="w-4 h-4" />
              <span>Home</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-semibold text-foreground">PactAI</h1>
              <Button variant="ghost" className="text-sm text-muted-foreground">
                AI Summarizer <ChevronDown className="w-4 h-4 ml-1" />
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm bg-deep-purple text-white px-2 py-1 rounded">
                PRO
              </span>
              <div className="w-8 h-8 bg-digital-lavender rounded-full flex items-center justify-center text-white font-semibold">
                U
              </div>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6">
            {messages.length === 1 ? (
              /* Welcome State */
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <h2 className="text-4xl font-semibold text-digital-lavender mb-4">
                    Hello, User!
                  </h2>
                  <p className="text-muted-foreground text-lg">
                    I've analyzed your document and I'm ready to help you
                    explore its contents.
                  </p>
                </div>
              </div>
            ) : (
              /* Chat Messages */
              <div className="space-y-6 max-w-4xl mx-auto">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      msg.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-3xl p-4 rounded-lg ${
                        msg.type === "user"
                          ? "bg-deep-purple text-white"
                          : "bg-muted border border-border text-foreground"
                      }`}
                    >
                      <p className="leading-relaxed">{msg.content}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-6 border-t border-border">
            <div className="max-w-4xl mx-auto">
              <div className="relative">
                <div className="flex items-center space-x-3 bg-muted rounded-full p-2 border border-border">
                  <Button size="sm" variant="ghost" className="rounded-full p-2">
                    <Plus className="w-4 h-4" />
                  </Button>
                  <Input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask PactAI"
                    className="flex-1 border-none bg-transparent focus:ring-0 focus:outline-none"
                  />
                  <Button size="sm" variant="ghost" className="rounded-full p-2">
                    <Settings className="w-4 h-4" />
                    <span className="ml-1 text-sm">Tools</span>
                  </Button>
                  <Button size="sm" variant="ghost" className="rounded-full p-2">
                    <Mic className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
