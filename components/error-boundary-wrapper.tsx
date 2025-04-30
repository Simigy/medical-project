'use client'

import dynamic from 'next/dynamic'
import React from 'react'

// Dynamically import the ErrorBoundary component with SSR disabled
const ErrorBoundary = dynamic(
  () => import("@/components/error-boundary"),
  { ssr: false }
)

export default function ErrorBoundaryWrapper({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
  )
}
