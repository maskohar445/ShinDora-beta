#!/usr/bin/env python3
import os

def edit_admin_page():
    admin_path = "/app/app/admin/page.js"
    if not os.path.exists(admin_path):
        print("Admin page not found at", admin_path)
        return False
        
    with open(admin_path, "r") as f:
        content = f.read()

    # 1. Update lucide-react imports
    old_import = """  FileText,
  ArrowLeft,
  HeartHandshake
} from 'lucide-react'"""

    new_import = """  FileText,
  ArrowLeft,
  HeartHandshake,
  Smile,
  Download
} from 'lucide-react'"""

    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✓ Admin: Imports updated")
    else:
        print("✗ Admin: Imports not matched")

    # 2. Add states and handlers
    old_states = """  const [activeTab, setActiveTab] = useState('videos') // videos, categories, users, playlists, ads, settings, pages, polling"""
    new_states = """  const [activeTab, setActiveTab] = useState('videos') // videos, categories, users, playlists, ads, settings, pages, polling
  const [emotes, setEmotes] = useState([])
  const [newEmoteCode, setNewEmoteCode] = useState('')
  const [newEmoteUrl, setNewEmoteUrl] = useState('')
  const [emoteUploadProgress, setEmoteUploadProgress] = useState(null)
  const emoteFileInputRef = useRef(null)

  const fetchEmotes = async () => {
    try {
      const res = await fetch('/api/emotes')
      if (res.ok) {
        const data = await res.json()
        setEmotes(Array.isArray(data) ? data : [])
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleSaveEmote = async (e) => {
    e.preventDefault()
    if (!newEmoteCode.trim() || !newEmoteUrl.trim()) return

    try {
      const res = await fetch('/api/emotes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: newEmoteCode, imageUrl: newEmoteUrl })
      })
      if (res.ok) {
        alert('🎉 Custom Emote berhasil ditambahkan!')
        setNewEmoteCode('')
        setNewEmoteUrl('')
        fetchEmotes()
      } else {
        const data = await res.json()
        alert(data.error || 'Gagal menambahkan emote!')
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleDeleteEmote = async (id) => {
    if (!confirm('Apakah Anda yakin ingin menghapus Custom Emote ini?')) return
    try {
      const res = await fetch(`/api/emotes?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Emote berhasil dihapus!')
        fetchEmotes()
      } else {
        alert('Gagal menghapus emote!')
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleEmoteUploadToImageKit = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setEmoteUploadProgress("Mengunggah Emote ke ImageKit...")
    try {
      const url = await uploadToImageKit(file, "emote")
      setNewEmoteUrl(url)
      alert('Emote berhasil diunggah ke ImageKit CDN!')
    } catch (err) {
      alert(err.message)
    } finally {
      setEmoteUploadProgress(null)
    }
  }"""

    if old_states in content:
        content = content.replace(old_states, new_states)
        print("✓ Admin: States and handlers added")
    else:
        print("✗ Admin: States not matched")

    # 3. Add fetchEmotes inside fetchAdminData
    old_fetch = """      const pollRes = await fetch('/api/polling')
      const plData = await pollRes.json()
      setPollingList(Array.isArray(plData) ? plData : [])"""

    new_fetch = """      const pollRes = await fetch('/api/polling')
      const plData = await pollRes.json()
      setPollingList(Array.isArray(plData) ? plData : [])
      fetchEmotes()"""

    if old_fetch in content:
        content = content.replace(old_fetch, new_fetch)
        print("✓ Admin: fetchEmotes hook added")
    else:
        print("✗ Admin: fetch hook not matched")

    # 4. Add "emotes" tab to sidebar links
    old_tabs = """              { id: 'polling', label: 'Anime Polling / Vote', icon: ListVideo },
              { id: 'settings', label: 'Settings & API settings', icon: Settings },
              { id: 'donasi', label: 'Donasi Manual', icon: HeartHandshake }"""

    new_tabs = """              { id: 'polling', label: 'Anime Polling / Vote', icon: ListVideo },
              { id: 'emotes', label: 'Custom Emotes & GIFs', icon: Smile },
              { id: 'settings', label: 'Settings & API settings', icon: Settings },
              { id: 'donasi', label: 'Donasi Manual', icon: HeartHandshake }"""

    if old_tabs in content:
        content = content.replace(old_tabs, new_tabs)
        print("✓ Admin: Sidebar links updated")
    else:
        print("✗ Admin: Sidebar links not matched")

    # 5. Add Custom Emotes renderer JSX block
    old_donasi = """        {activeTab === 'donasi' && ("""
    new_emotes_jsx = """        {activeTab === 'emotes' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="p-6 bg-[#0d0e1b] rounded-2xl border border-cyan-500/20 shadow-xl shadow-cyan-500/5 space-y-4">
              <h3 className="font-extrabold text-base text-cyan-400 uppercase tracking-wider border-b border-[#1e2038] pb-3">
                &bull; SISTEM MANAJEMEN CUSTOM EMOTE
              </h3>

              <form onSubmit={handleSaveEmote} className="space-y-4 text-xs text-left">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="font-bold opacity-60">Kode Shortcode (cth: :dora_joget:)</label>
                    <input
                      type="text"
                      placeholder="Masukkan shortcode..."
                      value={newEmoteCode}
                      onChange={(e) => setNewEmoteCode(e.target.value)}
                      className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-cyan-500 font-mono"
                      required
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-bold opacity-60">URL Gambar / GIF (ImageKit CDN)</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="https://ik.imagekit.io/..."
                        value={newEmoteUrl}
                        onChange={(e) => setNewEmoteUrl(e.target.value)}
                        className="flex-1 p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-cyan-500"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => emoteFileInputRef.current?.click()}
                        className="px-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold text-[10px] whitespace-nowrap transition-all"
                      >
                        Upload ImageKit
                      </button>
                      <input
                        type="file"
                        ref={emoteFileInputRef}
                        onChange={handleEmoteUploadToImageKit}
                        accept="image/*"
                        className="hidden"
                      />
                    </div>
                    {emoteUploadProgress && (
                      <p className="text-[9px] text-cyan-400 font-bold animate-pulse">{emoteUploadProgress}</p>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:opacity-90 text-black font-black uppercase tracking-wider text-xs shadow-lg shadow-cyan-500/10 transition-all flex items-center justify-center gap-1.5"
                >
                  <Plus className="w-4 h-4" />
                  Tambah Custom Emote Baru
                </button>
              </form>
            </div>

            <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto p-5 text-left space-y-4">
              <span className="text-[10px] font-black text-cyan-400 uppercase tracking-widest block border-b border-[#1e2038] pb-2">
                &bull; Daftar Emote Terdaftar ({emotes.length})
              </span>

              {emotes.length === 0 ? (
                <p className="text-center text-xs opacity-40 py-8 italic">Belum ada Custom Emote yang terdaftar di database.</p>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4">
                  {emotes.map((emote) => (
                    <div key={emote.id || emote._id} className="p-3 rounded-xl border border-[#1e2038] bg-black/20 flex flex-col items-center gap-3 relative group">
                      <div className="w-14 h-14 rounded-lg overflow-hidden border border-[#1e2038] bg-[#121324] flex items-center justify-center">
                        <img src={emote.imageUrl} alt={emote.code} className="max-w-full max-h-full object-contain" />
                      </div>
                      <span className="text-[10px] font-mono font-bold text-slate-300 select-all truncate max-w-full px-1 bg-[#121324] rounded">
                        {emote.code}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleDeleteEmote(emote.id)}
                        className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 hover:border-red-500/40 transition-all absolute top-2 right-2 opacity-0 group-hover:opacity-100 cursor-pointer"
                        title="Hapus Emote"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'donasi' && ("""

    if old_donasi in content:
        content = content.replace(old_donasi, new_emotes_jsx)
        print("✓ Admin: Emotes tab view added")
    else:
        print("✗ Admin: Donasi selector not matched")

    with open(admin_path, "w") as f:
        f.write(content)
    return True

