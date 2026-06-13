import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Building2, MapPin, Loader2, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API = 'http://localhost:8000';

export default function JobView() {
  const { index } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    loadJob();
  }, [index]);

  const loadJob = async () => {
    setLoading(true);
    try {
      const cacheRes = await axios.get(`${API}/api/jobs/cache`);
      if (cacheRes.data.jobs[index]) {
        setJob(cacheRes.data.jobs[index]);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const scrapeFullDescription = async () => {
    setScraping(true);
    try {
      const res = await axios.post(`${API}/api/scrape/${index}`);
      setJob(res.data);
    } catch (err) {
      console.error(err);
    }
    setScraping(false);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
        <Loader2 size={40} className="animate-spin" style={{ margin: '0 auto 16px' }} />
        <p>Loading job details...</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
        <p>Job not found.</p>
        <Link to="/" style={{ color: '#6366f1', marginTop: '16px', display: 'inline-block' }}>
          Back to Search
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'none',
          border: 'none',
          color: '#a1a1aa',
          cursor: 'pointer',
          fontSize: '14px',
          marginBottom: '20px',
          padding: '8px 0',
        }}
      >
        <ArrowLeft size={18} />
        Back to jobs
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: '24px' }}>
        {/* Main Content */}
        <div>
          {/* Header */}
          <div style={{
            background: '#18181b',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #3f3f46',
            marginBottom: '16px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px' }}>
                  {job.title}
                </h1>
                <div style={{ display: 'flex', gap: '16px', color: '#a1a1aa', fontSize: '14px' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Building2 size={16} /> {job.company}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={16} /> {job.location}
                  </span>
                </div>
              </div>
              <span style={{
                fontSize: '12px',
                fontWeight: 600,
                padding: '6px 12px',
                borderRadius: '8px',
                background: '#6366f120',
                color: '#6366f1',
              }}>
                {job.source}
              </span>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 24px',
                  background: '#6366f1',
                  color: '#fff',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: 600,
                  fontSize: '14px',
                }}
              >
                <ExternalLink size={16} />
                Apply Now
              </a>
              <button
                onClick={scrapeFullDescription}
                disabled={scraping}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 24px',
                  background: '#27272a',
                  color: '#e4e4e7',
                  border: '1px solid #3f3f46',
                  borderRadius: '8px',
                  cursor: scraping ? 'not-allowed' : 'pointer',
                  fontWeight: 500,
                  fontSize: '14px',
                }}
              >
                {scraping ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
                {scraping ? 'Loading...' : 'Get Full Description'}
              </button>
            </div>
          </div>

          {/* Description */}
          <div style={{
            background: '#18181b',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #3f3f46',
          }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
              Job Description
            </h2>
            {job.full_description ? (
              <div style={{
                fontSize: '14px',
                lineHeight: '1.8',
                color: '#d4d4d8',
                whiteSpace: 'pre-wrap',
              }}>
                {job.full_description}
              </div>
            ) : job.snippet ? (
              <p style={{ fontSize: '14px', lineHeight: '1.8', color: '#d4d4d8' }}>
                {job.snippet}
              </p>
            ) : (
              <p style={{ color: '#71717a' }}>
                Click "Get Full Description" to load the complete job posting.
              </p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div>
          {/* Quick Actions */}
          <div style={{
            background: '#18181b',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #3f3f46',
            marginBottom: '16px',
          }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#a1a1aa' }}>
              Quick Actions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Link
                to="/resume"
                state={{ job }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px',
                  background: '#27272a',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color: '#e4e4e7',
                  fontSize: '14px',
                }}
              >
                <FileText size={16} color="#6366f1" />
                Match My Resume
              </Link>
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px',
                  background: '#27272a',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color: '#e4e4e7',
                  fontSize: '14px',
                }}
              >
                <ExternalLink size={16} color="#22c55e" />
                Apply on {job.source}
              </a>
            </div>
          </div>

          {/* Requirements */}
          {job.requirements && job.requirements.length > 0 && (
            <div style={{
              background: '#18181b',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #3f3f46',
              marginBottom: '16px',
            }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#a1a1aa' }}>
                Requirements
              </h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {job.requirements.map((req, i) => (
                  <li key={i} style={{
                    display: 'flex',
                    gap: '8px',
                    padding: '8px 0',
                    borderBottom: i < job.requirements.length - 1 ? '1px solid #27272a' : 'none',
                    fontSize: '13px',
                    color: '#d4d4d8',
                  }}>
                    <CheckCircle2 size={14} color="#22c55e" style={{ flexShrink: 0, marginTop: '2px' }} />
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Responsibilities */}
          {job.responsibilities && job.responsibilities.length > 0 && (
            <div style={{
              background: '#18181b',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #3f3f46',
            }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#a1a1aa' }}>
                Responsibilities
              </h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {job.responsibilities.map((resp, i) => (
                  <li key={i} style={{
                    display: 'flex',
                    gap: '8px',
                    padding: '8px 0',
                    borderBottom: i < job.responsibilities.length - 1 ? '1px solid #27272a' : 'none',
                    fontSize: '13px',
                    color: '#d4d4d8',
                  }}>
                    <AlertCircle size={14} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
                    {resp}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
