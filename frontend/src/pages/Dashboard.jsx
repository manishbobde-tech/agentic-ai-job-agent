import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Building2, ExternalLink, Loader2, Filter } from 'lucide-react';
import axios from 'axios';

const API = 'http://localhost:8000';

export default function Dashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('Agentic AI Engineer');
  const [searched, setSearched] = useState(false);
  const [filter, setFilter] = useState('all');

  const searchJobs = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/search`, {
        query,
        num_results: 20,
      });
      setJobs(res.data.jobs);
      setSearched(true);
    } catch (err) {
      console.error('Search error:', err);
    }
    setLoading(false);
  };

  const getSourceColor = (source) => {
    const colors = {
      LinkedIn: '#0a66c2',
      Indeed: '#2164f3',
      Glassdoor: '#0caa41',
      Web: '#6366f1',
    };
    return colors[source] || '#6366f1';
  };

  const filteredJobs = filter === 'all' 
    ? jobs 
    : jobs.filter(j => j.source.toLowerCase() === filter);

  return (
    <div>
      {/* Search Header */}
      <div style={{
        background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)',
        borderRadius: '16px',
        padding: '32px',
        marginBottom: '24px',
      }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
          Find Your Next Agentic AI Role
        </h1>
        <p style={{ color: '#a1a1aa', marginBottom: '20px' }}>
          Search across LinkedIn, Indeed, and the web
        </p>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            background: '#27272a',
            borderRadius: '10px',
            padding: '0 16px',
            border: '1px solid #3f3f46',
          }}>
            <Search size={20} color="#a1a1aa" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchJobs()}
              placeholder="Search for jobs..."
              style={{
                flex: 1,
                background: 'none',
                border: 'none',
                outline: 'none',
                color: '#e4e4e7',
                padding: '14px 12px',
                fontSize: '15px',
              }}
            />
          </div>
          <button
            onClick={searchJobs}
            disabled={loading}
            style={{
              background: '#6366f1',
              color: '#fff',
              border: 'none',
              borderRadius: '10px',
              padding: '14px 28px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
            Search
          </button>
        </div>
      </div>

      {/* Filters */}
      {searched && (
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '20px',
          flexWrap: 'wrap',
        }}>
          {['all', 'linkedin', 'indeed', 'web'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: '1px solid #3f3f46',
                background: filter === f ? '#6366f1' : '#27272a',
                color: filter === f ? '#fff' : '#a1a1aa',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 500,
                textTransform: 'capitalize',
              }}
            >
              {f === 'all' ? `All (${jobs.length})` : f}
            </button>
          ))}
        </div>
      )}

      {/* Job Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <Loader2 size={40} className="animate-spin" style={{ margin: '0 auto 16px' }} />
          <p>Searching for jobs...</p>
        </div>
      ) : filteredJobs.length > 0 ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '16px',
        }}>
          {filteredJobs.map((job, index) => (
            <div
              key={index}
              onClick={() => navigate(`/job/${jobs.indexOf(job)}`)}
              style={{
                background: '#18181b',
                border: '1px solid #3f3f46',
                borderRadius: '12px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#6366f1';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#3f3f46';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  padding: '4px 10px',
                  borderRadius: '12px',
                  background: getSourceColor(job.source) + '20',
                  color: getSourceColor(job.source),
                }}>
                  {job.source}
                </span>
                <ExternalLink size={16} color="#a1a1aa" />
              </div>

              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px', lineHeight: '1.4' }}>
                {job.title}
              </h3>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#a1a1aa', fontSize: '13px' }}>
                  <Building2 size={14} />
                  {job.company}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#a1a1aa', fontSize: '13px' }}>
                  <MapPin size={14} />
                  {job.location}
                </div>
              </div>

              {job.snippet && (
                <p style={{
                  fontSize: '13px',
                  color: '#71717a',
                  lineHeight: '1.5',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {job.snippet}
                </p>
              )}

              {job.skills && job.skills.length > 0 && (
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '12px' }}>
                  {job.skills.slice(0, 4).map((skill, i) => (
                    <span key={i} style={{
                      fontSize: '11px',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      background: '#27272a',
                      color: '#a1a1aa',
                    }}>
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : searched ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <p style={{ fontSize: '18px' }}>No jobs found. Try a different search.</p>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <Search size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
          <p style={{ fontSize: '18px' }}>Search for Agentic AI Engineer jobs</p>
          <p style={{ fontSize: '14px', marginTop: '8px' }}>
            Results from LinkedIn, Indeed, and the web
          </p>
        </div>
      )}
    </div>
  );
}
