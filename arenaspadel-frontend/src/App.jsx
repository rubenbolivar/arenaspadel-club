import { useState } from 'react'
import PaymentPage from './pages/PaymentPage'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-800">
            Arenas Padel Club
          </h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <PaymentPage />
      </main>

      <footer className="bg-white border-t mt-auto">
        <div className="container mx-auto px-4 py-4 text-center text-gray-600">
          © 2024 Arenas Padel Club. Todos los derechos reservados.
        </div>
      </footer>
    </div>
  )
}

export default App
