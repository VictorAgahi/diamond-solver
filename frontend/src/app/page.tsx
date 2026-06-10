"use client";

import { useState, useRef } from "react";

export default function Home() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{ part1: number; part2: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      setResults(data);
    } catch {
      setError("An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 flex flex-col items-center justify-center p-8 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-violet-900/20 via-slate-900 to-sky-900/20">
      <div className="w-full max-w-2xl z-10 space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold bg-gradient-to-br from-violet-300 to-violet-600 bg-clip-text text-transparent">
            Diamond Solver Pro
          </h1>
          <p className="text-slate-400 text-lg">
            Upload your seed.txt to calculate maximum diamonds
          </p>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            relative overflow-hidden cursor-pointer
            border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 ease-out backdrop-blur-xl
            ${isDragOver 
              ? "border-violet-500 bg-slate-800/90 shadow-[0_10px_40px_rgba(139,92,246,0.3)] -translate-y-1" 
              : "border-slate-600/50 bg-slate-800/50 hover:border-violet-500 hover:bg-slate-800/80 hover:-translate-y-1 hover:shadow-[0_10px_30px_rgba(139,92,246,0.2)]"}
          `}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".txt"
          />
          <div className="space-y-4">
            <div className="text-6xl animate-[bounce_3s_ease-in-out_infinite]">💎</div>
            <h3 className="text-2xl font-medium text-slate-200">Drag & Drop your seed.txt here</h3>
            <p className="text-slate-400">or click to browse</p>
          </div>
        </div>

        {loading && (
          <div className="flex justify-center py-8">
            <div className="w-12 h-12 border-4 border-slate-600/50 border-t-violet-500 rounded-full animate-spin"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-center backdrop-blur-sm">
            {error}
          </div>
        )}

        {results && (
          <div className="bg-slate-800/70 border border-slate-700 rounded-2xl p-8 backdrop-blur-xl shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-6 border-b border-slate-700/50">
                <span className="text-slate-400 text-lg">Part 1 Score</span>
                <span className="text-4xl font-bold text-sky-400">{results.part1}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-lg">Part 2 Score</span>
                <span className="text-4xl font-bold text-sky-400">{results.part2}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
