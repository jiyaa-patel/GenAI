// import React from "react";
// import { Link } from "react-router-dom";
// import { ArrowRight } from "lucide-react";

// export function HeroSection() {
//   return (
//     <section id="home" className="relative bg-background py-24 px-4 overflow-hidden">
//       {/* Background and decorative elements */}
//       <div className="absolute inset-0 bg-gradient-to-br from-light-lavender/20 to-digital-lavender/10"></div>
//       <div className="absolute top-20 left-10 w-16 h-16 bg-digital-lavender/20 rounded-full blur-xl"></div>
//       <div className="absolute top-40 right-20 w-24 h-24 bg-sage-green/20 rounded-full blur-xl"></div>
//       <div className="absolute bottom-20 left-1/4 w-20 h-20 bg-light-lavender/30 rounded-full blur-xl"></div>

//       <div className="relative max-w-7xl mx-auto text-center">
//         {/* Main content */}
//         <div className="relative z-10 max-w-4xl mx-auto">
//           <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight">
//             Clarity{" "}
//             <span className="text-primary">
//               in seconds
//             </span>
//           </h1>

//           <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
//             No more confusing fine print. With one click, our AI makes legal documents simple, transparent, and stress-free for everyone.
//           </p>

//           <div className="flex flex-col items-center space-y-4 pb-8">
//             {/* Use Link instead of <a> */}
//             <Link to="/login">
//               <button className="bg-deep-purple hover:bg-deep-purple/90 text-white px-8 py-6 text-lg font-semibold rounded-full shadow-lg hover:shadow-xl transition-all duration-300 group">
//                 Get Started
//                 <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
//               </button>
//             </Link>

//             <p className="text-sm text-muted-foreground">Simplify legal docs. Just sign up.</p>
//           </div>
//         </div>
//       </div>
//     </section>
//   );
// }

// export default HeroSection;

// import React from 'react';
// // import './global.scss'; // Assuming this is your main SCSS file

// const HeroSection = () => {
//   return (
//     <div className="hero-section">
//       <div className="hero-content">
//         <h1 className="hero-title">
//           Clarity <span className="fade-in-text">in seconds</span>
//         </h1>
//         <p className="hero-subtitle">
//           No more confusing fine print. With one click, our AI makes legal
//           documents simple, transparent, and stress-free for everyone.
//         </p>
//         <button className="get-started-button">
//           Get Started <span className="arrow">→</span>
//         </button>
//         <p className="signup-text">
//           Simplify legal docs. Just sign up.
//         </p>
//       </div>
//       <div className="card-container">
//         <div className="card fade-in-card left">
//           <div className="card-icon">
//             <i className="fas fa-magic"></i>
//           </div>
//           <p className="card-text">No More Legal Confusion</p>
//           <p className="card-subtitle">Smart summaries at your fingertips</p>
//         </div>
//         <div className="card fade-in-card right">
//           <div className="card-icon">
//             <i className="fas fa-gavel"></i>
//           </div>
//           <p className="card-text">Law, Made Simple</p>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default HeroSection;

import React from 'react';
// import './global.scss'; // Assuming this is your main SCSS file

const HeroSection = () => {
  return (
    <div className="hero-section">
      <div className="hero-content">
        <h1 className="hero-title">
          Clarity <span className="fade-in-text">in seconds</span>
        </h1>
        <p className="hero-subtitle">
          No more confusing fine print. With one click, our AI makes legal
          documents simple, transparent, and stress-free for everyone.
        </p>
        <button className="get-started-button">
          Get Started <span className="arrow">→</span>
        </button>
        <p className="signup-text">
          Simplify legal docs. Just sign up.
        </p>
      </div>
      <div className="card-container">
        <div className="card fade-in-card">
          <div className="card-icon">
            <i className="fas fa-magic"></i>
          </div>
          <p className="card-text">No More Legal Confusion</p>
          <p className="card-subtitle">Smart summaries at your fingertips</p>
        </div>
        <div className="card fade-in-card right-card">
          <div className="ai-icon">
            AI
          </div>
          <p className="card-text">Law, Made Simple</p>
          <div className="processing-bar">
            Processing...
            <div className="progress-bar"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;