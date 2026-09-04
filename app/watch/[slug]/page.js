import { MongoClient } from 'mongodb'
import App from '../../page'

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;
  
  let video = null
  try {
    const client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    const db = client.db(process.env.DB_NAME)
    video = await db.collection('videos').findOne({ slug })
    await client.close()
  } catch (err) {
    console.error('[Metadata Fetch Error]:', err)
  }

  if (!video) {
    return {
      title: 'Konten Tidak Ditemukan - ShinDora Nesub',
    }
  }

  const title = `${video.title} - ${video.subCategory ? `${video.subCategory} | ` : ''}${video.animeTitle} - ShinDora Nesub`
  const description = video.description || `Tonton ${video.title} sub Indo gratis di ShinDora Nesub.`
  const imageUrl = video.thumbnailUrl || '/default-og.jpg'

  return {
    title: title,
    description: description,
    openGraph: {
      title: title,
      description: description,
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: video.title,
        },
      ],
      type: 'video.other',
    },
    twitter: {
      card: 'summary_large_image',
      title: title,
      description: description,
      images: [imageUrl],
    },
  }
}

export default async function WatchSlugPage({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;

  let video = null
  try {
    const client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    const db = client.db(process.env.DB_NAME)
    video = await db.collection('videos').findOne({ slug })
    await client.close()
  } catch (err) {
    console.error('[Watch JSON-LD Mongo Fetch Error]:', err)
  }

  const jsonLd = video ? {
    '@context': 'https://schema.org',
    '@type': 'VideoObject',
    'name': video.title,
    'description': video.description || `Tonton ${video.title} sub Indo gratis di ShinDora Nesub.`,
    'thumbnailUrl': [
      video.thumbnailUrl || 'https://shindoranesub.my.id/default-og.jpg'
    ],
    'uploadDate': new Date(video.createdAt || new Date()).toISOString(),
    'embedUrl': video.videoUrl || `https://shindoranesub.my.id/api/embed?id=${video.id}`,
    'interactionStatistic': {
      '@type': 'InteractionCounter',
      'interactionType': { '@type': 'WatchAction' },
      'userInteractionCount': video.views || 0
    }
  } : null;

  return (
    <>
      {jsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      )}
      <App />
    </>
  )
}
