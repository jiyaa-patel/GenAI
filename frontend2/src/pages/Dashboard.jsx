import React, { useState } from 'react';

const Dashboard = () => {
  const [files, setFiles] = useState([
    { id: 1, name: 'Research Paper.pdf', date: '2023-04-15', status: 'Completed' },
    { id: 2, name: 'Business Report.pdf', date: '2023-04-10', status: 'Completed' },
    { id: 3, name: 'Technical Documentation.pdf', date: '2023-04-05', status: 'Processing' },
  ]);

  const handleFileUpload = (e) => {
    e.preventDefault();
    // Handle file upload logic here
    alert('File upload functionality would be implemented here');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-foreground">Manage your PDF summaries and upload new documents</p>
      </div>

      {/* Upload Section */}
      <div className="card mb-12">
        <h2 className="text-2xl font-semibold text-foreground mb-6">Upload New PDF</h2>
        <div className="border-2 border-dashed border-primary border-opacity-30 rounded-2xl p-8 text-center bg-primary bg-opacity-5 hover:bg-opacity-10 transition-all duration-300 cursor-pointer mb-6">
          <div className="max-w-md mx-auto">
            <svg className="mx-auto h-12 w-12 text-primary mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-lg font-medium text-foreground mb-2">Drag and drop your PDF here</p>
            <p className="text-foreground mb-4">or</p>
            <button className="btn-primary">Select File</button>
            <p className="text-sm text-foreground mt-4">PDF files up to 100MB</p>
          </div>
        </div>
        <form onSubmit={handleFileUpload} className="mt-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-foreground mb-2" htmlFor="summary-type">
              Summary Type
            </label>
            <select id="summary-type" className="input-field">
              <option>Key Points</option>
              <option>Detailed Summary</option>
              <option>Bullet Points</option>
              <option>Executive Summary</option>
            </select>
          </div>
          <button type="submit" className="btn-primary w-full">
            Process Document
          </button>
        </form>
      </div>

      {/* Recent Files Section */}
      <div>
        <h2 className="text-2xl font-semibold text-foreground mb-6">Recent Files</h2>
        <div className="bg-card rounded-xl shadow-md overflow-hidden">
          {files.length > 0 ? (
            <ul className="divide-y divide-border">
              {files.map((file) => (
                <li key={file.id} className="p-4 hover:bg-secondary hover:bg-opacity-10 transition-colors duration-300">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="bg-primary bg-opacity-10 p-3 rounded-lg mr-4">
                        <svg className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="font-medium text-foreground">{file.name}</h3>
                        <p className="text-sm text-foreground">Uploaded on {file.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium mr-4 ${
                        file.status === 'Completed' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' 
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                      }`}>
                        {file.status}
                      </span>
                      <button className="text-primary hover:text-accent transition-colors duration-300">
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-8 text-center">
              <svg className="mx-auto h-12 w-12 text-foreground opacity-50 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-foreground">No files uploaded yet.</p>
              <p className="text-foreground">Upload your first PDF to get started.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;