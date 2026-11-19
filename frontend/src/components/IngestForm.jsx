import { useState } from "react";
import { ingestContent } from "../api";

export default function IngestForm({ onSuccess }) {
  const [type, setType] = useState("note");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!content.trim()) return;

    try {
      setLoading(true);
      setError(null);
      setSaved(false);

      const payload =
        type === "note"
          ? { type: "note", raw_text: content }
          : { type: "url", source: content.trim() };

      await ingestContent(payload);

      setContent("");
      setSaved(true);
      onSuccess?.();
    } catch (err) {
      setError(
        /no chunks/i.test(err.message)
          ? "Couldn't read text from that page. Some sites block automated access, so paste the text as a note instead."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  const tabs = [
    { id: "note", label: "Note" },
    { id: "url", label: "URL" },
  ];

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="font-display text-xl">Add to the knowledge base</h2>

      <div
        role="tablist"
        aria-label="Content type"
        className="mt-3 inline-flex rounded-lg bg-[var(--sand)] p-1"
      >
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={type === t.id}
            onClick={() => {
              setType(t.id);
              setContent("");
              setError(null);
              setSaved(false);
            }}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition focus-visible:outline-2 focus-visible:outline-[var(--sea)] ${
              type === t.id
                ? "bg-white text-[var(--ink)] shadow-sm"
                : "text-[var(--muted)] hover:text-[var(--ink)]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="mt-3">
        {type === "note" ? (
          <textarea
            aria-label="Note text"
            placeholder="Paste or write text to remember…"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={5}
            className="w-full resize-y rounded-lg border border-[var(--line)] bg-white p-3 text-sm outline-none focus:border-[var(--sea)] focus:ring-2 focus:ring-[var(--sea)]/25"
          />
        ) : (
          <input
            aria-label="Page URL"
            type="url"
            placeholder="https://wasalt.sa/en"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full rounded-lg border border-[var(--line)] bg-white p-3 text-sm outline-none focus:border-[var(--sea)] focus:ring-2 focus:ring-[var(--sea)]/25"
          />
        )}
      </div>

      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="mt-3 w-full rounded-lg bg-[var(--ink)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--sea)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--sea)] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Saving…" : type === "note" ? "Save note" : "Save page"}
      </button>

      {saved && (
        <p role="status" className="mt-2 text-sm text-[var(--sea)]">
          Saved. You can now ask about it.
        </p>
      )}
      {error && (
        <p role="alert" className="mt-2 text-sm text-[#8A3524]">
          {error}
        </p>
      )}
    </form>
  );
}