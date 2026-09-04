#!/usr/bin/env python3
import os

def resize_picker_emotes():
    picker_path = "/app/components/EmotePicker.jsx"
    if not os.path.exists(picker_path):
        print("EmotePicker.jsx not found")
        return False
        
    with open(picker_path, "r") as f:
        content = f.read()

    # 1. Resize width from w-60 to w-64, and image from w-8 h-8 to w-10 h-10
    old_width = "w-60 max-h-48"
    new_width = "w-64 max-h-56"
    content = content.replace(old_width, new_width)

    old_img = "className=\"w-8 h-8 object-contain\""
    new_img = "className=\"w-10 h-10 object-contain\""
    content = content.replace(old_img, new_img)

    with open(picker_path, "w") as f:
        f.write(content)
    print("✓ EmotePicker: Resized popover and emotes to w-10 h-10")
    return True

def edit_page_parser():
    page_path = "/app/app/page.js"
    if not os.path.exists(page_path):
        print("page.js not found")
        return False
        
    with open(page_path, "r") as f:
        content = f.read()

    old_parser = """  const parseEmotesToHtml = (text, emotesList = []) => {
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

    new_parser = """  const parseEmotesToHtml = (text, emotesList = []) => {
    if (!text) return '';
    const trimmed = text.trim();
    const isSoloEmote = emotesList.some(emote => emote.code === trimmed);
    const sizeClass = isSoloEmote 
      ? 'w-14 h-14 md:w-16 md:h-16 my-1 block mx-auto object-contain' 
      : 'w-8 h-8 md:w-9 md:h-9 mx-0.5 inline-block align-middle object-contain';

    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');

    emotesList.forEach(emote => {
      const escapedCode = emote.code.replace(/[.*+?^${}()|[\]\\\\]/g, '\\\\$&');
      const regex = new RegExp(escapedCode, 'g');
      escaped = escaped.replace(regex, `<img src="${emote.imageUrl}" alt="${emote.code}" title="${emote.code}" class="${sizeClass} pointer-events-none drop-shadow-sm" />`);
    });

    return escaped;
  };"""

    if old_parser in content:
        content = content.replace(old_parser, new_parser)
        print("✓ Home: Parser upgraded with Solo vs Mixed sizing")
    else:
        # Check with double quotes
        old_parser_double = old_parser.replace("'", '"')
        if old_parser_double in content:
            content = content.replace(old_parser_double, new_parser)
            print("✓ Home: Parser (double quotes) upgraded")
        else:
            # Let's try replacing a simpler substring
            print("✗ Home: Parser block not matched exactly")

    with open(page_path, "w") as f:
        f.write(content)
    return True

def edit_chat_parser():
    chat_path = "/app/components/FloatingChatWidget.jsx"
    if not os.path.exists(chat_path):
        print("FloatingChatWidget.jsx not found")
        return False
        
    with open(chat_path, "r") as f:
        content = f.read()

    old_parser = """  const parseEmotesToHtml = (text, emotesList = []) => {
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

    new_parser = """  const parseEmotesToHtml = (text, emotesList = []) => {
    if (!text) return '';
    const trimmed = text.trim();
    const isSoloEmote = emotesList.some(emote => emote.code === trimmed);
    const sizeClass = isSoloEmote 
      ? 'w-14 h-14 md:w-16 md:h-16 my-1 block mx-auto object-contain' 
      : 'w-8 h-8 md:w-9 md:h-9 mx-0.5 inline-block align-middle object-contain';

    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');

    emotesList.forEach(emote => {
      const escapedCode = emote.code.replace(/[.*+?^${}()|[\]\\\\]/g, '\\\\$&');
      const regex = new RegExp(escapedCode, 'g');
      escaped = escaped.replace(regex, `<img src="${emote.imageUrl}" alt="${emote.code}" title="${emote.code}" class="${sizeClass} pointer-events-none drop-shadow-sm" />`);
    });

    return escaped;
  };"""

    if old_parser in content:
        content = content.replace(old_parser, new_parser)
        print("✓ Chat: Parser upgraded with Solo vs Mixed sizing")
    else:
        old_parser_double = old_parser.replace("'", '"')
        if old_parser_double in content:
            content = content.replace(old_parser_double, new_parser)
            print("✓ Chat: Parser (double quotes) upgraded")
        else:
            print("✗ Chat: Parser block not matched exactly")

    with open(chat_path, "w") as f:
        f.write(content)
    return True

if __name__ == "__main__":
    resize_picker_emotes()
    edit_page_parser()
    edit_chat_parser()
    print("RESIZING EMOTES SCRIPT COMPLETED!")
