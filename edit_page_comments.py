#!/usr/bin/env python3
import os

def edit_page_comments():
    page_path = "/app/app/page.js"
    if not os.path.exists(page_path):
        print("page.js not found")
        return False
        
    with open(page_path, "r") as f:
        content = f.read()

    # 1. Replace parent.content rendering
    old_parent_content = """                                  <p className={`text-xs opacity-90 leading-relaxed ${
                                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                                  }`}>{parent.content}</p>"""

    new_parent_content = """                                  <div className={`text-xs opacity-90 leading-relaxed ${
                                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                                  }`} dangerouslySetInnerHTML={{ __html: parseEmotesToHtml(parent.content, emotes) }} />"""

    if old_parent_content in content:
        content = content.replace(old_parent_content, new_parent_content)
        print("✓ Home: Parent comment rendering updated")
    else:
        print("✗ Home: Parent comment rendering not matched")

    # 2. Replace reply.content rendering
    old_reply_content = """                                          <p className={`text-xs opacity-90 leading-relaxed break-words ${
                                            theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                                          }`}>{reply.content}</p>"""

    new_reply_content = """                                          <div className={`text-xs opacity-90 leading-relaxed break-words ${
                                            theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                                          }`} dangerouslySetInnerHTML={{ __html: parseEmotesToHtml(reply.content, emotes) }} />"""

    if old_reply_content in content:
        content = content.replace(old_reply_content, new_reply_content)
        print("✓ Home: Reply comment rendering updated")
    else:
        print("✗ Home: Reply comment rendering not matched")

    # 3. Replace main comment form textarea
    old_main_input = """                            <textarea
                              placeholder="Tulis opini nostalgia Anda tentang episode ini..."
                              value={newCommentText}
                              onChange={(e) => setNewCommentText(e.target.value)}
                              className={`w-full text-xs p-2.5 rounded-lg border outline-none min-h-[70px] ${
                                theme === 'dark' ? 'bg-[#121324] border-[#1e2038] text-white focus:border-cyan-500' : 'bg-slate-50 border-slate-200'
                              }`}
                            />"""

    new_main_input = """                            <div className="relative">
                              <textarea
                                placeholder="Tulis opini nostalgia Anda tentang episode ini..."
                                value={newCommentText}
                                onChange={(e) => setNewCommentText(e.target.value)}
                                className={`w-full text-xs p-2.5 pr-8 rounded-lg border outline-none min-h-[70px] ${
                                  theme === 'dark' ? 'bg-[#121324] border-[#1e2038] text-white focus:border-cyan-500' : 'bg-slate-50 border-slate-200'
                                }`}
                              />
                              <div className="absolute right-2 bottom-2">
                                <EmotePicker onSelectEmote={(code) => setNewCommentText(prev => prev + ' ' + code + ' ')} />
                              </div>
                            </div>"""

    if old_main_input in content:
        content = content.replace(old_main_input, new_main_input)
        print("✓ Home: Main comment input updated")
    else:
        print("✗ Home: Main comment input not matched")

    # 4. Replace reply comment form textarea
    old_reply_input = """                                      <textarea
                                        placeholder="Tulis balasan nostalgia Anda..."
                                        value={replyText}
                                        onChange={(e) => setReplyText(e.target.value)}
                                        className={`w-full text-xs p-2.5 rounded-lg border outline-none resize-none min-h-[60px] ${
                                          theme === 'dark' ? 'bg-[#121324] border-[#1e2038] text-white focus:border-cyan-500' : 'bg-slate-50 border-slate-200'
                                        }`}
                                        required
                                      />"""

    new_reply_input = """                                      <div className="relative">
                                        <textarea
                                          placeholder="Tulis balasan nostalgia Anda..."
                                          value={replyText}
                                          onChange={(e) => setReplyText(e.target.value)}
                                          className={`w-full text-xs p-2.5 pr-8 rounded-lg border outline-none resize-none min-h-[60px] ${
                                            theme === 'dark' ? 'bg-[#121324] border-[#1e2038] text-white focus:border-cyan-500' : 'bg-slate-50 border-slate-200'
                                          }`}
                                          required
                                        />
                                        <div className="absolute right-2 bottom-2">
                                          <EmotePicker onSelectEmote={(code) => setReplyText(prev => prev + ' ' + code + ' ')} />
                                        </div>
                                      </div>"""

    if old_reply_input in content:
        content = content.replace(old_reply_input, new_reply_input)
        print("✓ Home: Reply comment input updated")
    else:
        print("✗ Home: Reply comment input not matched")

    with open(page_path, "w") as f:
        f.write(content)
    return True

if __name__ == "__main__":
    edit_page_comments()
    print("SUCCESS: Comment section emote integration completed!")
