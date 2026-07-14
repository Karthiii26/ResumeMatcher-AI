import { useState, useRef } from 'react'

const API = import.meta.env.VITE_API_URL || ''   // Set VITE_API_URL on Vercel to your Render backend URL

const ACCEPTED = '.pdf,.docx,.jpg,.jpeg,.png,.webp'
const ACCEPTED_LABEL = 'PDF, DOCX, JPG, PNG, WEBP'

/* ── helpers ─────────────────────────────────────────────────────────────── */
function chipLabel(text, maxWords = 6) {
  const words = text.replace(/[*_`]/g, '').trim().split(/\s+/)
  return words.slice(0, maxWords).join(' ') + (words.length > maxWords ? '…' : '')
}

function scoreColor(s) {
  if (s >= 70) return { ring: '#22C55E', text: '#15803D', bg: '#F0FDF4', border: '#BBF7D0', label: 'Strong Match' }
  if (s >= 45) return { ring: '#F59E0B', text: '#B45309', bg: '#FFFBEB', border: '#FDE68A', label: 'Moderate Match' }
  return { ring: '#EF4444', text: '#B91C1C', bg: '#FEF2F2', border: '#FECACA', label: 'Weak Match' }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/* ── Gauge ───────────────────────────────────────────────────────────────── */
function Gauge({ score }) {
  const r = 54
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const { ring, text, label } = scoreColor(score)
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="160" height="160" viewBox="0 0 120 120" aria-label={`Match score: ${score}%`} role="img">
        <circle cx="60" cy="60" r={r} fill="none" stroke="#E2E8F0" strokeWidth="9" />
        <circle
          className="gauge-circle"
          cx="60" cy="60" r={r}
          fill="none" stroke={ring} strokeWidth="9" strokeLinecap="round"
          strokeDasharray={`${circ}`}
          style={{ '--target-offset': offset, strokeDashoffset: circ, transform: 'rotate(-90deg)', transformOrigin: '60px 60px' }}
        />
        <text x="60" y="56" textAnchor="middle" fontFamily="Space Grotesk,sans-serif" fontWeight="700" fontSize="22" fill={text}>{score}%</text>
        <text x="60" y="72" textAnchor="middle" fontFamily="DM Sans,sans-serif" fontWeight="400" fontSize="9" fill="#94A3B8">OVERALL</text>
      </svg>
      <span className="text-sm font-semibold tracking-wide uppercase" style={{ color: text }}>{label}</span>
    </div>
  )
}

/* ── Chip ────────────────────────────────────────────────────────────────── */
function Chip({ text, variant }) {
  const styles = {
    green: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    red:   'bg-red-50 text-red-600 border border-red-200',
    amber: 'bg-amber-50 text-amber-700 border border-amber-200',
  }
  return <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${styles[variant]}`}>{text}</span>
}

/* ── Result card ─────────────────────────────────────────────────────────── */
function ResultCard({ title, delay = '100', children }) {
  return (
    <div className={`bg-white rounded-2xl border border-slate-100 shadow-sm p-6 animate-fade-up delay-${delay}`}>
      <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4">{title}</h3>
      {children}
    </div>
  )
}

/* ── Sparkle icon ────────────────────────────────────────────────────────── */
function SparkleIcon({ size = 14, className = '' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className}>
      <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z" />
    </svg>
  )
}

/* ── Upload icon ─────────────────────────────────────────────────────────── */
function UploadIcon() {
  return (
    <svg className="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
    </svg>
  )
}

/* ── File icon ───────────────────────────────────────────────────────────── */
function FileIcon({ ext }) {
  const colors = {
    pdf:  { bg: '#FEE2E2', text: '#DC2626' },
    docx: { bg: '#DBEAFE', text: '#2563EB' },
    doc:  { bg: '#DBEAFE', text: '#2563EB' },
    jpg:  { bg: '#D1FAE5', text: '#059669' },
    jpeg: { bg: '#D1FAE5', text: '#059669' },
    png:  { bg: '#D1FAE5', text: '#059669' },
    webp: { bg: '#D1FAE5', text: '#059669' },
  }
  const c = colors[ext?.toLowerCase()] || { bg: '#F3F4F6', text: '#6B7280' }
  return (
    <div className="w-10 h-12 rounded-lg flex items-center justify-center text-xs font-bold uppercase"
      style={{ background: c.bg, color: c.text }}>
      {ext?.slice(0, 4)}
    </div>
  )
}