def edit_page_js():
    page_path = "/app/app/page.js"
    if not os.path.exists(page_path):
        print("page.js not found")
        return False
        
    with open(page_path, "r") as f:
        content = f.read()

    # 1. Import EmotePicker
    old_import = "import Image from 'next/image'"
    new_import = "import Image from 'next/image'\nimport EmotePicker from '@/components/EmotePicker'"
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✓ Home: EmotePicker imported")
    else:
        print("✗ Home: Import not matched")

    # 2. Add states and handlers inside App component
    old_app_start = """  const formatEpisodeBadge = (episodeStr) => {"""
    new_app_start = """  const [emotes, setEmotes] = useState([])

  const fetchEmotes = async () => {
    try {
      const res = await fetch('/api/emotes')
      if (res.ok) {
        const data = await res.json()
        setEmotes(Array.isArray(data) ? data : [])
      }
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchEmotes()
  }, [])

  const parseEmotesToHtml = (text, emotesList = []) => {
    if (!text) return '';
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');

    emotesList.forEach(emote => {
      const regex = new RegExp(emote.code, 'g');
      escaped = escaped.replace(regex, `<img src="${emote.imageUrl}" alt="${emote.code}" class="inline-block w-5 h-5 object-contain mx-0.5" title="${emote.code}" />`);
    });

    return escaped;
  };

  const formatEpisodeBadge = (episodeStr) => {"""

    if old_app_start in content:
        content = content.replace(old_app_start, new_app_start)
        print("✓ Home: States and helpers added")
    else:
        print("✗ Home: app start not matched")

    # 3. Replace {comment.content} in comments list rendering
    old_comment_content = "<p className=\"text-xs leading-relaxed opacity-95 text-slate-100\">{comment.content}</p>"
    new_comment_content = "<div className=\"text-xs leading-relaxed opacity-95 text-slate-100\" dangerouslySetInnerHTML={{ __html: parseEmotesToHtml(comment.content, emotes) }} />"
    if old_comment_content in content:
        content = content.replace(old_comment_content, new_comment_content)
        print("✓ Home: Comment renderer parsed")
    else:
        print("✗ Home: Comment renderer not matched")

    # 4. Insert EmotePicker inside Comment Form Input
    old_comment_form = """                  <textarea
                    placeholder="Tulis opini nostalgia kamu di sini..."
                    value={newCommentText}
                    onChange={(e) => setNewCommentText(e.target.value)}
                    className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white focus:border-cyan-500 outline-none transition-all h-20 leading-relaxed resize-none"
                    required
                  />
                  <div className="flex justify-end pt-1">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-black text-xs font-black rounded-lg shadow-lg flex items-center gap-1"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Kirim Opini</span>
                    </button>
                  </div>"""

    new_comment_form = """                  <div className="relative">
                    <textarea
                      placeholder="Tulis opini nostalgia kamu di sini..."
                      value={newCommentText}
                      onChange={(e) => setNewCommentText(e.target.value)}
                      className="w-full text-xs p-3 pr-10 rounded-lg bg-[#121324] border border-[#1e2038] text-white focus:border-cyan-500 outline-none transition-all h-20 leading-relaxed resize-none"
                      required
                    />
                    <div className="absolute right-2 bottom-2">
                      <EmotePicker onSelectEmote={(code) => setNewCommentText(prev => prev + ' ' + code + ' ')} />
                    </div>
                  </div>
                  <div className="flex justify-end pt-1">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-black text-xs font-black rounded-lg shadow-lg flex items-center gap-1"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Kirim Opini</span>
                    </button>
                  </div>"""

    if old_comment_form in content:
        content = content.replace(old_comment_form, new_comment_form)
        print("✓ Home: Comment form updated with EmotePicker")
    else:
        print("✗ Home: Comment form not matched")

    with open(page_path, "w") as f:
        f.write(content)
    return True

