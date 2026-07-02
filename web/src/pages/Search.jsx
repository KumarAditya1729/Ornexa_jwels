import { useState } from 'react';
import { Search as SearchIcon, Filter } from 'lucide-react';

export default function SearchPage() {
  const [filters, setFilters] = useState({
    category: '',
    metal: '',
    style: ''
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e?.preventDefault();
    setLoading(true);
    
    try {
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.metal) params.append('metal', filters.metal);
      if (filters.style) params.append('style', filters.style);
      
      const response = await fetch(`http://127.0.0.1:8000/api/search?${params.toString()}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Error searching:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="title">Product Catalog</h1>
      <p className="subtitle">Search and filter across the unified ORNEXA database.</p>

      <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
        
        {/* Filters Sidebar */}
        <div className="glass-panel" style={{ width: "300px" }}>
          <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.5rem" }}>
            <Filter size={18} /> Filters
          </h3>
          
          <form onSubmit={handleSearch} style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>Category</label>
              <select 
                value={filters.category}
                onChange={e => setFilters({...filters, category: e.target.value})}
                style={{ width: "100%", padding: "0.8rem", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", color: "white", outline: "none" }}
              >
                <option value="">All Categories</option>
                <option value="Ring">Ring</option>
                <option value="Necklace">Necklace</option>
                <option value="Earring">Earring</option>
                <option value="Bracelet">Bracelet</option>
                <option value="Pendant">Pendant</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>Metal Type</label>
              <select 
                value={filters.metal}
                onChange={e => setFilters({...filters, metal: e.target.value})}
                style={{ width: "100%", padding: "0.8rem", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", color: "white", outline: "none" }}
              >
                <option value="">All Metals</option>
                <option value="Gold">Gold</option>
                <option value="Silver">Silver</option>
                <option value="Platinum">Platinum</option>
                <option value="Rose Gold">Rose Gold</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontSize: "0.9rem", color: "var(--text-secondary)" }}>Style</label>
              <input 
                type="text" 
                placeholder="e.g. Temple, Kundan..."
                value={filters.style}
                onChange={e => setFilters({...filters, style: e.target.value})}
                style={{ width: "100%", padding: "0.8rem", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", color: "white", outline: "none" }}
              />
            </div>

            <button type="submit" className="btn-primary" style={{ justifyContent: "center", marginTop: "1rem" }}>
              <SearchIcon size={18} /> Apply Filters
            </button>
          </form>
        </div>

        {/* Results Grid */}
        <div style={{ flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: "center", padding: "4rem" }}><span className="loader"></span></div>
          ) : results ? (
            <>
              <p style={{ marginBottom: "1rem", color: "var(--text-secondary)" }}>Showing {results.length} results</p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1.5rem" }}>
                {results.map((p, i) => (
                  <div key={i} className="product-card">
                    <p style={{ fontSize: "0.8rem", color: "var(--accent-gold)", marginBottom: "0.5rem" }}>{p.canonical_id}</p>
                    <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>{p.product_name}</h3>
                    <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap" }}>
                      {p.metal_type && <span className="badge" style={{ background: "rgba(255,255,255,0.1)", color: "white" }}>{p.metal_type}</span>}
                      {p.style && p.style.slice(0,2).map(s => <span key={s} className="badge" style={{ background: "rgba(255,255,255,0.1)", color: "white" }}>{s}</span>)}
                    </div>
                    <p style={{ color: "var(--accent-gold)", fontWeight: "600" }}>{p.price.toLocaleString()} {p.currency}</p>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="glass-panel" style={{ textAlign: "center", padding: "4rem 2rem", background: "rgba(255,255,255,0.02)" }}>
              <SearchIcon size={48} style={{ color: "var(--border-subtle)", marginBottom: "1rem" }} />
              <h3>Enter filters to search</h3>
              <p style={{ color: "var(--text-secondary)" }}>Search across the 1,386 unified items.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
