export default function manifest() {
  return {
    name: 'ShinDora Nesub',
    short_name: 'ShinDora',
    description: 'Tempat Nonton Doraemon, Crayon Shin-chan Dan Ninja Hattori-kun Takarir Indonesia Gratis',
    start_url: '/',
    display: 'standalone',
    background_color: '#0a0b14',
    theme_color: '#0a0b14',
    icons: [
      {
        src: '/favicon.ico',
        sizes: '64x64 32x32 24x24 16x16',
        type: 'image/x-icon',
      },
      {
        src: '/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'any maskable',
      },
      {
        src: '/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any maskable',
      },
      {
        src: '/apple-icon.png',
        sizes: '180x180',
        type: 'image/png',
      },
    ],
  }
}
