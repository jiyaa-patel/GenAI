import React from 'react';
import './Steps.css';

const Steps = () => {
  return (
    <section id="pdf-summarizer" className="w-full">
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 w-full py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-12">
            {/* Header */}
            <div className="text-center">
              <h2 className="text-4xl md:text-5xl font-bold text-gray-800 dark:text-white mb-4">How To Summarize a PDF with AI</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
                Transform lengthy documents into concise summaries in just a few simple steps
              </p>
            </div>

            {/* Main Content */}
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              {/* Enhanced Illustration Section */}
              <div className="flex justify-center">
                <div className="relative">
                  {/* Main animation container */}
                  <div className="relative flex items-center justify-center space-x-10">
                    
                    {/* Animated AI Character */}
                    <div className="relative z-10">
                      <div className="w-40 h-48 bg-gradient-to-br from-white to-blue-50 dark:from-gray-800 dark:to-blue-900/30 rounded-2xl border-3 border-blue-200 dark:border-blue-700 shadow-2xl transform -rotate-6">
                        
                        {/* Face */}
                        <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
                          {/* Glasses */}
                          <div className="flex items-center justify-center space-x-4 mb-2">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-800 dark:to-blue-900 border-2 border-blue-300 dark:border-blue-600 rounded-full flex items-center justify-center shadow-inner">
                              <div className="w-4 h-4 bg-blue-600 dark:bg-blue-400 rounded-full"></div>
                            </div>
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-800 dark:to-blue-900 border-2 border-blue-300 dark:border-blue-600 rounded-full flex items-center justify-center shadow-inner">
                              <div className="w-4 h-4 bg-blue-600 dark:bg-blue-400 rounded-full"></div>
                            </div>
                          </div>
                          
                          {/* Glasses bridge */}
                          <div className="w-6 h-1 bg-blue-300 dark:bg-blue-600 mx-auto rounded-full"></div>
                          
                          {/* Smile */}
                          <div className="w-12 h-1 bg-pink-400 dark:bg-pink-500 mx-auto mt-4 rounded-full"></div>
                        </div>

                        {/* Body */}
                        <div className="absolute top-24 left-1/2 transform -translate-x-1/2 w-16 h-12 bg-gradient-to-br from-blue-200 to-blue-300 dark:from-blue-700 dark:to-blue-800 rounded-lg"></div>
                      </div>

                      {/* Floating elements around character */}
                      <div className="absolute -top-6 -right-6 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg">
                        AI
                      </div>
                      <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-cyan-400 dark:bg-cyan-600 rounded-full shadow-md"></div>
                    </div>

                    {/* Animated PDF Document with better styling */}
                    <div className="relative z-0 transform rotate-3">
                      <div className="w-28 h-36 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl shadow-2xl border-2 border-purple-200 dark:border-purple-700">
                        
                        {/* PDF header */}
                        <div className="bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-700 dark:to-pink-700 rounded-t-lg p-2">
                          <div className="flex items-center justify-center">
                            <div className="w-6 h-6 bg-white dark:bg-gray-800 rounded text-xs flex items-center justify-center font-bold text-purple-600 dark:text-purple-400 shadow-inner">
                              PDF
                            </div>
                          </div>
                        </div>

                        {/* Document content */}
                        <div className="p-3 space-y-2">
                          <div className="w-full h-1 bg-purple-400/60 dark:bg-purple-600 rounded-full"></div>
                          <div className="w-3/4 h-1 bg-purple-400/60 dark:bg-purple-600 rounded-full"></div>
                          <div className="w-full h-1 bg-purple-400/60 dark:bg-purple-600 rounded-full"></div>
                          <div className="w-1/2 h-1 bg-purple-400/60 dark:bg-purple-600 rounded-full"></div>
                          <div className="w-2/3 h-1 bg-purple-400/60 dark:bg-purple-600 rounded-full"></div>
                        </div>

                        {/* Shine effect */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-gray-700/30 transform -skew-x-12 animate-shine"></div>
                      </div>

                      {/* Arrow pointing from AI to PDF - Removed hover effects but kept static */}
                      <div className="absolute top-1/2 -left-8 transform -translate-y-1/2">
                        <div className="w-12 h-1 bg-blue-400 dark:bg-blue-600 rounded-full"></div>
                        <div className="absolute -right-2 top-1/2 transform -translate-y-1/2 w-0 h-0 border-t-4 border-b-4 border-l-8 border-blue-400 dark:border-blue-600 border-transparent"></div>
                      </div>
                    </div>
                  </div>

                  {/* Background decorative elements */}
                  <div className="absolute -top-8 -left-8 w-16 h-16 bg-blue-200/30 dark:bg-blue-700/30 rounded-full blur-xl"></div>
                  <div className="absolute -bottom-8 -right-8 w-20 h-20 bg-purple-200/30 dark:bg-purple-700/30 rounded-full blur-xl"></div>
                  <div className="absolute top-20 right-4 w-8 h-8 bg-cyan-300/40 dark:bg-cyan-600/40 rounded-full"></div>
                  <div className="absolute bottom-12 left-0 w-6 h-6 bg-pink-300/40 dark:bg-pink-600/40 rounded-full"></div>
                </div>
              </div>

              {/* Steps Section */}
              <div className="space-y-8">
                <div className="space-y-6">
                  {[
                    "Import or drag and drop your file into the AI PDF Summarizer above.",
                    "Review the provided overview of your document.",
                    "Use the 'Suggested questions' to dive deeper into any topic.",
                    "Ask our AI chat anything for instant insights.",
                    "Copy or download your summary to use however you need."
                  ].map((step, index) => (
                    <div key={index} className="flex items-start space-x-5 group">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                        {index + 1}
                      </div>
                      <p className="text-gray-700 dark:text-gray-300 text-lg leading-relaxed group-hover:text-gray-900 dark:group-hover:text-white group-hover:translate-x-1 transition-all duration-300">
                        {step}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom animations */}
      <style jsx>{`
        @keyframes shine {
          0% { left: -100%; }
          100% { left: 100%; }
        }
        .animate-shine {
          animation: shine 2s ease-in-out infinite;
        }
      `}</style>
    </section>
  );
};

export default Steps;