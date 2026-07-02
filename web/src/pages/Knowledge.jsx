import { useState } from 'react';
import { Send, Gem, Loader } from 'lucide-react';

export default function KnowledgePage() {
  const [query, setQuery] = useState('');
  const [chat, setChat] = useState([
    { role: 'assistant', content: 'Welcome to the ORNEXA Knowledge Explorer. Ask me anything about jewelry styles, history, or terminology.' }
  ]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setQuery('');
    setChat(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/knowledge?query=${encodeURIComponent(userMessage)}`);
      const data = await response.json();
      setChat(prev => [...prev, { role: 'assistant', content: data.explanation }]);
    } catch (error) {
      setChat(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error connecting to the knowledge base.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: "calc(100vh - 6rem)", display: "flex", flexDirection: "column" }}>
      <div>
        <h1 className="title">Knowledge Explorer</h1>
        <p className="subtitle">Semantic querying over the ORNEXA jewelry graph.</p>
      </div>

      <div className="glass-panel" style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", padding: 0 }}>
        
        <div style={{ flex: 1, overflowY: "auto", padding: "2rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {chat.map((msg, i) => (
            <div key={i} style={{ display: "flex", justifyContent: msg.role === 'user' ? "flex-end" : "flex-start" }}>
              <div style={{
                maxWidth: "75%",
                padding: "1rem 1.5rem",
                borderRadius: "var(--radius-lg)",
                background: msg.role === 'user' ? "rgba(212, 175, 55, 0.15)" : "rgba(255,255,255,0.05)",
                border: msg.role === 'user' ? "1px solid rgba(212, 175, 55, 0.3)" : "1px solid var(--border-subtle)",
                color: msg.role === 'user' ? "var(--accent-gold)" : "var(--text-primary)"
              }}>
                {msg.role === 'assistant' && (
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem", color: "var(--accent-gold)" }}>
                    <Gem size={16} /> <span style={{ fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "1px", fontWeight: "600" }}>ORNEXA</span>
                  </div>
                )}
                <div style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", justifyContent: "flex-start" }}>
              <div style={{ padding: "1rem 1.5rem", borderRadius: "var(--radius-lg)", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)" }}>
                <Loader size={20} className="upload-icon" style={{ animation: "rotation 1s linear infinite", margin: 0 }} />
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleAsk} style={{ padding: "1.5rem", borderTop: "1px solid var(--border-subtle)", display: "flex", gap: "1rem", background: "rgba(0,0,0,0.2)" }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about Kundan, Polki, or differences between styles..."
            style={{
              flex: 1,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              padding: "1rem 1.5rem",
              color: "white",
              fontFamily: "var(--font-sans)",
              fontSize: "1rem",
              outline: "none"
            }}
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            <Send size={20} />
          </button>
        </form>

      </div>
    </div>
  );
}
