import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-card border-t border-border mt-auto">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-xl font-bold text-primary mb-4">PDFSummarizer</h3>
            <p className="text-foreground max-w-md">
              Transform lengthy PDF documents into concise, actionable summaries with our AI-powered tool.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4">Navigation</h4>
            <ul className="space-y-2">
              <li><Link to="/" className="text-foreground hover:text-primary transition-colors duration-300">Home</Link></li>
              <li><Link to="/dashboard" className="text-foreground hover:text-primary transition-colors duration-300">Dashboard</Link></li>
              <li><Link to="/login" className="text-foreground hover:text-primary transition-colors duration-300">Login</Link></li>
              <li><Link to="/signup" className="text-foreground hover:text-primary transition-colors duration-300">Sign Up</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4">Legal</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-foreground hover:text-primary transition-colors duration-300">Privacy Policy</a></li>
              <li><a href="#" className="text-foreground hover:text-primary transition-colors duration-300">Terms of Service</a></li>
              <li><a href="#" className="text-foreground hover:text-primary transition-colors duration-300">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-border text-center text-foreground">
          <p>&copy; {new Date().getFullYear()} PactAI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;