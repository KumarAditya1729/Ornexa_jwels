import { useState, useEffect } from 'react';
import { DollarSign, Save } from 'lucide-react';

export default function SettingsPage() {
  const [rates, setRates] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/rates')
      .then(res => res.json())
      .then(data => {
        setRates(data);
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch('http://127.0.0.1:8000/api/rates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rates })
      });
      // Simulating a small delay for UI feedback
      setTimeout(() => setSaving(false), 500);
    } catch (err) {
      console.error(err);
      setSaving(false);
    }
  };

  const handleChange = (key, value) => {
    setRates(prev => ({ ...prev, [key]: parseFloat(value) || 0 }));
  };

  return (
    <div style={{ maxWidth: "800px" }}>
      <h1 className="title" style={{ marginBottom: "0.5rem" }}>Global Settings</h1>
      <p className="subtitle" style={{ marginBottom: "2rem" }}>Configure live material rates. Changes will immediately update all active un-invoiced quotations.</p>

      {loading ? (
        <span className="loader"></span>
      ) : (
        <div className="glass-panel">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "2rem", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "1rem" }}>
            <DollarSign size={24} color="var(--accent-gold)" />
            <h2 style={{ fontSize: "1.2rem" }}>Precious Metal Rates (INR / gram)</h2>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {Object.keys(rates).map(key => (
              <div key={key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <label style={{ fontSize: "1.1rem", color: "var(--text-secondary)", fontWeight: "500", minWidth: "150px" }}>{key}</label>
                <div style={{ position: "relative", flex: 1, maxWidth: "300px" }}>
                  <span style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-secondary)" }}>₹</span>
                  <input 
                    type="number"
                    value={rates[key]}
                    onChange={(e) => handleChange(key, e.target.value)}
                    style={{ 
                      width: "100%", padding: "0.8rem 1rem 0.8rem 2.5rem", 
                      background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-subtle)", 
                      borderRadius: "var(--radius-sm)", color: "white", fontSize: "1.1rem"
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: "3rem", display: "flex", justifyContent: "flex-end", borderTop: "1px solid var(--border-subtle)", paddingTop: "1.5rem" }}>
            <button className="btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : <><Save size={18} style={{ marginRight: "0.5rem" }} /> Save Global Rates</>}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
