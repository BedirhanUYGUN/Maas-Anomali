import { useState, useEffect } from 'react'
import { Upload, AlertTriangle, Download, CheckCircle, Filter, Loader2, TrendingUp, DollarSign, Clock, FileText, RefreshCw, Trash2, ListChecks } from 'lucide-react'

interface AnomalyDetails {
    salary_increase?: {
        prev_total: number;
        current_total: number;
        increase_pct: number;
    }
}

interface Anomaly {
    personel_ad: string;
    donem: string;
    maas: number;
    mesai: number;
    mesai_saati: number;
    ek: number;
    yardim: number;
    bes: number;
    avans: number;
    icra: number;
    borc: number;
    banka: number;
    kasa: number;
    issues: string[];
    diff: number | null;
    categories: string[];
    details: AnomalyDetails | null;
}

function App() {
    const [anomalies, setAnomalies] = useState<Anomaly[]>([])
    const [localFiles, setLocalFiles] = useState<string[]>([])
    const [selectedFiles, setSelectedFiles] = useState<string[]>([])
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 0 })
    const [message, setMessage] = useState('')
    const [filter, setFilter] = useState<'all' | 'maaş' | 'mesai'>('all')

    useEffect(() => {
        fetchAnomalies()
        fetchLocalFiles()
    }, [])

    const fetchAnomalies = async () => {
        try {
            const resp = await fetch('/api/v1/anomalies')
            if (resp.ok) {
                const data = await resp.json()
                setAnomalies(data)
            }
        } catch (err) {
            console.error("Fetch anomalies failed", err)
        }
    }

    const fetchLocalFiles = async () => {
        try {
            const resp = await fetch('/api/v1/files')
            if (resp.ok) {
                const data = await resp.json()
                setLocalFiles(data.files || [])
            }
        } catch (err) {
            console.error("Fetch local files failed", err)
        }
    }

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return

        setUploading(true)
        setMessage('')
        setUploadProgress({ current: 0, total: files.length })

        for (let i = 0; i < files.length; i++) {
            setUploadProgress(prev => ({ ...prev, current: i + 1 }))
            const formData = new FormData()
            formData.append('file', files[i])

            try {
                const resp = await fetch('/api/v1/upload', {
                    method: 'POST',
                    body: formData
                })

                if (!resp.ok) {
                    console.error("Upload error for", files[i].name)
                }
            } catch (err) {
                console.error("Network error for", files[i].name)
            }
        }

        setMessage(`${files.length} dosya işlendi.`)
        fetchAnomalies()
        setUploading(false)
    }

    const analyzeSelectedLocalFiles = async () => {
        if (selectedFiles.length === 0) return;

        setUploading(true)
        setMessage(`Toplu analiz başlatıldı: ${selectedFiles.length} dosya`)
        setUploadProgress({ current: 0, total: selectedFiles.length })

        for (let i = 0; i < selectedFiles.length; i++) {
            const filename = selectedFiles[i];
            setUploadProgress(prev => ({ ...prev, current: i + 1 }))
            try {
                const resp = await fetch(`/api/v1/analyze-local?filename=${encodeURIComponent(filename)}`, {
                    method: 'POST'
                })
                if (!resp.ok) console.error("Batch error for", filename)
            } catch (err) {
                console.error("Network error for", filename)
            }
        }

        setSelectedFiles([])
        setMessage(`${selectedFiles.length} yerel dosya başarıyla analiz edildi.`)
        fetchAnomalies()
        setUploading(false)
    }

    const clearRecords = async () => {
        if (!confirm("Tüm önceki verileri silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.")) return;

        try {
            const resp = await fetch('/api/v1/clear', { method: 'DELETE' })
            if (resp.ok) {
                setAnomalies([])
                setMessage("Tüm veriler temizlendi.")
            }
        } catch (err) {
            console.error("Clear failed", err)
        }
    }

    const toggleFileSelection = (filename: string) => {
        setSelectedFiles(prev =>
            prev.includes(filename)
                ? prev.filter(f => f !== filename)
                : [...prev, filename]
        )
    }

    const filteredAnomalies = anomalies.filter(anom => {
        if (filter === 'all') return true;
        return anom.categories.includes(filter);
    })

    return (
        <div className="container">
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>Maaş-Mesai Tespit <span style={{ fontSize: '1rem', verticalAlign: 'middle', opacity: 0.6 }}>v0.2.3</span></h1>
                <button className="btn btn-danger" onClick={clearRecords} title="Tüm veritabanını temizle">
                    <Trash2 size={16} /> Verileri Temizle
                </button>
            </header>

            <div className="main-grid">
                <div className="card">
                    <div className="upload-area" onClick={() => !uploading && document.getElementById('fileInput')?.click()}>
                        <input
                            id="fileInput"
                            type="file"
                            hidden
                            multiple
                            onChange={handleFileUpload}
                            accept=".pdf"
                            disabled={uploading}
                        />
                        {uploading ? (
                            <Loader2 size={40} color="#60a5fa" className="animate-spin" style={{ marginBottom: '0.5rem' }} />
                        ) : (
                            <Upload size={40} color="#60a5fa" style={{ marginBottom: '0.5rem' }} />
                        )}
                        <h3>{uploading ? 'İşleniyor...' : 'Dışarıdan PDF Yükle'}</h3>
                        <p style={{ opacity: 0.6, fontSize: '0.8rem' }}>Bilgisayarınızdan dosya seçin</p>
                        {uploading && uploadProgress.total > 0 && (
                            <div style={{ marginTop: '0.5rem', color: '#60a5fa', fontSize: '1rem', fontWeight: 'bold' }}>
                                {uploadProgress.current} / {uploadProgress.total}
                            </div>
                        )}
                    </div>
                    {message && !uploading && <p style={{ marginTop: '0.5rem', fontWeight: 'bold', color: '#10b981', fontSize: '0.8rem', textAlign: 'center' }}>{message}</p>}
                </div>

                <div className="card local-files-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><FileText size={20} color="#60a5fa" /> Yerel Dosyalar</h3>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button className="icon-btn" onClick={fetchLocalFiles} title="Listeyi Yenile"><RefreshCw size={18} /></button>
                        </div>
                    </div>
                    <div className="file-list">
                        {localFiles.length === 0 ? (
                            <p style={{ opacity: 0.5, fontSize: '0.8rem', fontStyle: 'italic', padding: '1rem' }}>Dizinde PDF dosyası bulunamadı.</p>
                        ) : (
                            localFiles.map((file, idx) => (
                                <div key={idx} className={`file-item ${selectedFiles.includes(file) ? 'selected' : ''}`} onClick={() => toggleFileSelection(file)}>
                                    <div className={`checkbox ${selectedFiles.includes(file) ? 'checked' : ''}`}></div>
                                    <span className="file-name">{file}</span>
                                </div>
                            ))
                        )}
                    </div>
                    <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.75rem', opacity: 0.6 }}>{selectedFiles.length} dosya seçildi</span>
                        <button
                            className="btn btn-primary"
                            disabled={selectedFiles.length === 0 || uploading}
                            onClick={analyzeSelectedLocalFiles}
                        >
                            <ListChecks size={18} /> Seçilenleri Analiz Et
                        </button>
                    </div>
                </div>
            </div>

            <section>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <Filter size={20} style={{ marginRight: '0.5rem', opacity: 0.6 }} />
                        <div className="filter-group">
                            <button
                                className={`btn ${filter === 'all' ? '' : 'btn-outline'}`}
                                onClick={() => setFilter('all')}
                                style={filter !== 'all' ? { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' } : {}}
                            >
                                Tümü ({anomalies.length})
                            </button>
                            <button
                                className={`btn ${filter === 'maaş' ? '' : 'btn-outline'}`}
                                onClick={() => setFilter('maaş')}
                                style={filter !== 'maaş' ? { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#fca5a5' } : {}}
                            >
                                Maaş Sorunları ({anomalies.filter(a => a.categories.includes('maaş')).length})
                            </button>
                            <button
                                className={`btn ${filter === 'mesai' ? '' : 'btn-outline'}`}
                                onClick={() => setFilter('mesai')}
                                style={filter !== 'mesai' ? { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#93c5fd' } : {}}
                            >
                                Mesai Sorunları ({anomalies.filter(a => a.categories.includes('mesai')).length})
                            </button>
                        </div>
                    </div>
                    <button className="btn" onClick={() => window.print()}>
                        <Download size={18} /> Raporu Yazdır
                    </button>
                </div>

                {filteredAnomalies.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
                        <CheckCircle size={48} color="#10b981" style={{ marginBottom: '1rem' }} />
                        <p>Seçili kategoride herhangi bir anomali tespit edilmedi.</p>
                    </div>
                ) : (
                    <div className="anomaly-list">
                        {filteredAnomalies.map((anom, idx) => {
                            const actsMaaş = anom.categories.includes('maaş');
                            const actsMesai = anom.categories.includes('mesai');

                            return (
                                <div key={idx} className={`anomaly-card ${actsMesai && !actsMaaş ? 'mesai-only' : ''}`}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div className="anomaly-title">{anom.personel_ad}</div>
                                        <div className="badge">{anom.donem}</div>
                                    </div>

                                    <div className="anomaly-detail">
                                        <div style={{ marginTop: '0.75rem' }}>
                                            {anom.issues.map((issue, i) => (
                                                <div key={i} className="issue-item">
                                                    <AlertTriangle size={16} /> {issue}
                                                </div>
                                            ))}
                                        </div>

                                        {anom.details?.salary_increase && (
                                            <div className="highlight-box">
                                                <TrendingUp size={16} />
                                                <div>
                                                    <div>Önceki Ay: <strong>{anom.details.salary_increase.prev_total.toLocaleString('tr-TR')} TL</strong></div>
                                                    <div>Bu Ay: <strong>{anom.details.salary_increase.current_total.toLocaleString('tr-TR')} TL</strong></div>
                                                    <div style={{ color: '#f87171', fontWeight: 'bold' }}>Artış: %{anom.details.salary_increase.increase_pct.toFixed(1)}</div>
                                                </div>
                                            </div>
                                        )}

                                        <div className="stats-grid">
                                            <div className="stat-item">
                                                <DollarSign size={14} />
                                                <span>Maaş+Mesai: <strong>{(anom.maas + anom.mesai).toLocaleString('tr-TR')} TL</strong></span>
                                            </div>
                                            <div className="stat-item">
                                                <Clock size={14} />
                                                <span>Mesai: <strong>{anom.mesai_saati} Saat</strong></span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </section>

            <footer style={{ marginTop: '4rem', textAlign: 'center', opacity: 0.4, fontSize: '0.8rem' }}>
                <p>© 2026 Maaş-Mesai Tespit Sistemi - Local Edition</p>
            </footer>

            <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .animate-spin { animation: spin 1s linear infinite; }
        
        .main-grid { display: grid; grid-template-columns: 1fr 1.5fr; gap: 1.5rem; margin-bottom: 2rem; }
        
        .local-files-card { display: flex; flex-direction: column; min-height: 250px; }
        .file-list { flex: 1; overflow-y: auto; max-height: 250px; background: rgba(0,0,0,0.1); border-radius: 0.5rem; }
        .file-item { 
            display: flex; 
            align-items: center; 
            gap: 0.75rem; 
            padding: 0.6rem 0.75rem; 
            border-bottom: 1px solid rgba(255,255,255,0.03);
            cursor: pointer;
            transition: all 0.2s;
        }
        .file-item:hover { background: rgba(255,255,255,0.05); }
        .file-item.selected { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
        
        .checkbox { 
            width: 18px; 
            height: 18px; 
            border: 2px solid rgba(255,255,255,0.2); 
            border-radius: 4px; 
            position: relative;
            transition: all 0.2s;
        }
        .checkbox.checked { background: #3b82f6; border-color: #3b82f6; }
        .checkbox.checked::after {
            content: '';
            position: absolute;
            left: 5px;
            top: 1px;
            width: 5px;
            height: 10px;
            border: solid white;
            border-width: 0 2px 2px 0;
            transform: rotate(45deg);
        }

        .file-name { flex: 1; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .btn-danger { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: #f87171; }
        .btn-danger:hover { background: #ef4444; color: white; }
        .btn-primary { background: #3b82f6; color: white; border: none; }
        .btn-primary:disabled { opacity: 0.3; cursor: not-allowed; }
        
        .icon-btn { background: none; border: none; color: #60a5fa; cursor: pointer; opacity: 0.6; transition: opacity 0.2s; }
        .icon-btn:hover { opacity: 1; }
        
        .filter-group { display: flex; gap: 0.5rem; }
        .issue-item { display: flex; gap: 0.5rem; margin-bottom: 0.4rem; font-weight: 500; }
        .anomaly-card { transition: transform 0.2s; }
        .anomaly-card:hover { transform: translateY(-2px); }
        .anomaly-card.mesai-only { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); }
        .anomaly-card.mesai-only .anomaly-title { color: #93c5fd; }
        .anomaly-card.mesai-only .badge { background: #3b82f6; }
        .anomaly-card.mesai-only .issue-item { color: #93c5fd; }
        
        .issue-item { color: #fca5a5; }
        
        .highlight-box {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin: 1rem 0;
            display: flex;
            gap: 1rem;
            align-items: center;
            font-size: 0.85rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .stats-grid {
            margin-top: 1rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
        }
      `}</style>
        </div>
    )
}

export default App
