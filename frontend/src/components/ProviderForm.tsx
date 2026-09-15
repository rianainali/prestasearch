import { useState, useEffect, type FormEvent } from "react";
import { addPrestataire, updatePrestataire } from "../services/api";
import ImageUploader from "./ImageUploader";
import type { Prestataire } from "../types";

interface Props {
  onPrestaAdded: () => void;
  editingProvider?: Prestataire | null;
  onCancelEdit?: () => void;
}

export default function ProviderForm({ onPrestaAdded, editingProvider, onCancelEdit }: Props) {
  const [name, setName] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [description, setDescription] = useState("");
  const [services, setServices] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [hourlyRate, setHourlyRate] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [imageBase64, setImageBase64] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const isEditing = !!editingProvider;

  useEffect(() => {
    if (editingProvider) {
      setName(editingProvider.name);
      setSpecialty(editingProvider.specialty);
      setDescription(editingProvider.description);
      setServices(editingProvider.services.join(", "));
      setCity(editingProvider.city);
      setCountry(editingProvider.country);
      setHourlyRate(editingProvider.hourly_rate > 0 ? String(editingProvider.hourly_rate) : "");
      setPhone(editingProvider.phone);
      setEmail(editingProvider.email);
      setImageBase64(editingProvider.image_base64 ? `data:image/jpeg;base64,${editingProvider.image_base64}` : "");
      setImageFile(null);
      setMessage("");
    }
  }, [editingProvider]);

  const resetForm = () => {
    setName("");
    setSpecialty("");
    setDescription("");
    setServices("");
    setCity("");
    setCountry("");
    setHourlyRate("");
    setPhone("");
    setEmail("");
    setImageBase64("");
    setImageFile(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name || !specialty || !description) return;

    setLoading(true);
    setMessage("");

    try {
      const form = new FormData();
      form.append("name", name);
      form.append("specialty", specialty);
      form.append("description", description);
      form.append("services", services);
      form.append("city", city);
      form.append("country", country);
      form.append("hourly_rate", hourlyRate || "0");
      form.append("phone", phone);
      form.append("email", email);
      if (imageFile) {
        form.append("image", imageFile);
      }

      if (isEditing && editingProvider) {
        form.append("keep_image", imageFile ? "false" : "true");
        await updatePrestataire(editingProvider.id, form);
        setMessage("Provider successfully updated!");
        setIsSuccess(true);
        onCancelEdit?.();
      } else {
        await addPrestataire(form);
        setMessage("Provider successfully added!");
        setIsSuccess(true);
      }

      resetForm();
      onPrestaAdded();
    } catch {
      setMessage(isEditing ? "Update failed." : "Failed to add provider.");
      setIsSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Name *
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="Provider name"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Specialty *
        </label>
        <input
          type="text"
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
          maxLength={100}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="E.g. Plumbing, Hairdressing, Web development..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description *
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={1000}
          required
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
          placeholder="Describe the services offered"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Services
        </label>
        <input
          type="text"
          value={services}
          onChange={(e) => setServices(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="repair, installation, troubleshooting (comma-separated)"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            City
          </label>
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            placeholder="Paris"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Country
          </label>
          <input
            type="text"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            placeholder="France"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Hourly rate ($)
        </label>
        <input
          type="number"
          value={hourlyRate}
          onChange={(e) => setHourlyRate(e.target.value)}
          min={0}
          step={1}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          placeholder="0"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phone
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            placeholder="+33 6 12 34 56 78"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            placeholder="contact@example.com"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Photo
        </label>
        <ImageUploader
          onImageSelect={(base64, file) => {
            setImageBase64(base64);
            setImageFile(file);
          }}
          preview={imageBase64}
          onClear={() => {
            setImageBase64("");
            setImageFile(null);
          }}
        />
      </div>

      <button
        type="submit"
        disabled={loading || !name || !specialty || !description}
        className={`w-full text-white py-2.5 px-4 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
          isEditing
            ? "bg-amber-600 hover:bg-amber-700"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {loading
          ? isEditing ? "Updating..." : "Adding..."
          : isEditing ? "Update provider" : "Add provider"}
      </button>

      {isEditing && (
        <button
          type="button"
          onClick={() => { resetForm(); onCancelEdit?.(); }}
          className="w-full py-2.5 px-4 rounded-lg font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      )}

      {message && (
        <p
          className={`text-sm text-center ${
            isSuccess ? "text-green-600" : "text-red-600"
          }`}
        >
          {message}
        </p>
      )}
    </form>
  );
}
