import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PenTool, Box, CheckCircle, FileText, ChevronRight, Settings, MessageSquare, Truck, Clock, DollarSign, Download, Paperclip, Upload } from 'lucide-react';

export default function StudioPage() {
  const [step, setStep] = useState(1);
  const [order, setOrder] = useState(null);
  const [requirement, setRequirement] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeNoteTab, setActiveNoteTab] = useState('internal');
  const [noteContent, setNoteContent] = useState('');
  const [searchParams] = useSearchParams();
  const fileInputRef = useRef(null);

  useEffect(() => {
    const urlOrderId = searchParams.get('orderId');
    if (urlOrderId) {
      setLoading(true);
      fetch(`http://127.0.0.1:8000/api/order/${urlOrderId}`)
        .then(res => res.json())
        .then(data => {
          setOrder(data);
          
          // Determine step based on status
          if (data.status === 'Requirement Received') setStep(1);
          else if (data.status.includes('Sketch')) setStep(2);
          else if (data.status.includes('CAD')) setStep(3);
          else setStep(4);
          
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [searchParams]);

  // Auto-refresh order state (Simulating WebSockets/Polling for the factory floor)
  const refreshOrder = async (orderId) => {
    const res = await fetch(`http://127.0.0.1:8000/api/order/${orderId}`);
    const data = await res.json();
    setOrder(data);
    return data;
  };

  // Step 1: Submit Requirement
  const submitRequirement = async (e) => {
    e.preventDefault();
    if (!requirement.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/order/new', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requirement, category: "Necklace" })
      });
      const data = await res.json();
      setOrder(data);
      
      // Auto-trigger sketch generation
      await fetch(`http://127.0.0.1:8000/api/order/${data.id}/generate_sketches`, { method: 'POST' });
      await refreshOrder(data.id);
      setStep(2);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Submit Feedback (Revision Loop)
  const submitFeedback = async (e) => {
    e.preventDefault();
    if (!feedback.trim()) return;
    setLoading(true);
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback })
      });
      
      // Generate new sketch based on feedback
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/generate_sketches`, { method: 'POST' });
      await refreshOrder(order.id);
      setFeedback('');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Approve Sketch
  const handleApproveSketch = async (sketch) => {
    setLoading(true);
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/approve_sketch?sketch_id=${sketch.id}`, { method: 'POST' });
      
      // Auto-trigger CAD generation
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/generate_cad`, { method: 'POST' });
      await refreshOrder(order.id);
      setStep(3);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Approve CAD and Generate Work Order
  const handleApproveCAD = async () => {
    setLoading(true);
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/approve_cad`, { method: 'POST' });
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/work_order`);
      await refreshOrder(order.id);
      setStep(4);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Advance Factory Production State
  const advanceProduction = async (stateName) => {
    setLoading(true);
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/manufacturing_state?state=${encodeURIComponent(stateName)}`, { method: 'POST' });
      await refreshOrder(order.id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Update Margin
  const handleUpdateMargin = async (newMargin) => {
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/update_margin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ margin_percent: parseInt(newMargin) })
      });
      await refreshOrder(order.id);
    } catch (err) {
      console.error(err);
    }
  };

  // Add Note
  const handleAddNote = async () => {
    if (!noteContent.trim()) return;
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: activeNoteTab, content: noteContent })
      });
      await refreshOrder(order.id);
      setNoteContent('');
    } catch (err) {
      console.error(err);
    }
  };

  // Mock Upload Attachment
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      await fetch(`http://127.0.0.1:8000/api/order/${order.id}/attach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: file.name, filetype: file.type || "unknown" })
      });
      await refreshOrder(order.id);
    } catch (err) {
      console.error(err);
    }
  };

  const manufacturingSteps = ["Production Released", "Casting", "Assembly", "Stone Setting", "Polishing", "QC", "Ready Dispatch"];
  const currentMfgIndex = order ? manufacturingSteps.indexOf(order.status) : -1;

  return (
    <div>
      <h1 className="title">ORNEXA Manufacturing OS</h1>
      <p className="subtitle">End-to-End Generative Design & Factory Tracking.</p>

      {/* Progress Wizard */}
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "3rem", padding: "0 2rem" }}>
        {[
          { num: 1, label: "Requirement", icon: <PenTool size={16}/> },
          { num: 2, label: "Review & Revision", icon: <Settings size={16}/> },
          { num: 3, label: "CAD Approval", icon: <Box size={16}/> },
          { num: 4, label: "Factory Tracking", icon: <Truck size={16}/> }
        ].map((s, i) => (
          <div key={s.num} style={{ display: "flex", alignItems: "center", gap: "1rem", opacity: step >= s.num ? 1 : 0.4 }}>
            <div style={{ 
              width: "36px", height: "36px", borderRadius: "50%", 
              background: step >= s.num ? "var(--accent-gold)" : "transparent",
              border: `2px solid ${step >= s.num ? "var(--accent-gold)" : "var(--border-subtle)"}`,
              color: step >= s.num ? "var(--bg-obsidian)" : "var(--text-secondary)",
              display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold"
            }}>
              {step > s.num ? <CheckCircle size={20} /> : s.num}
            </div>
            <span style={{ fontWeight: step >= s.num ? "600" : "400", color: step >= s.num ? "var(--accent-gold)" : "var(--text-secondary)" }}>
              {s.label}
            </span>
            {i < 3 && <ChevronRight size={20} color="var(--border-subtle)" style={{ marginLeft: "1rem" }}/>}
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "2rem" }}>
        
        {/* Main Workspace Column */}
        <div className="glass-panel" style={{ flex: 1, minHeight: "500px", display: "flex", flexDirection: "column" }}>
          
          {loading && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
              <span className="loader"></span>
              <p style={{ marginTop: "1rem", color: "var(--accent-gold)" }}>ORNEXA Core Processing...</p>
            </div>
          )}

          {/* Step 1: Input */}
          {!loading && step === 1 && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", maxWidth: "600px", margin: "0 auto", width: "100%" }}>
              <h2 style={{ marginBottom: "1.5rem", textAlign: "center" }}>New Custom Order</h2>
              <form onSubmit={submitRequirement} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <textarea 
                  value={requirement}
                  onChange={e => setRequirement(e.target.value)}
                  placeholder="E.g. A traditional Indian temple style gold necklace adorned with rich ruby stones..."
                  rows={5}
                  style={{
                    width: "100%", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-subtle)", 
                    borderRadius: "var(--radius-md)", padding: "1.5rem", color: "white", fontFamily: "var(--font-sans)", fontSize: "1.1rem", resize: "none"
                  }}
                />
                <button type="submit" className="btn-primary" style={{ justifyContent: "center", padding: "1rem" }} disabled={!requirement.trim()}>
                  Initialize Order Workflow <ChevronRight size={18} />
                </button>
              </form>
            </div>
          )}

          {/* Step 2: Multi-Revision Loop */}
          {!loading && step === 2 && order && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
                <div>
                  <h2>Review Concepts (v{order.version})</h2>
                  <p style={{ color: "var(--text-secondary)" }}>Design Brief: "{order.requirement}"</p>
                </div>
                <span className="badge">Order ID: {order.id}</span>
              </div>
              
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
                {order.sketches.map(s => (
                  <div key={s.id} className="product-card" style={{ padding: "1rem" }}>
                    <img src={s.url} alt="Concept" style={{ width: "100%", borderRadius: "var(--radius-sm)", marginBottom: "1rem", border: "1px solid var(--border-subtle)" }} />
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <h3 style={{ fontSize: "1.1rem" }}>{s.style}</h3>
                      <button className="btn-primary" style={{ padding: "0.5rem 1rem", fontSize: "0.9rem" }} onClick={() => handleApproveSketch(s)}>
                        Approve v{order.version}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Feedback Loop */}
              <div style={{ background: "rgba(255,255,255,0.03)", padding: "1.5rem", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}><MessageSquare size={18} /> Request Revision</h3>
                <form onSubmit={submitFeedback} style={{ display: "flex", gap: "1rem" }}>
                  <input 
                    type="text" 
                    value={feedback}
                    onChange={e => setFeedback(e.target.value)}
                    placeholder="E.g. Make the center motif significantly larger..."
                    style={{ flex: 1, background: "rgba(0,0,0,0.5)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: "0.8rem", color: "white" }}
                  />
                  <button type="submit" className="btn-primary" disabled={!feedback.trim()}>Generate v{order.version + 1}</button>
                </form>
              </div>
            </div>
          )}

          {/* Step 3: 3D CAD Review */}
          {!loading && step === 3 && order && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h2>3D Parametric CAD Approval</h2>
                <button className="btn-primary" onClick={handleApproveCAD}>Approve CAD & Extract BOM</button>
              </div>
              
              <div style={{ flex: 1, background: "#1a1a20", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative", minHeight: "400px" }}>
                <div style={{ textAlign: "center", color: "var(--text-secondary)" }}>
                  <Box size={64} style={{ opacity: 0.5, marginBottom: "1rem", margin: "0 auto" }} />
                  <h3>Interactive 3D Viewer</h3>
                  <p>Model generated from Approved Sketch v{order.version}</p>
                  <p style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>File: {order.cad_url}</p>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Factory Tracking & BOM */}
          {!loading && step === 4 && order && (
            <div>
              <h2 style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "2rem" }}>
                <Truck size={28} /> Factory Production Tracking
              </h2>

              {/* Manufacturing Timeline */}
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "3rem", padding: "1rem", background: "rgba(255,255,255,0.03)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                {manufacturingSteps.map((stateName, i) => {
                  const isCompleted = currentMfgIndex >= i;
                  const isActive = currentMfgIndex === i;
                  return (
                    <div key={stateName} style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: isCompleted ? 1 : 0.4, gap: "0.5rem", flex: 1 }}>
                      <div style={{ width: "20px", height: "20px", borderRadius: "50%", background: isCompleted ? "var(--accent-gold)" : "var(--border-subtle)", boxShadow: isActive ? "0 0 10px var(--accent-gold)" : "none" }}></div>
                      <span style={{ fontSize: "0.8rem", textAlign: "center", color: isCompleted ? "white" : "var(--text-secondary)" }}>{stateName}</span>
                      {isActive && i < manufacturingSteps.length - 1 && (
                        <button className="btn-primary" style={{ padding: "0.2rem 0.5rem", fontSize: "0.7rem", marginTop: "0.5rem" }} onClick={() => advanceProduction(manufacturingSteps[i+1])}>
                          Move to {manufacturingSteps[i+1]}
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>
              
              <div style={{ display: "flex", gap: "2rem" }}>
                {/* BOM Panel */}
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "2rem" }}>
                  <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-subtle)", padding: "1.5rem", borderRadius: "var(--radius-md)" }}>
                    <h3 style={{ marginBottom: "1.5rem", color: "var(--accent-gold)", borderBottom: "1px solid rgba(212, 175, 55, 0.3)", paddingBottom: "0.5rem" }}>
                      Bill of Materials (BOM)
                    </h3>
                    {order.bom ? (
                      <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
                        <thead>
                          <tr style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>
                            <th style={{ padding: "0.5rem 0" }}>Component</th>
                            <th style={{ padding: "0.5rem 0" }}>Quantity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {order.bom.map((item, i) => (
                            <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                              <td style={{ padding: "0.8rem 0", color: "white" }}>{item.component}</td>
                              <td style={{ padding: "0.8rem 0", color: "var(--accent-gold)" }}>{item.qty}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : <p>No BOM Extracted.</p>}
                  </div>

                  {/* Costing & Quotation Panel */}
                  {order.costing && (
                    <div className="quotation-panel" style={{ background: "var(--bg-obsidian)", border: "1px solid var(--accent-gold)", padding: "2rem", borderRadius: "var(--radius-md)" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem", borderBottom: "1px solid rgba(212, 175, 55, 0.3)", paddingBottom: "1rem" }}>
                        <h3 style={{ color: "var(--accent-gold)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                          <DollarSign size={20}/> Financial Quotation
                        </h3>
                        <button className="btn-primary" style={{ padding: "0.5rem 1rem", fontSize: "0.8rem", background: "transparent", border: "1px solid var(--accent-gold)", color: "var(--accent-gold)" }} onClick={() => window.print()}>
                          <Download size={14} style={{ marginRight: "0.5rem" }}/> Print to PDF
                        </button>
                      </div>

                      <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse", marginBottom: "1.5rem", fontSize: "0.95rem" }}>
                        <tbody>
                          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                            <td style={{ padding: "0.8rem 0", color: "var(--text-secondary)" }}>Material Cost (Live Gold Rate)</td>
                            <td style={{ padding: "0.8rem 0", color: "white", textAlign: "right" }}>₹{order.costing.material_cost.toLocaleString()}</td>
                          </tr>
                          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                            <td style={{ padding: "0.8rem 0", color: "var(--text-secondary)" }}>Gemstone Cost</td>
                            <td style={{ padding: "0.8rem 0", color: "white", textAlign: "right" }}>₹{order.costing.stone_cost.toLocaleString()}</td>
                          </tr>
                          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                            <td style={{ padding: "0.8rem 0", color: "var(--text-secondary)" }}>Making Charges</td>
                            <td style={{ padding: "0.8rem 0", color: "white", textAlign: "right" }}>₹{order.costing.making_cost.toLocaleString()}</td>
                          </tr>
                          <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                            <td style={{ padding: "0.8rem 0", color: "var(--text-secondary)" }}>CAD & Setup</td>
                            <td style={{ padding: "0.8rem 0", color: "white", textAlign: "right" }}>₹{order.costing.cad_cost.toLocaleString()}</td>
                          </tr>
                          <tr style={{ borderTop: "1px solid var(--border-subtle)" }}>
                            <td style={{ padding: "1rem 0", color: "white", fontWeight: "bold" }}>Total Manufacturing Cost</td>
                            <td style={{ padding: "1rem 0", color: "white", textAlign: "right", fontWeight: "bold" }}>₹{order.costing.total_cost.toLocaleString()}</td>
                          </tr>
                        </tbody>
                      </table>

                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "rgba(212, 175, 55, 0.05)", padding: "1rem", borderRadius: "var(--radius-sm)", border: "1px solid rgba(212, 175, 55, 0.2)" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                          <span style={{ color: "var(--text-secondary)" }}>Target Margin:</span>
                          <input 
                            type="number" 
                            defaultValue={order.costing.margin_percent} 
                            onBlur={(e) => handleUpdateMargin(e.target.value)}
                            style={{ width: "60px", background: "rgba(0,0,0,0.5)", border: "1px solid var(--border-subtle)", borderRadius: "4px", padding: "0.4rem", color: "white", textAlign: "center" }}
                          /> %
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ color: "var(--text-secondary)", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "1px" }}>Final Selling Price</div>
                          <div style={{ color: "var(--accent-gold)", fontSize: "1.5rem", fontWeight: "bold" }}>₹{order.costing.selling_price.toLocaleString()}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Specs & Attachments Panel */}
                <div style={{ width: "300px", display: "flex", flexDirection: "column", gap: "1rem" }}>
                  <img src={order.approved_sketch?.url} alt="Reference" style={{ width: "100%", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }} />
                  <button className="btn-primary" style={{ width: "100%", justifyContent: "center", background: "transparent", border: "1px solid var(--accent-gold)", color: "var(--accent-gold)" }}>
                    Download STL Mesh
                  </button>
                  
                  {/* Notes Panel */}
                  <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden", marginTop: "1rem" }}>
                    <div style={{ display: "flex", borderBottom: "1px solid var(--border-subtle)", background: "rgba(0,0,0,0.3)" }}>
                      {['internal', 'customer', 'production'].map(tab => (
                        <button 
                          key={tab} 
                          onClick={() => setActiveNoteTab(tab)}
                          style={{ flex: 1, padding: "0.5rem", background: "transparent", border: "none", color: activeNoteTab === tab ? "var(--accent-gold)" : "var(--text-secondary)", fontSize: "0.8rem", cursor: "pointer", borderBottom: activeNoteTab === tab ? "2px solid var(--accent-gold)" : "2px solid transparent", textTransform: "capitalize" }}
                        >
                          {tab}
                        </button>
                      ))}
                    </div>
                    <div style={{ padding: "1rem" }}>
                      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "1rem", minHeight: "40px" }}>
                        {order.notes[activeNoteTab] || `No ${activeNoteTab} notes yet.`}
                      </p>
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        <input 
                          type="text" 
                          value={noteContent}
                          onChange={e => setNoteContent(e.target.value)}
                          placeholder="Add note..."
                          style={{ flex: 1, background: "rgba(0,0,0,0.5)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: "0.4rem", color: "white", fontSize: "0.8rem" }}
                        />
                        <button className="btn-primary" style={{ padding: "0.4rem 0.8rem", fontSize: "0.8rem" }} onClick={handleAddNote}>Save</button>
                      </div>
                    </div>
                  </div>

                  {/* Attachments UI Mock */}
                  <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", padding: "1rem" }}>
                    <h4 style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <Paperclip size={14} /> Attachments ({order.attachments?.length || 0})
                    </h4>
                    {order.attachments?.map((att, i) => (
                      <div key={i} style={{ fontSize: "0.8rem", color: "white", padding: "0.5rem", background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-sm)", marginBottom: "0.5rem", display: "flex", justifyContent: "space-between" }}>
                        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{att.filename}</span>
                      </div>
                    ))}
                    <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileUpload} />
                    <button 
                      onClick={() => fileInputRef.current.click()}
                      style={{ width: "100%", padding: "1.5rem", background: "rgba(0,0,0,0.3)", border: "1px dashed var(--border-subtle)", borderRadius: "var(--radius-sm)", color: "var(--text-secondary)", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem", transition: "all 0.2s" }}
                      onMouseEnter={e => e.target.style.borderColor = "var(--accent-gold)"}
                      onMouseLeave={e => e.target.style.borderColor = "var(--border-subtle)"}
                    >
                      <Upload size={20} />
                      <span style={{ fontSize: "0.8rem" }}>Upload File</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Activity Timeline Sidebar */}
        <div className="glass-panel" style={{ width: "380px", minHeight: "500px", padding: "1.5rem" }}>
          <h3 style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: "1rem", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "white" }}>
            <Clock size={18}/> Activity Timeline
          </h3>
          
          {!order || order.approval_ledger.length === 0 ? (
            <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", textAlign: "center", marginTop: "2rem" }}>No activity recorded yet.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              {order.approval_ledger.slice().reverse().map((event, i) => (
                <div key={i} style={{ borderLeft: "2px solid var(--border-subtle)", paddingLeft: "1.2rem", position: "relative" }}>
                  <div style={{ position: "absolute", left: "-6px", top: "4px", width: "10px", height: "10px", borderRadius: "50%", background: event.action.includes("Approved") ? "#4ade80" : "var(--accent-gold)", boxShadow: `0 0 8px ${event.action.includes("Approved") ? "#4ade80" : "var(--accent-gold)"}` }}></div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.2rem" }}>
                    <p style={{ fontWeight: "600", color: "white", fontSize: "0.9rem" }}>{event.action}</p>
                    <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
                      {new Date(event.timestamp * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </p>
                  </div>
                  
                  {event.approved_by && (
                    <span className="badge" style={{ marginTop: "0.5rem", display: "inline-block", fontSize: "0.7rem", padding: "0.2rem 0.5rem" }}>By: {event.approved_by}</span>
                  )}
                  {event.remarks && (
                    <p style={{ fontSize: "0.85rem", fontStyle: "italic", background: "rgba(0,0,0,0.4)", padding: "0.6rem", borderRadius: "var(--radius-sm)", marginTop: "0.5rem", borderLeft: "2px solid var(--border-subtle)" }}>
                      "{event.remarks}"
                    </p>
                  )}
                  {event.version && (
                    <p style={{ fontSize: "0.75rem", color: "var(--accent-gold)", marginTop: "0.5rem" }}>Revision: v{event.version}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
