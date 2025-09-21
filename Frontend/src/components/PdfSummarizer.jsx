import React from "react";

export default function PDFSummarizer() {
  return (
    <section id="pdf-summarizer" className="py-20 px-4 bg-light-lavender/20">
      <div className="max-w-7xl mx-auto">
        <div className="space-y-12">
          {/* Header */}
          <div className="text-center">
            <h2 className="text-4xl md:text-5xl font-bold text-dark-charcoal mb-2">
              How To Summarize a PDF with AI
            </h2>
          </div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Illustration Section */}
            <div className="flex justify-center">
              <div className="relative">
                <div className="flex items-center space-x-8">
                  {/* Cute paper character with glasses */}
                  <div className="relative">
                    <div className="w-32 h-40 bg-white rounded-lg border-2 border-dark-charcoal transform -rotate-12 shadow-lg">
                      <div className="absolute top-6 left-1/2 transform -translate-x-1/2">
                        {/* Eyes with glasses */}
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-white border-2 border-dark-charcoal rounded-full flex items-center justify-center">
                            <div className="w-3 h-3 bg-dark-charcoal rounded-full"></div>
                          </div>
                          <div className="w-8 h-8 bg-white border-2 border-dark-charcoal rounded-full flex items-center justify-center">
                            <div className="w-3 h-3 bg-dark-charcoal rounded-full"></div>
                          </div>
                        </div>
                        {/* Glasses bridge */}
                        <div className="w-4 h-0.5 bg-dark-charcoal mx-auto mt-1"></div>
                        {/* Nose */}
                        <div className="w-1 h-2 bg-dark-charcoal mx-auto mt-2 rounded-full"></div>
                      </div>
                      {/* Pen in hand */}
                      <div className="absolute -right-2 top-16 w-1 h-12 bg-sage-green transform rotate-45"></div>
                      <div className="absolute -right-1 top-14 w-2 h-2 bg-digital-lavender rounded-full"></div>
                    </div>
                    {/* Shadow */}
                    <div className="absolute -bottom-2 left-2 w-28 h-6 bg-digital-lavender/30 rounded-full blur-sm"></div>
                  </div>

                  {/* PDF Document */}
                  <div className="relative">
                    <div className="w-24 h-32 bg-digital-lavender rounded-lg shadow-lg">
                      <div className="p-3 space-y-2">
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 bg-white rounded text-xs flex items-center justify-center font-bold text-digital-lavender">
                            PDF
                          </div>
                        </div>
                        <div className="space-y-1">
                          <div className="w-full h-1 bg-deep-purple/40 rounded"></div>
                          <div className="w-3/4 h-1 bg-deep-purple/40 rounded"></div>
                          <div className="w-full h-1 bg-deep-purple/40 rounded"></div>
                          <div className="w-1/2 h-1 bg-deep-purple/40 rounded"></div>
                        </div>
                      </div>
                    </div>
                    {/* Shadow */}
                    <div className="absolute -bottom-2 left-2 w-20 h-4 bg-digital-lavender/30 rounded-full blur-sm"></div>
                  </div>
                </div>

                {/* Decorative elements */}
                <div className="absolute -top-4 -left-4 w-3 h-3 bg-sage-green rounded-full"></div>
                <div className="absolute -top-2 right-8 w-2 h-2 bg-digital-lavender rounded-full"></div>
                <div className="absolute -bottom-4 right-4 text-2xl text-sage-green">+</div>
                <div className="absolute top-8 -right-8 text-xl text-digital-lavender">×</div>
              </div>
            </div>

            {/* Steps Section */}
            <div className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-deep-purple text-white rounded-full flex items-center justify-center font-bold">
                    1
                  </div>
                  <p className="text-dark-charcoal text-lg">
                    Import or drag and drop your file into the AI PDF Summarizer above.
                  </p>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-deep-purple text-white rounded-full flex items-center justify-center font-bold">
                    2
                  </div>
                  <p className="text-dark-charcoal text-lg">
                    Review the provided overview of your document.
                  </p>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-deep-purple text-white rounded-full flex items-center justify-center font-bold">
                    3
                  </div>
                  <p className="text-dark-charcoal text-lg">
                    Use the 'Suggested questions' to dive deeper into any topic.
                  </p>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-deep-purple text-white rounded-full flex items-center justify-center font-bold">
                    4
                  </div>
                  <p className="text-dark-charcoal text-lg">
                    Ask our AI chat anything for instant insights.
                  </p>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-deep-purple text-white rounded-full flex items-center justify-center font-bold">
                    5
                  </div>
                  <p className="text-dark-charcoal text-lg">
                    Copy or download your summary to use however you need.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
