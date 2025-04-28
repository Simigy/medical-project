"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Search, Heart, Clock, Settings, Menu } from "lucide-react"

export default function Header() {
  const pathname = usePathname()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  const navItems = [
    { path: "/", label: "Search", icon: <Search size={18} /> },
    { path: "/favorites", label: "Favorites", icon: <Heart size={18} /> },
    { path: "/history", label: "History", icon: <Clock size={18} /> },
    { path: "/settings", label: "Settings", icon: <Settings size={18} /> },
  ]

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="text-blue-600 mr-2">
                <svg
                  viewBox="0 0 24 24"
                  width="28"
                  height="28"
                  stroke="currentColor"
                  strokeWidth="2"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M8.5 2H5.5C3.6 2 2 3.6 2 5.5V8.5C2 10.4 3.6 12 5.5 12H8.5C10.4 12 12 10.4 12 8.5V5.5C12 3.6 10.4 2 8.5 2Z"></path>
                  <path d="M18.5 2H15.5C13.6 2 12 3.6 12 5.5V8.5C12 10.4 13.6 12 15.5 12H18.5C20.4 12 22 10.4 22 8.5V5.5C22 3.6 20.4 2 18.5 2Z"></path>
                  <path d="M8.5 12H5.5C3.6 12 2 13.6 2 15.5V18.5C2 20.4 3.6 22 5.5 22H8.5C10.4 22 12 20.4 12 18.5V15.5C12 13.6 10.4 12 8.5 12Z"></path>
                  <path d="M18.5 12H15.5C13.6 12 12 13.6 12 15.5V18.5C12 20.4 13.6 22 15.5 22H18.5C20.4 22 22 20.4 22 18.5V15.5C22 13.6 20.4 12 18.5 12Z"></path>
                </svg>
              </div>
              <span className="font-bold text-xl text-gray-800">MedSearch</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                href={item.path}
                className={`flex items-center text-sm font-medium transition-colors duration-200 ${
                  pathname === item.path
                    ? "text-blue-600 border-b-2 border-blue-600"
                    : "text-gray-600 hover:text-blue-600"
                }`}
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button onClick={toggleMenu} className="text-gray-600 hover:text-blue-600 focus:outline-none">
              <Menu size={24} />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    pathname === item.path
                      ? "text-blue-600 bg-blue-50"
                      : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span className="mr-3">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
