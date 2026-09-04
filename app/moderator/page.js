'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Trash2, Search, Filter, Shield, AlertTriangle, ArrowLeft } from 'lucide-react'

export default function ModeratorPage() {
  const router = useRouter()
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [loading, setLoading] = useState(false)
  const [theme, setTheme] = useState('dark')
  const [mounted, setMounted] = useState(false)
  
  // Real-time lists and tools
  const [comments, setComments] = useState([])
  const [videos, setVideos] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [episodeFilter, setEpisodeFilter] = useState('ALL')
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    setMounted(true)
    const savedTheme = localStorage.getItem('shindora-theme') || 'dark'
    setTheme(savedTheme)

    // Quick role check session
    const storedUser = localStorage.getItem('shindora-user')
    if (storedUser) {
      const parsed = JSON.parse(storedUser)
      setCurrentUser(parsed)
      if (parsed.role === 'moderator' || parsed.role === 'admin') {
        setIsAuthorized(true)
        fetchCommentsAndVideos()
      } else {
        alert('Akses Ditolak! Hanya peran Moderator atau Admin yang dapat mengakses panel ini!')
        router.push('/')
      }
    } else {
      alert('Silakan login sebagai moderator terlebih dahulu!')
      router.push('/login')
    }
    setLoading(false)
  }, [])

  const fetchCommentsAndVideos = async () => {
    try {
      const comRes = await fetch('/api/comments')
      if (!comRes.ok) throw new Error('Gagal mengambil data komentar dari server!')
      const comData = await comRes.json()
      setComments(Array.isArray(comData) ? comData : [])

      const vidRes = await fetch('/api/videos')
      if (!vidRes.ok) throw new Error('Gagal mengambil data video dari server!')
      const vidData = await vidRes.json()
      setVideos(Array.isArray(vidData) ? vidData : [])
    } catch (err) {
      console.error(err)
      alert('Koneksi Gagal: ' + err.message)
    }
  }

  // Deleting comment and all nested replying children
  const handleDeleteComment = async (commentId) => {
    if (!confirm('Hapus komentar ini beserta seluruh rantai balasannya? Tindakan ini tidak dapat dibatalkan.')) return

    try {
      const res = await fetch(`/api/comments?id=${commentId}`, {
        method: 'DELETE'
      })
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.error || 'Server menolak penghapusan komentar')
      }
      const data = await res.json()
      alert(`Berhasil menghapus ${data.deletedCount || 1} komentar/balasan!`)
      fetchCommentsAndVideos()
    } catch (err) {
      console.error(err)
      alert('Gagal menghapus komentar: ' + err.message)
    }
  }

  // Searched & Filtered comment lists
  const filteredComments = comments.filter(comment => {
    const matchesSearch = (comment.content || comment.text || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (comment.userName || '').toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesEpisode = episodeFilter === 'ALL' || comment.videoId === episodeFilter

    return matchesSearch && matchesEpisode
  })

  if (!mounted) {
    return (
      <div className="min-h-screen bg-[#0a0b14] flex items-center justify-center text-cyan-400">
        <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mr-3" />
        <span className="text-xs font-bold uppercase tracking-widest text-cyan-400 animate-pulse">Loading Moderator Panel...</span>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-cyan-400">
        <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mr-3" />
        <span className="text-xs font-bold uppercase tracking-widest text-cyan-400 animate-pulse">Memeriksa Hak Akses Moderator...</span>
      </div>
    )
  }

  if (!isAuthorized) return null

  const isDark = theme === 'dark'

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-200 ${
      isDark ? 'bg-[#0a0b14] text-[#e2e8f0]' : 'bg-[#f8fafc] text-[#0f172a]'
    }`}>
      
      {/* NAVBAR HEADER */}
      <header className={`border-b px-3 sm:px-6 py-3 sticky top-0 z-40 ${
        isDark ? 'border-slate-800 bg-[#0d0e1b]' : 'border-slate-200 bg-white shadow-sm'
      }`}>
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center justify-between w-full sm:w-auto">
            <Link href="/" className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-all border flex items-center gap-1 ${
              isDark 
                ? 'bg-slate-500/10 hover:bg-slate-500/20 border-slate-500/20 text-slate-300' 
                : 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-700'
            }`}>
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Website</span>
            </Link>

            <div className="flex items-center gap-2 sm:hidden">
              <span className="px-2 py-0.5 rounded text-[10px] font-black bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30">MODE STAF</span>
            </div>
          </div>

          <div className="flex items-center justify-center sm:justify-start gap-2 w-full sm:w-auto">
            <Shield className="w-5 h-5 text-cyan-500 fill-cyan-500/10 flex-shrink-0" />
            <span className="font-extrabold tracking-wider text-xs sm:text-sm bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent uppercase">
              Panel Moderasi Komentar
            </span>
          </div>
          
          <div className="flex items-center justify-end gap-2.5 w-full sm:w-auto border-t sm:border-0 pt-2 sm:pt-0 border-slate-500/10">
            {/* Theme switcher toggle */}
            <button
              onClick={() => {
                const nextTheme = isDark ? 'light' : 'dark'
                setTheme(nextTheme)
                localStorage.setItem('shindora-theme', nextTheme)
              }}
              className={`px-3 py-1 text-xs font-bold rounded-lg border transition-all ${
                isDark 
                  ? 'border-slate-800 bg-[#121324] hover:bg-slate-800 text-yellow-400' 
                  : 'border-slate-200 bg-slate-100 hover:bg-slate-200 text-slate-700 shadow-sm'
              }`}
            >
              {isDark ? '☀️ Terang' : '🌙 Gelap'}
            </button>
            
            {/* Cross-navigation button for Admin */}
            {currentUser && currentUser.role === 'admin' && (
              <Link
                href="/admin"
                className="px-2.5 py-1 rounded-lg text-[10px] font-black bg-pink-500/20 text-pink-600 dark:text-pink-400 border border-pink-500/30 hover:bg-pink-500/30 transition-all uppercase flex items-center gap-1"
                title="Menuju Panel Admin Utama"
              >
                ⚙️ PANEL ADMIN
              </Link>
            )}

            <span className="hidden sm:inline-block px-2.5 py-1 rounded-lg text-[10px] font-black bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30">MODE STAF</span>
          </div>
        </div>
      </header>

      {/* CORE MODERATION WORKSPACE */}
      <main className="max-w-7xl mx-auto p-3 sm:p-6 space-y-4 sm:space-y-6 flex-1 w-full">
        
        {/* Banner info */}
        <div className={`p-3.5 sm:p-4 rounded-xl border flex items-start gap-3 ${
          isDark ? 'border-cyan-500/20 bg-cyan-500/5' : 'border-cyan-200 bg-cyan-50/50'
        }`}>
          <AlertTriangle className="w-5 h-5 text-cyan-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <h3 className="font-extrabold text-xs sm:text-sm">Panduan Moderasi Opini Retro</h3>
            <p className={`text-[11px] sm:text-xs leading-relaxed ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
              Halaman ini memantau seluruh komentar/balasan. Menghapus komentar induk (parent) akan <strong>otomatis menghapus seluruh rantai balasannya</strong>.
            </p>
          </div>
        </div>

        {/* SEARCH AND FILTERS BAR */}
        <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 p-3 sm:p-4 rounded-xl border ${
          isDark ? 'bg-[#0d0e1b] border-[#1e2038]' : 'bg-white border-slate-200 shadow-sm'
        }`}>
          <div className="relative">
            <Search className={`absolute left-3 top-2.5 w-3.5 h-3.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`} />
            <input
              type="text"
              placeholder="Cari isi komentar atau nama user..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full text-xs pl-8 pr-3 py-2 rounded-lg outline-none transition-all border ${
                isDark 
                  ? 'bg-[#121324] border-[#1e2038] text-white placeholder-slate-500 focus:border-cyan-500' 
                  : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-cyan-600'
              }`}
            />
          </div>

          <div className="relative flex items-center">
            <Filter className={`absolute left-3 top-2.5 w-3.5 h-3.5 ${isDark ? 'text-slate-500' : 'text-slate-400'}`} />
            <select
              value={episodeFilter}
              onChange={(e) => setEpisodeFilter(e.target.value)}
              className={`w-full text-xs pl-8 pr-3 py-2 rounded-lg outline-none font-bold border ${
                isDark 
                  ? 'bg-[#121324] border-[#1e2038] text-white focus:border-cyan-500' 
                  : 'bg-white border-slate-300 text-slate-900 focus:border-cyan-600'
              }`}
            >
              <option value="ALL">Semua Video Episode</option>
              {videos.map(video => (
                <option key={video.id} value={video.id}>{video.animeTitle} - {video.episode} ({video.title})</option>
              ))}
            </select>
          </div>

          <div className={`text-right flex items-center justify-between sm:justify-end text-xs font-bold ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            <span>Total Komentar:</span>
            <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 ml-2">{filteredComments.length}</span>
          </div>
        </div>

        {/* DATA CONTAINER (RESPONSIVE CARD VIEW FOR MOBILE & TABLE VIEW FOR DESKTOP) */}
        
        {/* MOBILE CARD VIEW (< md breakpoint) */}
        <div className="block md:hidden space-y-3">
          {filteredComments.length === 0 ? (
            <div className={`p-6 text-center text-xs italic rounded-xl border ${isDark ? 'bg-[#0d0e1b] border-[#1e2038] text-slate-500' : 'bg-white border-slate-200 text-slate-400'}`}>
              Komentar tidak ditemukan atau database kosong.
            </div>
          ) : (
            filteredComments.map((comment) => {
              const targetVid = videos.find(v => v.id === comment.videoId)
              const commentId = comment.id || comment._id

              return (
                <div 
                  key={commentId}
                  className={`p-3.5 rounded-xl border space-y-3 ${isDark ? 'bg-[#0d0e1b] border-[#1e2038]' : 'bg-white border-slate-200 shadow-sm'}`}
                >
                  <div className="flex items-center justify-between border-b border-slate-500/10 pb-2">
                    <div className="flex items-center gap-2">
                      <img 
                        src={comment.userAvatar || comment.avatarUrl || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80'} 
                        alt="" 
                        className="w-7 h-7 rounded-full object-cover flex-shrink-0"
                      />
                      <div>
                        <p className={`font-extrabold text-xs ${isDark ? 'text-slate-100' : 'text-slate-900'}`}>{comment.userName || 'Anonim'}</p>
                        <span className="text-[9px] font-mono text-cyan-600 dark:text-cyan-400 font-semibold block">
                          {targetVid ? `${targetVid.animeTitle} - ${targetVid.episode}` : comment.videoId}
                        </span>
                      </div>
                    </div>

                    {comment.parentId ? (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-pink-500/10 text-pink-600 dark:text-pink-400 border border-pink-500/20">REPLY</span>
                    ) : (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">PARENT</span>
                    )}
                  </div>

                  <div className={`p-2.5 rounded-lg border text-xs leading-relaxed ${isDark ? 'bg-[#121324] border-[#1e2038] text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'}`}>
                    {comment.content || comment.text}
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <span className={`text-[9px] font-mono ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                      {comment.createdAt ? new Date(comment.createdAt).toLocaleDateString() : 'Baru saja'}
                    </span>

                    <button
                      onClick={() => handleDeleteComment(commentId)}
                      className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-600 dark:text-red-400 font-extrabold text-[11px] rounded-lg flex items-center gap-1.5 transition-all"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Hapus</span>
                    </button>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* DESKTOP TABLE VIEW (>= md breakpoint) */}
        <div className={`hidden md:block rounded-xl border overflow-hidden ${
          isDark ? 'bg-[#0d0e1b] border-[#1e2038]' : 'bg-white border-slate-200 shadow-sm'
        }`}>
          <table className="w-full text-xs text-left">
            <thead className={`text-[10px] uppercase font-bold tracking-wider border-b ${
              isDark ? 'bg-[#121324] border-[#1e2038] text-slate-400' : 'bg-slate-100 border-slate-200 text-slate-600'
            }`}>
              <tr>
                <th className="p-3">Pengirim</th>
                <th className="p-3">Episode Target</th>
                <th className="p-3">Isi Komentar / Pesan</th>
                <th className="p-3 text-center">Tipe</th>
                <th className="p-3 text-right">Aksi Hapus</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${isDark ? 'divide-[#1e2038]' : 'divide-slate-200'}`}>
              {filteredComments.length === 0 ? (
                <tr>
                  <td colSpan="5" className={`p-8 text-center italic ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    Komentar tidak ditemukan atau database kosong.
                  </td>
                </tr>
              ) : (
                filteredComments.map((comment) => {
                  const targetVid = videos.find(v => v.id === comment.videoId)
                  const commentId = comment.id || comment._id

                  return (
                    <tr key={commentId} className="hover:bg-slate-500/5 transition-all">
                      <td className="p-3 flex items-center gap-2">
                        <img 
                          src={comment.userAvatar || comment.avatarUrl || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=80'} 
                          alt="" 
                          className="w-7 h-7 rounded-full object-cover flex-shrink-0" 
                        />
                        <div>
                          <p className={`font-extrabold ${isDark ? 'text-slate-100' : 'text-slate-900'}`}>{comment.userName || 'Anonim'}</p>
                          <span className={`text-[9px] font-mono ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>{comment.userId || commentId}</span>
                        </div>
                      </td>
                      <td className="p-3 font-semibold text-cyan-600 dark:text-cyan-400">
                        {targetVid ? `${targetVid.animeTitle} - ${targetVid.episode}` : comment.videoId}
                      </td>
                      <td className="p-3 max-w-sm">
                        <p className={`leading-relaxed ${isDark ? 'text-slate-200' : 'text-slate-800'}`}>{comment.content || comment.text}</p>
                        <span className={`text-[9px] mt-1 block ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                          Diposting: {comment.createdAt ? new Date(comment.createdAt).toLocaleString() : 'Baru saja'}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        {comment.parentId ? (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-pink-500/10 text-pink-600 dark:text-pink-400 border border-pink-500/20">REPLY</span>
                        ) : (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">PARENT</span>
                        )}
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleDeleteComment(commentId)}
                          className="p-1.5 text-red-500 hover:bg-red-500/10 border border-red-500/20 hover:border-red-500/50 rounded-lg transition-all"
                          title="Hapus Komentar beserta Rantai Balasannya secara Rekursif"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

      </main>

      <footer className={`border-t py-4 text-center text-xs mt-8 ${
        isDark ? 'border-[#1e2038] bg-[#090a12] text-slate-500' : 'border-slate-200 bg-white text-slate-500 shadow-inner'
      }`}>
        <p>&copy; ShinDora Nesub Moderator Dashboard.</p>
      </footer>

    </div>
  )
}
