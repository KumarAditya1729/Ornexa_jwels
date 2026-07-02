import { useState, useRef } from 'react';
import { UploadCloud, Sparkles, Gem, ArrowRight, ShieldCheck } from 'lucide-react';

export default function CopilotPage() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setResult(null);
    }
  };

  const analyzeImage = async () => {
    if (!file) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Pointing to local FastAPI backend
      const response = await fetch('http://127.0.0.1:8000/api/copilot', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing image:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="title">ORNEXA Copilot</h1>
      <p className="subtitle">Upload a jewelry design to instantly extract intelligence.</p>

      {!previewUrl && (
        <div 
          className="upload-zone"
          onClick={() => fileInputRef.current?.click()}
        >
          <UploadCloud size={48} className="upload-icon" />
          <h3 style={{ color: "var(--text-primary)", marginBottom: "0.5rem" }}>Drop your image here</h3>
          <p style={{ color: "var(--text-secondary)" }}>Supports JPG, PNG, WEBP</p>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            style={{ display: "none" }} 
            accept="image/*"
          />
        </div>
      )}

      {previewUrl && (
        <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start" }}>
          <div className="glass-panel" style={{ width: "350px", textAlign: "center" }}>
            <img 
              src={previewUrl} 
              alt="Preview" 
              style={{ width: "100%", borderRadius: "var(--radius-sm)", marginBottom: "1.5rem" }} 
            />
            {!result && !loading && (
              <button className="btn-primary" style={{ width: "100%", justifyContent: "center" }} onClick={analyzeImage}>
                <Sparkles size={18} /> Analyze with ORNEXA
              </button>
            )}
            {loading && (
              <div style={{ padding: "1rem 0" }}>
                <span className="loader"></span>
                <p style={{ marginTop: "1rem", color: "var(--accent-gold)" }}>Extracting Intelligence...</p>
              </div>
            )}
            
            {result && (
              <button 
                className="btn-primary" 
                style={{ width: "100%", justifyContent: "center", background: "transparent", border: "1px solid var(--border-subtle)", color: "var(--text-primary)" }} 
                onClick={() => {
                  setFile(null);
                  setPreviewUrl(null);
                  setResult(null);
                }}
              >
                Upload New Image
              </button>
            )}
          </div>

          {result && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              <div className="glass-panel">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                  <h2 style={{ fontSize: "1.5rem", color: "var(--accent-gold)" }}>Vision Inference</h2>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#4ade80", fontSize: "0.9rem" }}>
                    <ShieldCheck size={16} /> Confidence: {(result.confidence * 100).toFixed(1)}%
                  </div>
                </div>
                
                <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                  <div style={{ background: "rgba(255,255,255,0.05)", padding: "1rem 1.5rem", borderRadius: "var(--radius-sm)", flex: 1 }}>
                    <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "1px" }}>Category</p>
                    <p style={{ fontSize: "1.5rem", fontWeight: "600" }}>{result.category}</p>
                  </div>
                  <div style={{ background: "rgba(255,255,255,0.05)", padding: "1rem 1.5rem", borderRadius: "var(--radius-sm)", flex: 1 }}>
                    <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "1px" }}>Metal</p>
                    <p style={{ fontSize: "1.5rem", fontWeight: "600" }}>{result.metal}</p>
                  </div>
                  {result.style && result.style.length > 0 && (
                    <div style={{ background: "rgba(255,255,255,0.05)", padding: "1rem 1.5rem", borderRadius: "var(--radius-sm)", flex: 1 }}>
                      <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "1px" }}>Style</p>
                      <p style={{ fontSize: "1.5rem", fontWeight: "600" }}>{result.style[0]}</p>
                    </div>
                  )}
                </div>
              </div>

              {result.knowledge && result.knowledge.definition && (
                <div className="glass-panel" style={{ borderLeft: "3px solid var(--accent-gold)" }}>
                  <h3 style={{ marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <Gem size={18} color="var(--accent-gold)" /> Knowledge Explorer
                  </h3>
                  <p style={{ color: "var(--text-secondary)" }}>{result.knowledge.definition}</p>
                  
                  {result.knowledge.related_styles && result.knowledge.related_styles.length > 0 && (
                    <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                      {result.knowledge.related_styles.map(tag => (
                        <span key={tag} className="badge">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <div className="glass-panel">
                <h3 style={{ marginBottom: "1rem" }}>Similar Products in Catalog</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  {result.similar_products.map((p, i) => (
                    <div key={i} className="product-card">
                      <p style={{ fontSize: "0.8rem", color: "var(--accent-gold)" }}>{p.canonical_id}</p>
                      <p style={{ fontWeight: "600", margin: "0.3rem 0" }}>{p.product_name}</p>
                      <p style={{ color: "var(--text-secondary)" }}>{p.price.toLocaleString()} {p.currency}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
}
