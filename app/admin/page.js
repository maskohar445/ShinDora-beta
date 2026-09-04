'use client'

import { useState, useEffect, useRef } from 'react'
import { 
  Tv, 
  TvIcon, 
  Trash2, 
  Edit3, 
  Plus, 
  Search, 
  Upload, 
  Save, 
  Users, 
  Settings, 
  ListVideo, 
  Megaphone,
  FolderMinus,
  Settings2,
  ChevronDown,
  FileText,
  ArrowLeft,
  HeartHandshake,
  Smile,
  Download
} from 'lucide-react'

const SUB_CATEGORIES_MAP = {
  'Doraemon': ["Stand by Me", "Movie / Standalone Film", "Season 1", "Season 2", "OVA", "Spesial"],
  'Crayon Shinchan': ["Movie", "Season 1", "Season 2", "Spesial", "Spinoff"],
  'Ninja Hattori-kun': ["Season 1", "Season 2", "Movie", "OVA"],
  'Chibi Maruko-chan': ["Season 1", "Season 2", "Movie"],
  'Tv Series': ["Season 1", "Season 2", "OVA"],
  'Movie': ["Doraemon", "Crayon Shinchan"]
};

const maskEmail = (email) => {
  if (!email || !email.includes('@')) return email;
  const [localPart, domain] = email.split('@');
  if (localPart.length <= 3) {
    return `${localPart[0]}***@${domain}`;
  }
  return `${localPart.substring(0, 3)}***@${domain}`;
}

const parseEpisodeNumber = (episodeStr) => {
  if (!episodeStr) return 0;
  const match = episodeStr.match(/\d+(\.\d+)?/);
  return match ? parseFloat(match[0]) : 0;
}

const sortVideosByEpisode = (videoList) => {
  if (!videoList) return [];
  return [...videoList].sort((a, b) => {
    const titleA = a.animeTitle || '';
    const titleB = b.animeTitle || '';
    const comp = titleA.localeCompare(titleB);
    if (comp !== 0) return comp;
    
    const numA = parseEpisodeNumber(a.episode);
    const numB = parseEpisodeNumber(b.episode);
    return numA - numB;
  });
}

export default function AdminPage() {
  const [isAdmin, setIsAdmin] = useState(false)
  const [theme, setTheme] = useState('dark')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const savedTheme = localStorage.getItem('shindora-theme') || 'dark'
    setTheme(savedTheme)
    setMounted(true)
  }, [])

  const [loading, setLoading] = useState(false)
  const [fallbackTrigger, setFallbackTrigger] = useState(false)
  const [activeTab, setActiveTab] = useState('videos') // videos, categories, users, playlists, ads, settings, pages, polling
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
  }
  const [searchQuery, setSearchQuery] = useState('')

  // Core collections data
  const [videos, setVideos] = useState([])
  const [categories, setCategories] = useState([])
  const [users, setUsers] = useState([])
  const [playlists, setPlaylists] = useState([])
  const [ads, setAds] = useState([])
  const [staticPages, setStaticPages] = useState([])
  const [donations, setDonations] = useState([])
  
  // Settings details
  const [logoPreview, setLogoPreview] = useState('')
  const [siteSettings, setSiteSettings] = useState({
    logoUrl: '',
    imagekitPublicKey: '',
    imagekitPrivateKey: '',
    imagekitUrlEndpoint: '',
    donationOverlayActive: true,
    saweriaStreamKey: '',
    trakteerStreamKey: '',
    takoStreamKey: '',
    announcementText: '',
    announcementBadge: 'PENGUMUMAN',
    isManualDonationActive: false,
    manualDonatorName: '',
    manualDonationAmount: '',
    manualDonationMessage: '',
    manualDonationPlatform: 'Saweria',
    donationPopupDuration: 6,
    donationMarqueeSpeed: 'Sedang',
    emailProvider: 'Mock/Simulasi',
    emailProviderCredentials: {
      smtpHost: '',
      smtpPort: '',
      smtpUser: '',
      smtpPass: ''
    },
    socialLinks: [],
    hero_banner_active: true,
    hero_badge_text: '',
    hero_title: '',
    hero_description: '',
    hero_featured_image: '',
    hero_featured_label: '',
    hero_featured_title: '',
    antiAdblockActive: false,
    antiAdblockMessage: '',
    antiCopyActive: false,
    antiDevToolsActive: false,
    live_chat_active: true,
    blocked_words: 'anjing, babi, bangsat, anjrit, fuck, shit, kontol, memek, asu, bajingan, tolol, bego, goblok, idiot, kampang, biadab, pante, pantek, lonte, jamet, peler, jembut, ngetot, ngentot, kimak, pecun, tetek, pussy, dick, asshole, bitch, bastard, cunt, motherfucker',
    onesignalRestApiKey: ''
  })

  // Modals / Create forms states
  const [showVideoModal, setShowVideoModal] = useState(false)
  const [editingVideo, setEditingVideo] = useState(null)
  const [statusFilter, setStatusFilter] = useState('all')
  const [videoForm, setVideoForm] = useState({
    title: '', slug: '', animeTitle: 'Doraemon', subCategory: '', subCategory2: '', episode: '', thumbnailUrl: '', videoUrl: '', videoUrl2: '', videoUrl3: '', description: '', views: 0, likes: 0, status: 'published', scheduledAt: '', duration: ''
  })
  const [isVideoSlugManuallyEdited, setIsVideoSlugManuallyEdited] = useState(false)
  const [tempDonName, setTempDonName] = useState('')
  const [tempDonAmount, setTempDonAmount] = useState('')
  const [tempDonMessage, setTempDonMessage] = useState('')
  const [tempDonPlatform, setTempDonPlatform] = useState('Saweria')

  const handleAddManualDonation = () => {
    if (!tempDonName.trim() || !tempDonAmount.trim()) {
      alert("Nama Donatur dan Nominal wajib diisi!");
      return;
    }
    const newItem = {
      id: `manual-don-${Date.now()}`,
      name: tempDonName,
      amount: tempDonAmount,
      message: tempDonMessage,
      platform: tempDonPlatform,
      createdAt: new Date().toISOString()
    };
    const updatedList = [...(siteSettings.manualDonationList || []), newItem];
    setSiteSettings({ ...siteSettings, manualDonationList: updatedList });
    setTempDonName('');
    setTempDonAmount('');
    setTempDonMessage('');
  };

  const handleRemoveManualDonation = (id) => {
    const updatedList = (siteSettings.manualDonationList || []).filter(item => item.id !== id);
    setSiteSettings({ ...siteSettings, manualDonationList: updatedList });
  };

  const handleClearAllManualDonations = () => {
    if (confirm("Apakah Anda yakin ingin menghapus seluruh daftar donasi manual? Tindakan ini tidak bisa dibatalkan.")) {
      setSiteSettings({ ...siteSettings, manualDonationList: [] });
    }
  };

  // Bulk CSV import field
  const [csvInput, setCsvInput] = useState('')
  const [showCsvBox, setShowCsvBox] = useState(false)

