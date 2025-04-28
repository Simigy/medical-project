export default function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">About MedSearch</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="prose max-w-none">
          <p>
            MedSearch is an advanced search portal designed for medical professionals, researchers, and students to
            quickly find information about active ingredients across multiple trusted medical and pharmaceutical
            databases.
          </p>

          <h2>Our Mission</h2>
          <p>
            Our mission is to simplify the process of searching for medical information by providing a unified interface
            to query multiple databases simultaneously. This saves valuable time and ensures comprehensive results.
          </p>

          <h2>Supported Databases</h2>
          <ul>
            <li>
              <strong>PubMed</strong> - Access to more than 33 million citations for biomedical literature.
            </li>
            <li>
              <strong>DrugBank</strong> - A comprehensive, freely accessible, online database containing information on
              drugs and drug targets.
            </li>
            <li>
              <strong>ClinicalTrials.gov</strong> - A database of privately and publicly funded clinical studies
              conducted around the world.
            </li>
          </ul>

          <h2>Privacy & Data</h2>
          <p>
            MedSearch does not store any personal health information. Search queries are processed securely and are not
            shared with third parties. For more information, please see our Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  )
}
