import { useMemo, useRef, useState } from 'react';
import {
  AlertCircle, ArrowLeft, BarChart3, CheckCircle2, ChevronDown, CircleHelp,
  FileText, Gauge, Lightbulb, Loader2, Mail, Menu, Search, ShieldCheck,
  Sparkles, Target, TrendingUp, Upload, X, Zap
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const demo = {
  ats_score: 78,
  grammar_analysis: [
    { issue: 'Weak action verb', explanation: 'Use a stronger verb to make the accomplishment more direct.', original_text: 'Worked on a web application', suggested_text: 'Developed a web application', severity: 'Medium' },
    { issue: 'Missing punctuation', explanation: 'Consistent punctuation improves readability and polish.', original_text: 'Built REST APIs using Node.js', suggested_text: 'Built REST APIs using Node.js.', severity: 'Low' }
  ],
  skills_analysis: {
    matched_skills: ['React', 'JavaScript', 'Node.js', 'SQL', 'Git'],
    missing_skills: ['Docker', 'AWS', 'CI/CD'],
    skills_to_improve: ['TypeScript', 'System Design'],
    gaps_explanation: 'The resume shows a strong full-stack foundation. Adding cloud, deployment and typed-JavaScript experience would improve alignment for modern software roles.'
  },
  improvement_suggestions: [
    { category: 'Content', suggestion: 'Add measurable outcomes to project bullets, such as users, latency, revenue, or performance improvements.', impact: 'High' },
    { category: 'Keywords', suggestion: 'Mirror important terms from the target job description where they accurately describe your experience.', impact: 'High' },
    { category: 'Formatting', suggestion: 'Keep section headings, dates and bullet indentation consistent throughout the document.', impact: 'Medium' }
  ],
  job_matching: {
    match_percentage: 82,
    fit_level: 'Good Match',
    strengths: ['Strong JavaScript and React alignment', 'Relevant backend/API experience', 'Projects demonstrate practical development'],
    gaps: ['Cloud deployment is not clearly demonstrated', 'CI/CD keywords are absent'],
    interview_questions: ['Explain one project where you improved performance.', 'How would you design authentication for a production API?', 'How have you used Git in a team development workflow?']
  },
  resume_details: {
    name: 'Demo Candidate',
    email: 'candidate@example.com',
    phone: '+91 98765 43210',
    summary: 'Full-stack developer with practical experience building web applications and APIs.'
  }
};

function ScoreRing({ score, label = 'ATS Score' }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const dash = (Math.max(0, Math.min(100, score)) / 100) * circumference;
  return (
    <div className="score-ring-wrap">
      <svg className="score-ring" viewBox="0 0 140 140">
        <circle className="ring-track" cx="70" cy="70" r={radius} />
        <circle className="ring-value" cx="70" cy="70" r={radius}
          strokeDasharray={`${dash} ${circumference}`} />
      </svg>
      <div className="score-center"><strong>{score}</strong><span>/100</span></div>
      <div className="score-label">{label}</div>
    </div>
  );
}

function Badge({ children, tone = 'neutral' }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

function Section({ icon: Icon, title, subtitle, children, action }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div className="section-title-wrap">
          <div className="icon-box"><Icon size={19} /></div>
          <div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const inputRef = useRef(null);

  const display = result || null;
  const score = display?.ats_score ?? 0;

  const scoreMessage = useMemo(() => {
    if (score >= 85) return 'Strong ATS readiness';
    if (score >= 70) return 'Good foundation';
    if (score >= 55) return 'Needs targeted improvements';
    return 'Major improvements recommended';
  }, [score]);

  const selectFile = (selected) => {
    const f = selected?.[0] || selected;
    if (!f) return;
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const extOk = /\.(pdf|docx|txt)$/i.test(f.name);
    if (!extOk && !allowed.includes(f.type)) {
      setError('Please upload a PDF, DOCX, or TXT resume.');
      return;
    }
    if (f.size > 8 * 1024 * 1024) {
      setError('File is too large. Maximum size is 8 MB.');
      return;
    }
    setError('');
    setFile(f);
    setResult(null);
  };

  const analyze = async () => {
    if (!file) { setError('Please upload your resume first.'); return; }
    setLoading(true); setError(''); setResult(null);
    const form = new FormData();
    form.append('file', file);
    if (jobDescription.trim()) form.append('job_description', jobDescription.trim());

    try {
      const headers = {};
      if (apiKey.trim()) headers['X-Gemini-API-Key'] = apiKey.trim();
      const response = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', body: form, headers });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || `Analysis failed (${response.status}).`);
      setResult(data);
      window.setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
    } catch (e) {
      setError(e.message || 'Could not connect to the analyzer. Make sure the backend is running.');
    } finally { setLoading(false); }
  };

  const loadDemo = () => {
    setFile({ name: 'demo-resume.pdf', size: 184000 });
    setResult(demo);
    setError('');
    window.setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' }), 50);
  };

  const reset = () => { setFile(null); setResult(null); setError(''); setJobDescription(''); };
  const downloadReport = () => {
    if (!display) return;
    const lines = [
      `RESUMATE AI — RESUME ANALYSIS REPORT`, ``, `ATS SCORE: ${display.ats_score}/100`,
      `JOB MATCH: ${display.job_matching?.match_percentage ?? 'N/A'}%`,
      `FIT: ${display.job_matching?.fit_level ?? 'N/A'}`, ``,
      `MATCHED SKILLS`, ...(display.skills_analysis?.matched_skills || []).map(x => `• ${x}`), ``,
      `MISSING SKILLS`, ...(display.skills_analysis?.missing_skills || []).map(x => `• ${x}`), ``,
      `IMPROVEMENTS`, ...(display.improvement_suggestions || []).map(x => `• [${x.impact}] ${x.suggestion}`), ``,
      `GRAMMAR`, ...(display.grammar_analysis || []).map(x => `• ${x.original_text} → ${x.suggested_text}`)
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'resumate-analysis.txt'; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" onClick={(e) => { e.preventDefault(); reset(); }}>
          <span className="brand-mark"><Sparkles size={17} /></span>
          <span>ResuMate<span className="brand-accent">AI</span></span>
        </a>
        <nav className={mobileMenu ? 'nav open' : 'nav'}>
          <a href="#analyze" onClick={() => setMobileMenu(false)}>Analyze</a>
          <a href="#how-it-works" onClick={() => setMobileMenu(false)}>How it works</a>
          <a href="#results" onClick={() => setMobileMenu(false)}>Results</a>
        </nav>
        <button className="menu-btn" onClick={() => setMobileMenu(v => !v)} aria-label="Menu"><Menu size={21}/></button>
      </header>

      <main>
        {!display && (
          <section className="hero" id="analyze">
            <div className="eyebrow"><Zap size={14}/> AI-powered resume intelligence</div>
            <h1>Turn your resume into an <span>ATS-ready</span> application.</h1>
            <p className="hero-copy">Upload your resume, optionally add a job description, and get practical AI feedback on ATS compatibility, skills, grammar and interview preparation.</p>
            <div className="hero-actions"><button className="text-btn" onClick={loadDemo}>See a demo analysis <ArrowLeft size={15} className="flip"/></button></div>
          </section>
        )}

        {!display ? (
          <section className="workspace" id="analyze">
            <div className="upload-card">
              <div
                className={`dropzone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => { e.preventDefault(); setDragging(false); selectFile(e.dataTransfer.files); }}
                onClick={() => inputRef.current?.click()}
              >
                <input ref={inputRef} type="file" hidden accept=".pdf,.docx,.txt" onChange={(e) => selectFile(e.target.files)} />
                {file ? (
                  <div className="selected-file" onClick={(e) => e.stopPropagation()}>
                    <div className="file-icon"><FileText size={25}/></div>
                    <div className="file-info"><strong>{file.name}</strong><span>{file.size ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : 'Ready for analysis'}</span></div>
                    <button className="icon-btn" onClick={() => setFile(null)} aria-label="Remove file"><X size={18}/></button>
                  </div>
                ) : (
                  <>
                    <div className="upload-icon"><Upload size={24}/></div>
                    <h3>Drop your resume here</h3>
                    <p>or click to browse your files</p>
                    <small>PDF, DOCX or TXT · Max 8 MB</small>
                  </>
                )}
              </div>

              <label className="field-label">Target job description <span>Optional</span></label>
              <textarea value={jobDescription} onChange={e => setJobDescription(e.target.value)}
                placeholder="Paste the job description here for a more targeted ATS match..." rows={7} />

              <label className="field-label">Gemini API key <span>Optional if configured on backend</span></label>
              <input className="text-input" type="password" value={apiKey} onChange={e => setApiKey(e.target.value)}
                placeholder="AIza..." autoComplete="off" />

              {error && <div className="error-box"><AlertCircle size={18}/><span>{error}</span></div>}
              <button className="primary-btn analyze-btn" onClick={analyze} disabled={loading || !file}>
                {loading ? <><Loader2 size={19} className="spin"/> Analyzing your resume...</> : <><Sparkles size={19}/> Analyze Resume</>}
              </button>
              <p className="privacy-note"><ShieldCheck size={14}/> Your resume is processed for analysis and is not stored by this frontend.</p>
            </div>

            <aside className="feature-card">
              <div className="mini-label">WHAT YOU GET</div>
              <h2>One analysis. Clear next steps.</h2>
              {[
                [Gauge, 'ATS score', 'A 0–100 compatibility score based on common ATS signals.'],
                [Target, 'Job matching', 'Compare your resume with a target job description.'],
                [TrendingUp, 'Skill gaps', 'See matched, missing and improvement areas.'],
                [Lightbulb, 'Actionable fixes', 'Prioritized suggestions you can apply immediately.']
              ].map(([Icon, title, copy]) => <div className="feature-row" key={title}><div className="feature-icon"><Icon size={18}/></div><div><strong>{title}</strong><p>{copy}</p></div></div>)}
            </aside>
          </section>
        ) : (
          <section className="results-page" id="results">
            <div className="results-toolbar">
              <button className="back-btn" onClick={() => setResult(null)}><ArrowLeft size={17}/> Analyze another resume</button>
              <button className="secondary-btn" onClick={downloadReport}><FileText size={16}/> Export report</button>
            </div>

            <div className="results-header">
              <div><div className="eyebrow"><CheckCircle2 size={14}/> Analysis complete</div><h1>Your resume report</h1><p>{display.resume_details?.name || 'Candidate'} · {scoreMessage}</p></div>
              <div className="header-score"><ScoreRing score={score}/></div>
            </div>

            <div className="stat-grid">
              <div className="stat-card"><div className="stat-icon"><Gauge size={18}/></div><span>ATS score</span><strong>{score}<small>/100</small></strong></div>
              <div className="stat-card"><div className="stat-icon"><Target size={18}/></div><span>Job match</span><strong>{display.job_matching?.match_percentage ?? '—'}<small>{display.job_matching ? '%' : ''}</small></strong></div>
              <div className="stat-card"><div className="stat-icon"><CheckCircle2 size={18}/></div><span>Matched skills</span><strong>{display.skills_analysis?.matched_skills?.length ?? 0}</strong></div>
              <div className="stat-card"><div className="stat-icon"><AlertCircle size={18}/></div><span>Missing skills</span><strong>{display.skills_analysis?.missing_skills?.length ?? 0}</strong></div>
            </div>

            <div className="result-grid">
              <Section icon={Target} title="Job Match" subtitle="How the resume aligns with the target role">
                <div className="match-summary">
                  <div className="match-number">{display.job_matching?.match_percentage ?? 0}%<span>match</span></div>
                  <Badge tone="purple">{display.job_matching?.fit_level || 'Not assessed'}</Badge>
                </div>
                <div className="two-col">
                  <div><h3 className="subhead">Strengths</h3><ul className="clean-list">{(display.job_matching?.strengths || []).map(x => <li key={x}><CheckCircle2 size={16}/>{x}</li>)}</ul></div>
                  <div><h3 className="subhead">Gaps</h3><ul className="clean-list">{(display.job_matching?.gaps || []).map(x => <li key={x}><AlertCircle size={16}/>{x}</li>)}</ul></div>
                </div>
              </Section>

              <Section icon={BarChart3} title="Skills Analysis" subtitle="What your resume communicates today">
                <div className="skill-group"><h3 className="subhead">Matched</h3><div className="chips">{(display.skills_analysis?.matched_skills || []).map(x => <Badge tone="green" key={x}>{x}</Badge>)}</div></div>
                <div className="skill-group"><h3 className="subhead">Missing</h3><div className="chips">{(display.skills_analysis?.missing_skills || []).map(x => <Badge tone="red" key={x}>{x}</Badge>)}</div></div>
                <div className="skill-group"><h3 className="subhead">Upskill</h3><div className="chips">{(display.skills_analysis?.skills_to_improve || []).map(x => <Badge tone="amber" key={x}>{x}</Badge>)}</div></div>
                <p className="explanation">{display.skills_analysis?.gaps_explanation}</p>
              </Section>

              <Section icon={Lightbulb} title="Improvement Plan" subtitle="Prioritized changes with practical impact">
                <div className="suggestions">{(display.improvement_suggestions || []).map((x, i) => <div className="suggestion" key={`${x.category}-${i}`}><div className="suggestion-top"><Badge tone={x.impact === 'High' ? 'red' : x.impact === 'Medium' ? 'amber' : 'neutral'}>{x.impact} impact</Badge><span>{x.category}</span></div><p>{x.suggestion}</p></div>)}</div>
              </Section>

              <Section icon={FileText} title="Grammar & Writing" subtitle="Specific edits detected in your resume">
                {(display.grammar_analysis || []).length ? <div className="grammar-list">{display.grammar_analysis.map((x, i) => <div className="grammar-item" key={i}><div className="grammar-top"><strong>{x.issue}</strong><Badge tone={x.severity === 'High' ? 'red' : x.severity === 'Medium' ? 'amber' : 'neutral'}>{x.severity}</Badge></div><p>{x.explanation}</p><div className="rewrite"><div><small>Original</small><span>{x.original_text}</span></div><div className="arrow">→</div><div><small>Suggested</small><span>{x.suggested_text}</span></div></div></div>)}</div> : <div className="empty-state"><CheckCircle2 size={22}/> No grammar issues were returned.</div>}
              </Section>

              <Section icon={CircleHelp} title="Interview Prep" subtitle="Questions generated from your resume and target role">
                <ol className="question-list">{(display.job_matching?.interview_questions || []).map((q, i) => <li key={i}><span>{i + 1}</span>{q}</li>)}</ol>
              </Section>

              <Section icon={Search} title="Candidate Details" subtitle="Information extracted from your resume">
                <div className="details-grid">
                  <div><small>Name</small><strong>{display.resume_details?.name || 'Not found'}</strong></div>
                  <div><small>Email</small><strong>{display.resume_details?.email || 'Not found'}</strong></div>
                  <div><small>Phone</small><strong>{display.resume_details?.phone || 'Not found'}</strong></div>
                </div>
                {display.resume_details?.summary && <div className="summary-box">{display.resume_details.summary}</div>}
              </Section>
            </div>
          </section>
        )}
      </main>

      <section className="how" id="how-it-works">
        <div className="how-inner"><div><div className="mini-label">HOW IT WORKS</div><h2>From upload to useful feedback in three steps.</h2></div>
          <div className="steps"><div><span>01</span><strong>Upload</strong><p>Drop a PDF, DOCX or TXT resume.</p></div><div><span>02</span><strong>Analyze</strong><p>AI evaluates ATS signals and role alignment.</p></div><div><span>03</span><strong>Improve</strong><p>Apply focused fixes and prepare for interviews.</p></div></div>
        </div>
      </section>

      <footer><div className="brand"><span className="brand-mark"><Sparkles size={15}/></span>ResuMate<span className="brand-accent">AI</span></div><span>AI resume analysis toolkit</span><a href="mailto:support@example.com"><Mail size={14}/> Support</a></footer>
    </div>
  );
}

export default App;
