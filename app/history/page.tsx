export default function HistoryPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Search History</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-8">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-16 w-16 mx-auto text-gray-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-700 mb-1">No search history</h3>
          <p className="text-gray-500">Your recent searches will appear here.</p>
        </div>
      </div>
    </div>
  )
}
