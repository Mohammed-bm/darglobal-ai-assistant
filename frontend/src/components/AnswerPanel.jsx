const NOISE = /Darglobal Register Interest English \| العربية/gi;

function parseSource(s) {
  const snippet = s.snippet || "";
  const m = snippet.match(/Source:\s*(https?:\/\/\S+)/i);
  const url = s.source || m?.[1] || null;
  const text = snippet
    .replace(/Source:\s*https?:\/\/\S+/i, "")
    .replace(NOISE, "")
    .replace(/\s+/g, " ")
    .trim();

  let brand = "Note";
  let label = "Saved note";
  if (url) {
    try {
      const u = new URL(url);
      const host = u.hostname.replace(/^www\./, "");
      brand = /darglobal/i.test(host)
        ? "DarGlobal"
        : /wasalt/i.test(host)
        ? "Wasalt"
        : host;
      label = host + (u.pathname === "/" ? "" : u.pathname);
    } catch {
      label = url;
    }
  }
  return { url, text, brand, label, score: Number(s.score) || 0 };
}

function Inline({ text }) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={i} className="font-semibold">
        {p.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{p}</span>
    )
  );
}

// Minimal renderer for the paragraphs, bullets and **bold** the models return
function RichText({ text }) {
  const blocks = [];
  let list = null;
  text.split("\n").forEach((line) => {
    const b = line.match(/^\s*[-*•]\s+(.*)/);
    if (b) {
      if (!list) {
        list = [];
        blocks.push({ type: "ul", items: list });
      }
      list.push(b[1]);
    } else {
      list = null;
      if (line.trim()) blocks.push({ type: "p", text: line.trim() });
    }
  });

  return (
    <div className="space-y-3 text-[17px] leading-relaxed">
      {blocks.map((b, i) =>
        b.type === "ul" ? (
          <ul key={i} className="ml-5 list-disc space-y-1 marker:text-[var(--brass)]">
            {b.items.map((it, j) => (
              <li key={j}>
                <Inline text={it} />
              </li>
            ))}
          </ul>
        ) : (
          <p key={i}>
            <Inline text={b.text} />
          </p>
        )
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="animate-pulse space-y-3" aria-label="Searching the knowledge base">
      <div className="h-4 w-11/12 rounded bg-[var(--sand)]" />
      <div className="h-4 w-full rounded bg-[var(--sand)]" />
      <div className="h-4 w-4/5 rounded bg-[var(--sand)]" />
      <div className="h-4 w-2/3 rounded bg-[var(--sand)]" />
    </div>
  );
}

function SourceItem({ s }) {
  const pct = Math.round(Math.min(Math.max(s.score, 0), 1) * 100);
  return (
    <details className="group border-t border-[var(--line)] py-3 first:border-t-0">
      <summary className="flex cursor-pointer list-none items-center gap-3 rounded focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--sea)]">
        <span className="shrink-0 rounded bg-[var(--ink)] px-2 py-0.5 text-xs font-medium text-white">
          {s.brand}
        </span>
        <span className="min-w-0 flex-1 truncate text-sm text-[var(--sea)]">
          {s.label}
        </span>
        <span className="flex shrink-0 items-center gap-2 text-xs text-[var(--muted)]">
          <span className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-[var(--sand)] sm:block">
            <span
              className="block h-full rounded-full bg-[var(--brass)]"
              style={{ width: `${pct}%` }}
            />
          </span>
          {pct}% match
        </span>
      </summary>
      <div className="mt-3 pl-1">
        <p className="text-sm leading-relaxed text-[var(--muted)]">{s.text}</p>
        {s.url && (
          <a
            href={s.url}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-block break-all text-sm text-[var(--sea)] underline underline-offset-2"
          >
            Open page
          </a>
        )}
      </div>
    </details>
  );
}

export default function AnswerPanel({ question, answer, loading, error }) {
  if (!question && !loading && !answer && !error) {
    return (
      <div className="rounded-xl border border-dashed border-[var(--line)] p-8 text-center">
        <p className="font-display text-2xl">Ask your first question</p>
        <p className="mx-auto mt-2 max-w-md text-[var(--muted)]">
          Pick a suggestion above or type your own. Answers are built only from
          the pages saved here, and each one lists its sources.
        </p>
      </div>
    );
  }

  const sources = Array.isArray(answer?.sources)
    ? answer.sources.map(parseSource)
    : [];

  return (
    <article className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-[var(--line)] sm:p-8">
      <p className="text-sm text-[var(--muted)]">You asked</p>
      <h2 className="font-display mt-1 text-2xl leading-snug">{question}</h2>

      <div className="mt-6">
        {loading && <Skeleton />}

        {error && (
          <p role="alert" className="rounded-lg bg-[#F8E9E5] p-4 text-[#8A3524]">
            Something went wrong: {error}. Check your connection and ask again.
          </p>
        )}

        {answer && <RichText text={answer.answer || ""} />}
      </div>

      {sources.length > 0 && (
        <div className="mt-8">
          <h3 className="font-display text-lg">
            Sources{" "}
            <span className="text-sm text-[var(--muted)]">
              ({sources.length} passages used)
            </span>
          </h3>
          <div className="mt-2">
            {sources.map((s, i) => (
              <SourceItem key={i} s={s} />
            ))}
          </div>
        </div>
      )}
    </article>
  );
}