import type { Prestataire, SearchResult } from "../types";

const BASE = "/api";

export async function getPrestataires(): Promise<Prestataire[]> {
  const res = await fetch(`${BASE}/prestataires`);
  if (!res.ok) throw new Error("Failed to fetch prestataires");
  return res.json();
}

export async function addPrestataire(form: FormData): Promise<string> {
  const res = await fetch(`${BASE}/prestataires`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Failed to add prestataire");
  const data = await res.json();
  return data.prestataire_id;
}

export async function updatePrestataire(
  id: string,
  form: FormData
): Promise<string> {
  const res = await fetch(`${BASE}/prestataires/${id}`, {
    method: "PUT",
    body: form,
  });
  if (!res.ok) throw new Error("Failed to update prestataire");
  const data = await res.json();
  return data.prestataire_id;
}

export async function searchPrestataires(
  text?: string,
  imageBase64?: string
): Promise<SearchResult[]> {
  const res = await fetch(`${BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, image_base64: imageBase64 }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.detail || "Search failed.");
  }
  return res.json();
}
