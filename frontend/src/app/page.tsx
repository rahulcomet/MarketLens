"use client";

import { useMemo, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from "chart.js";

import { fetchNews, fetchPrices } from "../lib/api";
import type { NewsArticle, NewsResponse, PriceRange, PricesResponse } from "../lib/types";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

const ranges: PriceRange[] = ["1W", "1M", "100D"];
const requestCooldownMs = 1000;

const heroCopy = {
  headline: "Markets, without the noise.",
  subhead: "A clean, signal-first view of price action and the most relevant coverage for your ticker.",
};

export default function Home() {
  const [ticker, setTicker] = useState("AAPL");
  const [range, setRange] = useState<PriceRange>("1M");
  const [priceData, setPriceData] = useState<PricesResponse | null>(null);
  const [newsData, setNewsData] = useState<NewsResponse | null>(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [newsLoading, setNewsLoading] = useState(false);
  const [priceError, setPriceError] = useState<string | null>(null);
  const [newsError, setNewsError] = useState<string | null>(null);
  const [lastPriceRequest, setLastPriceRequest] = useState(0);
  const [lastNewsRequest, setLastNewsRequest] = useState(0);

  const chartData = useMemo(() => {
    if (!priceData) return null;
    const labels = priceData.points.map((point) => point.date);
    const values = priceData.points.map((point) => point.close);
    return {
      labels,
      datasets: [
        {
          label: `${priceData.ticker} Close`,
          data: values,
          fill: true,
          borderColor: "#0d7265",
          backgroundColor: "rgba(13, 114, 101, 0.15)",
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    };
  }, [priceData]);

  async function handlePrices(event: React.FormEvent) {
    event.preventDefault();
    const now = Date.now();
    if (now - lastPriceRequest < requestCooldownMs) {
      setPriceError("Please wait 1s before requesting prices again.");
      return;
    }
    setLastPriceRequest(now);
    setPriceLoading(true);
    setPriceError(null);
    try {
      const prices = await fetchPrices(ticker.trim(), range);
      setPriceData(prices);
    } catch (err) {
      // Avoid Promise.all here: parallel price/news calls can trigger API failures.
      setPriceError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setPriceLoading(false);
    }
  }

  async function handleNews() {
    const now = Date.now();
    if (now - lastNewsRequest < requestCooldownMs) {
      setNewsError("Please wait 1s before requesting news again.");
      return;
    }
    setLastNewsRequest(now);
    setNewsLoading(true);
    setNewsError(null);
    try {
      const news = await fetchNews(ticker.trim());
      setNewsData(news);
    } catch (err) {
      // Avoid Promise.all here: parallel price/news calls can trigger API failures.
      setNewsError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setNewsLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Stock Market Visualizer</p>
          <h1>{heroCopy.headline}</h1>
          <p className="subhead">{heroCopy.subhead}</p>
        </div>
        <form className="ticker-form" onSubmit={handlePrices}>
          <label className="field">
            <span>Ticker</span>
            <input
              value={ticker}
              onChange={(event) => setTicker(event.target.value.toUpperCase())}
              placeholder="AAPL"
            />
          </label>
          <div className="range-group">
            {ranges.map((item) => (
              <button
                type="button"
                key={item}
                className={item === range ? "range active" : "range"}
                onClick={() => setRange(item)}
              >
                {item}
              </button>
            ))}
          </div>
          <button type="submit" className="primary" disabled={priceLoading}>
            {priceLoading ? "Loading prices." : "Analyze prices"}
          </button>
          <button
            type="button"
            className="primary"
            onClick={handleNews}
            disabled={newsLoading}
          >
            {newsLoading ? "Loading news." : "Fetch news"}
          </button>
        </form>
      </header>

      {priceError ? <div className="error">{priceError}</div> : null}
      {newsError ? <div className="error">{newsError}</div> : null}

      <section className="grid">
        <div className="card chart-card">
          <div className="card-header">
            <div>
              <p className="label">Price trend</p>
              <h2>{priceData ? `${priceData.ticker} - ${priceData.range}` : "Waiting for data"}</h2>
            </div>
            <span className="pill">Daily close</span>
          </div>
          <div className="chart-wrapper">
            {chartData ? (
              <Line
                data={chartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { ticks: { maxTicksLimit: 6 } },
                    y: { ticks: { callback: (value) => `$${value}` } },
                  },
                }}
              />
            ) : (
              <div className="empty">Submit a ticker to see the chart.</div>
            )}
          </div>
        </div>

        <div className="card news-card">
          <div className="card-header">
            <div>
              <p className="label">Curated news</p>
              <h2>{newsData ? "Top headlines" : "Awaiting selection"}</h2>
            </div>
            <span className="pill">LLM ranked</span>
          </div>
          {newsData ? (
            <div className="news-list">
              <p className="summary">{newsData.summary}</p>
              {newsData.articles.map((article) => (
                <NewsItem key={article.url} article={article} />
              ))}
            </div>
          ) : (
            <div className="empty">News will appear after you analyze a ticker.</div>
          )}
        </div>
      </section>
    </div>
  );
}

function NewsItem({ article }: { article: NewsArticle }) {
  return (
    <article className="news-item">
      <div>
        <h3>{article.title}</h3>
        <p className="meta">
          {article.source ? article.source : "Source"} - Score {article.relevance_score.toFixed(2)}
        </p>
        {article.summary ? <p className="snippet">{article.summary}</p> : null}
      </div>
      <a href={article.url} target="_blank" rel="noreferrer">
        Read
      </a>
    </article>
  );
}
