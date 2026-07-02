import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Filter, MoreHorizontal, Eye, Download } from 'lucide-react';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('All');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/orders')
      .then(res => res.json())
      .then(data => {
        setOrders(data);
        setLoading(false);
      });
  }, []);

  const getStatusColor = (status) => {
    const s = status.toLowerCase();
    if (s.includes('received')) return { bg: 'rgba(255,255,255,0.1)', color: 'white' };
    if (s.includes('review') || s.includes('sketch')) return { bg: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' };
    if (s.includes('approved') || s.includes('order created')) return { bg: 'rgba(212, 175, 55, 0.2)', color: 'var(--accent-gold)' };
    if (s.includes('qc') || s.includes('dispatch')) return { bg: 'rgba(74, 222, 128, 0.2)', color: '#4ade80' };
    return { bg: 'rgba(167, 139, 250, 0.2)', color: '#c084fc' }; // Manufacturing states
  };

  const filteredOrders = orders.filter(o => {
    if (filter === 'All') return true;
    if (filter === 'Design') return o.status.includes('Requirement') || o.status.includes('Sketch');
    if (filter === 'CAD') return o.status.includes('CAD');
    if (filter === 'Manufacturing') return !['Requirement Received', 'Sketch Review', 'Sketch Approved', 'CAD Review', 'CAD Approved'].includes(o.status);
    return true;
  });

  const handleExportCSV = () => {
    const headers = ['Order ID', 'Requirement', 'Category', 'Status', 'Version', 'Last Updated'];
    const csvContent = [
      headers.join(','),
      ...filteredOrders.map(o => 
        `"${o.id}","${o.requirement.replace(/"/g, '""')}","${o.category}","${o.status}","${o.version}","${new Date(o.updated_at * 1000).toLocaleDateString()}"`
      )
    ].join('\\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `ornexa_orders_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <div>
          <h1 className="title" style={{ marginBottom: "0.5rem" }}>Order Management</h1>
          <p className="subtitle">Track and manage all custom manufacturing workflows.</p>
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button className="btn-primary" style={{ background: "transparent", border: "1px solid var(--border-subtle)", color: "white" }} onClick={handleExportCSV}>
            <Download size={16} style={{ marginRight: "0.5rem" }} /> Export CSV
          </button>
          <button className="btn-primary" onClick={() => navigate('/studio')}>
            + New Custom Order
          </button>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
        {['All', 'Design', 'CAD', 'Manufacturing'].map(f => (
          <button 
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: "0.5rem 1.5rem",
              borderRadius: "50px",
              background: filter === f ? "var(--accent-gold)" : "rgba(255,255,255,0.05)",
              color: filter === f ? "var(--bg-obsidian)" : "var(--text-secondary)",
              border: `1px solid ${filter === f ? "var(--accent-gold)" : "var(--border-subtle)"}`,
              cursor: "pointer",
              fontWeight: filter === f ? "bold" : "normal",
              transition: "all 0.2s"
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Orders Table */}
      <div className="glass-panel" style={{ padding: "0" }}>
        {loading ? (
          <div style={{ padding: "3rem", textAlign: "center" }}><span className="loader"></span></div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                <th style={{ padding: "1.5rem" }}>Order ID</th>
                <th style={{ padding: "1.5rem" }}>Requirement Brief</th>
                <th style={{ padding: "1.5rem" }}>Category</th>
                <th style={{ padding: "1.5rem" }}>Status</th>
                <th style={{ padding: "1.5rem" }}>Version</th>
                <th style={{ padding: "1.5rem" }}>Last Updated</th>
                <th style={{ padding: "1.5rem" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map(order => {
                const colors = getStatusColor(order.status);
                return (
                  <tr key={order.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)", transition: "background 0.2s" }} className="table-row-hover">
                    <td style={{ padding: "1.5rem", fontWeight: "bold", color: "white" }}>{order.id}</td>
                    <td style={{ padding: "1.5rem", maxWidth: "250px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {order.requirement}
                    </td>
                    <td style={{ padding: "1.5rem", color: "var(--text-secondary)" }}>{order.category}</td>
                    <td style={{ padding: "1.5rem" }}>
                      <span style={{ 
                        background: colors.bg, color: colors.color, padding: "0.4rem 0.8rem", 
                        borderRadius: "50px", fontSize: "0.8rem", fontWeight: "600" 
                      }}>
                        {order.status}
                      </span>
                    </td>
                    <td style={{ padding: "1.5rem", color: "var(--text-secondary)" }}>v{order.version}</td>
                    <td style={{ padding: "1.5rem", color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                      {new Date(order.updated_at * 1000).toLocaleDateString()}
                    </td>
                    <td style={{ padding: "1.5rem" }}>
                      <button 
                        onClick={() => navigate(`/studio?orderId=${order.id}`)}
                        style={{ background: "transparent", border: "none", color: "var(--accent-gold)", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem" }}
                      >
                        <Eye size={16} /> Open
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
        
        {!loading && filteredOrders.length === 0 && (
          <div style={{ padding: "3rem", textAlign: "center", color: "var(--text-secondary)" }}>
            <FileText size={48} style={{ opacity: 0.3, marginBottom: "1rem" }} />
            <p>No orders found for this filter.</p>
          </div>
        )}
      </div>
      
      <style>{`
        .table-row-hover:hover {
          background: rgba(255,255,255,0.02);
        }
      `}</style>
    </div>
  );
}
