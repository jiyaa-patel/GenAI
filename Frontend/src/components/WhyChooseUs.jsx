// src/components/WhyChooseUs.jsx
import React from "react";
import { Users, Star, Shield } from "lucide-react";

export default function WhyChooseUs() {
  const features = [
    {
      icon: Users,
      title: "People Trust Us",
      description:
        "Over a billion users have used our service to simplify their work with digital documents.",
      highlight: "1+ billion",
    },
    {
      icon: Star,
      title: "Businesses Trust Us",
      description:
        "We're one of the highest-rated PDF software on major B2B software listing platforms: Capterra, G2, and TrustPilot.",
      highlight: "5 stars",
    },
    {
      icon: Shield,
      title: "Security Standards",
      description:
        "Your safety is our priority. PactAI is ISO/IEC 27001 certified and GDPR, CCPA, and SOC compliant.",
      highlight: "Certified",
    },
  ];

  return (
    <section id="why-choose-us" className="py-20 px-4 bg-muted/30">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Why Choose PactAI?
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <div
                key={index}
                className="bg-card rounded-lg p-8 shadow-sm border border-border hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col items-center text-center space-y-4">
                  {/* Icon with highlight badge */}
                  <div className="relative">
                    <div className="w-16 h-16 bg-digital-lavender/20 rounded-full flex items-center justify-center mb-2">
                      <IconComponent className="w-8 h-8 text-deep-purple" />
                    </div>
                    {feature.highlight && (
                      <div className="absolute -top-2 -right-2 bg-sage-green text-white text-xs font-bold px-2 py-1 rounded-full">
                        {feature.highlight}
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="space-y-3">
                    <h3 className="text-xl font-semibold text-foreground">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
