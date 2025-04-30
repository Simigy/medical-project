// This is a basic server component with no client-side functionality
export default function BasicPage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333' }}>Basic Test Page</h1>
      <p style={{ color: '#666' }}>This is a very basic Next.js page with no client components.</p>
      <p>Current time on server: {new Date().toLocaleTimeString()}</p>
    </div>
  )
}
