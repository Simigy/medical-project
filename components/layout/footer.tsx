import Link from "next/link"
import { ExternalLink, Info, Shield, Github } from "lucide-react"

export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-3">MedSearch</h3>
            <p className="text-gray-300 text-sm">
              Advanced search portal for medical and pharmaceutical databases. Find specific active ingredients across
              multiple trusted sources.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Supported Databases</h3>
            <ul className="text-gray-300 text-sm space-y-2">
              <li className="flex items-center">
                <ExternalLink size={14} className="mr-1" />
                <a
                  href="https://pubmed.ncbi.nlm.nih.gov/"
                  className="hover:text-blue-300 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  PubMed
                </a>
              </li>
              <li className="flex items-center">
                <ExternalLink size={14} className="mr-1" />
                <a
                  href="https://go.drugbank.com/"
                  className="hover:text-blue-300 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  DrugBank
                </a>
              </li>
              <li className="flex items-center">
                <ExternalLink size={14} className="mr-1" />
                <a
                  href="https://clinicaltrials.gov/"
                  className="hover:text-blue-300 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  ClinicalTrials.gov
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3">Resources</h3>
            <ul className="text-gray-300 text-sm space-y-2">
              <li className="flex items-center">
                <Info size={14} className="mr-1" />
                <Link href="/about" className="hover:text-blue-300 transition-colors">
                  About
                </Link>
              </li>
              <li className="flex items-center">
                <Shield size={14} className="mr-1" />
                <Link href="/privacy" className="hover:text-blue-300 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li className="flex items-center">
                <Github size={14} className="mr-1" />
                <a
                  href="https://github.com/"
                  className="hover:text-blue-300 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub Repository
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-4 border-t border-gray-700 text-center">
          <p className="text-sm text-gray-400">© {new Date().getFullYear()} MedSearch. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
