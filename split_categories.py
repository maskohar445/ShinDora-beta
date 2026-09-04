#!/usr/bin/env python3
import os

def edit_admin_categories():
    admin_path = "/app/app/admin/page.js"
    if not os.path.exists(admin_path):
        print("Admin page not found at", admin_path)
        return False
        
    with open(admin_path, "r") as f:
        content = f.read()

    # 1. Insert new states and submit handlers
    old_states = """  const [catName, setCatName] = useState('')
  const [catParentId, setCatParentId] = useState('none')
  const [editingCat, setEditingCat] = useState(null)"""

    new_states = """  const [catName, setCatName] = useState('')
  const [catParentId, setCatParentId] = useState('none')
  const [editingCat, setEditingCat] = useState(null)
  const [mainCatName, setMainCatName] = useState('')
  const [subCatName, setSubCatName] = useState('')
  const [selectedMainId, setSelectedMainId] = useState('')

  const handleCreateMainCategory = async (e) => {
    e.preventDefault()
    if (!mainCatName.trim()) return
    const payload = {
      name: mainCatName,
      slug: mainCatName.toLowerCase().replace(/[^a-z0-9\\s-]/g, "").replace(/[\\s_]+/g, "-").replace(/-+/g, "-").trim().replace(/^-+|-+$/g, ""),
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
      alert("Pilih Kategori Utama Induk dan isi Nama Sub-Kategori!")
      return
    }
    const payload = {
      name: subCatName,
      slug: subCatName.toLowerCase().replace(/[^a-z0-9\\s-]/g, "").replace(/[\\s_]+/g, "-").replace(/-+/g, "-").trim().replace(/^-+|-+$/g, ""),
      parent_id: selectedMainId
    }
    try {
      const res = await fetch("/api/categories", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        alert("🎉 Sub-Kategori berhasil disimpan!")
        setSubCatName("")
        setSelectedMainId("")
        fetchAdminData()
      } else {
        const errData = await res.json()
        throw new Error(errData.error || "Gagal menyimpan sub-kategori")
      }
    } catch (err) {
      alert(err.message)
    }
  }"""

    if old_states in content:
        content = content.replace(old_states, new_states)
        print("✓ Admin: Category split states & handlers added")
    else:
        print("✗ Admin: States not matched")

    # 2. Replace Categories management activeTab rendering JSX
    old_categories_tab = """        {activeTab === 'categories' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-[#0d0e1b] rounded-xl border border-[#1e2038] space-y-4 self-start">
              <h3 className="font-extrabold text-sm text-white">{editingCat ? 'Edit Kategori' : 'Tambah Kategori Baru'}</h3>
              <form onSubmit={handleSaveCategory} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[10px] opacity-60 uppercase font-bold tracking-wider">Nama Kategori</label>
                  <input
                    type="text"
                    placeholder="misal: Doraemon..."
                    value={catName}
                    onChange={(e) => setCatName(e.target.value)}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-red-500"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] opacity-60 uppercase font-bold tracking-wider">Kategori Induk / Sub-Kategori</label>
                  <select
                    value={catParentId}
                    onChange={(e) => setCatParentId(e.target.value)}
                    className="w-full text-xs p-2 rounded bg-[#121324] border border-[#1e2038] text-white outline-none focus:border-red-500"
                  >
                    <option value="none">Tidak Ada (Jadikan Kategori Utama)</option>
                    {categories
                      .filter(c => (!c.parent_id || c.parent_id === 'none') && (!editingCat || c.id !== editingCat.id))
                      .map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                  </select>
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="submit" className="flex-1 py-1.5 bg-red-500 hover:bg-red-600 text-white font-extrabold text-xs rounded">
                    {editingCat ? 'Simpan' : 'Tambah'}
                  </button>
                  {editingCat && (
                    <button type="button" onClick={() => { setEditingCat(null); setCatName(''); setCatParentId('none'); }} className="px-3 bg-slate-500/10 text-xs rounded">
                      Batal
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div className="md:col-span-2 bg-[#0d0e1b] rounded-xl border border-[#1e2038] overflow-x-auto">
              <table className="w-full text-xs text-left min-w-[500px]">
                <thead className="bg-[#121324] text-[10px] uppercase opacity-60">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Nama Kategori</th>
                    <th className="p-3">Sub-Kategori</th>
                    <th className="p-3">Slug</th>
                    <th className="p-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2038]">
                  {searchedCategories.map((cat, index) => {
                    const parentCat = categories.find(p => p.id && cat.parent_id && String(p.id) === String(cat.parent_id));
                    return (
                      <tr key={cat._id || cat.id || `cat-${index}`}>
                        <td className="p-3 font-mono opacity-50">{cat.id}</td>
                        <td className="p-3 font-bold">{cat.name}</td>
                        <td className="p-3">
                          {parentCat ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300">
                              Sub dari: {parentCat.name}
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-500/20 text-green-300">
                              Kategori Utama
                            </span>
                          )}
                        </td>
                        <td className="p-3 text-pink-400 font-mono">{cat.slug}</td>
                        <td className="p-3 text-right">
                          <div className="inline-flex gap-1">
                            <button
                              onClick={() => { setEditingCat(cat); setCatName(cat.name); setCatParentId(cat.parent_id || 'none'); }}
                              className="p-1 text-cyan-400 hover:bg-cyan-500/10 rounded"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeleteCategory(cat.id)}
                              className="p-1 text-red-400 hover:bg-red-500/10 rounded"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}"""

    new_categories_tab = """        {activeTab === 'categories' && (
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
                      <th className="p-3">Slug</th>
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
                            <td className="p-3 text-pink-400 font-mono">{cat.slug}</td>
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
                      <th className="p-3">Slug</th>
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
                              <td className="p-3 text-pink-400 font-mono">{cat.slug}</td>
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
        )}"""

    if old_categories_tab in content:
        content = content.replace(old_categories_tab, new_categories_tab)
        print("✓ Admin: Categories tab view upgraded with split tables and forms")
    else:
        # Check if single quotes vs double quotes was the issue
        old_categories_tab_d = old_categories_tab.replace("'", '"')
        if old_categories_tab_d in content:
            content = content.replace(old_categories_tab_d, new_categories_tab)
            print("✓ Admin: Categories tab (double quotes) upgraded")
        else:
            print("✗ Admin: Categories tab selector not matched")

    with open(admin_path, "w") as f:
        f.write(content)
    return True

if __name__ == "__main__":
    edit_admin_categories()
    print("SUCCESS: Category restructuring completed!")
