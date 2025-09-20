import React, { useState } from "react";
import {
  MessageSquare,
  Search,
  Menu,
  ChevronDown,
  FileText,
  Home,
  Upload,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../ui/Button";

export default function UploadInterface() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const navigate = useNavigate();

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);
    const files = Array.from(event.dataTransfer.files);
    setSelectedFiles(files);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleSummarize = () => {
    if (selectedFiles.length > 0) navigate("/chat");
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-80 bg-dark-charcoal text-white flex flex-col">
        <div className="p-4 border-b border-gray-700 flex items-center space-x-3">
          <Menu className="w-5 h-5" />
          <Search className="w-5 h-5" />
        </div>

        <div className="p-4">
          <Button className="w-full bg-transparent border border-gray-600 hover:bg-gray-700 text-white flex items-center space-x-2">
            <MessageSquare className="w-4 h-4" />
            <span>New chat</span>
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-2">
          <h3 className="text-sm font-medium text-gray-400 mb-3">History</h3>
          <div className="space-y-2">
            {[
              "Document Analysis Report",
              "Research Paper Summary",
              "Legal Document Review",
              "Financial Report Analysis",
              "Technical Manual Summary",
            ].map((item, idx) => (
              <div
                key={idx}
                className="flex items-center space-x-3 p-2 rounded hover:bg-gray-700 cursor-pointer"
              >
                <FileText className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-300">{item}</span>
              </div>
            ))}
          </div>
        </div>

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
        <div className="p-6 border-b border-border flex items-center justify-between">
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

        <div className="flex-1 p-8 flex items-center justify-center">
          <div className="w-full max-w-4xl">
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                isDragOver
                  ? "border-deep-purple bg-digital-lavender/10"
                  : "border-deep-purple bg-deep-purple/5"
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <div className="flex justify-center mb-8 space-x-4">
                <div className="w-16 h-20 bg-white border-2 border-deep-purple rounded-lg flex items-center justify-center">
                  <FileText className="w-8 h-8 text-deep-purple" />
                </div>
                <div className="w-16 h-20 bg-digital-lavender rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xs">PDF</span>
                </div>
                <div className="w-16 h-20 bg-white border-2 border-deep-purple rounded-lg flex items-center justify-center">
                  <FileText className="w-8 h-8 text-deep-purple" />
                </div>
              </div>

              <div className="mb-6">
                <label htmlFor="file-upload">
                  <Button className="bg-white text-dark-charcoal border border-gray-300 hover:bg-gray-50 px-8 py-3">
                    <Upload className="w-4 h-4 mr-2" />
                    CHOOSE FILES
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </label>
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>

              <p className="text-white text-lg mb-8">or drop files here</p>

              {selectedFiles.length > 0 && (
                <div className="mb-6">
                  <p className="text-white mb-2">Selected files:</p>
                  <div className="space-y-1">
                    {selectedFiles.map((file, index) => (
                      <p key={index} className="text-digital-lavender text-sm">
                        {file.name}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-start">
              <Button
                onClick={handleSummarize}
                disabled={selectedFiles.length === 0}
                className="bg-dark-charcoal text-white hover:bg-dark-charcoal/90 px-8 py-2 disabled:opacity-50"
              >
                Summarize
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
