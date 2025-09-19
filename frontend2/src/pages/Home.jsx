import React from 'react';
import { Link } from 'react-router-dom';
import Steps from './Steps';
import WhyChooseUs from './WhyChooseUs';

const Home = () => {
  return (
    <div className="w-full">
      {/* Hero Section - Full width blue card */}
      <section className="py-16 md:py-24 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center">
            <div className="md:w-1/2 mb-10 md:mb-0">
              <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-6">
                Transform Lengthy Legal Doucments into <span className="text-primary">Concise Summaries</span>
              </h1>
              <p className="text-xl text-foreground mb-8">
                Save time and extract key information from your documents with our AI-powered Legal summarization tool.
              </p>
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <Link
                  to="/signup"
                  className="inline-flex items-center justify-center px-8 py-3 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-xl dark:from-blue-700 dark:to-purple-700 dark:hover:from-blue-800 dark:hover:to-purple-800"
                >
                  Get Started
                  <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </Link>
              </div>
            </div>
            <div className="md:w-1/2 flex justify-center">
              <div className="relative">
                <div className="bg-primary bg-opacity-10 rounded-2xl p-8 transform rotate-3 w-full max-w-md">
                  <div className="bg-white dark:bg-card rounded-xl shadow-lg p-6 transform -rotate-3">
                    <h3 className="text-xl font-semibold text-foreground mb-4">Document Summary</h3>
                    <div className="space-y-3">
                      <div className="h-4 bg-secondary rounded-full w-3/4"></div>
                      <div className="h-4 bg-secondary rounded-full"></div>
                      <div className="h-4 bg-secondary rounded-full w-5/6"></div>
                      <div className="h-4 bg-secondary rounded-full w-4/5"></div>
                      <div className="h-4 bg-secondary rounded-full w-2/3"></div>
                    </div>
                    <div className="mt-6 pt-4 border-t border-border flex justify-between items-center">
                      <span className="text-sm text-foreground">Summary generated in 12 seconds</span>
                      <button className="text-primary text-sm font-medium">Copy Summary</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Steps Component */}
      <Steps />

      {/* Why Choose Us Component */}
      <WhyChooseUs />
    </div>
  );
};

export default Home;