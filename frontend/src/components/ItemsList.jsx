// SQLite's datetime('now') is UTC without a timezone marker, so mark it as UTC
function formatDate(value) {
  if (!value) return "";
  const iso = /Z|[+-]\d\d:?\d\d$/.test(value) ? value : value.replace(" ", "T") + "Z";
  const d = new Date(iso);
  return isNaN(d) ? value : d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
}

export default function ItemsList({ items, loading }) {
  return (
    <div>
      <h2 className="font-display text-xl">
        Saved items{" "}
        <span className="text-sm text-[var(--muted)]">({items.length})</span>
      </h2>

      {loading && <p className="mt-3 text-sm text-[var(--muted)]">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="mt-3 text-sm text-[var(--muted)]">
          Nothing saved yet. Add a note or a page above.
        </p>
      )}

      <ul className="mt-3 max-h-[28rem] divide-y divide-[var(--line)] overflow-y-auto border-y border-[var(--line)]">
        {items.map((item) => (
          <li key={item.id} className="py-3">
            <div className="flex items-center justify-between gap-2">
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  item.type === "url"
                    ? "bg-[var(--sea)] text-white"
                    : "bg-[var(--sand)] text-[var(--ink)]"
                }`}
              >
                {item.type === "url" ? "Page" : "Note"}
              </span>
              <time className="text-xs text-[var(--muted)]">
                {formatDate(item.created_at)}
              </time>
            </div>
            <p className="mt-1.5 line-clamp-2 break-words text-sm leading-snug">
              {item.preview}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}