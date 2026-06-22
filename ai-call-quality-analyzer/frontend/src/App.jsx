import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Bar,
  Doughnut,
} from "react-chartjs-2";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  Tooltip,
);

const API_BASE_URL = "http://127.0.0.1:8000";

const formatNumber = (value) => new Intl.NumberFormat("en-US").format(value || 0);

const formatDecimal = (value, digits = 1) =>
  Number(value || 0).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });

const getQualityBand = (score) => {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Good";
  if (score >= 60) return "Fair";
  return "Poor";
};

const emptySummary = {
  total_calls: 0,
  completed_calls: 0,
  dropped_calls: 0,
  failed_calls: 0,
  average_quality_score: 0,
  average_latency_ms: 0,
  average_jitter_ms: 0,
  average_packet_loss_percent: 0,
  average_throughput_kbps: 0,
  problem_counts: {},
};

function App() {
  const [summary, setSummary] = useState(emptySummary);
  const [regions, setRegions] = useState([]);
  const [problemCalls, setProblemCalls] = useState([]);
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchJson = async (path, options) => {
    const response = await fetch(`${API_BASE_URL}${path}`, options);

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `Request failed with status ${response.status}`);
    }

    return response.json();
  };

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [summaryData, regionData, problemData, callData] = await Promise.all([
        fetchJson("/analytics/summary"),
        fetchJson("/analytics/regions"),
        fetchJson("/analytics/problems?max_quality_score=75&limit=10000"),
        fetchJson("/calls?limit=10000"),
      ]);

      setSummary(summaryData);
      setRegions(regionData);
      setProblemCalls(problemData);
      setCalls(callData);
      setLastUpdated(new Date());
    } catch (requestError) {
      setError(
        "Unable to reach the FastAPI backend. Start it with `uvicorn main:app --reload` on port 8000.",
      );
      console.error(requestError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const handleSeed = async () => {
    setSeeding(true);
    setError("");

    try {
      await fetchJson("/seed?count=1000", { method: "POST" });
      await loadDashboard();
    } catch (requestError) {
      setError("Unable to generate simulated calls. Confirm the backend is running.");
      console.error(requestError);
    } finally {
      setSeeding(false);
    }
  };

  const worstRegion = useMemo(() => {
    if (!regions.length) {
      return { label: "No data", detail: "Seed calls to rank regions" };
    }

    const lowest = [...regions].sort(
      (first, second) => first.average_quality_score - second.average_quality_score,
    )[0];

    return {
      label: lowest.region,
      detail: `${formatDecimal(lowest.average_quality_score, 1)} quality score`,
    };
  }, [regions]);

  const failedDroppedCalls = summary.failed_calls + summary.dropped_calls;

  const qualityDistribution = useMemo(() => {
    const bands = {
      Excellent: 0,
      Good: 0,
      Fair: 0,
      Poor: 0,
    };

    calls.forEach((call) => {
      bands[getQualityBand(call.quality_score)] += 1;
    });

    return bands;
  }, [calls]);

  const poorCallsByRegion = useMemo(() => {
    const counts = regions.reduce((accumulator, region) => {
      accumulator[region.region] = 0;
      return accumulator;
    }, {});

    problemCalls.forEach((call) => {
      counts[call.region] = (counts[call.region] || 0) + 1;
    });

    return counts;
  }, [problemCalls, regions]);

  const chartTextColor = "#b9c8e6";
  const gridColor = "rgba(148, 163, 184, 0.15)";

  const baseBarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        borderColor: "rgba(125, 211, 252, 0.35)",
        borderWidth: 1,
        titleColor: "#f8fafc",
        bodyColor: "#dbeafe",
        padding: 12,
      },
    },
    scales: {
      x: {
        ticks: { color: chartTextColor },
        grid: { display: false },
      },
      y: {
        beginAtZero: true,
        ticks: { color: chartTextColor },
        grid: { color: gridColor },
      },
    },
  };

  const qualityDistributionData = {
    labels: Object.keys(qualityDistribution),
    datasets: [
      {
        data: Object.values(qualityDistribution),
        backgroundColor: ["#22c55e", "#38bdf8", "#f59e0b", "#ef4444"],
        borderColor: "rgba(15, 23, 42, 0.85)",
        borderWidth: 4,
        hoverOffset: 12,
      },
    ],
  };

  const latencyData = {
    labels: regions.map((region) => region.region),
    datasets: [
      {
        label: "Average latency",
        data: regions.map((region) => region.average_latency_ms),
        backgroundColor: "rgba(56, 189, 248, 0.75)",
        borderColor: "#7dd3fc",
        borderRadius: 14,
        borderWidth: 1,
      },
    ],
  };

  const poorCallData = {
    labels: Object.keys(poorCallsByRegion),
    datasets: [
      {
        label: "Poor calls",
        data: Object.values(poorCallsByRegion),
        backgroundColor: "rgba(244, 114, 182, 0.72)",
        borderColor: "#f9a8d4",
        borderRadius: 14,
        borderWidth: 1,
      },
    ],
  };

  const statCards = [
    {
      label: "Total Calls",
      value: formatNumber(summary.total_calls),
      detail: `${formatNumber(summary.completed_calls)} completed`,
      accent: "blue",
    },
    {
      label: "Average Quality Score",
      value: formatDecimal(summary.average_quality_score, 1),
      detail: "0 to 100 voice health index",
      accent: "green",
    },
    {
      label: "Failed/Dropped Calls",
      value: formatNumber(failedDroppedCalls),
      detail: `${formatNumber(summary.failed_calls)} failed / ${formatNumber(summary.dropped_calls)} dropped`,
      accent: "pink",
    },
    {
      label: "Average Latency",
      value: `${formatDecimal(summary.average_latency_ms, 1)} ms`,
      detail: `${formatDecimal(summary.average_jitter_ms, 1)} ms avg jitter`,
      accent: "amber",
    },
    {
      label: "Worst Region",
      value: worstRegion.label,
      detail: worstRegion.detail,
      accent: "violet",
    },
  ];

  const visibleProblemCalls = problemCalls.slice(0, 12);
  const showEmptyState = !loading && !summary.total_calls && !error;

  return (
    <main className="dashboard-shell">
      <section className="hero-panel">
        <div className="hero-glow hero-glow-one" />
        <div className="hero-glow hero-glow-two" />

        <nav className="topbar">
          <div className="brand-mark">AI</div>
          <div>
            <p className="eyebrow">Carrier-grade VoIP intelligence</p>
            <h1>AI Call Quality Analyzer</h1>
            <p className="subtitle">
              Telecommunications analytics platform for simulated VoIP call quality monitoring.
            </p>
          </div>
        </nav>

        <div className="hero-actions">
          <button className="primary-button" onClick={handleSeed} disabled={seeding || loading}>
            {seeding ? "Generating Calls..." : "Generate 1000 Simulated Calls"}
          </button>
          <button className="secondary-button" onClick={loadDashboard} disabled={loading || seeding}>
            {loading ? "Refreshing..." : "Refresh Analytics"}
          </button>
        </div>
      </section>

      {error && <div className="alert">{error}</div>}

      {showEmptyState && (
        <section className="empty-state">
          <div>
            <p className="eyebrow">Ready for telemetry</p>
            <h2>No call records yet</h2>
            <p>
              Generate a realistic 1000-call dataset to populate KPIs, charts, and root-cause
              diagnostics.
            </p>
          </div>
          <button className="primary-button" onClick={handleSeed} disabled={seeding}>
            Generate 1000 Simulated Calls
          </button>
        </section>
      )}

      <section className="kpi-grid" aria-label="Call quality key performance indicators">
        {statCards.map((card) => (
          <article className={`kpi-card accent-${card.accent}`} key={card.label}>
            <p>{card.label}</p>
            <strong>{card.value}</strong>
            <span>{card.detail}</span>
          </article>
        ))}
      </section>

      <section className="chart-grid">
        <article className="chart-card distribution-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">Quality mix</p>
              <h2>Call quality distribution</h2>
            </div>
            <span>{formatNumber(calls.length)} scored calls</span>
          </div>
          <div className="chart-container doughnut-container">
            <Doughnut
              data={qualityDistributionData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: "bottom",
                    labels: {
                      color: chartTextColor,
                      boxWidth: 12,
                      padding: 18,
                    },
                  },
                  tooltip: baseBarOptions.plugins.tooltip,
                },
                cutout: "68%",
              }}
            />
          </div>
        </article>

        <article className="chart-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">Regional transport</p>
              <h2>Region-wise average latency</h2>
            </div>
            <span>ms</span>
          </div>
          <div className="chart-container">
            <Bar data={latencyData} options={baseBarOptions} />
          </div>
        </article>

        <article className="chart-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">Trouble density</p>
              <h2>Region-wise poor call count</h2>
            </div>
            <span>score {"<="} 75 or flagged</span>
          </div>
          <div className="chart-container">
            <Bar data={poorCallData} options={baseBarOptions} />
          </div>
        </article>
      </section>

      <section className="table-card">
        <div className="card-heading">
          <div>
            <p className="eyebrow">Root-cause queue</p>
            <h2>Problematic calls</h2>
          </div>
          <span>
            {lastUpdated
              ? `Updated ${lastUpdated.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}`
              : "Waiting for data"}
          </span>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Call ID</th>
                <th>Region</th>
                <th>Quality</th>
                <th>Problem Flags</th>
                <th>Root Cause</th>
              </tr>
            </thead>
            <tbody>
              {visibleProblemCalls.length ? (
                visibleProblemCalls.map((call) => (
                  <tr key={call.call_id}>
                    <td className="mono">{call.call_id}</td>
                    <td>
                      <span className="region-pill">{call.region}</span>
                    </td>
                    <td>
                      <span className={`score-pill ${call.quality_score < 60 ? "critical" : ""}`}>
                        {call.quality_score}
                      </span>
                    </td>
                    <td>
                      <div className="flag-list">
                        {call.problem_flags.map((flag) => (
                          <span key={flag}>{flag.replaceAll("_", " ")}</span>
                        ))}
                      </div>
                    </td>
                    <td>{call.root_cause}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="no-results">
                    No problematic calls detected. Generate seed data or refresh analytics.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

export default App;
