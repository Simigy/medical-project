export default function FavoritesPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Saved Favorites</h1>
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
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-700 mb-1">No favorites yet</h3>
          <p className="text-gray-500">Save search results to access them quickly later.</p>
        </div>
      </div>
    </div>
  )
}
