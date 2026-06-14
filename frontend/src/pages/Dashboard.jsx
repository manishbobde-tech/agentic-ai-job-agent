import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Building2, ExternalLink, Loader2, Globe, Filter, Home, X } from 'lucide-react';
import axios from 'axios';

const API = 'http://localhost:8000';

const USA_STATES = [
  "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
  "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
  "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
  "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
  "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
  "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
  "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
  "Wisconsin", "Wyoming"
];

const STATE_CITIES = {
  "California": ["San Francisco", "Los Angeles", "San Diego", "San Jose", "Sacramento", "Palo Alto", "Mountain View", "Santa Clara", "Irvine", "San Mateo"],
  "New York": ["New York City", "Manhattan", "Brooklyn", "Buffalo", "Albany", "Long Island"],
  "Texas": ["Austin", "Houston", "Dallas", "San Antonio", "Fort Worth", "Plano"],
  "Washington": ["Seattle", "Bellevue", "Redmond", "Tacoma", "Spokane"],
  "Massachusetts": ["Boston", "Cambridge", "Somerville", "Worcester", "Springfield"],
  "Colorado": ["Denver", "Boulder", "Colorado Springs", "Fort Collins"],
  "Illinois": ["Chicago", "Naperville", "Aurora", "Springfield"],
  "Georgia": ["Atlanta", "Savannah", "Augusta", "Athens"],
  "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
  "North Carolina": ["Charlotte", "Raleigh", "Durham", "Chapel Hill"],
  "Virginia": ["Arlington", "Alexandria", "Richmond", "Virginia Beach"],
  "Oregon": ["Portland", "Eugene", "Salem", "Bend"],
  "Arizona": ["Phoenix", "Scottsdale", "Tucson", "Chandler"],
  "Michigan": ["Detroit", "Ann Arbor", "Grand Rapids", "Lansing"],
  "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
  "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
  "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
  "Minnesota": ["Minneapolis", "St. Paul", "Rochester", "Bloomington"],
  "Maryland": ["Baltimore", "Bethesda", "Rockville", "Columbia"],
  "Missouri": ["Kansas City", "St. Louis", "Springfield", "Columbia"],
  "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha"],
  "Remote": ["Remote"]
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('Agentic AI Engineer');
  const [searched, setSearched] = useState(false);
  
  // Location filters
  const [country, setCountry] = useState('USA');
  const [state, setState] = useState('');
  const [city, setCity] = useState('');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [showFilters, setShowFilters] = useState(true);
  
  const [availableCities, setAvailableCities] = useState([]);

  useEffect(() => {
    if (state && STATE_CITIES[state]) {
      setAvailableCities(STATE_CITIES[state]);
      setCity('');
    } else {
      setAvailableCities([]);
      setCity('');
    }
  }, [state]);

  const searchJobs = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/search`, {
        query,
        country,
        state,
        city,
        remote_only: remoteOnly,
        num_results: 20,
      });
      setJobs(res.data.jobs);
      setSearched(true);
    } catch (err) {
      console.error('Search error:', err);
    }
    setLoading(false);
  };

  const clearFilters = () => {
    setState('');
    setCity('');
    setRemoteOnly(false);
  };

  const getSourceColor = (source) => {
    const colors = {
      LinkedIn: '#0a66c2',
      Indeed: '#2164f3',
      Glassdoor: '#0caa41',
      BuiltIn: '#f26522',
      Dice: '#006aff',
      Web: '#6366f1',
    };
    return colors[source] || '#6366f1';
  };

  const filteredJobs = jobs;

  return (
    <div>
      {/* Search Header */}
      <div style={{
        background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)',
        borderRadius: '16px',
        padding: '32px',
        marginBottom: '24px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Globe size={28} color="#818cf8" />
          <h1 style={{ fontSize: '28px', fontWeight: 700 }}>Find AI Jobs in the USA</h1>
        </div>
        <p style={{ color: '#a1a1aa', marginBottom: '20px' }}>
          Search across LinkedIn, Indeed, BuiltIn, and more
        </p>
        
        {/* Main Search */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
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
              placeholder="Job title or keyword..."
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
            onClick={() => setShowFilters(!showFilters)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '14px 20px',
              background: showFilters ? '#6366f1' : '#27272a',
              color: showFilters ? '#fff' : '#a1a1aa',
              border: '1px solid #3f3f46',
              borderRadius: '10px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
            }}
          >
            <Filter size={16} />
            Filters
          </button>
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
            Search Jobs
          </button>
        </div>

        {/* Location Filters */}
        {showFilters && (
          <div style={{
            background: '#27272a',
            borderRadius: '12px',
            padding: '16px',
            border: '1px solid #3f3f46',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MapPin size={16} color="#818cf8" />
                <span style={{ fontSize: '14px', fontWeight: 600 }}>Location Filters</span>
              </div>
              {(state || city || remoteOnly) && (
                <button
                  onClick={clearFilters}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    background: 'none',
                    border: 'none',
                    color: '#818cf8',
                    cursor: 'pointer',
                    fontSize: '12px',
                  }}
                >
                  <X size={12} /> Clear
                </button>
              )}
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
              {/* Country */}
              <div>
                <label style={{ fontSize: '12px', color: '#a1a1aa', marginBottom: '6px', display: 'block' }}>
                  Country
                </label>
                <select
                  value={country}
                  onChange={(e) => { setCountry(e.target.value); setState(''); setCity(''); }}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#18181b',
                    border: '1px solid #3f3f46',
                    borderRadius: '8px',
                    color: '#e4e4e7',
                    fontSize: '14px',
                    outline: 'none',
                    cursor: 'pointer',
                  }}
                >
                  <option value="USA">🇺🇸 United States</option>
                  <option value="Remote">🌍 Remote Only</option>
                </select>
              </div>

              {/* State */}
              <div>
                <label style={{ fontSize: '12px', color: '#a1a1aa', marginBottom: '6px', display: 'block' }}>
                  State
                </label>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#18181b',
                    border: '1px solid #3f3f46',
                    borderRadius: '8px',
                    color: '#e4e4e7',
                    fontSize: '14px',
                    outline: 'none',
                    cursor: 'pointer',
                  }}
                >
                  <option value="">All States</option>
                  {USA_STATES.map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* City */}
              <div>
                <label style={{ fontSize: '12px', color: '#a1a1aa', marginBottom: '6px', display: 'block' }}>
                  City
                </label>
                <select
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  disabled={!state}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: '#18181b',
                    border: '1px solid #3f3f46',
                    borderRadius: '8px',
                    color: state ? '#e4e4e7' : '#52525b',
                    fontSize: '14px',
                    outline: 'none',
                    cursor: state ? 'pointer' : 'not-allowed',
                  }}
                >
                  <option value="">{state ? 'All Cities' : 'Select state first'}</option>
                  {availableCities.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              {/* Remote Toggle */}
              <div>
                <label style={{ fontSize: '12px', color: '#a1a1aa', marginBottom: '6px', display: 'block' }}>
                  Job Type
                </label>
                <button
                  onClick={() => setRemoteOnly(!remoteOnly)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    background: remoteOnly ? '#22c55e20' : '#18181b',
                    border: `1px solid ${remoteOnly ? '#22c55e' : '#3f3f46'}`,
                    borderRadius: '8px',
                    color: remoteOnly ? '#22c55e' : '#e4e4e7',
                    fontSize: '14px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                  }}
                >
                  <Home size={16} />
                  {remoteOnly ? 'Remote Only' : 'All Types'}
                </button>
              </div>
            </div>

            {/* Active Filters */}
            {(state || city || remoteOnly) && (
              <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {state && (
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    background: '#6366f120',
                    color: '#818cf8',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <MapPin size={12} /> {state}
                    <X size={12} style={{ cursor: 'pointer' }} onClick={() => { setState(''); setCity(''); }} />
                  </span>
                )}
                {city && (
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    background: '#22c55e20',
                    color: '#22c55e',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <Building2 size={12} /> {city}
                    <X size={12} style={{ cursor: 'pointer' }} onClick={() => setCity('')} />
                  </span>
                )}
                {remoteOnly && (
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    background: '#f59e0b20',
                    color: '#f59e0b',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <Home size={12} /> Remote
                    <X size={12} style={{ cursor: 'pointer' }} onClick={() => setRemoteOnly(false)} />
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Source Filters */}
      {searched && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px',
        }}>
          <p style={{ color: '#a1a1aa', fontSize: '14px' }}>
            Found <span style={{ color: '#e4e4e7', fontWeight: 600 }}>{filteredJobs.length}</span> jobs
            {state && ` in ${state}`}
            {city && `, ${city}`}
            {remoteOnly && ' (Remote)'}
          </p>
        </div>
      )}

      {/* Job Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <Loader2 size={40} className="animate-spin" style={{ margin: '0 auto 16px' }} />
          <p>Searching for jobs in {state || 'all locations'}...</p>
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
                position: 'relative',
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
              {/* Remote Badge */}
              {job.remote && (
                <div style={{
                  position: 'absolute',
                  top: '12px',
                  right: '12px',
                  padding: '4px 8px',
                  borderRadius: '6px',
                  background: '#22c55e20',
                  color: '#22c55e',
                  fontSize: '11px',
                  fontWeight: 600,
                }}>
                  Remote
                </div>
              )}

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
              </div>

              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px', lineHeight: '1.4', paddingRight: job.remote ? '60px' : 0 }}>
                {job.title}
              </h3>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#a1a1aa', fontSize: '13px' }}>
                  <Building2 size={14} />
                  {job.company}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#a1a1aa', fontSize: '13px' }}>
                  <MapPin size={14} />
                  {job.location || 'Not specified'}
                </div>
              </div>

              {job.snippet && (
                <p style={{
                  fontSize: '13px',
                  color: '#71717a',
                  lineHeight: '1.5',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
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

              <div style={{
                marginTop: '12px',
                paddingTop: '12px',
                borderTop: '1px solid #27272a',
                display: 'flex',
                justifyContent: 'flex-end',
              }}>
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  color: '#6366f1',
                  fontSize: '13px',
                  fontWeight: 500,
                }}>
                  View Details <ExternalLink size={12} />
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : searched ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <MapPin size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
          <p style={{ fontSize: '18px' }}>No jobs found in this location</p>
          <p style={{ fontSize: '14px', marginTop: '8px' }}>Try a different state, city, or remote filter</p>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <Globe size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
          <p style={{ fontSize: '18px' }}>Search for AI jobs in the USA</p>
          <p style={{ fontSize: '14px', marginTop: '8px' }}>
            Filter by state, city, or remote positions
          </p>
        </div>
      )}
    </div>
  );
}