// Category Form state
  const [catName, setCatName] = useState('')
  const [catParentId, setCatParentId] = useState('none')
  const [editingCat, setEditingCat] = useState(null)
  const [mainCatName, setMainCatName] = useState('')
  const [subCatName, setSubCatName] = useState('')
  const [selectedMainId, setSelectedMainId] = useState('')

  // State Baru untuk Sub-Kategori 2
  const [subCat2Name, setSubCat2Name] = useState('')
  const [selectedSub1Id, setSelectedSub1Id] = useState('')

  const handleCreateMainCategory = async (e) => {
    e.preventDefault()
    if (!mainCatName.trim()) return
    const payload = {
      name: mainCatName,
      parent_id: null
    }
    try {
      const res = await fetch("/api/categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert("🎉 Kategori Utama berhasil disimpan!")
        setMainCatName("")
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || "Gagal menyimpan kategori utama")
      }
    } catch (err) {
      alert(err.message)
    }
  }

  const handleCreateSubCategory = async (e) => {
    e.preventDefault()
    if (!subCatName.trim() || !selectedMainId) {
      alert("Pilih Kategori Utama Induk dan isi Nama Sub-Kategori 1!")
      return
    }
    const payload = {
      name: subCatName,
      parent_id: selectedMainId
    }
    try {
      const res = await fetch("/api/categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert("🎉 Sub-Kategori 1 berhasil disimpan!")
        setSubCatName("")
        setSelectedMainId("")
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || "Gagal menyimpan sub-kategori 1")
      }
    } catch (err) {
      alert(err.message)
    }
  }

  // Handler Baru untuk Sub-Kategori 2
  const handleCreateSubCategory2 = async (e) => {
    e.preventDefault()
    if (!subCat2Name.trim() || !selectedSub1Id) {
      alert("Pilih Induk Sub-Kategori 1 dan isi Nama Sub-Kategori 2!")
      return
    }
    const payload = {
      name: subCat2Name,
      parent_id: selectedSub1Id
    }
    try {
      const res = await fetch("/api/categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert("🎉 Sub-Kategori 2 berhasil disimpan!")
        setSubCat2Name("")
        setSelectedSub1Id("")
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || "Gagal menyimpan sub-kategori 2")
      }
    } catch (err) {
      alert(err.message)
    }
  }

  // Playlist Form state
  const [playlistForm, setPlaylistForm] = useState({
    title: '', videoIds: []
  })
  const [editingPlaylist, setEditingPlaylist] = useState(null)
  const [playlistVideoSearch, setPlaylistVideoSearch] = useState('')

  // Ad Form state
  const [adForm, setAdForm] = useState({
    slot: 'banner_top', title: '', imageUrl: '', targetUrl: '', isActive: true, isRaw: false, rawCode: '', openInNewTab: true
  })
  const [editingAd, setEditingAd] = useState(null)

  // Pages Manager Form state
  const [showPageModal, setShowPageModal] = useState(false)
  const [editingPage, setEditingPage] = useState(null)
  const [pageForm, setPageForm] = useState({
    title: '', slug: '', content: '', showInFooter: true
  })
  const [isSlugManuallyEdited, setIsSlugManuallyEdited] = useState(false)

  // Donation Simulation Form state
  const [donForm, setDonForm] = useState({
    name: '', amount: 'Rp 10.000', message: '', platform: 'Saweria'
  })
  const [isSubmittingDonation, setIsSubmittingDonation] = useState(false)

  // Polling Manager Form State
  const [pollingList, setPollingList] = useState([])
  const [showPollModal, setShowPollModal] = useState(false)
  const [editingPoll, setEditingPoll] = useState(null)
  const [pollForm, setPollForm] = useState({
    title: '', options: [{ id: 'opt-1', name: '', imageUrl: '', votes: 0 }], isActive: true
  })

  // Logo Upload ImageKit State
  const [logoUploadProgress, setLogoUploadProgress] = useState(null)
  const logoFileInputRef = useRef(null)

  // Hero Featured Image Upload State
  const [heroImageUploadProgress, setHeroImageUploadProgress] = useState(null)
  const heroImageFileInputRef = useRef(null)

  // Ad Banner Image Upload State
  const adFileInputRef = useRef(null)
  const [adUploadProgress, setAdUploadProgress] = useState(null)

  const uploadToImageKit = async (file, prefix) => {
    if (!file) throw new Error('Tidak ada berkas terpilih!');

    const validFormats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validFormats.includes(file.type)) {
      throw new Error('Format berkas tidak valid! Hanya mendukung JPG, PNG, atau WEBP.');
    }

    const maxSize = 1 * 1024 * 1024;
    if (file.size > maxSize) {
      throw new Error('Gagal! Batas ukuran file maksimal adalah 1 MB (1024 KB).');
    }

    try {
      const authRes = await fetch('/api/imagekit/auth');
      if (!authRes.ok) {
        const errData = await authRes.json();
        throw new Error(errData.error || 'Gagal mengautentikasi ImageKit di backend');
      }
      const authData = await authRes.json();

      const formData = new FormData();
      formData.append('file', file);
      formData.append('fileName', `${prefix}_${Date.now()}_${file.name}`);
      formData.append('publicKey', authData.publicKey);
      formData.append('signature', authData.signature);
      formData.append('expire', authData.expire.toString());
      formData.append('token', authData.token);

      const ikRes = await fetch('https://upload.imagekit.io/api/v1/files/upload', {
        method: 'POST',
        body: formData
      });

      if (!ikRes.ok) {
        const ikErr = await ikRes.json();
        throw new Error(ikErr.message || 'ImageKit menolak unggahan berkas');
      }

      const ikData = await ikRes.json();
      return ikData.url;

    } catch (err) {
      console.error(`[ImageKit ${prefix} Upload Error]:`, err);
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const endpoint = siteSettings.imagekitUrlEndpoint || 'https://ik.imagekit.io/shindora';
          const mockUrl = `${endpoint}/mock_${prefix}_${Date.now()}_${file.name}`;
          resolve(mockUrl);
        };
        reader.readAsDataURL(file);
      });
    }
  };

  const handleAdUploadToImageKit = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setAdUploadProgress("Mengunggah Banner ke ImageKit...")
    try {
      const url = await uploadToImageKit(file, "ad")
      setAdForm(prev => ({ ...prev, imageUrl: url }))
      alert('Gambar Banner berhasil diunggah ke ImageKit CDN!')
    } catch (err) {
      alert(err.message)
    } finally {
      setAdUploadProgress(null)
    }
  }

  // Polling Option Upload State
  const pollFileInputRef = useRef(null)
  const [uploadingPollOptionIndex, setUploadingPollOptionIndex] = useState(null)
  const [pollUploadProgress, setPollUploadProgress] = useState(null)

  const handlePollOptionUploadToImageKit = async (e) => {
    const file = e.target.files[0]
    if (!file || uploadingPollOptionIndex === null) return

    setPollUploadProgress(`Mengunggah Gambar Opsi ${uploadingPollOptionIndex + 1} ke ImageKit...`)
    try {
      const url = await uploadToImageKit(file, "poll")
      const updatedOptions = [...pollForm.options]
      updatedOptions[uploadingPollOptionIndex].imageUrl = url
      setPollForm({ ...pollForm, options: updatedOptions })
      alert(`Gambar Opsi ${uploadingPollOptionIndex + 1} berhasil diunggah ke ImageKit CDN!`)
    } catch (err) {
      alert(err.message)
    } finally {
      setPollUploadProgress(null)
      setUploadingPollOptionIndex(null)
    }
  }

  // Video Thumbnail Upload State
  const videoFileInputRef = useRef(null)
  const [videoUploadProgress, setVideoUploadProgress] = useState(null)

  const handleVideoThumbnailUploadToImageKit = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setVideoUploadProgress("Mengunggah Thumbnail ke ImageKit...")
    try {
      const url = await uploadToImageKit(file, "video")
      setVideoForm(prev => ({ ...prev, thumbnailUrl: url }))
      alert('Thumbnail video berhasil diunggah ke ImageKit CDN!')
    } catch (err) {
      alert(err.message)
    } finally {
      setVideoUploadProgress(null)
    }
  }

  const handleHeroImageUploadToImageKit = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setHeroImageUploadProgress("Mengunggah Gambar Hero ke ImageKit...")
    try {
      const url = await uploadToImageKit(file, "hero")
      setSiteSettings(prev => ({ ...prev, hero_featured_image: url }))
      alert('Gambar Utama Hero berhasil diunggah ke ImageKit CDN!')
    } catch (err) {
      alert(err.message)
    } finally {
      setHeroImageUploadProgress(null)
    }
  }

  const handleLogoUploadToImageKit = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setLogoUploadProgress("Mengunggah Logo ke ImageKit...")
    try {
      const url = await uploadToImageKit(file, "logo")
      setSiteSettings(prev => ({ ...prev, logoUrl: url }))
      setLogoPreview(url)
      alert('Logo berhasil diunggah ke ImageKit CDN!')
    } catch (err) {
      alert(err.message)
    } finally {
      setLogoUploadProgress(null)
    }
  }

  // Social link Form state
  const [newSocialName, setNewSocialName] = useState('')
  const [newSocialUrl, setNewSocialUrl] = useState('')

  // Admin Login Gate state
  const [adminPasswordInput, setAdminPasswordInput] = useState('')
  const [adminLoginError, setAdminLoginError] = useState('')
  const [isVerifyingAdmin, setIsVerifyingAdmin] = useState(false)

  useEffect(() => {
    document.documentElement.classList.add('dark')

    const validationTimer = setTimeout(() => {
      const storedUser = localStorage.getItem('shindora-user')
      if (storedUser) {
        const parsed = JSON.parse(storedUser)
        if (parsed.role === 'admin') {
          setIsAdmin(true)
          fetchAdminData()
        } else {
          setIsAdmin(false)
        }
      } else {
        setIsAdmin(false)
      }
      setLoading(false)
    }, 1200)

    const fallbackTimer = setTimeout(() => {
      setFallbackTrigger(true)
    }, 2500)

    return () => {
      clearTimeout(validationTimer)
      clearTimeout(fallbackTimer)
    }
  }, [])

  const handleAdminPasswordSubmit = async (e) => {
    e.preventDefault()
    setAdminLoginError('')
    setIsVerifyingAdmin(true)

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'admin@shindora.com',
          password: adminPasswordInput,
          isStaffOnly: true
        })
      })
      const data = await res.json()

      if (res.ok && data && !data.error) {
        localStorage.setItem('shindora-user', JSON.stringify(data))
        setIsAdmin(true)
        fetchAdminData()
      } else {
        setAdminLoginError(data.error || 'Kata Sandi Admin Salah!')
      }
    } catch (err) {
      console.error(err)
      setAdminLoginError('Koneksi server gagal!')
    } finally {
      setIsVerifyingAdmin(false)
    }
  }

  const fetchAdminData = async () => {
    try {
      const vRes = await fetch('/api/videos?showAll=true')
      const v = await vRes.json()
      setVideos(Array.isArray(v) ? v : [])

      const cRes = await fetch('/api/categories')
      const c = await cRes.json()
      setCategories(Array.isArray(c) ? c : [])

      const uRes = await fetch('/api/users')
      const u = await uRes.json()
      setUsers(Array.isArray(u) ? u : [])

      const pRes = await fetch('/api/playlists')
      const p = await pRes.json()
      setPlaylists(Array.isArray(p) ? p : [])

      const aRes = await fetch('/api/promo')
      const a = await aRes.json()
      setAds(Array.isArray(a) ? a : [])

      const sRes = await fetch('/api/settings')
      const s = await sRes.json()
      if (s && s.id) {
        setSiteSettings(s)
        setLogoPreview(s.logoUrl || '')
      }

      const pgRes = await fetch('/api/pages')
      const pg = await pgRes.json()
      setStaticPages(Array.isArray(pg) ? pg : [])

      const donRes = await fetch('/api/donations')
      const don = await donRes.json()
      setDonations(Array.isArray(don) ? don : [])

      const pollRes = await fetch('/api/polling')
      const plData = await pollRes.json()
      setPollingList(Array.isArray(plData) ? plData : [])
      fetchEmotes()
    } catch (err) {
      console.error('Error loading admin databases:', err)
    }
  }

  // Videos CRUD
  const handleSaveVideo = async (e) => {
    e.preventDefault()
    const method = editingVideo ? 'PUT' : 'POST'
    const payload = editingVideo ? { ...videoForm, id: editingVideo.id } : { ...videoForm, id: `vid-temp-${Date.now()}`, views: Number(videoForm.views || 0), likes: Number(videoForm.likes || 0), createdAt: new Date() }
    const previousVideos = [...videos]

    if (editingVideo) {
      setVideos(videos.map(v => v.id === editingVideo.id ? payload : v))
    } else {
      setVideos([payload, ...videos])
    }

    setShowVideoModal(false)
    setEditingVideo(null)
    const originalForm = { ...videoForm }
    setVideoForm({ title: '', slug: '', animeTitle: 'Doraemon', subCategory: '', subCategory2: '', episode: '', thumbnailUrl: '', videoUrl: '', videoUrl2: '', videoUrl3: '', description: '', views: 0, likes: 0, status: 'published', scheduledAt: '', duration: '' })

    try {
      const res = await fetch('/api/videos', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingVideo ? { ...originalForm, id: editingVideo.id } : originalForm)
      })
      if (res.ok) {
        fetchAdminData()
      } else {
        throw new Error('Gagal menyimpan data ke database server!')
      }
    } catch (err) {
      console.error(err)
      alert(`Error: ${err.message}. Mengembalikan daftar video...`)
      setVideos(previousVideos)
    }
  }

  const handleDeleteVideo = async (id) => {
    if (!confirm('Hapus video ini secara permanen?')) return
    const previousVideos = [...videos]

    setVideos(videos.filter(v => v.id !== id))

    try {
      const res = await fetch(`/api/videos?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        fetchAdminData()
      } else {
        throw new Error('Gagal menghapus video dari server!')
      }
    } catch (err) {
      console.error(err)
      alert(`Error: ${err.message}. Mengurungkan penghapusan video...`)
      setVideos(previousVideos)
    }
  }

  const handleBulkCSVImport = async () => {
    if (!csvInput.trim()) return
    try {
      const res = await fetch('/api/videos/bulk-csv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ csvData: csvInput })
      })
      const data = await res.json()
      if (res.ok && data.success) {
        alert(`Berhasil mengimpor ${data.count} video retro!`)
        setCsvInput('')
        setShowCsvBox(false)
        fetchAdminData()
      } else {
        alert(data.error || 'Gagal mengimpor CSV!')
      }
    } catch (err) {
      console.error(err)
    }
  }

  // Custom Static Pages CRUD
  const handleSavePage = async (e) => {
    e.preventDefault()
    if (!pageForm.title.trim() || !pageForm.slug.trim()) return
    const method = editingPage ? 'PUT' : 'POST'
    const payload = editingPage ? { ...pageForm, id: editingPage.id } : pageForm

    try {
      const res = await fetch('/api/pages', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert('Halaman statis berhasil disimpan!')
        setPageForm({ title: '', slug: '', content: '', showInFooter: true })
        setEditingPage(null)
        setShowPageModal(false)
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menyimpan halaman statis')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menyimpan halaman statis: " + err.message)
    }
  }

  const handleDeletePage = async (id) => {
    if (!confirm('Hapus halaman statis ini secara permanen?')) return
    try {
      const res = await fetch(`/api/pages?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Halaman statis berhasil dihapus!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menghapus halaman statis')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menghapus halaman statis: " + err.message)
    }
  }

  // Polling / Voting CRUD handlers
  const handleSavePoll = async (e) => {
    e.preventDefault()
    if (!pollForm.title.trim() || pollForm.options.length === 0) return
    const method = editingPoll ? 'PUT' : 'POST'
    const payload = editingPoll ? { ...pollForm, id: editingPoll.id } : pollForm

    try {
      const res = await fetch('/api/polling', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert('Polling anime berhasil disimpan!')
        setPollForm({ title: '', options: [{ id: 'opt-1', name: '', imageUrl: '', votes: 0 }], isActive: true })
        setEditingPoll(null)
        setShowPollModal(false)
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menyimpan polling')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menyimpan polling: " + err.message)
    }
  }

  const handleDeletePoll = async (id) => {
    if (!confirm('Hapus topik polling ini beserta seluruh datanya?')) return
    try {
      const res = await fetch(`/api/polling?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Polling berhasil dihapus!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menghapus polling')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menghapus polling: " + err.message)
    }
  }

  const handleResetPollVotes = async (poll) => {
    if (!confirm('Reset semua jumlah suara/counter untuk polling ini kembali ke 0?')) return
    const resetOptions = poll.options.map(o => ({ ...o, votes: 0 }))
    try {
      const res = await fetch('/api/polling', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: poll.id, options: resetOptions })
      })
      if (res.ok) {
        alert('Perolehan suara berhasil di-reset!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal mereset perolehan suara')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal mereset perolehan suara: " + err.message)
    }
  }

  // Categories CRUD
  const handleSaveCategory = async (e) => {
    e.preventDefault()
    if (!catName.trim()) return
    const method = editingCat ? 'PUT' : 'POST'
    const payload = editingCat 
      ? { id: editingCat.id, name: catName, slug: catName.toLowerCase().replace(/ /g, '-'), parent_id: catParentId === 'none' ? null : catParentId } 
      : { name: catName, slug: catName.toLowerCase().replace(/ /g, '-'), parent_id: catParentId === 'none' ? null : catParentId }

    try {
      const res = await fetch('/api/categories', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert('Kategori berhasil disimpan!')
        setCatName('')
        setCatParentId('none')
        setEditingCat(null)
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menyimpan kategori ke server')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menyimpan kategori: " + err.message)
    }
  }

  const handleDeleteCategory = async (id) => {
    if (!confirm('Hapus kategori ini?')) return
    try {
      const res = await fetch(`/api/categories?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Kategori berhasil dihapus!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menghapus kategori dari server')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menghapus kategori: " + err.message)
    }
  }

  // User Management
  const handleUserRoleChange = async (user, newRole) => {
    try {
      const res = await fetch('/api/users', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: user.id, role: newRole })
      })
      if (res.ok) {
        alert('Peran pengguna berhasil diperbarui!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal memperbarui peran pengguna')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal memperbarui peran pengguna: " + err.message)
    }
  }

  const handleToggleUserBan = async (user) => {
    try {
      const res = await fetch('/api/users', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: user.id, isBanned: !user.isBanned })
      })
      if (res.ok) {
        alert(user.isBanned ? 'Status cekal pengguna berhasil dicabut!' : 'Pengguna berhasil dicekal!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal memperbarui status cekal')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal memperbarui status cekal: " + err.message)
    }
  }

  // Official Playlist CRUD
  const handleSavePlaylist = async (e) => {
    e.preventDefault()
    if (!playlistForm.title.trim()) return
    const videoIds = playlistForm.videoIds

    // Automatically sort videoIds before saving
    const selectedVideos = videos.filter(v => videoIds.includes(v.id))
    const sortedSelected = sortVideosByEpisode(selectedVideos)
    const sortedVideoIds = sortedSelected.map(v => v.id)

    const payload = editingPlaylist
      ? { id: editingPlaylist.id, title: playlistForm.title, videoIds: sortedVideoIds }
      : { title: playlistForm.title, ownerId: null, isPrivate: false, videoIds: sortedVideoIds }

    const method = editingPlaylist ? 'PUT' : 'POST'

    try {
      const res = await fetch('/api/playlists', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert('Playlist berhasil disimpan!')
        setPlaylistForm({ title: '', videoIds: [] })
        setEditingPlaylist(null)
        setPlaylistVideoSearch('')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menyimpan playlist')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menyimpan playlist: " + err.message)
    }
  }

  const handleDeletePlaylist = async (id) => {
    if (!confirm('Hapus playlist ini?')) return
    try {
      const res = await fetch(`/api/playlists?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Playlist berhasil dihapus!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menghapus playlist')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menghapus playlist: " + err.message)
    }
  }

  // Ads/Iklan CRUD
  const handleSaveAd = async (e) => {
    e.preventDefault()
    const method = editingAd ? 'PUT' : 'POST'
    const payload = editingAd ? { ...adForm, id: editingAd.id } : adForm

    try {
      const res = await fetch('/api/promo', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert('Iklan/promosi berhasil disimpan!')
        setAdForm({ slot: 'banner_top', title: '', imageUrl: '', targetUrl: '', isActive: true, isRaw: false, rawCode: '', openInNewTab: true })
        setEditingAd(null)
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menyimpan iklan')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menyimpan iklan: " + err.message)
    }
  }

  const handleDeleteAd = async (id) => {
    if (!confirm('Hapus slot iklan ini?')) return
    try {
      const res = await fetch(`/api/promo?id=${id}`, { method: 'DELETE' })
      if (res.ok) {
        alert('Iklan berhasil dihapus!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menghapus iklan')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menghapus iklan: " + err.message)
    }
  }

  const handleSaveOverlaySettings = async () => {
    const payload = {
      saweriaStreamKey: siteSettings.saweriaStreamKey,
      trakteerStreamKey: siteSettings.trakteerStreamKey,
      takoStreamKey: siteSettings.takoStreamKey,
      donationPopupDuration: Number(siteSettings.donationPopupDuration || 6)
    };
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert("🎉 Pengaturan overlay donasi berhasil disimpan!");
        fetchAdminData();
      } else {
        throw new Error("Gagal menyimpan!");
      }
    } catch (err) {
      console.error(err);
      alert("Gagal menyimpan pengaturan overlay donasi: " + err.message);
    }
  };

  const handleSaveRunningTextSettings = async () => {
    const payload = {
      announcementText: siteSettings.announcementText,
      announcementBadge: siteSettings.announcementBadge,
      donationMarqueeSpeed: siteSettings.donationMarqueeSpeed || 'Sedang',
      donationOverlayActive: siteSettings.donationOverlayActive === undefined ? true : siteSettings.donationOverlayActive
    };
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert("🎉 Pengaturan running text berhasil disimpan dan ditampilkan!");
        fetchAdminData();
      } else {
        throw new Error("Gagal menyimpan!");
      }
    } catch (err) {
      console.error(err);
      alert("Gagal menyimpan pengaturan running text: " + err.message);
    }
  };

  // Settings & social
  const handleSaveSettings = async () => {
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(siteSettings)
      })
      if (res.ok) {
        alert('Pengaturan Website Berhasil Disimpan!')
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || 'Gagal menyimpan pengaturan')
      }
    } catch (err) {
      console.error(err)
      alert("Gagal menyimpan pengaturan website: " + err.message)
    }
  }

  const handleAddSocialLink = () => {
    if (!newSocialName.trim() || !newSocialUrl.trim()) return
    const newLink = { id: Date.now().toString(), name: newSocialName, url: newSocialUrl }
    const updatedLinks = [...(siteSettings.socialLinks || []), newLink]
    setSiteSettings({ ...siteSettings, socialLinks: updatedLinks })
    setNewSocialName('')
    setNewSocialUrl('')
  }

  const handleRemoveSocialLink = (id) => {
    const updatedLinks = siteSettings.socialLinks.filter(l => l.id !== id)
    setSiteSettings({ ...siteSettings, socialLinks: updatedLinks })
  }

  // Filtering list search queries
  const searchedVideos = videos.filter(v => {
    const q = searchQuery.toLowerCase().trim();
    const matchesSearch = !q ||
                          v.title.toLowerCase().includes(q) || 
                          v.id.includes(q) || 
                          (v.episode && v.episode.toLowerCase().includes(q)) ||
                          (v.animeTitle && v.animeTitle.toLowerCase().includes(q)) ||
                          (v.subCategory && v.subCategory.toLowerCase().includes(q)) ||
                          (v.subCategory2 && v.subCategory2.toLowerCase().includes(q));
    
    if (statusFilter === 'published') {
      return matchesSearch && (!v.status || v.status === 'published');
    }
    if (statusFilter === 'draft') {
      return matchesSearch && v.status === 'draft';
    }
    if (statusFilter === 'scheduled') {
      return matchesSearch && v.status === 'scheduled';
    }
    return matchesSearch;
  })
  const searchedCategories = categories.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()))
  const searchedUsers = users.filter(u => u.name.toLowerCase().includes(searchQuery.toLowerCase()) || u.email.toLowerCase().includes(searchQuery.toLowerCase()))
  const searchedPlaylists = playlists.filter(p => p.ownerId === null && p.title.toLowerCase().includes(searchQuery.toLowerCase()))
  const searchedAds = ads.filter(a => a.title.toLowerCase().includes(searchQuery.toLowerCase()))

  if (!mounted) {
    return null;
  }

  if (loading) {
    return (
      <div className="dark min-h-screen bg-slate-950 text-cyan-400 flex flex-col items-center justify-center p-4">
        <div className="w-10 h-10 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-xs font-semibold uppercase tracking-wider text-cyan-400 animate-pulse">Pemeriksaan Sesi Admin Shindora...</p>
        
        {fallbackTrigger && (
          <div className="mt-8 space-y-3 max-w-xs text-center animate-fade-in">
            <p className="text-[10px] opacity-60 leading-relaxed">
              Sesi otentikasi mengambil waktu terlalu lama untuk dimuat atau terganggu.
            </p>
            <a
              href="/login"
              className="inline-block px-5 py-2 bg-red-600 hover:bg-red-700 text-white font-black text-xs rounded-lg transition-all"
            >
              Kembali ke Login
            </a>
          </div>
        )}
      </div>
    )
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-[#07080f] text-[#e2e8f0] flex items-center justify-center p-4 relative">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-red-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-72 h-72 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="w-full max-w-md rounded-2xl border border-red-500/20 bg-[#0d0e1b]/95 p-6 md:p-8 shadow-2xl relative">
          <a href="/" className="absolute top-4 right-4 text-xs font-bold text-slate-400 hover:text-white transition-all">
            &times; Beranda
          </a>

          <div className="text-center space-y-2 mb-6">
            <div className="inline-flex items-center justify-center p-2 bg-red-500 rounded-xl text-black font-black mb-1">
              <Tv className="w-5 h-5 fill-current" />
            </div>
            <h2 className="text-xl md:text-2xl font-black uppercase tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-red-400 via-pink-400 to-purple-500">
              PENGENDALI UTAMA
            </h2>
            <p className="text-xs opacity-60">Masukkan Kata Sandi Admin untuk mengonfigurasi sistem.</p>
          </div>

          {adminLoginError && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold text-center mb-4">
              ⚠️ {adminLoginError}
            </div>
          )}

          <form onSubmit={handleAdminPasswordSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] uppercase font-bold tracking-wider opacity-60">KATA SANDI ADMIN</label>
              <input
                type="password"
                placeholder="Masukkan kata sandi admin..."
                value={adminPasswordInput}
                onChange={(e) => setAdminPasswordInput(e.target.value)}
                className="w-full px-3 py-2 rounded-lg text-xs outline-none border bg-[#121324] border-[#1e2038] text-white focus:border-red-500 transition-all"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isVerifyingAdmin}
              className="w-full py-2.5 bg-gradient-to-r from-red-400 to-pink-500 text-white hover:opacity-90 font-extrabold text-xs transition-all tracking-wider uppercase"
            >
              {isVerifyingAdmin ? 'Memverifikasi...' : 'MASUK SEBAGAI PENGENDALI'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen flex flex-col md:flex-row ${theme === 'dark' ? 'dark-theme bg-[#0a0b14] text-[#e2e8f0]' : 'light-theme bg-[#f8fafc] text-[#0f172a]'}`}>
      
      <style dangerouslySetInnerHTML={{ __html: `
        .light-theme {
          --bg-main: #f8fafc;
          --bg-card: #ffffff;
          --bg-input: #ffffff;
          --border-color: #cbd5e1;
          --text-main: #0f172a;
          --text-muted: #475569;
        }
        .light-theme .bg-slate-950,
        .light-theme .bg-slate-900,
        .light-theme .bg-\\[\\#0a0b14\\] {
          background-color: var(--bg-main) !important;
          color: var(--text-main) !important;
        }
        .light-theme .bg-\\[\\#0d0e1b\\] {
          background-color: var(--bg-card) !important;
          color: var(--text-main) !important;
          border: 1px solid var(--border-color) !important;
        }
        .light-theme .bg-\\[\\#121324\\] {
          background-color: var(--bg-input) !important;
          color: var(--text-main) !important;
          border-color: var(--border-color) !important;
        }
        .light-theme .border-slate-800,
        .light-theme .border-\\[\\#1e2038\\],
        .light-theme .divide-\\[\\#1e2038\\] {
          border-color: var(--border-color) !important;
        }
        .light-theme .text-white,
        .light-theme .text-slate-100,
        .light-theme .text-slate-200 {
          color: var(--text-main) !important;
        }
        .light-theme .text-slate-300,
        .light-theme .text-slate-400 {
          color: var(--text-muted) !important;
        }
        .light-theme .bg-\\[\\#121324\\]::placeholder {
          color: #94a3b8 !important;
        }
        .light-theme select {
          background-color: var(--bg-card) !important;
          color: var(--text-main) !important;
          border-color: var(--border-color) !important;
        }
        .light-theme textarea {
          background-color: var(--bg-input) !important;
          color: var(--text-main) !important;
          border-color: var(--border-color) !important;
        }
        .light-theme .hover\\:bg-slate-500\\/5:hover {
          background-color: #f1f5f9 !important;
        }
        
        .light-theme table,
        .light-theme tbody,
        .light-theme tr,
        .light-theme td {
          background-color: #ffffff !important;
          color: #0f172a !important;
          border-color: #e2e8f0 !important;
        }
        .light-theme tr:nth-child(even) td {
          background-color: #f8fafc !important;
        }
        .light-theme table tr:hover td {
          background-color: #f1f5f9 !important;
        }
        .light-theme table thead,
        .light-theme table thead tr,
        .light-theme table thead th {
          background-color: #e2e8f0 !important;
          color: #1e293b !important;
          font-weight: 700 !important;
          opacity: 1 !important;
        }
        
        .light-theme .bg-black\\/30,
        .light-theme .bg-black\\/20,
        .light-theme .bg-black\\/40 {
          background-color: #f1f5f9 !important;
          border-color: #cbd5e1 !important;
          color: #0f172a !important;
        }
        .light-theme .text-red-400,
        .light-theme .text-pink-400 {
          color: #be185d !important;
        }
        .light-theme .text-cyan-400 {
          color: #0369a1 !important;
        }
        .light-theme label,
        .light-theme span.text-\\[10px\\] {
          color: #334155 !important;
          font-weight: 700 !important;
        }
        .light-theme select option {
          background-color: #ffffff !important;
          color: #0f172a !important;
        }
      `}} />

      {/* Sidebar - Fully Responsive */}
      <aside className={`w-full md:w-64 flex md:flex-col justify-between p-2 sm:p-4 border-b md:border-r border-slate-500/10 transition-all duration-200 overflow-x-auto md:overflow-x-visible ${
        theme === 'dark' ? 'bg-[#0d0e1b] border-[#1e2038]' : 'bg-white border-slate-200 shadow-sm'
      }`}>
        <div className="flex md:flex-col items-center md:items-stretch justify-between md:justify-start gap-4 md:space-y-6 w-full">
          <div className="flex items-center gap-2 px-2 flex-shrink-0">
            <div className="p-1 bg-red-500 rounded text-black font-black text-xs">AP</div>
            <span className="font-extrabold tracking-widest text-xs md:text-sm bg-gradient-to-r from-red-400 to-pink-500 bg-clip-text text-transparent">ADMIN SHINDORA</span>
          </div>

          <div className="flex md:flex-col gap-1.5 overflow-x-auto md:overflow-visible w-full scrollbar-hide">
            <a
              href="/"
              className={`px-3 py-2 text-xs font-bold rounded-lg flex items-center gap-2 transition-all whitespace-nowrap flex-shrink-0 md:flex-shrink md:w-full border ${
                theme === 'dark' 
                  ? 'bg-slate-500/5 hover:bg-slate-500/15 border-slate-500/10 text-cyan-400' 
                  : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
              }`}
              title="Kembali ke Website Publik"
            >
              <ArrowLeft className="w-4 h-4 flex-shrink-0" />
              <span>Lihat Website</span>
            </a>

            {[
              { id: 'videos', label: 'Videos Database', icon: TvIcon },
              { id: 'categories', label: 'Categories & Genres', icon: ListVideo },
              { id: 'users', label: 'User Roles & Moderation', icon: Users },
              { id: 'playlists', label: 'Official Playlists', icon: Tv },
              { id: 'ads', label: 'Ads slots', icon: Megaphone },
              { id: 'pages', label: 'Custom Static Pages', icon: FileText },
              { id: 'polling', label: 'Anime Polling / Vote', icon: ListVideo },
              { id: 'emotes', label: 'Custom Emotes & GIFs', icon: Smile },
              { id: 'settings', label: 'Settings & API settings', icon: Settings },
              { id: 'donasi', label: 'Donasi Manual', icon: HeartHandshake }
            ].map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setSearchQuery(''); }}
                  className={`px-3 py-2 text-xs font-bold rounded-lg flex items-center gap-2 transition-all whitespace-nowrap flex-shrink-0 md:flex-shrink md:w-full ${
                    activeTab === tab.id 
                      ? (theme === 'dark' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-red-50 text-red-600 border border-red-200') 
                      : (theme === 'dark' ? 'hover:bg-slate-500/5 opacity-70 text-slate-300' : 'hover:bg-slate-100 text-slate-600')
                  }`}
                  title={tab.label}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        <div className="p-2 border-t border-slate-500/10 space-y-1 hidden md:block">
          <div className="text-[10px] opacity-50 font-bold">Admin mode active</div>
        </div>
      </aside>

      {/* Main Content Container */}
      <main className="flex-1 p-3 sm:p-6 space-y-6 overflow-y-auto h-auto md:h-screen">
        
        <div className={`flex flex-col sm:flex-row justify-between sm:items-center border-b pb-4 gap-4 ${
          theme === 'dark' ? 'border-[#1e2038]' : 'border-slate-200'
        }`}>
          <div>
            <div className="flex items-center justify-between sm:justify-start gap-4">
              <h1 className="text-base sm:text-xl font-black">Panel Dashboard Pengendali Utama</h1>
              <button
                onClick={() => {
                  const nextTheme = theme === 'dark' ? 'light' : 'dark'
                  setTheme(nextTheme)
                  localStorage.setItem('shindora-theme', nextTheme)
                }}
                className={`px-2.5 py-1 text-[10px] sm:text-xs font-bold rounded-lg border transition-all ${
                  theme === 'dark' 
                    ? 'border-[#1e2038] bg-[#121324] hover:bg-[#1a1c32] text-yellow-400' 
                    : 'border-slate-200 bg-white hover:bg-slate-100 text-slate-700 shadow-sm'
                }`}
              >
                {theme === 'dark' ? '☀️ Mode Terang' : '🌙 Mode Gelap'}
              </button>
            </div>
            <p className="text-xs opacity-60 mt-0.5">Kelola data, kategori, pengguna, iklan, dan kunci integrasi sistem.</p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 opacity-55" />
            <input
              type="text"
              placeholder={`Cari dalam tab ${activeTab}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-8 pr-3 py-1.5 rounded-lg text-xs outline-none transition-all border ${
                theme === 'dark' 
                  ? 'bg-[#121324] border-[#1e2038] text-white focus:border-red-500' 
                  : 'bg-white border-slate-200 text-slate-900 focus:border-red-500'
              }`}
            />
          </div>
        </div>

        {activeTab === 'videos' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center bg-[#0d0e1b] p-4 rounded-xl border border-[#1e2038] gap-3">
              <div>
                <h3 className="font-extrabold text-sm">Kelola Data Video Retro ({videos.length})</h3>
                <p className="text-[11px] opacity-60">Tambah video, hapus, atau import massal via format CSV sederhana.</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => { 
                    setEditingVideo(null); 
                    setVideoForm({
                      title: '', slug: '', animeTitle: 'Doraemon', subCategory: '', subCategory2: '', episode: '', thumbnailUrl: '', videoUrl: '', videoUrl2: '', videoUrl3: '', description: '', views: 0, likes: 0, status: 'published', scheduledAt: '', duration: ''
                    });
                    setIsVideoSlugManuallyEdited(false); 
                    setShowVideoModal(true); 
                  }}
                  className="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white font-extrabold text-xs flex items-center gap-1 shadow-lg"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Tambah Video</span>
                </button>
                <button
                  onClick={() => setShowCsvBox(!showCsvBox)}
                  className="px-3 py-2 rounded-lg bg-slate-500/15 hover:bg-slate-500/25 border border-[#1e2038] font-bold text-xs"
                >
                  Bulk CSV Import
                </button>
              </div>
            </div>

            {/* Filter Status Bar */}
            <div className="flex flex-wrap gap-1.5 p-1 bg-[#0d0e1b] rounded-lg border border-[#1e2038] w-max select-none">
              {[
                { id: 'all', label: 'Semua Video' },
                { id: 'published', label: 'Publik' },
                { id: 'draft', label: 'Draft' },
                { id: 'scheduled', label: 'Terschedul / Jadwal' }
              ].map(item => (
                <button
                  key={item.id}
                  onClick={() => setStatusFilter(item.id)}
                  className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all ${
                    statusFilter === item.id
                      ? 'bg-red-500 text-white shadow-md'
                      : 'text-slate-400 hover:text-white hover:bg-slate-500/5'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            {showCsvBox && (
              <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 space-y-3">
                <h4 className="text-xs font-extrabold text-red-400">Import Banyak Episode Anime Sekaligus</h4>
                <p className="text-[10px] opacity-75 leading-relaxed">
                  Masukkan baris teks episode baru Anda di bawah ini dengan format koma: <br/>
                  <code className="text-red-300 font-mono text-[9px] bg-black/40 px-1 py-0.5 rounded">Judul Video,Judul Anime,Nomor Episode,URL Thumbnail,URL Video Embed,Deskripsi Singkat</code>
                </p>
                <textarea
                  value={csvInput}
                  onChange={(e) => setCsvInput(e.target.value)}
                  placeholder="Doraemon: Mesin Pengendali Mimpi,Doraemon,Eps 3,https://unsplash.com/...,https://youtube.com/embed/...,Petualangan seru Nobita di dalam mimpi."
                  className="w-full h-32 text-xs p-3 rounded-lg border bg-[#121324] border-[#1e2038] outline-none text-white font-mono"
                />
                <div className="flex justify-end gap-2">
                  <button onClick={() => setShowCsvBox(false)} className="px-3 py-1.5 text-xs opacity-60">Batal</button>
                  <button onClick={handleBulkCSVImport} className="px-4 py-1.5 bg-red-500 hover:bg-red-600 text-white text-xs font-black rounded">Proses Impor CSV</button>
                </div>
              </div>
            )}

            <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
              <table className="w-full text-xs text-left min-w-[600px]">
                <thead className="bg-[#121324] text-[10px] uppercase font-bold tracking-wider opacity-60 border-b border-[#1e2038]">
                  <tr>
                    <th className="p-3">Thumbnail &amp; Judul</th>
                    <th className="p-3">Anime</th>
                    <th className="p-3">Eps</th>
                    <th className="p-3 text-center">Views</th>
                    <th className="p-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2038]">
                  {searchedVideos.map(video => (
                    <tr key={video.id} className="hover:bg-slate-500/5 transition-all">
                      <td className="p-3 flex items-center gap-3">
                        <img src={video.thumbnailUrl} alt="" className="w-12 h-8 rounded object-cover flex-shrink-0" />
                        <div>
                          <p className="font-extrabold text-slate-100">{video.title}</p>
                          <div className="flex flex-wrap items-center gap-1.5 mt-0.5">
                            <span className="text-[10px] font-mono opacity-50">{video.slug || video.id}</span>
                            {/* Publication Status Badge */}
                            {(!video.status || video.status === 'published') && (
                              <span className="px-2 py-0.5 rounded bg-green-500/10 text-green-400 border border-green-500/20 font-black text-[9px] uppercase tracking-wider">
                                PUBLIK
                              </span>
                            )}
                            {video.status === 'draft' && (
                              <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-black text-[9px] uppercase tracking-wider">
                                DRAFT
                              </span>
                            )}
                            {video.status === 'scheduled' && (
                              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-black text-[9px] uppercase tracking-wider" title={`Rilis: ${video.scheduledAt ? new Date(video.scheduledAt).toLocaleString('id-ID') : '?'}`}>
                                JADWAL ({video.scheduledAt ? new Date(video.scheduledAt).toLocaleString('id-ID', { dateStyle: 'short', timeStyle: 'short' }) : '?'})
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="p-3 font-semibold text-cyan-400">
                        {video.animeTitle}
                        {video.subCategory ? ` > ${video.subCategory}` : ""}
                        {video.subCategory2 ? ` > ${video.subCategory2}` : ""}
                      </td>
                      <td className="p-3"><span className="px-1.5 py-0.5 rounded bg-pink-500/10 text-pink-400 font-bold text-[10px]">{video.episode}</span></td>
                      <td className="p-3 text-center opacity-70">{video.views?.toLocaleString()}</td>
                      <td className="p-3 text-right">
                        <div className="inline-flex gap-1.5">
                          <button
                            onClick={() => {
                              setEditingVideo(video);
                              setVideoForm({ status: 'published', scheduledAt: '', duration: '', ...video, slug: video.slug || '', duration: video.duration || '' });
                              setIsVideoSlugManuallyEdited(false);
                              setShowVideoModal(true);
                            }}
                            className="p-1.5 text-cyan-400 hover:bg-cyan-500/10 border border-cyan-500/20 rounded"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteVideo(video.id)}
                            className="p-1.5 text-red-400 hover:bg-red-500/10 border border-red-500/20 rounded"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'categories' && (
          <div className="space-y-6 max-w-6xl mx-auto">
            
            {/* TWO SEPARATE FORM CARDS SIDE-BY-SIDE */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Card 1: Tambah Kategori Utama */}
              <div className="bg-[#0d0e1b] p-5 rounded-2xl border border-slate-800 shadow-sm space-y-4">
                <h3 className="font-extrabold text-sm text-cyan-400 flex items-center gap-1.5">
                  ➕ Tambah Kategori Utama
                </h3>
                <form onSubmit={handleCreateMainCategory} className="space-y-3.5 text-xs text-left">
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Nama Kategori Utama
                    </label>
                    <input
                      type="text"
                      value={mainCatName}
                      onChange={(e) => setMainCatName(e.target.value)}
                      placeholder="misal: TV Series, Movie, OVA"
                      className="w-full px-3 py-2.5 rounded-xl border border-[#1e2038] bg-[#121324] text-white focus:border-pink-500 outline-none"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-2.5 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-xl text-xs uppercase tracking-wider transition-all"
                  >
                    Simpan Kategori Utama
                  </button>
                </form>
              </div>

              {/* Card 2: Tambah Sub-Kategori */}
              <div className="bg-[#0d0e1b] p-5 rounded-2xl border border-slate-800 shadow-sm space-y-4">
                <h3 className="font-extrabold text-sm text-cyan-400 flex items-center gap-1.5">
                  📂 Tambah Sub-Kategori (Judul Anime)
                </h3>
                <form onSubmit={handleCreateSubCategory} className="space-y-3.5 text-xs text-left">
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Pilih Kategori Utama Induk
                    </label>
                    <select
                      value={selectedMainId}
                      onChange={(e) => setSelectedMainId(e.target.value)}
                      className="w-full px-3 py-2.5 rounded-xl border border-[#1e2038] bg-[#121324] text-white outline-none"
                      required
                    >
                      <option value="">-- Pilih Kategori Utama --</option>
                      {categories
                        .filter(c => !c.parent_id || c.parent_id === 'none')
                        .map((main) => (
                          <option key={main.id} value={main.id}>
                            {main.name}
                          </option>
                        ))}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">
                      Nama Sub-Kategori
                    </label>
                    <input
                      type="text"
                      value={subCatName}
                      onChange={(e) => setSubCatName(e.target.value)}
                      placeholder="misal: Doraemon, Crayon Shin-chan"
                      className="w-full px-3 py-2.5 rounded-xl border border-[#1e2038] bg-[#121324] text-white focus:border-pink-500 outline-none"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs uppercase tracking-wider transition-all"
                  >
                    Simpan Sub-Kategori
                  </button>
                </form>
              </div>

            </div>

            {/* TWO SEPARATE TABLES FOR MAIN AND SUB CATEGORIES */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-left">
              
              {/* Table 1: Daftar Kategori Utama */}
              <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] p-4 space-y-3.5 overflow-x-auto">
                <span className="text-[10px] font-black text-pink-400 uppercase tracking-widest block">
                  &bull; Daftar Kategori Utama ({categories.filter(c => !c.parent_id || c.parent_id === 'none').length})
                </span>
                <table className="w-full text-xs text-left">
                  <thead className="bg-[#121324] text-[10px] uppercase opacity-60 border-b border-[#1e2038]">
                    <tr>
                      <th className="p-3">Nama Kategori</th>
                      <th className="p-3 text-right">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e2038]">
                    {categories.filter(c => !c.parent_id || c.parent_id === 'none').length === 0 ? (
                      <tr>
                        <td colSpan="3" className="p-8 text-center opacity-50 italic">Belum ada Kategori Utama.</td>
                      </tr>
                    ) : (
                      categories
                        .filter(c => !c.parent_id || c.parent_id === 'none')
                        .map((cat, index) => (
                          <tr key={cat.id || `main-${index}`} className="hover:bg-slate-500/5 transition-all text-slate-300">
                            <td className="p-3 font-bold text-white">{cat.name}</td>
                            <td className="p-3 text-right">
                              <button
                                onClick={() => handleDeleteCategory(cat.id)}
                                className="p-1.5 text-red-400 hover:bg-red-500/10 border border-red-500/20 rounded cursor-pointer"
                                title="Hapus Kategori Utama"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* Table 2: Daftar Sub-Kategori */}
              <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] p-4 space-y-3.5 overflow-x-auto">
                <span className="text-[10px] font-black text-pink-400 uppercase tracking-widest block">
                  &bull; Daftar Sub-Kategori ({categories.filter(c => c.parent_id && c.parent_id !== 'none').length})
                </span>
                <table className="w-full text-xs text-left">
                  <thead className="bg-[#121324] text-[10px] uppercase opacity-60 border-b border-[#1e2038]">
                    <tr>
                      <th className="p-3">Nama Sub-Kategori</th>
                      <th className="p-3">Kategori Induk</th>
                      <th className="p-3 text-right">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e2038]">
                    {categories.filter(c => c.parent_id && c.parent_id !== 'none').length === 0 ? (
                      <tr>
                        <td colSpan="4" className="p-8 text-center opacity-50 italic">Belum ada Sub-Kategori.</td>
                      </tr>
                    ) : (
                      categories
                        .filter(c => c.parent_id && c.parent_id !== 'none')
                        .map((cat, index) => {
                          const parentCat = categories.find(p => p.id && cat.parent_id && String(p.id) === String(cat.parent_id));
                          return (
                            <tr key={cat.id || `sub-${index}`} className="hover:bg-slate-500/5 transition-all text-slate-300">
                              <td className="p-3 font-bold text-white">{cat.name}</td>
                              <td className="p-3 font-semibold text-cyan-400">{parentCat ? parentCat.name : "Tidak Diketahui"}</td>
                              <td className="p-3 text-right">
                                <button
                                  onClick={() => handleDeleteCategory(cat.id)}
                                  className="p-1.5 text-red-400 hover:bg-red-500/10 border border-red-500/20 rounded cursor-pointer"
                                  title="Hapus Sub-Kategori"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            </tr>
                          );
                        })
                    )}
                  </tbody>
                </table>
              </div>

            </div>

          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
            <table className="w-full text-xs text-left min-w-[600px]">
              <thead className="bg-[#121324] opacity-65 text-[10px] uppercase">
                <tr>
                  <th className="p-3">User Detail</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Peran (Role)</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Aksi Moderasi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e2038]">
                {searchedUsers.map((user, index) => (
                  <tr key={user._id || user.id || `user-${index}`}>
                    <td className="p-3 flex items-center gap-2.5">
                      <img src={user.avatarUrl} alt="" className="w-8 h-8 rounded-full object-cover" />
                      <span className="font-bold text-slate-100">{user.name}</span>
                    </td>
                    <td className="p-3 font-mono opacity-80">{maskEmail(user.email)}</td>
                    <td className="p-3">
                      <select
                        value={user.role}
                        onChange={(e) => handleUserRoleChange(user, e.target.value)}
                        className="bg-[#121324] border border-[#1e2038] text-xs rounded px-2 py-0.5"
                      >
                        <option value="user">User Biasa</option>
                        <option value="moderator">Moderator / Staf</option>
                        <option value="admin">Super Admin</option>
                      </select>
                    </td>
                    <td className="p-3">
                      {user.isBanned ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-black bg-red-500/20 text-red-400 border border-red-500/30">BANNED</span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] font-black bg-green-500/20 text-green-400 border border-green-500/30">AKTIF</span>
                      )}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleToggleUserBan(user)}
                        className={`px-3 py-1 text-[10px] font-black rounded border transition-all ${
                          user.isBanned
                            ? 'bg-green-500/10 border-green-500/30 text-green-400 hover:bg-green-500/20'
                            : 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20'
                        }`}
                      >
                        {user.isBanned ? 'Lepas Ban' : 'Banned / Blokir'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'playlists' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-[#0d0e1b] rounded-xl border border-[#1e2038] space-y-4 self-start">
              <h3 className="font-extrabold text-sm text-white">
                {editingPlaylist ? 'Edit Urutan Playlist Official' : 'Tambah Playlist Official Baru'}
              </h3>
              <form onSubmit={handleSavePlaylist} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[10px] opacity-60 uppercase font-bold tracking-wider">Judul Playlist</label>
                  <input
                    type="text"
                    placeholder="misal: Maraton Doraemon Terbaik..."
                    value={playlistForm.title}
                    onChange={(e) => setPlaylistForm({ ...playlistForm, title: e.target.value })}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] opacity-60 uppercase font-bold tracking-wider">Pilih Video / Episode ({playlistForm.videoIds.length} dipilih)</label>
                  
                  {/* Search box for filtering videos inside official playlist selection */}
                  <div className="relative mb-2">
                    <input
                      type="text"
                      placeholder="Cari episode / judul / anime..."
                      value={playlistVideoSearch}
                      onChange={(e) => setPlaylistVideoSearch(e.target.value)}
                      className="w-full text-[11px] p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-pink-500 placeholder-slate-500"
                    />
                  </div>

                  <div className="w-full max-h-[220px] overflow-y-auto p-2.5 rounded bg-[#121324] border border-[#1e2038] space-y-2">
                    {sortVideosByEpisode(videos).filter(vid => {
                      if (!playlistVideoSearch.trim()) return true;
                      const term = playlistVideoSearch.toLowerCase();
                      const epNum = parseEpisodeNumber(vid.episode).toString();
                      return vid.title.toLowerCase().includes(term) ||
                        vid.animeTitle.toLowerCase().includes(term) ||
                        (vid.episode && vid.episode.toLowerCase().includes(term)) ||
                        epNum === term;
                    }).map((vid) => {
                      const isChecked = playlistForm.videoIds.includes(vid.id);
                      const displayLabel = `[${vid.animeTitle}] ${vid.episode} - ${vid.title}`;
                      
                      return (
                        <label key={vid.id} className="flex items-start gap-2.5 text-xs text-slate-300 hover:text-white cursor-pointer select-none">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {
                              const nextVideoIds = isChecked
                                ? playlistForm.videoIds.filter(id => id !== vid.id)
                                : [...playlistForm.videoIds, vid.id];
                              setPlaylistForm({ ...playlistForm, videoIds: nextVideoIds });
                            }}
                            className="mt-0.5 rounded border-slate-500 text-pink-500 focus:ring-pink-500 focus:ring-offset-[#121324]"
                          />
                          <span className="leading-snug">{displayLabel}</span>
                        </label>
                      );
                    })}
                    {videos.length === 0 && (
                      <p className="text-[11px] opacity-40 italic py-1">Tidak ada video yang tersedia di database.</p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="submit" className="flex-1 py-1.5 bg-red-500 hover:bg-red-600 text-white font-extrabold text-xs rounded">
                    {editingPlaylist ? 'Simpan Perubahan' : 'Tambah Playlist'}
                  </button>
                  {editingPlaylist && (
                    <button type="button" onClick={() => { setEditingPlaylist(null); setPlaylistForm({ title: '', videoIds: [] }); setPlaylistVideoSearch(''); }} className="px-3 bg-slate-500/10 text-xs rounded">
                      Batal
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div className="md:col-span-2 bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
              <table className="w-full text-xs text-left min-w-[500px]">
                <thead className="bg-[#121324] opacity-60 text-[10px] uppercase">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Judul Playlist</th>
                    <th className="p-3">Isi Video (Episode IDs)</th>
                    <th className="p-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2038]">
                  {searchedPlaylists.map((pl, index) => (
                    <tr key={pl._id || pl.id || `playlist-${index}`}>
                      <td className="p-3 font-mono opacity-50">{pl.id}</td>
                      <td className="p-3 font-extrabold text-slate-100">{pl.title}</td>
                      <td className="p-3 font-mono text-pink-400 max-w-[200px] truncate">{pl.videoIds.join(', ')}</td>
                      <td className="p-3 text-right">
                        <div className="inline-flex gap-1.5">
                          <button
                            onClick={() => {
                              setEditingPlaylist(pl);
                              setPlaylistForm({ title: pl.title, videoIds: pl.videoIds || [] });
                            }}
                            className="p-1 text-cyan-400 hover:bg-cyan-500/10 rounded"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeletePlaylist(pl.id)}
                            className="p-1 text-red-400 hover:bg-red-500/10 rounded"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'ads' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-[#0d0e1b] rounded-xl border border-[#1e2038] space-y-4 self-start">
              <h3 className="font-extrabold text-sm text-white">{editingAd ? 'Edit Iklan' : 'Tambah Iklan Baru'}</h3>
              <form onSubmit={handleSaveAd} className="space-y-3.5 text-xs">
                <div className="space-y-1">
                  <label className="text-[10px] opacity-60 font-bold uppercase tracking-wider">Posisi Slot</label>
                  <select
                    value={adForm.slot}
                    onChange={(e) => setAdForm({ ...adForm, slot: e.target.value })}
                    className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                  >
                    <option value="banner_top">Banner Atas Header (Sponsor Utama)</option>
                    <option value="banner_below_player">Banner Bawah Video Player (Watch Page)</option>
                    <option value="banner_sidebar">Banner Sidebar Kanan (Feed / Watch Page)</option>
                    <option value="banner_between_feed">Banner Di Antara Feed Episode (Home / Catalog Grid)</option>
                    <option value="banner_below_comments">Banner Bawah Komentar (Watch Page)</option>
                    <option value="banner_above_playlist">Banner Di Atas Widget Playlist Maraton</option>
                    <option value="banner_popup">Pop-up Modal / Floating Banner Saweria (Pojok Layar)</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] opacity-60 font-bold uppercase tracking-wider">Judul / Slogan Iklan</label>
                  <input
                    type="text"
                    value={adForm.title}
                    onChange={(e) => setAdForm({ ...adForm, title: e.target.value })}
                    className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                    placeholder="Dukung Operational ShinDora via Saweria!"
                    required
                  />
                </div>

                <div className="flex items-center gap-2 py-1">
                  <input
                    type="checkbox"
                    checked={adForm.isRaw || false}
                    onChange={(e) => setAdForm({ ...adForm, isRaw: e.target.checked })}
                    id="adIsRaw"
                  />
                  <label htmlFor="adIsRaw" className="text-[11px] font-bold opacity-80 cursor-pointer text-cyan-400">Gunakan Kode Script / Raw Ad HTML</label>
                </div>

                {adForm.isRaw ? (
                  <div className="space-y-1 animate-fade-in">
                    <label className="text-[10px] opacity-60 font-bold uppercase tracking-wider">Kode Script / Iframe / AdSense Code</label>
                    <textarea
                      value={adForm.rawCode || ''}
                      onChange={(e) => setAdForm({ ...adForm, rawCode: e.target.value })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none h-24 font-mono leading-relaxed focus:border-cyan-500"
                      placeholder="Paste your <script> or <iframe> code from Adsterra, Monetag, Google AdSense, etc."
                      required={adForm.isRaw}
                    />
                  </div>
                ) : (
                  <>
                    <div className="space-y-1 animate-fade-in">
                      <label className="text-[10px] opacity-60 font-bold uppercase tracking-wider">URL Gambar Banner</label>
                      <div className="flex gap-1.5">
                        <input
                          type="text"
                          value={adForm.imageUrl || ''}
                          onChange={(e) => setAdForm({ ...adForm, imageUrl: e.target.value })}
                          className="flex-1 p-2 bg-[#121324] rounded border border-[#1e2038] text-white outline-none"
                          placeholder="https://images.unsplash.com/..."
                          required={!adForm.isRaw}
                        />
                        <button
                          type="button"
                          onClick={() => adFileInputRef.current?.click()}
                          className="px-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-bold text-[10px]"
                        >
                          Upload ImageKit
                        </button>
                        <input
                          type="file"
                          ref={adFileInputRef}
                          onChange={handleAdUploadToImageKit}
                          accept="image/*"
                          className="hidden"
                        />
                      </div>
                      {adUploadProgress && (
                        <p className="text-[9px] text-cyan-400 font-bold animate-pulse">{adUploadProgress}</p>
                      )}
                    </div>
                    <div className="space-y-1 animate-fade-in">
                      <label className="text-[10px] opacity-60 font-bold uppercase tracking-wider">Tautan Target Link</label>
                      <input
                        type="text"
                        value={adForm.targetUrl}
                        onChange={(e) => setAdForm({ ...adForm, targetUrl: e.target.value })}
                        className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                        placeholder="https://saweria.co/shindora"
                        required={!adForm.isRaw}
                      />
                    </div>
                  </>
                )}
                <div className="flex flex-col gap-2 pt-1">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={adForm.openInNewTab === undefined ? true : adForm.openInNewTab}
                      onChange={(e) => setAdForm({ ...adForm, openInNewTab: e.target.checked })}
                      id="adTargetNew"
                    />
                    <label htmlFor="adTargetNew" className="text-[11px] font-bold opacity-80 cursor-pointer">Buka Tautan di Tab Baru (target=&quot;_blank&quot;)</label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={adForm.isActive}
                      onChange={(e) => setAdForm({ ...adForm, isActive: e.target.checked })}
                      id="adActive"
                    />
                    <label htmlFor="adActive" className="text-[11px] font-bold opacity-80 cursor-pointer">Aktifkan Slot Iklan Ini</label>
                  </div>
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="submit" className="flex-1 py-1.5 bg-red-500 hover:bg-red-600 text-white font-extrabold text-xs rounded">
                    {editingAd ? 'Simpan' : 'Tambah Iklan'}
                  </button>
                  {editingAd && (
                    <button type="button" onClick={() => { setEditingAd(null); setAdForm({ slot: 'banner_top', title: '', imageUrl: '', targetUrl: '', isActive: true, isRaw: false, rawCode: '', openInNewTab: true }); }} className="px-3 bg-slate-500/10 text-xs rounded">
                      Batal
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div className="md:col-span-2 bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
              <table className="w-full text-xs text-left min-w-[500px]">
                <thead className="bg-[#121324] opacity-60 text-[10px] uppercase">
                  <tr>
                    <th className="p-3">Posisi</th>
                    <th className="p-3">Slogan Iklan</th>
                    <th className="p-3">Status</th>
                    <th className="p-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2038]">
                  {searchedAds.map((ad, index) => (
                    <tr key={ad._id || ad.id || `ad-${index}`}>
                      <td className="p-3 font-mono text-cyan-400">{ad.slot}</td>
                      <td className="p-3 font-bold text-slate-100">{ad.title}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-black ${ad.isActive ? 'bg-green-500/10 text-green-400' : 'bg-slate-500/10 text-slate-400'}`}>
                          {ad.isActive ? 'AKTIF' : 'NON-AKTIF'}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <div className="inline-flex gap-1">
                          <button
                            onClick={() => { setEditingAd(ad); setAdForm(ad); }}
                            className="p-1 text-cyan-400 hover:bg-cyan-500/10 rounded"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteAd(ad.id)}
                            className="p-1 text-red-400 hover:bg-red-500/10 rounded"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-5 bg-[#0d0e1b] rounded-xl border border-[#1e2038] space-y-4">
              <h3 className="font-extrabold text-sm text-cyan-400 uppercase tracking-wider">&bull; Konfigurasi API &amp; Website</h3>
              
              <div className="space-y-1.5">
                <label className="text-[10px] uppercase font-bold tracking-wider opacity-60">Logo Website URL (Manual / Upload Preview)</label>
                <div className="flex flex-col sm:flex-row gap-2">
                  <input
                    type="text"
                    placeholder="https://domain.com/logo.png"
                    value={siteSettings.logoUrl}
                    onChange={(e) => {
                      setSiteSettings({ ...siteSettings, logoUrl: e.target.value })
                      setLogoPreview(e.target.value)
                    }}
                    className="flex-1 text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => logoFileInputRef.current?.click()}
                    className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-bold"
                  >
                    Upload Logo
                  </button>
                  <input
                    type="file"
                    ref={logoFileInputRef}
                    onChange={handleLogoUploadToImageKit}
                    accept="image/*"
                    className="hidden"
                  />
                </div>

                {logoUploadProgress && (
                  <p className="text-[10px] text-cyan-400 font-bold animate-pulse">{logoUploadProgress}</p>
                )}

                {logoPreview && (
                  <div className="p-2 border border-dashed border-[#1e2038] rounded mt-1 bg-black/30">
                    <span className="text-[9px] opacity-40 uppercase block mb-1">Live Preview Logo:</span>
                    <img src={logoPreview} alt="Live Logo Preview" className="h-8 max-w-[150px] object-contain rounded" />
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-500/10">
                <div className="space-y-1.5 col-span-full">
                  <span className="text-[10px] font-black text-purple-400 uppercase tracking-widest block">Storage & Media Settings (ImageKit)</span>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] opacity-60 font-bold uppercase">ImageKit Public Key</label>
                  <input
                    type="text"
                    value={siteSettings.imagekitPublicKey || ''}
                    onChange={(e) => setSiteSettings({ ...siteSettings, imagekitPublicKey: e.target.value })}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038]"
                    placeholder="public_***"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] opacity-60 font-bold uppercase">ImageKit Private Key</label>
                  <input
                    type="password"
                    value={siteSettings.imagekitPrivateKey || ''}
                    onChange={(e) => setSiteSettings({ ...siteSettings, imagekitPrivateKey: e.target.value })}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038]"
                    placeholder="private_***"
                  />
                </div>
                <div className="space-y-1.5 col-span-full">
                  <label className="text-[10px] opacity-60 font-bold uppercase">ImageKit URL Endpoint</label>
                  <input
                    type="text"
                    value={siteSettings.imagekitUrlEndpoint || ''}
                    onChange={(e) => setSiteSettings({ ...siteSettings, imagekitUrlEndpoint: e.target.value })}
                    className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038]"
                    placeholder="https://ik.imagekit.io/your_id"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-500/10">
                <div className="space-y-1.5 col-span-full flex items-center justify-between">
                  <span className="text-[10px] font-black text-orange-400 uppercase tracking-widest block">Interactive Donation Overlay Settings</span>
                  <div className="flex items-center gap-1.5">
                    <input
                      type="checkbox"
                      checked={siteSettings.donationOverlayActive === undefined ? true : siteSettings.donationOverlayActive}
                      onChange={(e) => setSiteSettings({ ...siteSettings, donationOverlayActive: e.target.checked })}
                      id="donOverlayActive"
                    />
                    <label htmlFor="donOverlayActive" className="text-[9px] font-bold opacity-80 cursor-pointer">AKTIFKAN OVERLAY</label>
                  </div>
                </div>
                <div className="space-y-1.5 p-3 rounded-lg border border-slate-500/10 bg-slate-500/5">
                  <label className="text-[10px] text-pink-500 font-bold uppercase">Saweria Stream Key</label>
                  <input
                    type="text"
                    value={siteSettings.saweriaStreamKey || ''}
                    onChange={(e) => setSiteSettings({ ...siteSettings, saweriaStreamKey: e.target.value })}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] font-mono text-pink-300"
                    placeholder="saweria-key-xyz"
                  />
                  <div className="mt-1 text-[9px] text-slate-400 space-y-1">
                    <div>
                      <span className="font-bold text-slate-300">Webhook URL:</span>{' '}
                      <code className="bg-black/30 px-1 py-0.5 rounded text-pink-400 select-all">
                        https://shindoranesub.my.id/api/webhooks/saweria
                      </code>
                    </div>
                    <div>
                      <span className="font-bold text-slate-300">OBS Alert URL:</span>{' '}
                      <code className="bg-black/30 px-1 py-0.5 rounded text-cyan-400 select-all font-mono break-all block mt-0.5">
                        https://saweria.co/widgets/alert?streamKey={siteSettings.saweriaStreamKey || 'streamKey'}
                      </code>
                    </div>
                  </div>
                </div>
                <div className="space-y-1.5 p-3 rounded-lg border border-slate-500/10 bg-slate-500/5">
                  <label className="text-[10px] text-red-500 font-bold uppercase">Trakteer Stream Key</label>
                  <input
                    type="text"
                    value={siteSettings.trakteerStreamKey || ''}
                    onChange={(e) => setSiteSettings({ ...siteSettings, trakteerStreamKey: e.target.value })}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] font-mono text-red-300"
                    placeholder="trakteer-key-xyz"
                  />
                  <div className="mt-1 text-[9px] text-slate-400 space-y-1">
                    <div>
                      <span className="font-bold text-slate-300">Webhook URL:</span>{' '}
                      <code className="bg-black/30 px-1 py-0.5 rounded text-red-400 select-all">
                        https://shindoranesub.my.id/api/webhooks/trakteer
                      </code>
                    </div>
                    <div>
                      <span className="font-bold text-slate-300">OBS Alert URL:</span>{' '}
                      <code className="bg-black/30 px-1 py-0.5 rounded text-cyan-400 select-all font-mono break-all block mt-0.5">
                        https://stream.trakteer.id/notification/?key={siteSettings.trakteerStreamKey || 'key'}
                      </code>
                    </div>
                  </div>
                </div>
                <div className="space-y-1.5 p-3 rounded-lg border border-slate-500/10 bg-slate-500/5 col-span-full">
                  <label className="text-[10px] text-purple-400 font-bold uppercase">Tako.id Stream Key</label>
                  <input
                    type="text"
                    value={siteSettings.takoStreamKey || ''}
                    onChange={(e) => setSiteSettings({ ...siteSettings, takoStreamKey: e.target.value })}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] font-mono text-purple-300"
                    placeholder="tako-key-xyz"
                  />
                  <div className="mt-1 text-[9px] text-slate-400 space-y-1">
                    <div>
                      <span className="font-bold text-slate-300">Webhook URL:</span>{' '}
                      <code className="bg-black/30 px-1 py-0.5 rounded text-purple-400 select-all">
                        https://shindoranesub.my.id/api/webhooks/tako
                      </code>
                    </div>
                    <div>
                      <span className="font-bold text-slate-300">OBS Alert URL:</span>{' '}
                      <code className="bg-black/30 px-1 py-0.5 rounded text-cyan-400 select-all font-mono break-all block mt-0.5">
                        https://tako.id/overlay/alert?overlay_key={siteSettings.takoStreamKey || 'overlay_key'}
                      </code>
                    </div>
                  </div>
                </div>
                <div className="space-y-1.5 col-span-full">
                  <label className="text-[10px] opacity-60 font-bold uppercase">Durasi Tampil Popup Overlay (Detik)</label>
                  <input
                    type="number"
                    value={siteSettings.donationPopupDuration || 6}
                    onChange={(e) => setSiteSettings({ ...siteSettings, donationPopupDuration: Number(e.target.value) })}
                    className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    min="2"
                    max="30"
                  />
                </div>
                <div className="space-y-1.5 col-span-full">
                  <label className="text-[10px] opacity-60 font-bold uppercase">Kecepatan Running Text (Marquee Speed)</label>
                  <select
                    value={siteSettings.donationMarqueeSpeed || 'Sedang'}
                    onChange={(e) => setSiteSettings({ ...siteSettings, donationMarqueeSpeed: e.target.value })}
                    className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none font-bold"
                  >
                    <option value="Lambat">Lambat (Halus - 25 detik)</option>
                    <option value="Sedang">Sedang (Standar - 15 detik)</option>
                    <option value="Cepat">Cepat (Kilat - 8 detik)</option>
                  </select>
                </div>

                <div className="space-y-1.5 col-span-full pt-3">
                  <button
                    type="button"
                    onClick={handleSaveOverlaySettings}
                    className="w-full py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 hover:opacity-90 text-white text-xs font-black rounded-lg shadow-md uppercase tracking-wider"
                  >
                    SIMPAN PENGATURAN OVERLAY DONASI
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-500/10 space-y-3.5 mt-4 text-left">
                <span className="text-[10px] font-black text-orange-400 uppercase tracking-widest block">&bull; Pengaturan Running Text Di Atas (Top Announcement Bar)</span>
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/30 space-y-3">
                  <div className="space-y-1">
                    <label className="text-[9px] opacity-60 uppercase font-bold">Input Teks Running / Pengumuman</label>
                    <textarea
                      placeholder="Masukkan pesan berjalan di atas website..."
                      value={siteSettings.announcementText || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, announcementText: e.target.value })}
                      className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none h-20"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <label className="text-[9px] opacity-60 uppercase font-bold">Dropdown Badge / Icon Prefix</label>
                      <select
                        value={siteSettings.announcementBadge || 'PENGUMUMAN'}
                        onChange={(e) => setSiteSettings({ ...siteSettings, announcementBadge: e.target.value })}
                        className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none font-bold"
                      >
                        <option value="PENGUMUMAN">PENGUMUMAN</option>
                        <option value="DONASI TERBARU">DONASI TERBARU</option>
                        <option value="SAWERIA">SAWERIA</option>
                        <option value="TRAKTEER">TRAKTEER</option>
                        <option value="INFO">INFO</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[9px] opacity-60 uppercase font-bold">Kecepatan Teks</label>
                      <select
                        value={siteSettings.donationMarqueeSpeed || 'Sedang'}
                        onChange={(e) => setSiteSettings({ ...siteSettings, donationMarqueeSpeed: e.target.value })}
                        className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none font-bold"
                      >
                        <option value="Pelan">Pelan (Halus - 20s)</option>
                        <option value="Sedang">Sedang (Standar - 15s)</option>
                        <option value="Cepat">Cepat (Kilat - 10s)</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    <input
                      type="checkbox"
                      checked={siteSettings.donationOverlayActive === undefined ? true : siteSettings.donationOverlayActive}
                      onChange={(e) => setSiteSettings({ ...siteSettings, donationOverlayActive: e.target.checked })}
                      id="topBarAnnounceActive"
                    />
                    <label htmlFor="topBarAnnounceActive" className="text-xs font-bold opacity-80 cursor-pointer">Tampilkan Running Text di Bagian Atas Website (On/Off)</label>
                  </div>

                  <button
                    onClick={handleSaveRunningTextSettings}
                    className="w-full py-2 bg-gradient-to-r from-orange-500 to-pink-500 text-black text-xs font-black rounded shadow-md uppercase tracking-wider"
                  >
                    SIMPAN &amp; TAMPILKAN RUNNING TEXT
                  </button>
                </div>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-slate-500/10">
                <span className="text-[10px] font-black text-pink-400 uppercase tracking-widest block mb-2">Provider Email Auth</span>
                <select
                  value={siteSettings.emailProvider}
                  onChange={(e) => setSiteSettings({ ...siteSettings, emailProvider: e.target.value })}
                  className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white font-bold"
                >
                  <option value="Mock/Simulasi">Mock/Simulasi</option>
                  <option value="Supabase Auth">Supabase Auth</option>
                  <option value="Firebase Auth">Firebase Auth</option>
                  <option value="Custom SMTP / Resend API">Custom SMTP / Resend API</option>
                </select>
              </div>

              {siteSettings.emailProvider === 'Custom SMTP / Resend API' && (
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/20 space-y-3 mt-2">
                  <span className="text-[9px] font-black text-pink-400 uppercase block tracking-wider">&bull; SMTP / Resend API Credentials</span>
                  
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold opacity-60 uppercase">Resend API Key</label>
                    <input
                      type="text"
                      placeholder="re_123456789..."
                      value={siteSettings.emailProviderCredentials?.resendApiKey || ''}
                      onChange={(e) => setSiteSettings({
                        ...siteSettings,
                        emailProviderCredentials: {
                          ...(siteSettings.emailProviderCredentials || {}),
                          resendApiKey: e.target.value
                        }
                      })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <div className="space-y-1.5 sm:col-span-2">
                      <label className="text-[10px] font-bold opacity-60 uppercase">SMTP Host</label>
                      <input
                        type="text"
                        placeholder="smtp.mailtrap.io"
                        value={siteSettings.emailProviderCredentials?.smtpHost || ''}
                        onChange={(e) => setSiteSettings({
                          ...siteSettings,
                          emailProviderCredentials: {
                            ...(siteSettings.emailProviderCredentials || {}),
                            smtpHost: e.target.value
                          }
                        })}
                        className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold opacity-60 uppercase">SMTP Port</label>
                      <input
                        type="text"
                        placeholder="587"
                        value={siteSettings.emailProviderCredentials?.smtpPort || ''}
                        onChange={(e) => setSiteSettings({
                          ...siteSettings,
                          emailProviderCredentials: {
                            ...(siteSettings.emailProviderCredentials || {}),
                            smtpPort: e.target.value
                          }
                        })}
                        className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold opacity-60 uppercase">SMTP User / Email Pengirim</label>
                    <input
                      type="text"
                      placeholder="noreply@domainanda.com"
                      value={siteSettings.emailProviderCredentials?.smtpUser || ''}
                      onChange={(e) => setSiteSettings({
                        ...siteSettings,
                        emailProviderCredentials: {
                          ...(siteSettings.emailProviderCredentials || {}),
                          smtpUser: e.target.value
                        }
                      })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold opacity-60 uppercase">SMTP Password / App Password</label>
                    <input
                      type="password"
                      placeholder="••••••••"
                      value={siteSettings.emailProviderCredentials?.smtpPass || ''}
                      onChange={(e) => setSiteSettings({
                        ...siteSettings,
                        emailProviderCredentials: {
                          ...(siteSettings.emailProviderCredentials || {}),
                          smtpPass: e.target.value
                        }
                      })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    />
                  </div>
                </div>
              )}

              {siteSettings.emailProvider === 'Supabase Auth' && (
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/20 space-y-3 mt-2">
                  <span className="text-[9px] font-black text-pink-400 uppercase block tracking-wider">&bull; Supabase Auth Credentials</span>
                  
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold opacity-60 uppercase">SUPABASE_URL</label>
                    <input
                      type="text"
                      placeholder="https://your-project.supabase.co"
                      value={siteSettings.emailProviderCredentials?.supabaseUrl || ''}
                      onChange={(e) => setSiteSettings({
                        ...siteSettings,
                        emailProviderCredentials: {
                          ...(siteSettings.emailProviderCredentials || {}),
                          supabaseUrl: e.target.value
                        }
                      })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold opacity-60 uppercase">SUPABASE_ANON_KEY</label>
                    <input
                      type="password"
                      placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                      value={siteSettings.emailProviderCredentials?.supabaseAnonKey || ''}
                      onChange={(e) => setSiteSettings({
                        ...siteSettings,
                        emailProviderCredentials: {
                          ...(siteSettings.emailProviderCredentials || {}),
                          supabaseAnonKey: e.target.value
                        }
                      })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    />
                  </div>
                </div>
              )}

              {siteSettings.emailProvider === 'Firebase Auth' && (
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/20 space-y-3 mt-2">
                  <span className="text-[9px] font-black text-pink-400 uppercase block tracking-wider">&bull; Firebase Auth Credentials</span>
                  
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold opacity-60 uppercase">FIREBASE_API_KEY</label>
                    <input
                      type="text"
                      placeholder="AIzaSyA1..."
                      value={siteSettings.emailProviderCredentials?.firebaseApiKey || ''}
                      onChange={(e) => setSiteSettings({
                        ...siteSettings,
                        emailProviderCredentials: {
                          ...(siteSettings.emailProviderCredentials || {}),
                          firebaseApiKey: e.target.value
                        }
                      })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold opacity-60 uppercase">FIREBASE_AUTH_DOMAIN</label>
                      <input
                        type="text"
                        placeholder="project.firebaseapp.com"
                        value={siteSettings.emailProviderCredentials?.firebaseAuthDomain || ''}
                        onChange={(e) => setSiteSettings({
                          ...siteSettings,
                          emailProviderCredentials: {
                            ...(siteSettings.emailProviderCredentials || {}),
                            firebaseAuthDomain: e.target.value
                          }
                        })}
                        className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-bold opacity-60 uppercase">FIREBASE_PROJECT_ID</label>
                      <input
                        type="text"
                        placeholder="project-id-xyz"
                        value={siteSettings.emailProviderCredentials?.firebaseProjectId || ''}
                        onChange={(e) => setSiteSettings({
                          ...siteSettings,
                          emailProviderCredentials: {
                            ...(siteSettings.emailProviderCredentials || {}),
                            firebaseProjectId: e.target.value
                          }
                        })}
                        className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                      />
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={handleSaveSettings}
                className="w-full py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:opacity-90 text-black text-xs font-black rounded-lg transition-all flex items-center justify-center gap-1 shadow-lg uppercase tracking-wider"
              >
                <Save className="w-4 h-4" />
                <span>Simpan Seluruh Pengaturan</span>
              </button>
            </div>

            <div className="p-5 bg-[#0d0e1b] rounded-xl border border-[#1e2038] space-y-4">
              <h3 className="font-extrabold text-sm text-purple-400 uppercase tracking-wider">&bull; Tautan Sosial Media &amp; Donasi</h3>
              
              <div className="p-3 bg-black/40 rounded-lg space-y-3 border border-[#1e2038]">
                <span className="text-[10px] font-bold opacity-60 uppercase block">Tambah Tautan Baru:</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="Nama (TikTok, Saweria, YouTube)"
                    value={newSocialName}
                    onChange={(e) => setNewSocialName(e.target.value)}
                    className="p-2 text-xs bg-[#121324] rounded border border-[#1e2038]"
                  />
                  <input
                    type="text"
                    placeholder="https://saweria.co/..."
                    value={newSocialUrl}
                    onChange={(e) => setNewSocialUrl(e.target.value)}
                    className="p-2 text-xs bg-[#121324] rounded border border-[#1e2038]"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleAddSocialLink}
                  className="w-full py-1.5 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded flex items-center justify-center gap-1"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Tambah Link Sosmed / Donasi</span>
                </button>
              </div>

              <div className="space-y-2">
                <span className="text-[10px] opacity-50 uppercase font-black">Tautan Terdaftar:</span>
                {(!siteSettings.socialLinks || siteSettings.socialLinks.length === 0) ? (
                  <p className="text-xs opacity-50 italic">Belum ada tautan sosial media yang terdaftar.</p>
                ) : (
                  <div className="space-y-1.5">
                    {siteSettings.socialLinks.map((link) => (
                      <div key={link.id} className="flex items-center justify-between p-2 rounded bg-slate-500/5 text-xs">
                        <div>
                          <span className="font-extrabold text-slate-100">{link.name}:</span>
                          <span className="opacity-60 text-[10px] font-mono ml-2 truncate">{link.url}</span>
                        </div>
                        <button
                          onClick={() => handleRemoveSocialLink(link.id)}
                          className="text-red-400 hover:text-red-500"
                        >
                          Hapus
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-slate-500/10 space-y-3.5 mt-4">
                <h3 className="font-extrabold text-sm text-pink-500 uppercase tracking-wider">&bull; Pengaturan Hero Banner Beranda</h3>
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/30 space-y-3">
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#121324] border border-[#1e2038]">
                    <div className="space-y-0.5">
                      <span className="text-xs font-bold text-slate-200">Tampilkan Hero Banner Beranda</span>
                      <span className="text-[10px] opacity-50 block">Menampilkan atau menyembunyikan blok banner utama di halaman beranda</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={siteSettings.hero_banner_active === undefined ? true : siteSettings.hero_banner_active}
                        onChange={(e) => setSiteSettings({ ...siteSettings, hero_banner_active: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-slate-500/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-pink-500 peer-checked:after:bg-white peer-checked:after:border-white"></div>
                    </label>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold">Badge Text</label>
                    <input
                      type="text"
                      placeholder="e.g. ✨ NOSTALGIA MASA KECIL"
                      value={siteSettings.hero_badge_text || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, hero_badge_text: e.target.value })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-pink-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold">Judul Utama Hero</label>
                    <input
                      type="text"
                      placeholder="e.g. Putar Kembali Kenangan Indah Hari Minggu Anda!"
                      value={siteSettings.hero_title || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, hero_title: e.target.value })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-pink-500"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold">Deskripsi Hero</label>
                    <textarea
                      placeholder="e.g. Tonton kartun-kartun masa kecil favorit Anda..."
                      value={siteSettings.hero_description || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, hero_description: e.target.value })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none h-20 focus:border-pink-500"
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold">Gambar Unggulan (Hero Card Image URL)</label>
                    <div className="flex flex-col sm:flex-row gap-2">
                      <input
                        type="text"
                        placeholder="https://domain.com/image.jpg"
                        value={siteSettings.hero_featured_image || ''}
                        onChange={(e) => setSiteSettings({ ...siteSettings, hero_featured_image: e.target.value })}
                        className="flex-1 text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-pink-500"
                      />
                      <button
                        type="button"
                        onClick={() => heroImageFileInputRef.current?.click()}
                        className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-bold"
                      >
                        Upload
                      </button>
                      <input
                        type="file"
                        ref={heroImageFileInputRef}
                        onChange={handleHeroImageUploadToImageKit}
                        accept="image/*"
                        className="hidden"
                      />
                    </div>
                    {heroImageUploadProgress && (
                      <p className="text-[10px] text-pink-400 font-bold animate-pulse">{heroImageUploadProgress}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div className="space-y-1">
                      <label className="text-[10px] opacity-60 uppercase font-bold">Label Card Unggulan</label>
                      <input
                        type="text"
                        placeholder="e.g. KOLEKSI TERPOPULER"
                        value={siteSettings.hero_featured_label || ''}
                        onChange={(e) => setSiteSettings({ ...siteSettings, hero_featured_label: e.target.value })}
                        className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] opacity-60 uppercase font-bold">Judul Card Unggulan</label>
                      <input
                        type="text"
                        placeholder="e.g. Crayon Shinchan: Kenakalan..."
                        value={siteSettings.hero_featured_title || ''}
                        onChange={(e) => setSiteSettings({ ...siteSettings, hero_featured_title: e.target.value })}
                        className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                      />
                    </div>
                  </div>

                  <button
                    onClick={handleSaveSettings}
                    className="w-full py-2 bg-gradient-to-r from-pink-500 to-rose-600 hover:opacity-90 text-white text-xs font-bold rounded shadow-lg uppercase tracking-wider mt-2"
                  >
                    Simpan Perubahan Banner
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-500/10 space-y-3.5 mt-4">
                <h3 className="font-extrabold text-sm text-yellow-500 uppercase tracking-wider">&bull; Sistem Proteksi Website</h3>
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/30 space-y-3">
                  <div className="flex items-center justify-between p-2 rounded bg-[#121324] border border-[#1e2038]">
                    <div className="space-y-0.5">
                      <span className="text-xs font-bold text-slate-200">Aktifkan Anti AdBlock</span>
                      <span className="text-[10px] opacity-50 block">Kunci layar jika adblock aktif</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={siteSettings.antiAdblockActive || false}
                        onChange={(e) => setSiteSettings({ ...siteSettings, antiAdblockActive: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-slate-500/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-500 peer-checked:after:bg-black peer-checked:after:border-black"></div>
                    </label>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold">Pesan Anti AdBlock Popup</label>
                    <textarea
                      placeholder="e.g. Mohon matikan AdBlock Anda..."
                      value={siteSettings.antiAdblockMessage || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, antiAdblockMessage: e.target.value })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-yellow-500 h-16 leading-relaxed"
                    />
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-[#121324] border border-[#1e2038]">
                    <div className="space-y-0.5">
                      <span className="text-xs font-bold text-slate-200">Aktifkan Anti Copy / Inspect Element</span>
                      <span className="text-[10px] opacity-50 block">Blokir klik kanan, seleksi teks & F12</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={siteSettings.antiCopyActive || false}
                        onChange={(e) => setSiteSettings({ ...siteSettings, antiCopyActive: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-slate-500/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-500 peer-checked:after:bg-black peer-checked:after:border-black"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-[#121324] border border-[#1e2038]">
                    <div className="space-y-0.5">
                      <span className="text-xs font-bold text-slate-200">Aktifkan Anti Developer Tools (Block DevTools / F12)</span>
                      <span className="text-[10px] opacity-50 block">Mencegah & mendeteksi pembukaan inspect element, Ctrl+Shift+I, dan view-source</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={siteSettings.antiDevToolsActive || false}
                        onChange={(e) => setSiteSettings({ ...siteSettings, antiDevToolsActive: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-slate-500/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-500 peer-checked:after:bg-black peer-checked:after:border-black"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-[#121324] border border-[#1e2038]">
                    <div className="space-y-0.5">
                      <span className="text-xs font-bold text-slate-200">Aktifkan Balon Live Chat (On/Off)</span>
                      <span className="text-[10px] opacity-50 block">Menampilkan atau menyembunyikan widget live chat di seluruh halaman publik</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={siteSettings.live_chat_active === undefined ? true : siteSettings.live_chat_active}
                        onChange={(e) => setSiteSettings({ ...siteSettings, live_chat_active: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 bg-slate-500/20 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-500 peer-checked:after:bg-black peer-checked:after:border-black"></div>
                    </label>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold text-slate-300">Sensor Kata-Kata Kasar (Blocked Words)</label>
                    <textarea
                      placeholder="e.g. anjing, babi, bangsat..."
                      value={siteSettings.blocked_words || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, blocked_words: e.target.value })}
                      className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-yellow-500 h-16 leading-relaxed"
                    />
                    <span className="text-[9px] opacity-40 block">Daftar kata kasar yang dipisahkan dengan koma. Kata yang cocok otomatis disensor menjadi tanda bintang (****).</span>
                  </div>

                  <button
                    onClick={handleSaveSettings}
                    className="w-full py-2 bg-gradient-to-r from-yellow-500 to-amber-600 hover:opacity-90 text-black text-xs font-black rounded shadow-lg uppercase tracking-wider mt-2"
                  >
                    Simpan Perubahan Proteksi
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-500/10 space-y-3.5 mt-4">
                <h3 className="font-extrabold text-sm text-cyan-400 uppercase tracking-wider">&bull; Injeksi Head Ad Scripts Global</h3>
                <div className="p-3.5 rounded-lg border border-[#1e2038] bg-black/30 space-y-3">
                  <div className="space-y-1">
                    <label className="text-[10px] opacity-60 uppercase font-bold">Global Head Ad Scripts (AdSense, Adsterra, Monetag Popunder)</label>
                    <textarea
                      placeholder="e.g. <script src='https://pagead2.googlesyndication.com...'></script>"
                      value={siteSettings.globalHeadScripts || ''}
                      onChange={(e) => setSiteSettings({ ...siteSettings, globalHeadScripts: e.target.value })}
                      className="w-full text-xs p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-cyan-500 h-32 leading-relaxed font-mono"
                    />
                    <span className="text-[9px] opacity-40 block">Menempelkan kode script/head tag ini secara otomatis ke dalam tag &lt;head&gt; di seluruh halaman.</span>
                  </div>

                  <button
                    onClick={handleSaveSettings}
                    className="w-full py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:opacity-90 text-black text-xs font-black rounded shadow-lg uppercase tracking-wider mt-2"
                  >
                    Simpan Perubahan Head Script
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

        {activeTab === 'emotes' && (
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

        {activeTab === 'donasi' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="p-6 bg-[#0d0e1b] rounded-2xl border border-pink-500/20 shadow-xl shadow-pink-500/5 space-y-4">
              <h3 className="font-extrabold text-base text-pink-500 uppercase tracking-wider flex items-center justify-between border-b border-pink-500/10 pb-3">
                <span className="flex items-center gap-2">
                  <HeartHandshake className="w-5 h-5 text-pink-500 animate-pulse" />
                  <span>&bull; SISTEM DONASI MANUAL / SIMULASI OVERLAY</span>
                </span>
                <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase ${siteSettings.isManualDonationActive ? 'bg-pink-600 text-white animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
                  {siteSettings.isManualDonationActive ? 'AKTIF (ON)' : 'MATI (OFF)'}
                </span>
              </h3>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-xl border border-pink-500/20 bg-pink-500/5">
                  <div className="space-y-0.5 text-left">
                    <span className="text-xs text-pink-400 font-bold uppercase block">Aktifkan Sistem Donasi Manual</span>
                    <p className="text-[10px] text-slate-400 leading-relaxed text-left">
                      Mengaktifkan tampilan running text dan popup simulasi donasi kustom di halaman depan.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={siteSettings.isManualDonationActive || false}
                      onChange={(e) => setSiteSettings({ ...siteSettings, isManualDonationActive: e.target.checked })}
                      className="w-5 h-5 cursor-pointer accent-pink-500"
                      id="isManualDonationActiveCard"
                    />
                  </div>
                </div>

                {siteSettings.isManualDonationActive && (
                  <div className="space-y-5 animate-fadeIn">
                    {/* Display settings inputs */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-xl border border-[#1e2038] bg-black/40 text-left">
                      <div className="space-y-1.5 col-span-full">
                        <span className="text-[10px] font-black text-pink-400 uppercase tracking-widest block">&bull; Pengaturan Tampilan Donasi</span>
                      </div>
                      <div className="space-y-1.5">
                        <label className="text-[10px] opacity-60 uppercase font-black tracking-wider text-slate-300">Kecepatan Running Text (Marquee Speed)</label>
                        <select
                          value={siteSettings.manualDonationSpeed || 'Sedang'}
                          onChange={(e) => setSiteSettings({ ...siteSettings, manualDonationSpeed: e.target.value })}
                          className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white outline-none font-bold"
                        >
                          <option value="Lambat">Lambat (Halus - 25s)</option>
                          <option value="Sedang">Sedang (Standar - 15s)</option>
                          <option value="Cepat">Cepat (Kilat - 10s)</option>
                        </select>
                      </div>

                      <div className="space-y-1.5">
                        <label className="text-[10px] opacity-60 uppercase font-black tracking-wider text-slate-300">Durasi Tampil Popup Overlay (Detik)</label>
                        <input
                          type="number"
                          value={siteSettings.manualDonationDuration || 6}
                          onChange={(e) => setSiteSettings({ ...siteSettings, manualDonationDuration: Number(e.target.value) })}
                          className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white font-bold"
                          min="2"
                          max="30"
                        />
                      </div>
                    </div>

                    {/* New multi-input form */}
                    <div className="space-y-4 p-5 rounded-xl border border-[#1e2038] bg-black/40 text-left">
                      <span className="text-[10px] font-black text-pink-400 uppercase tracking-widest block">&bull; Form Isian Data Donatur Baru</span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="text-[10px] opacity-60 uppercase font-black tracking-wider text-slate-300">Nama Donatur</label>
                          <input
                            type="text"
                            value={tempDonName}
                            onChange={(e) => setTempDonName(e.target.value)}
                            className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white focus:border-pink-500 outline-none transition-all font-bold"
                            placeholder="cth: Budi, Anonim"
                          />
                        </div>
                        
                        <div className="space-y-1.5">
                          <label className="text-[10px] opacity-60 uppercase font-black tracking-wider text-slate-300">Nominal Donasi</label>
                          <input
                            type="text"
                            value={tempDonAmount}
                            onChange={(e) => setTempDonAmount(e.target.value)}
                            className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white focus:border-pink-500 outline-none transition-all font-bold"
                            placeholder="cth: Rp 15.000 atau 15000"
                          />
                        </div>

                        <div className="space-y-1.5 col-span-full">
                          <label className="text-[10px] opacity-60 uppercase font-black tracking-wider text-slate-300">Pesan Donasi</label>
                          <textarea
                            value={tempDonMessage}
                            onChange={(e) => setTempDonMessage(e.target.value)}
                            className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white focus:border-pink-500 outline-none transition-all h-24 font-bold leading-relaxed resize-none"
                            placeholder="cth: Semangat terus min upload episode baru!"
                          />
                        </div>

                        <div className="space-y-1.5 col-span-full">
                          <label className="text-[10px] opacity-60 uppercase font-black tracking-wider text-slate-300">Platform</label>
                          <select
                            value={tempDonPlatform}
                            onChange={(e) => setTempDonPlatform(e.target.value)}
                            className="w-full text-xs p-3 rounded-lg bg-[#121324] border border-[#1e2038] text-white outline-none font-bold cursor-pointer"
                          >
                            <option value="Saweria">Saweria</option>
                            <option value="Trakteer">Trakteer</option>
                            <option value="Tako.id">Tako.id</option>
                            <option value="Manual">Manual</option>
                          </select>
                        </div>
                      </div>

                      <div className="flex gap-3 pt-2">
                        <button
                          type="button"
                          onClick={handleAddManualDonation}
                          className="flex-1 py-3 rounded-xl bg-gradient-to-r from-pink-500 via-pink-600 to-purple-600 hover:opacity-95 text-white text-xs font-black uppercase tracking-wider transition-all shadow-lg flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                          <Plus className="w-4 h-4" />
                          <span>+ Tambah Donasi Manual ke Daftar</span>
                        </button>
                      </div>
                    </div>

                    {/* Table listing manual donations */}
                    <div className="space-y-3.5 p-5 rounded-xl border border-[#1e2038] bg-black/40 text-left">
                      <div className="flex items-center justify-between border-b border-[#1e2038] pb-3 mb-2">
                        <span className="text-[10px] font-black text-pink-400 uppercase tracking-widest block">
                          &bull; Daftar Donasi Manual ({ (siteSettings.manualDonationList || []).length })
                        </span>
                        {(siteSettings.manualDonationList || []).length > 0 && (
                          <button
                            type="button"
                            onClick={handleClearAllManualDonations}
                            className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-[10px] font-bold uppercase transition-all cursor-pointer"
                          >
                            HAPUS SEMUA DAFTAR DONASI
                          </button>
                        )}
                      </div>

                      {(!siteSettings.manualDonationList || siteSettings.manualDonationList.length === 0) ? (
                        <p className="text-center text-xs opacity-40 py-4 italic">Belum ada data donasi manual dalam daftar.</p>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full text-xs text-left">
                            <thead className="bg-[#121324] text-[10px] uppercase font-black opacity-60 border-b border-[#1e2038]">
                              <tr>
                                <th className="p-3">Nama</th>
                                <th className="p-3">Nominal</th>
                                <th className="p-3">Pesan</th>
                                <th className="p-3">Platform</th>
                                <th className="p-3 text-right">Aksi</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-[#1e2038]">
                              {siteSettings.manualDonationList.map((item) => (
                                <tr key={item.id} className="hover:bg-slate-500/5 transition-all text-slate-300">
                                  <td className="p-3 font-bold text-white">{item.name}</td>
                                  <td className="p-3 text-emerald-400 font-extrabold">{item.amount}</td>
                                  <td className="p-3 max-w-[200px] truncate italic">&ldquo;{item.message}&rdquo;</td>
                                  <td className="p-3">
                                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase text-white ${
                                      item.platform === 'Saweria' ? 'bg-pink-600' :
                                      item.platform === 'Trakteer' ? 'bg-red-600' :
                                      item.platform === 'Tako.id' ? 'bg-purple-600' : 'bg-slate-600'
                                    }`}>
                                      {item.platform}
                                    </span>
                                  </td>
                                  <td className="p-3 text-right">
                                    <button
                                      type="button"
                                      onClick={() => handleRemoveManualDonation(item.id)}
                                      className="p-1.5 text-red-400 hover:bg-red-500/10 border border-red-500/20 rounded-md cursor-pointer"
                                      title="Hapus Item"
                                    >
                                      <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>

                    {/* Master save button */}
                    <div className="pt-2">
                      <button
                        type="button"
                        onClick={async () => {
                          await handleSaveSettings();
                          alert("🎉 Seluruh daftar donasi manual dan pengaturan berhasil disimpan secara permanen di database!");
                        }}
                        className="w-full py-3.5 rounded-xl bg-gradient-to-r from-pink-500 via-purple-600 to-pink-500 hover:opacity-95 text-white text-xs font-black uppercase tracking-wider transition-all shadow-lg shadow-pink-500/25 flex items-center justify-center gap-2 cursor-pointer transform active:scale-95"
                      >
                        <Save className="w-4 h-4" />
                        <span>SIMPAN SELURUH DAFTAR &amp; TAYANGKAN SEKARANG</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'pages' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center bg-[#0d0e1b] p-4 rounded-xl border border-[#1e2038] gap-3">
              <div>
                <h3 className="font-extrabold text-sm text-white">Kelola Halaman Statis &amp; Dokumen</h3>
                <p className="text-[11px] opacity-60">Sediakan dokumen hukum seperti DMCA Disclaimer, Privacy Policy, Terms, dll.</p>
              </div>
              <button
                onClick={() => {
                  setEditingPage(null)
                  setPageForm({ title: '', slug: '', content: '', showInFooter: true })
                  setIsSlugManuallyEdited(false)
                  setShowPageModal(true)
                }}
                className="px-4 py-2 rounded-lg bg-pink-500 hover:bg-pink-600 text-white font-extrabold text-xs flex items-center gap-1 shadow-lg"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Buat Halaman Baru</span>
              </button>
            </div>

            <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
              <table className="w-full text-xs text-left min-w-[500px]">
                <thead className="bg-[#121324] text-[10px] uppercase font-bold opacity-60 border-b border-[#1e2038]">
                  <tr>
                    <th className="p-3">Judul Dokumen</th>
                    <th className="p-3">Slug URL</th>
                    <th className="p-3 text-center">Tampilkan di Footer</th>
                    <th className="p-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2038]">
                  {staticPages.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="p-8 text-center opacity-50 italic">Belum ada halaman statis yang terdaftar.</td>
                    </tr>
                  ) : (
                    staticPages.map((page, idx) => (
                      <tr key={page._id || page.id || `pg-${idx}`} className="hover:bg-slate-500/5 transition-all">
                        <td className="p-3 font-extrabold text-slate-100">{page.title}</td>
                        <td className="p-3 font-mono text-cyan-400">/page/{page.slug}</td>
                        <td className="p-3 text-center">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-black ${page.showInFooter ? 'bg-green-500/10 text-green-400' : 'bg-slate-500/10 text-slate-400'}`}>
                            {page.showInFooter ? 'YA' : 'TIDAK'}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <div className="inline-flex gap-2">
                            <a
                              href={`/page/${page.slug}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-1.5 text-pink-400 hover:bg-pink-500/10 border border-pink-500/20 rounded font-bold text-[10px]"
                            >
                              Live Preview
                            </a>
                            <button
                              onClick={() => {
                                setEditingPage(page)
                                setPageForm(page)
                                setIsSlugManuallyEdited(false)
                                setShowPageModal(true)
                              }}
                              className="p-1.5 text-cyan-400 hover:bg-cyan-500/10 border border-cyan-500/20 rounded"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeletePage(page.id)}
                              className="p-1.5 text-red-400 hover:bg-red-500/10 border border-red-500/20 rounded"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {showPageModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#0d0e1b] border border-[#1e2038] rounded-2xl w-full max-w-lg p-6 relative space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
              <button
                onClick={() => setShowPageModal(false)}
                className="absolute top-4 right-4 p-1 rounded hover:bg-slate-500/5 text-xs opacity-65"
              >
                &times;
              </button>
              <h3 className="font-black text-white text-base border-b border-slate-500/10 pb-2">
                {editingPage ? 'Ubah Informasi Halaman Statis' : 'Buat Halaman Statis Baru'}
              </h3>

              <form onSubmit={handleSavePage} className="space-y-3.5 text-xs">
                <div className="space-y-1">
                  <label className="font-bold opacity-60">Judul Halaman</label>
                  <input
                    type="text"
                    value={pageForm.title}
                    onChange={(e) => {
                      const newTitle = e.target.value;
                      const slugValue = isSlugManuallyEdited ? pageForm.slug : newTitle
                        .toLowerCase()
                        .replace(/[^a-z0-9\s-]/g, '')
                        .replace(/[\s_]+/g, '-')
                        .replace(/-+/g, '-')
                        .trim()
                        .replace(/^-+|-+$/g, '');
                      setPageForm({ ...pageForm, title: newTitle, slug: slugValue });
                    }}
                    placeholder="Contoh: DMCA Disclaimer"
                    className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-bold opacity-60">Slug URL Dinamis</label>
                  <input
                    type="text"
                    value={pageForm.slug}
                    onChange={(e) => {
                      setIsSlugManuallyEdited(true);
                      setPageForm({ ...pageForm, slug: e.target.value.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/[\s_]+/g, '-') });
                    }}
                    placeholder="contoh: dmca-policy"
                    className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none font-mono"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-bold opacity-60">Konten Halaman (HTML / Markdown ringkas)</label>
                  <textarea
                    value={pageForm.content}
                    onChange={(e) => setPageForm({ ...pageForm, content: e.target.value })}
                    placeholder="<h2>Kebijakan Kami</h2><p>Tulis teks di sini...</p>"
                    className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none h-40 font-mono"
                    required
                  />
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    checked={pageForm.showInFooter}
                    onChange={(e) => setPageForm({ ...pageForm, showInFooter: e.target.checked })}
                    id="pageShowFooter"
                  />
                  <label htmlFor="pageShowFooter" className="text-xs font-bold opacity-80 cursor-pointer">Tampilkan Link Halaman Ini di Navigation Footer</label>
                </div>

                <div className="flex gap-2.5 pt-2 border-t border-slate-500/10">
                  <button type="submit" className="flex-1 py-2 bg-pink-500 hover:bg-pink-600 text-white font-extrabold rounded">
                    Simpan Halaman
                  </button>
                  <button type="button" onClick={() => setShowPageModal(false)} className="px-4 py-2 bg-slate-500/15 text-slate-300 rounded">
                    Batal
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'polling' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center bg-[#0d0e1b] p-4 rounded-xl border border-[#1e2038] gap-3">
              <div>
                <h3 className="font-extrabold text-sm text-white">Anime Request &amp; Polling Manager</h3>
                <p className="text-[11px] opacity-60">Sediakan opsi bagi pengunjung untuk melakukan voting anime nostalgia berikutnya.</p>
              </div>
              <button
                onClick={() => {
                  setEditingPoll(null)
                  setPollForm({ title: '', options: [{ id: 'opt-1', name: '', imageUrl: '', votes: 0 }], isActive: true })
                  setShowPollModal(true)
                }}
                className="px-4 py-2 rounded-lg bg-pink-500 hover:bg-pink-600 text-white font-extrabold text-xs flex items-center gap-1 shadow-lg"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Buat Polling Baru</span>
              </button>
            </div>

            <div className="bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
              <table className="w-full text-xs text-left min-w-[500px]">
                <thead className="bg-[#121324] text-[10px] uppercase font-bold opacity-60 border-b border-[#1e2038]">
                  <tr>
                    <th className="p-3">Pertanyaan / Topik Polling</th>
                    <th className="p-3">Opsi Pilihan (Votes)</th>
                    <th className="p-3 text-center">Status</th>
                    <th className="p-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2038]">
                  {pollingList.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="p-8 text-center opacity-50 italic">Belum ada polling yang terdaftar.</td>
                    </tr>
                  ) : (
                    pollingList.map((poll, idx) => {
                      const totalVotes = poll.options.reduce((sum, o) => sum + (o.votes || 0), 0)
                      return (
                        <tr key={poll._id || poll.id || `poll-${idx}`} className="hover:bg-slate-500/5 transition-all">
                          <td className="p-3">
                            <p className="font-extrabold text-slate-100">{poll.title}</p>
                            <span className="text-[10px] opacity-50 font-mono">ID: {poll.id} &bull; Total Suara: {totalVotes}</span>
                          </td>
                          <td className="p-3 space-y-1 max-w-sm">
                            {poll.options.map(o => (
                              <div key={o.id} className="flex justify-between text-[11px]">
                                <span className="opacity-90">{o.name}</span>
                                <span className="text-cyan-400 font-bold font-mono">{o.votes || 0} votes</span>
                              </div>
                            ))}
                          </td>
                          <td className="p-3 text-center">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-black ${poll.isActive ? 'bg-green-500/10 text-green-400' : 'bg-slate-500/10 text-slate-400'}`}>
                              {poll.isActive ? 'AKTIF' : 'MATI'}
                            </span>
                          </td>
                          <td className="p-3 text-right">
                            <div className="inline-flex gap-2">
                              <button
                                onClick={() => handleResetPollVotes(poll)}
                                className="px-2 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded text-[10px] font-black border border-amber-500/20"
                                title="Reset total vote ke 0"
                              >
                                Reset Hasil
                              </button>
                              <button
                                onClick={() => {
                                  setEditingPoll(poll)
                                  setPollForm(poll)
                                  setShowPollModal(true)
                                }}
                                className="p-1.5 text-cyan-400 hover:bg-cyan-500/10 border border-cyan-500/20 rounded"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeletePoll(poll.id)}
                                className="p-1.5 text-red-400 hover:bg-red-500/10 border border-red-500/20 rounded"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {showPollModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#0d0e1b] border border-[#1e2038] rounded-2xl w-full max-w-lg p-6 relative space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
              <button
                onClick={() => setShowPollModal(false)}
                className="absolute top-4 right-4 p-1 rounded hover:bg-slate-500/5 text-xs opacity-65"
              >
                &times;
              </button>
              <h3 className="font-black text-white text-base border-b border-slate-500/10 pb-2">
                {editingPoll ? 'Ubah Informasi Polling Anime' : 'Buat Topik Polling Baru'}
              </h3>

              <form onSubmit={handleSavePoll} className="space-y-4 text-xs">
                <div className="space-y-1">
                  <label className="font-bold opacity-60">Judul / Pertanyaan Polling</label>
                  <input
                    type="text"
                    value={pollForm.title}
                    onChange={(e) => setPollForm({ ...pollForm, title: e.target.value })}
                    placeholder="Contoh: Request Anime Nostalgia Pilihanmu"
                    className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038] text-white outline-none"
                    required
                  />
                </div>

                <div className="space-y-3 pt-2 border-t border-slate-500/10">
                  <div className="flex justify-between items-center">
                    <span className="font-black uppercase tracking-wider text-[10px] text-pink-500">Pilihan Opsi Anime (Opsi Pilihan)</span>
                    <button
                      type="button"
                      onClick={() => {
                        const newId = `opt-${Date.now()}`
                        setPollForm({
                          ...pollForm,
                          options: [...pollForm.options, { id: newId, name: '', imageUrl: '', votes: 0 }]
                        })
                      }}
                      className="px-2 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-[9px] font-black"
                    >
                      + Tambah Opsi
                    </button>
                  </div>

                  <div className="space-y-3.5 max-h-[250px] overflow-y-auto scrollbar-hide">
                    {pollForm.options.map((opt, oIdx) => (
                      <div key={opt.id} className="p-3 rounded-lg border border-[#1e2038] bg-black/20 space-y-2 relative text-left">
                        <button
                          type="button"
                          onClick={() => {
                            const updatedOptions = pollForm.options.filter(o => o.id !== opt.id)
                            setPollForm({ ...pollForm, options: updatedOptions })
                          }}
                          className="absolute top-1.5 right-1.5 text-red-400 font-bold hover:text-red-500"
                        >
                          &times;
                        </button>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <label className="text-[9px] opacity-60 font-bold">Nama Anime</label>
                            <input
                              type="text"
                              value={opt.name}
                              onChange={(e) => {
                                const updatedOptions = [...pollForm.options]
                                updatedOptions[oIdx].name = e.target.value
                                setPollForm({ ...pollForm, options: updatedOptions })
                              }}
                              placeholder="Contoh: Digimon"
                              className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038]"
                              required
                            />
                          </div>
                          <div className="space-y-1">
                            <label className="text-[9px] opacity-60 font-bold">Nilai Awal Vote</label>
                            <input
                              type="number"
                              value={opt.votes || 0}
                              onChange={(e) => {
                                const updatedOptions = [...pollForm.options]
                                updatedOptions[oIdx].votes = Number(e.target.value)
                                setPollForm({ ...pollForm, options: updatedOptions })
                              }}
                              className="w-full p-2.5 rounded bg-[#121324] border border-[#1e2038]"
                              min="0"
                            />
                          </div>
                        </div>

                        <div className="space-y-1">
                          <label className="text-[9px] opacity-60 font-bold">URL Gambar Thumbnail</label>
                          <div className="flex flex-col sm:flex-row gap-1.5">
                            <input
                              type="text"
                              value={opt.imageUrl || ''}
                              onChange={(e) => {
                                const updatedOptions = [...pollForm.options]
                                updatedOptions[oIdx].imageUrl = e.target.value
                                setPollForm({ ...pollForm, options: updatedOptions })
                              }}
                              placeholder="https://images.unsplash.com/..."
                              className="flex-1 p-2 bg-[#121324] rounded border border-[#1e2038]"
                            />
                            <button
                              type="button"
                              onClick={() => {
                                setUploadingPollOptionIndex(oIdx)
                                setTimeout(() => pollFileInputRef.current?.click(), 50)
                              }}
                              className="px-2 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-[9px] font-bold"
                            >
                              Upload ImageKit
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  {pollUploadProgress && (
                    <p className="text-[10px] text-cyan-400 font-bold animate-pulse mt-1.5">{pollUploadProgress}</p>
                  )}
                  <input
                    type="file"
                    ref={pollFileInputRef}
                    onChange={handlePollOptionUploadToImageKit}
                    accept="image/*"
                    className="hidden"
                  />
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    checked={pollForm.isActive}
                    onChange={(e) => setPollForm({ ...pollForm, isActive: e.target.checked })}
                    id="pollActive"
                  />
                  <label htmlFor="pollActive" className="text-xs font-bold opacity-80 cursor-pointer">Aktifkan Polling Ini di Frontend (On/Off)</label>
                </div>

                <div className="flex gap-2.5 pt-2 border-t border-slate-500/10">
                  <button type="submit" className="flex-1 py-2 bg-pink-500 hover:bg-pink-600 text-white font-extrabold rounded">
                    Simpan Polling
                  </button>
                  <button type="button" onClick={() => setShowPollModal(false)} className="px-4 py-2 bg-slate-500/15 text-slate-300 rounded">
                    Batal
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {showVideoModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#0d0e1b] border border-[#1e2038] rounded-2xl w-full max-w-lg p-6 relative space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
              <button
                onClick={() => setShowVideoModal(false)}
                className="absolute top-4 right-4 p-1 rounded hover:bg-slate-500/5 text-xs opacity-65"
              >
                &times;
              </button>
              <h3 className="font-black text-white text-base border-b border-slate-500/10 pb-2">
                {editingVideo ? 'Ubah Informasi Video Retro' : 'Tambah Video Baru ke Shindora'}
              </h3>

              <form onSubmit={handleSaveVideo} className="space-y-4 text-xs">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Judul Episode</label>
                    <input
                      type="text"
                      value={videoForm.title}
                      onChange={(e) => {
                        const newTitle = e.target.value;
                        const generatedSlug = newTitle
                          .toLowerCase()
                          .replace(/[^a-z0-9\s-]/g, '')
                          .replace(/[\s_]+/g, '-')
                          .replace(/-+/g, '-')
                          .trim()
                          .replace(/^-+|-+$/g, '');
                        
                        setVideoForm(prev => ({
                          ...prev,
                          title: newTitle,
                          slug: isVideoSlugManuallyEdited ? prev.slug : generatedSlug
                        }));
                      }}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038]"
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Slug SEO URL</label>
                    <input
                      type="text"
                      value={videoForm.slug}
                      onChange={(e) => {
                        setIsVideoSlugManuallyEdited(true);
                        setVideoForm(prev => ({ 
                          ...prev, 
                          slug: e.target.value.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/[\s_]+/g, '-') 
                        }));
                      }}
                      placeholder="auto-generated-slug"
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] font-mono"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Kategori Utama</label>
                    <select
                      value={videoForm.animeTitle}
                      onChange={(e) => {
                        const newMain = e.target.value;
                        setVideoForm({ 
                          ...videoForm, 
                          animeTitle: newMain, 
                          subCategory: '',
                          subCategory2: '' 
                        });
                      }}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                      required
                    >
                      {(() => {
                        const mainCategories = categories.filter(c => !c.parent_id || c.parent_id === 'none');
                        if (mainCategories.length === 0) {
                          return (
                            <>
                              <option value="Doraemon">Doraemon</option>
                              <option value="Crayon Shinchan">Crayon Shinchan</option>
                              <option value="Ninja Hattori-kun">Ninja Hattori-kun</option>
                              <option value="Chibi Maruko-chan">Chibi Maruko-chan</option>
                            </>
                          );
                        }
return mainCategories.map(c => (
                    <option key={c.id || c._id} value={c.name}>
                      {cleanCategoryName(c.name)}
                    </option>
                  ));
                })()}
              </select>
            </div>

            <div className="space-y-1">
              <label className="font-bold opacity-60">Sub-Kategori 1</label>
              <select
                value={videoForm.subCategory || ''}
                onChange={(e) => setVideoForm({ 
                  ...videoForm, 
                  subCategory: e.target.value, 
                  subCategory2: '' 
                })}
                className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white disabled:opacity-40"
                disabled={!videoForm.animeTitle}
              >
                <option value="">-- Tanpa Sub-Kategori 1 --</option>
                {(() => {
                  if (!videoForm.animeTitle) return null;

                  const selectedMain = categories.find(
                    c => (c.name === videoForm.animeTitle || cleanCategoryName(c.name) === cleanCategoryName(videoForm.animeTitle)) && 
                         (!c.parent_id || c.parent_id === 'none')
                  );
                  
                  if (!selectedMain) return null;
                  const mainId = String(selectedMain.id || selectedMain._id);

                  const subs = categories.filter(
                    c => c.parent_id && String(c.parent_id) === mainId
                  );

                  return subs.map((sub) => (
                    <option key={sub.id || sub._id} value={sub.name}>
                      {cleanCategoryName(sub.name)}
                    </option>
                  ));
                })()}
              </select>
            </div>

            <div className="space-y-1">
              <label className="font-bold opacity-60">Sub-Kategori 2</label>
              <select
                value={videoForm.subCategory2 || ''}
                onChange={(e) => setVideoForm({ ...videoForm, subCategory2: e.target.value })}
                className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white disabled:opacity-40"
                disabled={!videoForm.subCategory}
              >
                <option value="">-- Tanpa Sub-Kategori 2 --</option>
                {(() => {
                  if (!videoForm.subCategory) return null;

                  const selectedSub1 = categories.find(
                    c => c.name === videoForm.subCategory || 
                         cleanCategoryName(c.name) === cleanCategoryName(videoForm.subCategory)
                  );
                  
                  if (!selectedSub1) return null;
                  const sub1Id = String(selectedSub1.id || selectedSub1._id);

                  const sub2s = categories.filter(
                    c => c.parent_id && String(c.parent_id) === sub1Id
                  );

                  return sub2s.map((sub2) => (
                    <option key={sub2.id || sub2._id} value={sub2.name}>
                      {cleanCategoryName(sub2.name)}
                    </option>
                  ));
                })()}
              </select>
            </div>

                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Nomor Episode</label>
                    <input
                      type="text"
                      value={videoForm.episode || ''}
                      onChange={(e) => setVideoForm({ ...videoForm, episode: e.target.value })}
                      placeholder="Contoh: Eps 01, Eps 001, OVA, dll."
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038]"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="font-bold opacity-60">Thumbnail Gambar URL (Link Eksternal)</label>
                  <div className="flex flex-col sm:flex-row gap-1.5">
                    <input
                      type="text"
                      value={videoForm.thumbnailUrl}
                      onChange={(e) => setVideoForm({ ...videoForm, thumbnailUrl: e.target.value })}
                      className="flex-1 p-2 rounded bg-[#121324] border border-[#1e2038]"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => videoFileInputRef.current?.click()}
                      className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-bold"
                    >
                      Upload ImageKit
                    </button>
                    <input
                      type="file"
                      ref={videoFileInputRef}
                      onChange={handleVideoThumbnailUploadToImageKit}
                      accept="image/*"
                      className="hidden"
                    />
                  </div>
                  {videoUploadProgress && (
                    <p className="text-[10px] text-cyan-400 font-bold animate-pulse">{videoUploadProgress}</p>
                  )}
                </div>

                <div className="space-y-1">
                  <label className="font-bold opacity-60">Server 1 (Direct URL / Raw Iframe Tag)</label>
                  <input
                    type="text"
                    value={videoForm.videoUrl}
                    onChange={(e) => setVideoForm({ ...videoForm, videoUrl: e.target.value })}
                    className="w-full p-2 rounded bg-[#121324] border border-[#1e2038]"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Server 2 (Direct URL / Raw Iframe Tag)</label>
                    <input
                      type="text"
                      value={videoForm.videoUrl2 || ''}
                      onChange={(e) => setVideoForm({ ...videoForm, videoUrl2: e.target.value })}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038]"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Server 3 (Direct URL / Raw Iframe Tag)</label>
                    <input
                      type="text"
                      value={videoForm.videoUrl3 || ''}
                      onChange={(e) => setVideoForm({ ...videoForm, videoUrl3: e.target.value })}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038]"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="font-bold opacity-60">Deskripsi Singkat</label>
                  <textarea
                    value={videoForm.description}
                    onChange={(e) => setVideoForm({ ...videoForm, description: e.target.value })}
                    className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] h-16"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-bold opacity-60">Durasi Video (Format HH:MM:SS atau MM:SS)</label>
                  <input
                    type="text"
                    placeholder="misal: 23:40 atau 01:45:00"
                    value={videoForm.duration || ''}
                    onChange={(e) => setVideoForm({ ...videoForm, duration: e.target.value })}
                    className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Status Publikasi</label>
                    <select
                      value={videoForm.status || 'published'}
                      onChange={(e) => setVideoForm({ ...videoForm, status: e.target.value })}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038]"
                    >
                      <option value="published">Publik / Published</option>
                      <option value="draft">Draft</option>
                      <option value="scheduled">Terjadwal / Scheduled</option>
                    </select>
                  </div>

                  {videoForm.status === 'scheduled' && (
                    <div className="space-y-1 animate-fade-in">
                      <label className="font-bold opacity-60">Tanggal & Waktu Rilis</label>
                      <input
                        type="datetime-local"
                        value={videoForm.scheduledAt ? videoForm.scheduledAt.substring(0, 16) : ''}
                        onChange={(e) => setVideoForm({ ...videoForm, scheduledAt: e.target.value })}
                        className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                        required
                      />
                    </div>
                  )}
                </div>

                <div className="flex gap-2.5 pt-2 border-t border-slate-500/10">
                  <button type="submit" className="flex-1 py-2 bg-red-500 hover:bg-red-600 text-white font-extrabold rounded">
                    Simpan Video
                  </button>
                  <button type="button" onClick={() => setShowVideoModal(false)} className="px-4 py-2 bg-slate-500/15 text-slate-300 rounded">
                    Batal
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

      </main>
    </div>
  )
}
