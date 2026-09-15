export interface Prestataire {
  id: string;
  name: string;
  specialty: string;
  description: string;
  services: string[];
  city: string;
  country: string;
  hourly_rate: number;
  phone: string;
  email: string;
  rating: number;
  image_base64: string;
  created_at: string;
}

export interface SearchResult {
  prestataire: Prestataire;
  similarity_score: number;
}

export interface SearchRequest {
  text?: string;
  image_base64?: string;
}
