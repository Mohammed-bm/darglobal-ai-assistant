import { useState } from "react";

const SUGGESTIONS = [
  "What projects does DarGlobal have in Oman or Qatar?",
  "Which brands does DarGlobal partner with?",
  "What is the new Jeddah development?",
  "What is Wasalt?",
];

export default function QueryBox({ onAsk, loading }) {
  const [question, setQuestion] = useState("");

  function submit(q) {
    const text = q.trim();
    if (!text || loading) return;
    onAsk(text);
  }

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(question);
        }}
        className="flex flex-col gap-2 rounded-xl bg-white/[0.07] p-2 ring-1 ring-white/15 focus-within:ring-2 focus-within:ring-[var(--brass)] sm:flex-row"
      >
        <label htmlFor="question" className="sr-only">
          Your question
        </label>
        <input
          id="question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about DarGlobal or Wasalt"
          className="min-w-0 flex-1 bg-transparent px-4 py-3 text-base text-white outline-none placeholder:text-white/50"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-lg bg-[var(--brass)] px-7 py-3 font-medium text-[var(--ink)] transition hover:brightness-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Searching…" : "Ask"}
        </button>
      </form>

      <div className="mt-4 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            disabled={loading}
            onClick={() => {
              setQuestion(s);
              submit(s);
            }}
            className="rounded-full border border-white/25 px-3.5 py-1.5 text-sm text-white/80 transition hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}