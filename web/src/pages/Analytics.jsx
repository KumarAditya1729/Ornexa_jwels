import { useState, useEffect } from 'react';
import { Target, Search, BookOpen, Image as ImageIcon, Box } from 'lucide-react';

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/analytics');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return <div style={{ textAlign: "center", padding: "4rem" }}><span className="loader"></span></div>;
  }

  return (
    <div>
      <h1 className="title">ORNEXA Intelligence Metrics</h1>
      <p className="subtitle">The story behind the system. Live benchmark results across the 4 pillars.</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.5rem", marginBottom: "2rem" }}>
        
        <div className="glass-panel" style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <div style={{ padding: "1rem", background: "rgba(212, 175, 55, 0.1)", borderRadius: "50%", color: "var(--accent-gold)" }}>
            <Box size={32} />
          </div>
          <div>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", textTransform: "uppercase", letterSpacing: "1px" }}>Total Indexed</p>
            <h2 style={{ fontSize: "2.5rem", margin: 0 }}>1,386</h2>
          </div>
        </div>

        <div className="glass-panel" style={{ display: "flex", alignItems: "center", gap: "1.5rem", background: "linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(0,0,0,0) 100%)" }}>
          <div style={{ padding: "1rem", background: "var(--accent-gold)", borderRadius: "50%", color: "var(--bg-obsidian)" }}>
            <Target size={32} />
          </div>
          <div>
            <p style={{ color: "var(--accent-gold)", fontSize: "0.9rem", textTransform: "uppercase", letterSpacing: "1px", fontWeight: "600" }}>Overall Score</p>
            <h2 style={{ fontSize: "2.5rem", margin: 0 }}>{((data?.overall || 0) * 100).toFixed(1)}%</h2>
          </div>
        </div>

      </div>

      <h3 style={{ marginBottom: "1.5rem", marginTop: "3rem" }}>Pillar Benchmarks</h3>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1.5rem" }}>
        <div className="glass-panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}><Search size={20} color="var(--accent-gold)"/> Search Engine</h3>
            <span style={{ fontSize: "1.5rem", fontWeight: "600" }}>{((data?.search_accuracy || 0) * 100).toFixed(0)}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${(data?.search_accuracy || 0) * 100}%`, height: "100%", background: "var(--accent-gold)" }}></div>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}><BookOpen size={20} color="var(--accent-gold)"/> Taxonomy & Classification</h3>
            <span style={{ fontSize: "1.5rem", fontWeight: "600" }}>{((data?.taxonomy_accuracy || 0) * 100).toFixed(0)}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${(data?.taxonomy_accuracy || 0) * 100}%`, height: "100%", background: "var(--accent-gold)" }}></div>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}><BookOpen size={20} color="var(--accent-gold)"/> Knowledge Explorer</h3>
            <span style={{ fontSize: "1.5rem", fontWeight: "600" }}>{((data?.knowledge_accuracy || 0) * 100).toFixed(0)}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${(data?.knowledge_accuracy || 0) * 100}%`, height: "100%", background: "var(--accent-gold)" }}></div>
          </div>
        </div>

        <div className="glass-panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}><ImageIcon size={20} color="var(--accent-gold)"/> Vision (YOLOv8n)</h3>
            <span style={{ fontSize: "1.5rem", fontWeight: "600" }}>{((data?.classification_accuracy || 0) * 100).toFixed(1)}%</span>
          </div>
          <div style={{ width: "100%", height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
            <div style={{ width: `${(data?.classification_accuracy || 0) * 100}%`, height: "100%", background: "var(--accent-gold)" }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
