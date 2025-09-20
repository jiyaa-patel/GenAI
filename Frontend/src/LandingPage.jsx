import React from "react";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import PDFSummarizer from "./components/PdfSummarizer";
import UploadInterface from "./components/UploadInterface";
import Footer from "./components/Footer";
import WhyChooseUs from "./components/WhyChooseUs";


export default function LandingPage() {
  return (
    <div className="bg-background text-foreground">
      <Navbar />
      <HeroSection />
      <PDFSummarizer />
      <WhyChooseUs />
      <div className="py-20 px-4 bg-light-lavender/20">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-12">
            Try it Yourself
          </h2>
          <UploadInterface />
        </div>
      </div>
      <Footer />
    </div>
  );
}
