'use client';

import { useState, useEffect, useRef } from 'react';
import { Smile } from 'lucide-react';

export default function EmotePicker({ onSelectEmote }) {
  const [isOpen, setIsOpen] = useState(false);
  const [emotes, setEmotes] = useState([]);
  const containerRef = useRef(null);

  useEffect(() => {
    fetchEmotes();

    // Close on click outside
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchEmotes = async () => {
    try {
      const res = await fetch('/api/emotes');
      if (res.ok) {
        const data = await res.json();
        setEmotes(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('[Fetch Emotes Error]:', err);
    }
  };

  const handleEmoteClick = (code) => {
    onSelectEmote(code);
    setIsOpen(false);
  };

  return (
    <div className="relative inline-block" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="p-1.5 rounded-lg hover:bg-slate-500/10 text-slate-400 hover:text-cyan-400 transition-all flex items-center justify-center cursor-pointer"
        title="Pilih Custom Emote"
      >
        <Smile className="w-4 h-4 md:w-5 md:h-5" />
      </button>

      {isOpen && (
        <div className="absolute bottom-10 right-0 z-50 p-3 bg-[#0d0e1b]/95 backdrop-blur-md border border-[#1e2038] rounded-xl shadow-2xl w-64 max-h-56 overflow-y-auto scrollbar-hide animate-fade-in flex flex-col gap-2">
          <div className="text-[9px] uppercase font-bold text-slate-400 tracking-wider border-b border-[#1e2038] pb-1">
            Custom Emote &amp; GIF
          </div>
          
          {emotes.length === 0 ? (
            <div className="text-[10px] text-slate-500 italic text-center py-4">
              Belum ada emote.
            </div>
          ) : (
            <div className="grid grid-cols-4 gap-1.5 p-1">
              {emotes.map((emote) => (
                <button
                  key={emote.id || emote._id}
                  type="button"
                  onClick={() => handleEmoteClick(emote.code)}
                  className="p-1 rounded bg-[#121324] hover:bg-cyan-500/10 border border-[#1e2038] hover:border-cyan-500/40 transition-all flex items-center justify-center group relative cursor-pointer"
                  title={emote.code}
                >
                  <img
                    src={emote.imageUrl}
                    alt={emote.code}
                    className="w-10 h-10 object-contain"
                  />
                  {/* Tooltip on Hover */}
                  <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block bg-black text-white text-[8px] font-bold px-1 py-0.5 rounded whitespace-nowrap z-55 border border-white/10 pointer-events-none">
                    {emote.code}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
