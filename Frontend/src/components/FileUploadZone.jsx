import React, { useState, useCallback } from "react";
import { FileText, Upload, ChevronDown } from "lucide-react";

// ✅ simple cn utility to merge class names
function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function FileUploadZone({
  onFilesSelected,
  maxFiles = 10,
  acceptedTypes = [".pdf", ".doc", ".docx", ".txt"],
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileSelect = useCallback((e) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  }, []);

  const handleFiles = (files) => {
    const validFiles = files.slice(0, maxFiles);
    setSelectedFiles(validFiles);
    if (onFilesSelected) {
      onFilesSelected(validFiles);
    }
  };

  return (
    <div className="w-full">
      {/* Upload Zone */}
      <div
        className={cn(
          "relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200",
          "bg-gradient-to-br from-[#512DA8] to-[#B39DDB]",
          "border-[#D1C4E9]",
          isDragOver && "border-[#B39DDB] bg-opacity-90"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* PDF Icons */}
        <div className="flex justify-center items-center gap-4 mb-8">
          <div className="relative">
            <FileText className="w-16 h-16 text-white/80" />
            <div className="absolute -top-1 -right-1 bg-white/20 rounded px-1 py-0.5">
              <span className="text-xs text-white font-medium">PDF</span>
            </div>
          </div>
          <div className="relative">
            <FileText className="w-12 h-12 text-white/60" />
            <div className="absolute -top-1 -right-1 bg-white/20 rounded px-1 py-0.5">
              <span className="text-xs text-white font-medium">DOC</span>
            </div>
          </div>
        </div>

        {/* Upload Button */}
        <div className="space-y-4">
          <button
            className="bg-white/90 hover:bg-white text-[#424242] font-medium px-8 py-3 rounded-lg shadow-sm transition-all duration-200 hover:shadow-md flex items-center justify-center"
            onClick={() => document.getElementById("file-input")?.click()}
          >
            <Upload className="w-4 h-4 mr-2" />
            CHOOSE FILES
            <ChevronDown className="w-4 h-4 ml-2" />
          </button>

          <p className="text-white/90 text-lg">or drop files here</p>
        </div>

        {/* Hidden File Input */}
        <input
          id="file-input"
          type="file"
          multiple
          accept={acceptedTypes.join(",")}
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Selected Files Display */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 p-4 bg-white rounded-lg border border-[#D1C4E9]">
          <h3 className="font-medium text-[#424242] mb-2">Selected Files:</h3>
          <ul className="space-y-1">
            {selectedFiles.map((file, index) => (
              <li
                key={index}
                className="text-sm text-[#666666] flex items-center gap-2"
              >
                <FileText className="w-4 h-4 text-[#B39DDB]" />
                {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
