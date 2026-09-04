#!/usr/bin/env python3
import os

def edit_admin_page():
    admin_path = "/app/app/admin/page.js"
    if not os.path.exists(admin_path):
        print("Admin page not found")
        return False
        
    with open(admin_path, "r") as f:
        content = f.read()

    # 1. Update videoForm state declarations to include subCategory2
    old_form_state = "title: '', slug: '', animeTitle: 'Doraemon', subCategory: '', episode: '', thumbnailUrl: '', videoUrl: '', videoUrl2: '', videoUrl3: '', description: '', views: 0, likes: 0, status: 'published', scheduledAt: ''"
    new_form_state = "title: '', slug: '', animeTitle: 'Doraemon', subCategory: '', subCategory2: '', episode: '', thumbnailUrl: '', videoUrl: '', videoUrl2: '', videoUrl3: '', description: '', views: 0, likes: 0, status: 'published', scheduledAt: ''"
    content = content.replace(old_form_state, new_form_state)

    # 2. Update category selection onChange in Form Modal to reset both sub-categories
    old_category_select = """                    <select
                      value={videoForm.animeTitle}
                      onChange={(e) => {
                        const newMain = e.target.value;
                        setVideoForm({ 
                          ...videoForm, 
                          animeTitle: newMain, 
                          subCategory: '' 
                        });
                      }}"""
    new_category_select = """                    <select
                      value={videoForm.animeTitle}
                      onChange={(e) => {
                        const newMain = e.target.value;
                        setVideoForm({ 
                          ...videoForm, 
                          animeTitle: newMain, 
                          subCategory: '',
                          subCategory2: '' 
                        });
                      }}"""
    content = content.replace(old_category_select, new_category_select)

    # 3. Update VideoForm Modal inside admin/page.js to display both Sub-Kategori 1 and Sub-Kategori 2
    old_sub_inputs = """                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Sub-Kategori</label>
                    <select
                      value={videoForm.subCategory || ''}
                      onChange={(e) => setVideoForm({ ...videoForm, subCategory: e.target.value })}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    >
                      <option value="">-- Tanpa Sub-Kategori --</option>
                      {(() => {
                        // 1. Cari kategori utama berdasarkan nama
                        const selectedMain = categories.find(
                          c => c.name === videoForm.animeTitle && (!c.parent_id || c.parent_id === 'none')
                        );
                        
                        if (!selectedMain) return null;
                        // 2. Normalisasi ID ke bentuk String
                        const mainId = String(selectedMain.id || selectedMain._id);
                        // 3. Filter sub-kategori yang parent_id-nya cocok
                        const subs = categories.filter(
                          c => c.parent_id && String(c.parent_id) === mainId
                        );
                        return subs.map((sub) => (
                          <option key={sub.id || sub._id} value={sub.name}>
                            {sub.name}
                          </option>
                        ));
                      })()}
                    </select>
                  </div>"""

    new_sub_inputs = """                  <div className="space-y-1">
                    <label className="font-bold opacity-60">Sub-Kategori 1</label>
                    <select
                      value={videoForm.subCategory || ''}
                      onChange={(e) => setVideoForm({ ...videoForm, subCategory: e.target.value })}
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    >
                      <option value="">-- Tanpa Sub-Kategori 1 --</option>
                      {(() => {
                        const selectedMain = categories.find(
                          c => c.name === videoForm.animeTitle && (!c.parent_id || c.parent_id === 'none')
                        );
                        
                        if (!selectedMain) return null;
                        const mainId = String(selectedMain.id || selectedMain._id);
                        const subs = categories.filter(
                          c => c.parent_id && String(c.parent_id) === mainId
                        );
                        return subs.map((sub) => (
                          <option key={sub.id || sub._id} value={sub.name}>
                            {sub.name}
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
                      className="w-full p-2 rounded bg-[#121324] border border-[#1e2038] text-white"
                    >
                      <option value="">-- Tanpa Sub-Kategori 2 --</option>
                      {(() => {
                        const selectedMain = categories.find(
                          c => c.name === videoForm.animeTitle && (!c.parent_id || c.parent_id === 'none')
                        );
                        
                        if (!selectedMain) return null;
                        const mainId = String(selectedMain.id || selectedMain._id);
                        const subs = categories.filter(
                          c => c.parent_id && String(c.parent_id) === mainId
                        );
                        return subs.map((sub) => (
                          <option key={sub.id || sub._id} value={sub.name}>
                            {sub.name}
                          </option>
                        ));
                      })()}
                    </select>
                  </div>"""
    content = content.replace(old_sub_inputs, new_sub_inputs)

    # 4. Update table rendering to display full category hierarchy consistently
    old_video_category_td = """                      <td className="p-3 font-semibold text-cyan-400">{video.animeTitle}</td>"""
    new_video_category_td = """                      <td className="p-3 font-semibold text-cyan-400">
                        {video.animeTitle}
                        {video.subCategory ? ` > ${video.subCategory}` : ""}
                        {video.subCategory2 ? ` > ${video.subCategory2}` : ""}
                      </td>"""
    content = content.replace(old_video_category_td, new_video_category_td)

    # 5. Automatically sort videoIds in handleSavePlaylist before sending to backend
    old_save_playlist = """  const handleSavePlaylist = async (e) => {
    e.preventDefault()
    if (!playlistForm.title.trim()) return
    const videoIds = playlistForm.videoIds

    const payload = editingPlaylist
      ? { id: editingPlaylist.id, title: playlistForm.title, videoIds }
      : { title: playlistForm.title, ownerId: null, isPrivate: false, videoIds }"""

    new_save_playlist = """  const handleSavePlaylist = async (e) => {
    e.preventDefault()
    if (!playlistForm.title.trim()) return
    const videoIds = playlistForm.videoIds

    // Automatically sort videoIds before saving
    const selectedVideos = videos.filter(v => videoIds.includes(v.id))
    const sortedSelected = sortVideosByEpisode(selectedVideos)
    const sortedVideoIds = sortedSelected.map(v => v.id)

    const payload = editingPlaylist
      ? { id: editingPlaylist.id, title: playlistForm.title, videoIds: sortedVideoIds }
      : { title: playlistForm.title, ownerId: null, isPrivate: false, videoIds: sortedVideoIds }"""
    content = content.replace(old_save_playlist, new_save_playlist)

    with open(admin_path, "w") as f:
        f.write(content)
    print("✓ Admin: VideoForm and Playlist Auto-sorting completed")
    return True

