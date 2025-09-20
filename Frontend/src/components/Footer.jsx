import React from "react";
import { Link } from "react-router-dom";
import { Mail, Phone, Twitter, Linkedin, Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-deep-purple text-white">
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* About Section */}
          <div className="lg:col-span-1">
            <h3 className="text-lg font-semibold mb-4">About PDF Summarizer</h3>
            <p className="text-light-lavender mb-4 text-sm leading-relaxed">
              AI-powered document summarization and analysis assistance for professionals and students worldwide.
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span className="text-light-lavender">support@pdfsummarizer.com</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span className="text-light-lavender">+1 (555) 123-4567</span>
              </div>
            </div>
          </div>

          {/* Services / Support / Legal / Resources remain the same */}
          {/* ... your other sections unchanged ... */}

        </div>

        {/* Bottom Section */}
        <div className="border-t border-digital-lavender/20 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Social Links (external) */}
            <div className="flex space-x-4">
              <a
                href="https://twitter.com"
                className="w-8 h-8 bg-digital-lavender/20 rounded-full flex items-center justify-center hover:bg-digital-lavender/30 transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Twitter className="w-4 h-4" />
              </a>
              <a
                href="https://linkedin.com"
                className="w-8 h-8 bg-digital-lavender/20 rounded-full flex items-center justify-center hover:bg-digital-lavender/30 transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Linkedin className="w-4 h-4" />
              </a>
              <a
                href="https://github.com"
                className="w-8 h-8 bg-digital-lavender/20 rounded-full flex items-center justify-center hover:bg-digital-lavender/30 transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Github className="w-4 h-4" />
              </a>
            </div>

            {/* Internal navigation */}
            <div className="flex space-x-4">
              <Link to="/login" className="text-sm hover:text-white">
                Login
              </Link>
              <Link to="/signup" className="text-sm bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
                Sign Up
              </Link>
            </div>

            {/* Copyright */}
            <div className="text-sm text-light-lavender">
              © 2025 PDF Summarizer. All rights reserved.
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