/* ── Loader ──────────────────────────────────────────────────────────────── */
function Loader() {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 space-y-8 animate-fade-in">
      <div className="flex flex-col items-center justify-center py-6 gap-3">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 rounded-full border-4 border-slate-100"></div>
          <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin"></div>
        </div>
        <p className="text-sm font-semibold font-heading text-slate-700 animate-pulse mt-2">
          Analyzing resume and job description...
        </p>
        <p className="text-xs text-slate-400">
          This usually takes 2–5 seconds
        </p>
      </div>

      <div className="space-y-4">
        <div className="h-4 bg-slate-100 rounded-lg w-1/4 animate-pulse"></div>
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="sm:col-span-1 h-36 bg-slate-50 border border-slate-100 rounded-2xl animate-pulse"></div>
          <div className="sm:col-span-3 grid grid-cols-3 gap-4">
            <div className="h-36 bg-slate-50 border border-slate-100 rounded-2xl animate-pulse"></div>
            <div className="h-36 bg-slate-50 border border-slate-100 rounded-2xl animate-pulse"></div>
            <div className="h-36 bg-slate-50 border border-slate-100 rounded-2xl animate-pulse"></div>
          </div>
        </div>

        <div className="space-y-3 pt-2">
          <div className="h-4 bg-slate-100 rounded-lg w-1/5 animate-pulse"></div>
          <div className="h-20 bg-slate-50 border border-slate-100 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    </div>
  )
}