def edit_page_js():
    page_path = "/app/app/page.js"
    if not os.path.exists(page_path):
        print("page.js not found")
        return False
        
    with open(page_path, "r") as f:
        content = f.read()

    # 1. Update renderCategoryBadges to display both subCategory and subCategory2
    old_badge_helper = """  const renderCategoryBadges = (animeTitle, subCategory, textClass = "text-[8px]") => {
    if (!animeTitle) return null;
    const parts = animeTitle.split(' > ');
    const mainCat = parts[0];
    const subCat = subCategory || (parts.length === 2 ? parts[1] : null);

    if (subCat) {
      return (
        <div className="flex flex-wrap gap-1">
          <span className={`px-1.5 py-0.5 rounded font-bold bg-black/80 text-cyan-400 uppercase ${textClass}`}>
            {mainCat}
          </span>
          <span className={`px-1.5 py-0.5 rounded font-bold bg-cyan-500 text-black uppercase ${textClass}`}>
            {subCat}
          </span>
        </div>
      );
    }
    return (
      <span className={`px-1.5 py-0.5 rounded font-bold bg-black/80 text-cyan-400 uppercase ${textClass}`}>
        {mainCat}
      </span>
    );
  };"""

    new_badge_helper = """  const renderCategoryBadges = (animeTitle, subCategory, textClass = "text-[8px]", subCategory2) => {
    if (!animeTitle) return null;
    const parts = animeTitle.split(' > ');
    const mainCat = parts[0];
    const subCat = subCategory || (parts.length >= 2 ? parts[1] : null);
    const subCat2 = subCategory2 || (parts.length >= 3 ? parts[2] : null);

    return (
      <div className="flex flex-wrap gap-1">
        <span className={`px-1.5 py-0.5 rounded font-bold bg-black/80 text-cyan-400 uppercase ${textClass}`}>
          {mainCat}
        </span>
        {subCat && (
          <span className={`px-1.5 py-0.5 rounded font-bold bg-cyan-500 text-black uppercase ${textClass}`}>
            {subCat}
          </span>
        )}
        {subCat2 && (
          <span className={`px-1.5 py-0.5 rounded font-bold bg-purple-500 text-white uppercase ${textClass}`}>
            {subCat2}
          </span>
        )}
      </div>
    );
  };"""
    content = content.replace(old_badge_helper, new_badge_helper)

    # 2. Update renderCategoryBadges calls to pass subCategory2
    old_call_1 = "{renderCategoryBadges(video.animeTitle, video.subCategory, \"text-[8px]\")}"
    new_call_1 = "{renderCategoryBadges(video.animeTitle, video.subCategory, \"text-[8px]\", video.subCategory2)}"
    content = content.replace(old_call_1, new_call_1)

    old_call_2 = "{renderCategoryBadges(video.animeTitle, video.subCategory, \"text-[9px]\")}"
    new_call_2 = "{renderCategoryBadges(video.animeTitle, video.subCategory, \"text-[9px]\", video.subCategory2)}"
    content = content.replace(old_call_2, new_call_2)

    old_call_3 = "{renderCategoryBadges(activeVideo.animeTitle, activeVideo.subCategory, \"text-[10px]\")}"
    new_call_3 = "{renderCategoryBadges(activeVideo.animeTitle, activeVideo.subCategory, \"text-[10px]\", activeVideo.subCategory2)}"
    content = content.replace(old_call_3, new_call_3)

    # 3. Update playNextPlaylistItem queue selection to sort the list
    old_play_next = """    const playlistVids = currentPlaylist.videoIds
      .map(vidId => videos.find(v => v.id === vidId))
      .filter(Boolean)"""

    new_play_next = """    const playlistVids = sortVideosByEpisode(
      currentPlaylist.videoIds
        .map(vidId => videos.find(v => v.id === vidId))
        .filter(Boolean)
    )"""
    content = content.replace(old_play_next, new_play_next)

    # 4. Update the visual Playlist queue render JSX block to automatically sort the elements
    old_queue_jsx = """                      {currentPlaylist.videoIds
                        .map(vidId => videos.find(v => v.id === vidId))
                        .filter(Boolean)
                        .map((vid) => {"""

    new_queue_jsx = """                      {sortVideosByEpisode(
                        currentPlaylist.videoIds
                          .map(vidId => videos.find(v => v.id === vidId))
                          .filter(Boolean)
                      ).map((vid) => {"""
    content = content.replace(old_queue_jsx, new_queue_jsx)

    with open(page_path, "w") as f:
        f.write(content)
    print("✓ Home: Category badges and Playlist Auto-sorting completed")
    return True

if __name__ == "__main__":
    edit_admin_page()
    edit_page_js()
    print("ALL SORTING & DUAL SUB-CATEGORY CHANGES SUCCESSFULLY APPLIED!")