def edit_chat_widget():
    chat_path = "/app/components/FloatingChatWidget.jsx"
    if not os.path.exists(chat_path):
        print("FloatingChatWidget not found")
        return False
        
    with open(chat_path, "r") as f:
        content = f.read()

    # 1. Import EmotePicker
    old_import = "import { MessageSquare, X, Send } from 'lucide-react'"
    new_import = "import { MessageSquare, X, Send } from 'lucide-react'\nimport EmotePicker from '@/components/EmotePicker'"
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✓ Chat: EmotePicker imported")
    else:
        print("✗ Chat: Import not matched")

    # 2. Add state and fetch inside FloatingChatWidget
    old_widget_start = "  const [currentUser, setCurrentUser] = useState(null)"
    new_widget_start = """  const [currentUser, setCurrentUser] = useState(null)
  const [emotes, setEmotes] = useState([])

  const fetchEmotes = async () => {
    try {
      const res = await fetch('/api/emotes')
      if (res.ok) {
        const data = await res.json()
        setEmotes(Array.isArray(data) ? data : [])
      }
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchEmotes()
  }, [])

  const parseEmotesToHtml = (text, emotesList = []) => {
    if (!text) return '';
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');

    emotesList.forEach(emote => {
      const regex = new RegExp(emote.code, 'g');
      escaped = escaped.replace(regex, `<img src="${emote.imageUrl}" alt="${emote.code}" class="inline-block w-5 h-5 object-contain mx-0.5" title="${emote.code}" />`);
    });

    return escaped;
  };"""

    if old_widget_start in content:
        content = content.replace(old_widget_start, new_widget_start)
        print("✓ Chat: States and fetcher added")
    else:
        print("✗ Chat: widget start not matched")

    # 3. Replace {msg.content} with dangerouslySetInnerHTML
    old_content = """                      <div className={`p-2.5 rounded-2xl text-[11px] leading-relaxed break-words ${
                        isMe 
                          ? 'bg-cyan-500 text-black font-semibold rounded-tr-none' 
                          : 'bg-[#121324] border border-[#1e2038] text-slate-100 rounded-tl-none'
                      }`}>
                        {msg.content}
                      </div>"""

    new_content = """                      <div className={`p-2.5 rounded-2xl text-[11px] leading-relaxed break-words ${
                        isMe 
                          ? 'bg-cyan-500 text-black font-semibold rounded-tr-none' 
                          : 'bg-[#121324] border border-[#1e2038] text-slate-100 rounded-tl-none'
                      }`} dangerouslySetInnerHTML={{ __html: parseEmotesToHtml(msg.content, emotes) }} />"""

    if old_content in content:
        content = content.replace(old_content, new_content)
        print("✓ Chat: Message renderer parsed")
    else:
        print("✗ Chat: Message renderer not matched")

    # 4. Add EmotePicker inside input form footer
    old_input = """          <form onSubmit={handleSendMessage} className="p-2 border-t border-[#1e2038] bg-[#0c0d18] flex gap-2 items-center">
            <input
              type="text"
              placeholder={currentUser ? "Tulis sesuatu di sini..." : "Silakan login untuk mengirim..."}
              disabled={!currentUser}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 text-xs p-2 rounded-xl bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-cyan-500 placeholder-slate-500"
            />"""

    new_input = """          <form onSubmit={handleSendMessage} className="p-2 border-t border-[#1e2038] bg-[#0c0d18] flex gap-1.5 items-center">
            <div className="flex-1 relative flex items-center">
              <input
                type="text"
                placeholder={currentUser ? "Tulis sesuatu di sini..." : "Silakan login untuk mengirim..."}
                disabled={!currentUser}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="w-full text-xs p-2 pr-8 rounded-xl bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-cyan-500 placeholder-slate-500"
              />
              <div className="absolute right-1">
                <EmotePicker onSelectEmote={(code) => setInputText(prev => prev + ' ' + code + ' ')} />
              </div>
            </div>"""

    if old_input in content:
        content = content.replace(old_input, new_input)
        print("✓ Chat: Form input updated with EmotePicker")
    else:
        print("✗ Chat: Form input not matched")

    with open(chat_path, "w") as f:
        f.write(content)
    return True

if __name__ == "__main__":
    edit_admin_page()
    edit_page_js()
    edit_chat_widget()
    print("ALL FRONTEND FILES SUCCESSFULLY MODIFIED!")