/* ── Main App ────────────────────────────────────────────────────────────── */
export default function App() {
  const [resumeFile, setResumeFile] = useState(null)   // File object
  const [jdText, setJdText]         = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading]       = useState(false)
  const [results, setResults]       = useState(null)
  const [error, setError]           = useState('')
  const fileRef = useRef()
  const resultsRef = useRef(null)

  const canAnalyze = !!resumeFile && jdText.trim().length > 0

  /* ── File handling ─────────────────────────────────────────────────────── */
  function pickFile(file) {
    if (!file) return
    const ext = file.name.split('.').pop().toLowerCase()
    const allowed = ['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'webp']
    if (!allowed.includes(ext)) {
      setError(`Unsupported format ".${ext}". Please upload a PDF, DOCX, JPG, PNG, or WEBP file.`)
      return
    }
    setError('')
    setResults(null)
    setResumeFile(file)
  }

  function handleFileInput(e) { pickFile(e.target.files?.[0]) }

  function handleDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    pickFile(e.dataTransfer.files?.[0])
  }

  function clearFile(e) {
    e.stopPropagation()
    setResumeFile(null)
    setResults(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  /* ── Submit ────────────────────────────────────────────────────────────── */
  const handleAnalyze = async () => {
    if (!canAnalyze) return
    setError('')
    setResults(null)
    setLoading(true)

    const form = new FormData()
    form.append('jd_text', jdText)
    form.append('resume_file', resumeFile, resumeFile.name)

    try {
      console.log('Sending request to /analyze...');
      const res  = await fetch(`${API}/analyze`, { method: 'POST', body: form })
      console.log('Response status:', res.status);
      const data = await res.json()
      console.log('Received data:', data);
      if (!res.ok || data.error) throw new Error(data.error || 'Analysis failed.')
      setResults(data)
      console.log('Successfully set results state.');

      // If user is at the top of the page, smoothly scroll to the results
      if (window.scrollY < 50) {
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 150);
      }
    } catch (err) {
      console.error('Error during analysis:', err);
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const matched     = results ? [...results.strong_matches, ...results.partial_matches] : []
  const missing     = results ? results.missing_matches : []
  const suggestions = results ? results.suggestions : []

  console.log('App rendering. results:', !!results, 'loading:', loading);
  const fileExt     = resumeFile?.name.split('.').pop()

  return (
    <div className="min-h-screen font-body" style={{ backgroundColor: '#EBF0FA' }}>
      <main className="max-w-5xl mx-auto px-6 pt-16 pb-20 space-y-8">

        {/* ── Hero ────────────────────────────────────────────────────────── */}
        <div className="flex flex-col items-center text-center gap-4">
          <div className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-white border border-slate-200 shadow-sm text-xs font-medium text-slate-600">
            <SparkleIcon size={12} className="text-blue-500" />
            AI-powered resume screening
          </div>
          <h1 className="font-heading font-bold text-5xl sm:text-6xl tracking-tight" style={{ color: '#0D1526', lineHeight: 1.1 }}>
            Resume Matcher AI
          </h1>
          <p className="text-base text-slate-500 max-w-lg leading-relaxed">
            Upload your resume and a{' '}
            <span className="text-blue-500 font-medium">job description</span>{' '}
            to see how well they align — with a{' '}
            <span className="text-blue-500 font-medium">match score</span>,{' '}
            keyword breakdown, and tips to improve.
          </p>
        </div>

        {/* ── Input cards ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">

          {/* ── Resume upload card ─────────────────────────────────────── */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
            <div className="flex items-center justify-between px-5 pt-4 pb-3 border-b border-slate-100">
              <span className="font-heading font-semibold text-sm text-slate-700">Your Resume</span>
              <span className="text-xs text-slate-400">{ACCEPTED_LABEL}</span>
            </div>

            {/* Drop zone */}
            <div
              className={`
                flex-1 flex flex-col items-center justify-center
                m-4 rounded-xl border-2 border-dashed cursor-pointer
                transition-all duration-200 min-h-[260px]
                ${isDragging
                  ? 'border-blue-400 bg-blue-50'
                  : resumeFile
                    ? 'border-slate-200 bg-slate-50'
                    : 'border-slate-200 bg-slate-50 hover:border-blue-300 hover:bg-blue-50'
                }
              `}
              onClick={() => !resumeFile && fileRef.current.click()}
              onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              role="button"
              tabIndex={0}
              aria-label="Upload resume file"
              onKeyDown={e => e.key === 'Enter' && !resumeFile && fileRef.current.click()}
            >
              {resumeFile ? (
                /* ── File selected state ── */
                <div className="flex flex-col items-center gap-4 p-6 text-center">
                  <FileIcon ext={fileExt} />
                  <div>
                    <p className="font-medium text-sm text-slate-700 break-all">{resumeFile.name}</p>
                    <p className="text-xs text-slate-400 mt-1">{formatBytes(resumeFile.size)}</p>
                  </div>
                  <div className="flex gap-2 mt-1">
                    <button
                      onClick={() => fileRef.current.click()}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 hover:bg-blue-100 transition-colors"
                    >
                      Replace
                    </button>
                    <button
                      onClick={clearFile}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 bg-white border border-slate-200 hover:bg-slate-100 transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ) : (
                /* ── Empty drop zone ── */
                <div className="flex flex-col items-center gap-3 p-8 text-center select-none">
                  <UploadIcon />
                  <div>
                    <p className="text-sm font-medium text-slate-600">
                      <span className="text-blue-500">Click to upload</span> or drag & drop
                    </p>
                    <p className="text-xs text-slate-400 mt-1">PDF, DOCX, JPG, PNG, WEBP</p>
                  </div>
                </div>
              )}
            </div>

            <input
              ref={fileRef}
              type="file"
              accept={ACCEPTED}
              className="hidden"
              onChange={handleFileInput}
              aria-label="Resume file input"
            />
          </div>

          {/* ── JD textarea card ────────────────────────────────────────── */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
            <div className="flex items-center justify-between px-5 pt-4 pb-3 border-b border-slate-100">
              <label htmlFor="jd-input" className="font-heading font-semibold text-sm text-slate-700">
                Job Description
              </label>
              <span className="text-xs text-slate-400 tabular-nums">{jdText.length.toLocaleString()} chars</span>
            </div>
            <textarea
              id="jd-input"
              value={jdText}
              onChange={e => setJdText(e.target.value)}
              placeholder="Paste the job description here…"
              className="
                flex-1 w-full px-5 py-4 resize-none text-sm text-slate-700 leading-relaxed
                placeholder:text-slate-400 bg-white focus:outline-none min-h-[300px]
              "
            />
          </div>
        </div>

        {/* ── Analyze button ───────────────────────────────────────────────── */}
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={handleAnalyze}
            disabled={loading || !canAnalyze}
            aria-busy={loading}
            className="
              inline-flex items-center justify-center gap-2
              px-10 py-3 rounded-xl font-heading font-semibold text-sm
              text-white shadow-md transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            "
            style={{ background: '#4A5568' }}
            onMouseEnter={e => { if (!loading && canAnalyze) e.currentTarget.style.background = '#374151' }}
            onMouseLeave={e => { e.currentTarget.style.background = '#4A5568' }}
          >
            {loading ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Analyzing…
              </>
            ) : (
              <>
                <SparkleIcon size={14} />
                Analyze Match
              </>
            )}
          </button>

          {/* Empty state hint */}
          {!canAnalyze && !loading && (
            <p className="text-xs text-slate-500">
              Add both your{' '}
              <span className="text-blue-500 cursor-pointer" onClick={() => fileRef.current.click()}>resume</span>
              {' '}and a{' '}
              <span className="text-blue-500 cursor-pointer" onClick={() => document.getElementById('jd-input').focus()}>job description</span>
              {' '}to analyze.
            </p>
          )}

          {/* Error */}
          {error && (
            <div role="alert" className="max-w-md w-full rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 text-center animate-fade-in">
              {error}
            </div>
          )}
        </div>

        {/* ── Loader ── */}
        {loading && <Loader />}

        {/* ── Results ── */}
        {results && (
          <section ref={resultsRef} aria-label="Analysis results" className="space-y-5 animate-fade-in">

            <div className="flex items-center gap-3 pt-2">
              <div className="flex-1 h-px bg-slate-200" />
              <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">Results</span>
              <div className="flex-1 h-px bg-slate-200" />
            </div>

            {/* Score + stats */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="sm:col-span-1 bg-white rounded-2xl border border-slate-100 shadow-sm p-6 flex items-center justify-center animate-scale-in">
                <Gauge score={results.overall_score} />
              </div>
              <div className="sm:col-span-3 grid grid-cols-3 gap-4">
                {[
                  { label: 'Strong Matches',  count: results.strong_matches.length,  color: '#22C55E', bg: '#F0FDF4', border: '#BBF7D0' },
                  { label: 'Partial Matches', count: results.partial_matches.length, color: '#F59E0B', bg: '#FFFBEB', border: '#FDE68A' },
                  { label: 'Missing',         count: results.missing_matches.length, color: '#EF4444', bg: '#FEF2F2', border: '#FECACA' },
                ].map((s, i) => (
                  <div key={s.label}
                    className={`rounded-2xl border p-5 flex flex-col gap-1 animate-fade-up delay-${(i + 1) * 100}`}
                    style={{ background: s.bg, borderColor: s.border }}
                  >
                    <span className="text-3xl font-heading font-bold" style={{ color: s.color }}>{s.count}</span>
                    <span className="text-xs font-medium text-slate-600">{s.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Matched */}
            <ResultCard title="Matched Requirements" delay="200">
              {matched.length === 0
                ? <p className="text-sm text-slate-400 italic">No matches found.</p>
                : <div className="flex flex-wrap gap-2">
                    {matched.map((m, i) => (
                      <Chip key={i} text={chipLabel(m.jd_requirement)}
                        variant={results.strong_matches.includes(m) ? 'green' : 'amber'} />
                    ))}
                  </div>
              }
            </ResultCard>

            {/* Missing */}
            <ResultCard title="Missing Requirements" delay="300">
              {missing.length === 0
                ? <p className="text-sm text-emerald-600 font-medium">Your resume covers all requirements.</p>
                : <div className="flex flex-wrap gap-2">
                    {missing.map((m, i) => <Chip key={i} text={chipLabel(m.jd_requirement)} variant="red" />)}
                  </div>
              }
            </ResultCard>

            {/* Suggestions */}
            <ResultCard title="Suggestions to Improve Your Match" delay="400">
              {suggestions.length === 0
                ? <p className="text-sm text-slate-400 italic">No improvements needed — your resume is well-aligned.</p>
                : <ul className="space-y-3">
                    {suggestions.map((s, i) => {
                      const clean = s.replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1')
                      return (
                        <li key={i} className="flex gap-3 text-sm text-slate-700 leading-relaxed">
                          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                          {clean}
                        </li>
                      )
                    })}
                  </ul>
              }
            </ResultCard>

          </section>
        )}
      </main>

      <footer className="text-center text-xs text-slate-400 pb-8 border-t border-slate-200 pt-6" style={{ backgroundColor: '#EBF0FA' }}>
        © 2026 ResumeMatcher AI. All rights reserved.
      </footer>
    </div>
  )
}
