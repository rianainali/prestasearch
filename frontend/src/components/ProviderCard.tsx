import type { SearchResult } from "../types";

interface Props {
  result: SearchResult;
}

function scoreColor(score: number): string {
  if (score >= 0.8) return "bg-green-100 text-green-800";
  if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

export default function ProviderCard({ result }: Props) {
  const { prestataire, similarity_score } = result;
  const pct = Math.round(similarity_score * 100);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col">
      {prestataire.image_base64 ? (
        <img
          src={`data:image/jpeg;base64,${prestataire.image_base64}`}
          alt={prestataire.name}
          className="w-full h-40 object-cover"
        />
      ) : (
        <div className="w-full h-40 bg-gray-100 flex items-center justify-center text-gray-400 text-4xl">
          ?
        </div>
      )}
      <div className="p-4 flex flex-col flex-1">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">
            {prestataire.name}
          </h3>
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded-full shrink-0 ${scoreColor(
              similarity_score
            )}`}
          >
            {pct}%
          </span>
        </div>
        <p className="text-xs font-medium text-blue-600 mb-1">
          {prestataire.specialty}
        </p>
        {prestataire.city && (
          <p className="text-xs text-gray-500 mb-2">
            {prestataire.city}{prestataire.country ? `, ${prestataire.country}` : ""}
          </p>
        )}
        <p className="text-gray-600 text-xs mb-3 line-clamp-2 flex-1">
          {prestataire.description}
        </p>
        {prestataire.services.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {prestataire.services.slice(0, 3).map((s) => (
              <span
                key={s}
                className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
              >
                {s}
              </span>
            ))}
          </div>
        )}
        <div className="flex items-center justify-between mt-auto">
          {prestataire.hourly_rate > 0 && (
            <p className="text-blue-600 font-bold text-sm">
              {prestataire.hourly_rate.toFixed(0)} $/h
            </p>
          )}
          {prestataire.rating > 0 && (
            <p className="text-yellow-500 text-sm font-medium">
              {"★".repeat(Math.round(prestataire.rating))} {prestataire.rating.toFixed(1)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
