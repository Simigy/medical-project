"use client"

import { useState, useEffect, useRef } from "react"
import { Terminal, XCircle } from "lucide-react"

interface SearchLogsProps {
  logs: string[]
  isVisible: boolean
  onClose: () => void
}

export default function SearchLogs({ logs, isVisible, onClose }: SearchLogsProps) {
  const logsEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to the bottom when new logs are added
  useEffect(() => {
    if (isVisible && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [logs, isVisible])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Terminal size={20} className="mr-2 text-gray-500" />
            Batch Search Logs
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500 focus:outline-none"
          >
            <XCircle size={24} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 bg-gray-900 text-gray-200 font-mono text-sm">
          {logs.length === 0 ? (
            <div className="text-gray-500 italic">No logs available</div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">
                {log.startsWith("ERROR:") ? (
                  <span className="text-red-400">{log}</span>
                ) : log.startsWith("WARNING:") ? (
                  <span className="text-yellow-400">{log}</span>
                ) : log.includes("Found") ? (
                  <span className="text-green-400">{log}</span>
                ) : (
                  <span>{log}</span>
                )}
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
        
        <div className="p-3 bg-gray-100 border-t flex justify-between items-center">
          <div className="text-sm text-gray-500">
            {logs.length} log entries
          </div>
          <button
            onClick={() => {
              const logText = logs.join("\n")
              const blob = new Blob([logText], { type: "text/plain" })
              const url = URL.createObjectURL(blob)
              const a = document.createElement("a")
              a.href = url
              a.download = `batch-search-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.txt`
              document.body.appendChild(a)
              a.click()
              document.body.removeChild(a)
              URL.revokeObjectURL(url)
            }}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            Download Logs
          </button>
        </div>
      </div>
    </div>
  )
}
