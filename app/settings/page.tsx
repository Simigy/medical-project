export default function SettingsPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Settings</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-3">Search Preferences</h2>
            <div className="space-y-4">
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    defaultChecked
                  />
                  <span className="ml-2 text-gray-700">Save search history</span>
                </label>
              </div>
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    defaultChecked
                  />
                  <span className="ml-2 text-gray-700">Open results in new tab</span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-3">Default Databases</h2>
            <div className="space-y-4">
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    defaultChecked
                  />
                  <span className="ml-2 text-gray-700">PubMed</span>
                </label>
              </div>
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-gray-700">DrugBank</span>
                </label>
              </div>
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-gray-700">ClinicalTrials.gov</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
