import { useState, useEffect } from "react";
import ChatInterface from "./components/ChatInterface";
import ProviderForm from "./components/ProviderForm";
import { getPrestataires } from "./services/api";
import type { Prestataire } from "./types";

type Tab = "search" | "admin";

export default function App() {
  const [tab, setTab] = useState<Tab>("search");
  const [prestataires, setPrestataires] = useState<Prestataire[]>([]);
  const [editingProvider, setEditingProvider] = useState<Prestataire | null>(null);

  const fetchPrestataires = () => {
    getPrestataires().then(setPrestataires).catch(console.error);
  };

  useEffect(() => {
    fetchPrestataires();
  }, []);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <h1 className="text-xl font-bold text-gray-900">PrestaSearch</h1>
        <nav className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setTab("search")}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === "search"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Search
          </button>
          <button
            onClick={() => setTab("admin")}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === "admin"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Admin
          </button>
        </nav>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-hidden">
        {tab === "search" ? (
          <ChatInterface />
        ) : (
          <div className="h-full overflow-y-auto">
            <div className="max-w-5xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Form */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    {editingProvider ? "Edit provider" : "Add provider"}
                  </h2>
                  <ProviderForm
                    onPrestaAdded={fetchPrestataires}
                    editingProvider={editingProvider}
                    onCancelEdit={() => setEditingProvider(null)}
                  />
                </div>
              </div>

              {/* Directory */}
              <div className="lg:col-span-2">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Directory
                  </h2>
                  <span className="text-sm text-gray-500">
                    {prestataires.length} providers
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {prestataires.map((p) => (
                    <div
                      key={p.id}
                      className={`bg-white rounded-lg shadow-sm border p-4 ${
                        editingProvider?.id === p.id
                          ? "border-amber-400 ring-2 ring-amber-200"
                          : "border-gray-200"
                      }`}
                    >
                      <div className="flex gap-3">
                        {p.image_base64 ? (
                          <img
                            src={`data:image/jpeg;base64,${p.image_base64}`}
                            alt={p.name}
                            className="w-16 h-16 object-cover rounded"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-gray-100 rounded flex items-center justify-center text-gray-400 text-xl shrink-0">
                            ?
                          </div>
                        )}
                        <div className="min-w-0 flex-1">
                          <h3 className="font-medium text-gray-900 text-sm truncate">
                            {p.name}
                          </h3>
                          <p className="text-blue-600 text-xs font-medium">
                            {p.specialty}
                          </p>
                          <p className="text-gray-500 text-xs mt-0.5">
                            {p.city}{p.country ? `, ${p.country}` : ""}
                          </p>
                          {p.hourly_rate > 0 && (
                            <p className="text-gray-700 font-bold text-sm mt-1">
                              {p.hourly_rate.toFixed(0)} $/h
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => setEditingProvider(p)}
                          className="self-start text-gray-400 hover:text-amber-600 transition-colors p-1"
                          title="Edit"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                            <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
