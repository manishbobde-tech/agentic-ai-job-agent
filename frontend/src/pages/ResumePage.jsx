import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { FileText, Zap, CheckCircle, AlertTriangle, ArrowRight, Loader2, Copy, Download } from 'lucide-react';
import axios from 'axios';

const API = 'http://localhost:8000';

export default function ResumePage() {
  const location = useLocation();
  const passedJob = location.state?.job;

  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState(passedJob?.full_description || passedJob?.snippet || '');
  const [jobTitle, setJobTitle] = useState(passedJob?.title || '');
  const [analysis, setAnalysis] = useState(null);
  const [tailored, setTailored] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('analyze');

  const analyzeMatch = async () => {
    if (!resumeText || !jobDescription) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/match`, {
        resume_text: resumeText,
        job_description: jobDescription,
        job_title: jobTitle,
      });
      setAnalysis(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const tailorResume = async () => {
    if (!resumeText || !jobDescription) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/tailor`, {
        resume_text: resumeText,
        job_description: jobDescription,
        job_title: jobTitle,
        instructions: 'Make it ATS-friendly, highlight relevant experience, add missing keywords naturally.',
      });
      setTailored(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>
        Resume Matcher & Tailor
      </h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
        {/* Resume Input */}
        <div style={{
          background: '#18181b',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid #3f3f46',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <FileText size={18} color="#6366f1" />
            <h3 style={{ fontSize: '14px', fontWeight: 600 }}>Your Resume</h3>
          </div>
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume here...

Example:
EXPERIENCE
Software Engineer | Google | 2020-2023
- Built ML pipelines using Python and TensorFlow
- Deployed LLM-powered features serving 10M+ users

SKILLS
Python, TypeScript, React, AWS, Docker, LangChain"
            style={{
              width: '100%',
              height: '300px',
              background: '#27272a',
              border: '1px solid #3f3f46',
              borderRadius: '8px',
              padding: '12px',
              color: '#e4e4e7',
              fontSize: '13px',
              fontFamily: 'monospace',
              resize: 'vertical',
              outline: 'none',
            }}
          />
        </div>

        {/* Job Description Input */}
        <div style={{
          background: '#18181b',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid #3f3f46',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Zap size={18} color="#f59e0b" />
            <h3 style={{ fontSize: '14px', fontWeight: 600 }}>Job Description</h3>
          </div>
          {passedJob && (
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="Job Title"
              style={{
                width: '100%',
                background: '#27272a',
                border: '1px solid #3f3f46',
                borderRadius: '8px',
                padding: '10px 12px',
                color: '#e4e4e7',
                fontSize: '13px',
                marginBottom: '8px',
                outline: 'none',
              }}
            />
          )}
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here...

The job description will be analyzed to:
- Match your skills against requirements
- Identify missing keywords
- Tailor your resume for ATS"
            style={{
              width: '100%',
              height: '280px',
              background: '#27272a',
              border: '1px solid #3f3f46',
              borderRadius: '8px',
              padding: '12px',
              color: '#e4e4e7',
              fontSize: '13px',
              fontFamily: 'monospace',
              resize: 'vertical',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <button
          onClick={analyzeMatch}
          disabled={loading || !resumeText || !jobDescription}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: '#6366f1',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading || !resumeText || !jobDescription ? 0.5 : 1,
          }}
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
          Analyze Match
        </button>
        <button
          onClick={tailorResume}
          disabled={loading || !resumeText || !jobDescription}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 24px',
            background: '#22c55e',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading || !resumeText || !jobDescription ? 0.5 : 1,
          }}
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
          Tailor My Resume
        </button>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div style={{
          background: '#18181b',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #3f3f46',
          marginBottom: '16px',
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>Analysis Results</h2>
          
          {/* Score */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '20px',
            padding: '16px',
            background: '#27272a',
            borderRadius: '8px',
          }}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              border: `4px solid ${getScoreColor(analysis.match_score)}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: 700,
              color: getScoreColor(analysis.match_score),
            }}>
              {analysis.match_score}%
            </div>
            <div>
              <p style={{ fontWeight: 600, marginBottom: '4px' }}>Match Score</p>
              <p style={{ color: '#a1a1aa', fontSize: '13px' }}>
                {analysis.match_score >= 80 ? 'Great match! Your resume aligns well.' :
                 analysis.match_score >= 50 ? 'Good match. Some improvements possible.' :
                 'Needs work. Add more relevant keywords.'}
              </p>
            </div>
          </div>

          {/* Summary */}
          {analysis.summary && (
            <p style={{ marginBottom: '16px', color: '#d4d4d8', lineHeight: '1.6' }}>
              {analysis.summary}
            </p>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {/* Matched Skills */}
            {analysis.matched_skills?.length > 0 && (
              <div>
                <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#22c55e', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle size={14} /> Matched Skills
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {analysis.matched_skills.map((skill, i) => (
                    <span key={i} style={{
                      padding: '4px 10px',
                      borderRadius: '6px',
                      background: '#22c55e20',
                      color: '#22c55e',
                      fontSize: '12px',
                    }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Skills */}
            {analysis.missing_skills?.length > 0 && (
              <div>
                <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#ef4444', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={14} /> Missing Skills
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {analysis.missing_skills.map((skill, i) => (
                    <span key={i} style={{
                      padding: '4px 10px',
                      borderRadius: '6px',
                      background: '#ef444420',
                      color: '#ef4444',
                      fontSize: '12px',
                    }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths */}
            {analysis.strengths?.length > 0 && (
              <div>
                <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#22c55e', marginBottom: '8px' }}>
                  Strengths
                </h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {analysis.strengths.map((s, i) => (
                    <li key={i} style={{ fontSize: '13px', color: '#d4d4d8', padding: '4px 0' }}>
                      • {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Improvements */}
            {analysis.improvements?.length > 0 && (
              <div>
                <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#f59e0b', marginBottom: '8px' }}>
                  Suggested Improvements
                </h4>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {analysis.improvements.map((imp, i) => (
                    <li key={i} style={{ fontSize: '13px', color: '#d4d4d8', padding: '4px 0' }}>
                      • {imp}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Keywords to Add */}
          {analysis.keywords_to_add?.length > 0 && (
            <div style={{ marginTop: '16px', padding: '12px', background: '#27272a', borderRadius: '8px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#6366f1', marginBottom: '8px' }}>
                Keywords to Add to Resume
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {analysis.keywords_to_add.map((kw, i) => (
                  <span key={i} style={{
                    padding: '4px 10px',
                    borderRadius: '6px',
                    background: '#6366f120',
                    color: '#6366f1',
                    fontSize: '12px',
                  }}>
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tailored Resume */}
      {tailored && (
        <div style={{
          background: '#18181b',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #22c55e',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: 600 }}>Tailored Resume</h2>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => copyToClipboard(tailored.tailored_resume)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  background: '#27272a',
                  border: '1px solid #3f3f46',
                  borderRadius: '6px',
                  color: '#e4e4e7',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                <Copy size={14} /> Copy
              </button>
              <button
                onClick={() => {
                  const blob = new Blob([tailored.tailored_resume], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'tailored_resume.txt';
                  a.click();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  background: '#22c55e',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 600,
                }}
              >
                <Download size={14} /> Download
              </button>
            </div>
          </div>

          <textarea
            value={tailored.tailored_resume}
            onChange={(e) => setTailored({ ...tailored, tailored_resume: e.target.value })}
            style={{
              width: '100%',
              minHeight: '400px',
              background: '#27272a',
              border: '1px solid #3f3f46',
              borderRadius: '8px',
              padding: '16px',
              color: '#e4e4e7',
              fontSize: '13px',
              fontFamily: 'monospace',
              lineHeight: '1.6',
              resize: 'vertical',
              outline: 'none',
            }}
          />

          {/* Changes Made */}
          {tailored.changes_made?.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>Changes Made</h4>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {tailored.changes_made.map((change, i) => (
                  <li key={i} style={{
                    fontSize: '13px',
                    color: '#d4d4d8',
                    padding: '6px 0',
                    borderBottom: '1px solid #27272a',
                  }}>
                    ✓ {change}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Tips */}
          {tailored.tips?.length > 0 && (
            <div style={{ marginTop: '16px', padding: '12px', background: '#27272a', borderRadius: '8px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>Pro Tips</h4>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {tailored.tips.map((tip, i) => (
                  <li key={i} style={{ fontSize: '13px', color: '#a1a1aa', padding: '4px 0' }}>
                    💡 {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
