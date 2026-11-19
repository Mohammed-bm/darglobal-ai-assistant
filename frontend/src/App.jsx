import { useEffect, useState } from "react";
import QueryBox from "./components/QueryBox";
import AnswerPanel from "./components/AnswerPanel";
import IngestForm from "./components/IngestForm";
import ItemsList from "./components/ItemsList";
import { fetchItems, queryKnowledge } from "./api";

export default function App() {
  const [items, setItems] = useState([]);
  const [itemsLoading, setItemsLoading] = useState(true);
  const [asked, setAsked] = useState("");
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState(null);

  async function loadItems() {
    try {
      setItems(await fetchItems());
    } catch (e) {
      console.error(e);
    } finally {
      setItemsLoading(false);
    }
  }

  useEffect(() => {
    loadItems();
  }, []);

  async function ask(question) {
    setAsked(question);
    setAsking(true);
    setError(null);
    setAnswer(null);
    try {
      setAnswer(await queryKnowledge(question));
    } catch (e) {
      setError(e.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--limestone)] text-[var(--text)]">
      <header className="bg-[var(--ink)] text-white">
        <div className="mx-auto max-w-6xl px-5 pb-10 pt-10 sm:pt-14">
          <h1 className="font-display text-4xl leading-[1.1] sm:text-5xl">
            DarGlobal &amp; Wasalt AI Assistant
          </h1>
          <p className="mt-3 max-w-xl text-base text-white/70">
            Ask about projects, markets, partners and news. Every answer comes
            with the pages it was drawn from.
          </p>
          <div className="mt-8">
            <QueryBox onAsk={ask} loading={asking} />
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-10 px-5 py-10 lg:grid-cols-[minmax(0,1fr)_340px]">
        <section aria-live="polite">
          <AnswerPanel
            question={asked}
            answer={answer}
            loading={asking}
            error={error}
          />
        </section>

        <aside className="space-y-10">
          <IngestForm onSuccess={loadItems} />
          <ItemsList items={items} loading={itemsLoading} />
        </aside>
      </main>
    </div>
  );
}