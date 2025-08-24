import React from "react";
import { Check } from "lucide-react";

const features = [
  "Summarize PDF files on Mac, Windows, and Linux",
  "Trusted by 1.7 billion people since 2013",
  "Free and easy to use—no installation required",
];

export default function FeatureList() {
  return (
    <div className="space-y-4">
      {features.map((feature, index) => (
        <div key={index} className="flex items-start gap-3">
          <div className="flex-shrink-0 w-6 h-6 rounded-full bg-[#A5D6A7] flex items-center justify-center mt-0.5">
            <Check className="w-4 h-4 text-white" />
          </div>
          <p className="text-[#424242] text-lg leading-relaxed">{feature}</p>
        </div>
      ))}
    </div>
  );
}
