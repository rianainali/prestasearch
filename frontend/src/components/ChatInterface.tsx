import { useState, useRef, useEffect, useCallback, type DragEvent } from "react";
import { searchPrestataires } from "../services/api";
import { chatStream } from "../services/chatStream";
import type { SearchResult } from "../types";
import ProviderCard from "./ProviderCard";

const MAX_SIZE = 5 * 1024 * 1024; // 5MB

interface Message {
  role: "user" | "assistant";
  content: string;
  results?: SearchResult[];
  imagePreview?: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [imageBase64, setImageBase64] = useState("");
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Process a file (from drop, paste, or file input) into base64
  const processFile = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) return;
    if (file.size > MAX_SIZE) return;
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.split(",")[1];
      setImageBase64(base64);
    };
    reader.readAsDataURL(file);
  }, []);

  // Handle drag & drop on the entire chat area
  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  // Handle paste (Ctrl+V) anywhere on the page
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;
      for (const item of items) {
        if (item.type.startsWith("image/")) {
          e.preventDefault();
          const file = item.getAsFile();
          if (file) processFile(file);
          return;
        }
      }
    };
    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, [processFile]);

  const handleSend = async () => {
    const text = input.trim();
    const image = imageBase64;
    if (!text && !image) return;

    const userMsg: Message = {
      role: "user",
      content: text,
      imagePreview: image || undefined,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setImageBase64("");
    setLoading(true);

    try {
      const results = await searchPrestataires(text || undefined, image || undefined);

      const assistantMsg: Message = {
        role: "assistant",
        content: "",
        results,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      let accumulated = "";
      for await (const token of chatStream(text || undefined, image || undefined)) {
        accumulated += token;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: accumulated,
          };
          return updated;
        });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Sorry, an error occurred.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: message },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex flex-col h-full relative"
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={(e) => {
        if (e.currentTarget === e.target || !e.currentTarget.contains(e.relatedTarget as Node)) {
          setDragOver(false);
        }
      }}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {dragOver && (
        <div className="absolute inset-0 z-50 bg-blue-500/10 border-2 border-dashed border-blue-500 rounded-lg flex items-center justify-center pointer-events-none">
          <p className="text-blue-600 font-semibold text-lg bg-white px-6 py-3 rounded-lg shadow">
            Drop your image here
          </p>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-2xl mb-2">Find a provider</p>
            <p className="text-sm">
              Describe your need, drop a photo or paste it (Ctrl+V)
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5"
                  : "space-y-3"
              }`}
            >
              {msg.imagePreview && (
                <img
                  src={`data:image/jpeg;base64,${msg.imagePreview}`}
                  alt="Uploaded"
                  className="max-h-24 rounded mb-2"
                />
              )}
              {msg.role === "assistant" && msg.content && (
                <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-2.5 text-gray-800 whitespace-pre-wrap">
                  {msg.content}
                </div>
              )}
              {msg.role === "user" && msg.content && <p>{msg.content}</p>}
              {msg.results && msg.results.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
                  {msg.results.map((r) => (
                    <ProviderCard key={r.prestataire.id} result={r} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-2.5 text-gray-500">
              <span className="animate-pulse">Searching...</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Image preview bar */}
      {imageBase64 && (
        <div className="px-4 pb-2 flex items-center gap-2">
          <div className="relative inline-block">
            <img
              src={`data:image/jpeg;base64,${imageBase64}`}
              alt="Preview"
              className="h-16 rounded border border-gray-200"
            />
            <button
              type="button"
              onClick={() => setImageBase64("")}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center hover:bg-red-600"
            >
              x
            </button>
          </div>
          <span className="text-xs text-gray-500">Image attached</span>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex gap-2 items-end">
          <label
            className={`p-2.5 rounded-lg border transition-colors shrink-0 cursor-pointer ${
              imageBase64
                ? "bg-blue-100 border-blue-300 text-blue-600"
                : "border-gray-300 text-gray-500 hover:bg-gray-50"
            }`}
            title="Attach an image"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) processFile(file);
                e.target.value = "";
              }}
            />
          </label>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={loading}
            placeholder="Describe your need..."
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || (!input.trim() && !imageBase64)}
            className="bg-blue-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
