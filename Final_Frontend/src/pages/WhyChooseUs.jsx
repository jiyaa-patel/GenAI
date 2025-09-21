import React from 'react';
import { Users, Star, Shield } from 'lucide-react';

const WhyChooseUs = () => {
  const features = [
    {
      icon: Users,
      title: "People Trust Us",
      description: "Over a billion users have used our service to simplify their work with digital documents.",
      highlight: "1B+",
      iconBg: "bg-blue-100 dark:bg-blue-900/20",
      iconColor: "text-blue-600 dark:text-blue-400"
    },
    {
      icon: Star,
      title: "Businesses Trust Us",
      description: "We're one of the highest-rated PDF software on major B2B software listing platforms.",
      highlight: "5★",
      iconBg: "bg-amber-100 dark:bg-amber-900/20",
      iconColor: "text-amber-600 dark:text-amber-400"
    },
    {
      icon: Shield,
      title: "Security Standards",
      description: "Your safety is our priority. ISO/IEC 27001 certified and GDPR, CCPA, and SOC compliant.",
      highlight: "Certified",
      iconBg: "bg-green-100 dark:bg-green-900/20",
      iconColor: "text-green-600 dark:text-green-400"
    },
  ];

  return (
    <section id="why-choose-us" className="w-full">
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 w-full py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">Why Choose PactAI?</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Trusted by millions worldwide for secure, reliable, and efficient PDF summarization
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-100 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-2"
                >
                  <div className="flex flex-col items-center text-center space-y-6">
                    {/* Enhanced Icon with gradient background */}
                    <div className="relative">
                      <div className={`w-20 h-20 ${feature.iconBg} rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300`}>
                        <IconComponent className={`w-10 h-10 ${feature.iconColor}`} />
                      </div>
                      {feature.highlight && (
                        <div className="absolute -top-3 -right-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-bold px-3 py-2 rounded-full shadow-lg">
                          {feature.highlight}
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="space-y-4">
                      <h3 className="text-2xl font-bold text-foreground group-hover:text-primary transition-colors duration-300">
                        {feature.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed text-lg">
                        {feature.description}
                      </p>
                    </div>

                    {/* Decorative element */}
                    <div className="w-16 h-1 bg-gradient-to-r from-primary to-accent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Additional trust indicators */}
        {/* <div className="mt-16 text-center">
          <p className="text-muted-foreground mb-6">Trusted by industry leaders</p>
          <div className="flex justify-center items-center gap-12 flex-wrap opacity-60">
            <div className="text-2xl font-bold text-gray-500 dark:text-gray-400">Capterra</div>
            <div className="text-2xl font-bold text-gray-500 dark:text-gray-400">G2</div>
            <div className="text-2xl font-bold text-gray-500 dark:text-gray-400">TrustPilot</div>
            <div className="text-2xl font-bold text-gray-500 dark:text-gray-400">ISO 27001</div>
          </div>
        </div> */}
        </div>
      </div>
    </section>
  );
};

export default WhyChooseUs;