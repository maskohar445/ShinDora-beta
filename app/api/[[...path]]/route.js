export const dynamic = 'force-dynamic'
import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'
import nodemailer from 'nodemailer'

let client
let db
let connectionPromise = null

async function triggerOneSignalNotification(db, video) {
  try {
    const settings = await db.collection("settings").findOne({ id: "site_settings" })
    const onesignalAppId = process.env.NEXT_PUBLIC_ONESIGNAL_APP_ID || settings?.onesignalAppId
    const onesignalRestKey = process.env.ONESIGNAL_REST_API_KEY || settings?.onesignalRestApiKey
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "https://shindoranesub.my.id"

    if (!onesignalAppId || !onesignalRestKey) {
      console.warn("[OneSignal Info]: OneSignal App ID or Rest API Key not configured.")
      return
    }

    const payload = {
      app_id: onesignalAppId,
      included_segments: ["Subscribed Users"],
      headings: { en: `Episode Baru: ${video.animeTitle || "Anime"} 🎬` },
      contents: { en: `Tonton ${video.title} (${video.episode || "Eps 1"}) sekarang!` },
      big_picture: video.thumbnailUrl,
      url: `${baseUrl}/watch/${video.slug}`
    }

    const response = await fetch("https://onesignal.com/api/v1/notifications", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Basic ${onesignalRestKey}`
      },
      body: JSON.stringify(payload)
    })

    const data = await response.json()
    console.log("[OneSignal Response]:", data)
  } catch (err) {
    console.error("[OneSignal Error]:", err)
  }
}

async function connectToMongo() {
  if (db) return db
  if (!connectionPromise) {
    connectionPromise = (async () => {
      const tempClient = new MongoClient(process.env.MONGO_URL)
      await tempClient.connect()
      const tempDb = tempClient.db(process.env.DB_NAME)
      db = tempDb
      client = tempClient
      return tempDb
    })()
  }
  return connectionPromise
}

function generateSlug(text) {
  if (!text) return ''
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
}

// Helper pembersih karakter prefix indentasi (seperti ↳)
function cleanCatName(text) {
  if (!text) return ''
  return text.replace(/[^a-zA-Z0-9\s-]/g, '').trim()
}

async function deleteImageKitFileByUrl(url, privateKey) {
  if (!url || !url.includes('ik.imagekit.io') || !privateKey) return

  try {
    const urlParts = url.split('/')
    const fileName = urlParts[urlParts.length - 1]
    if (!fileName) return

    const authHeader = 'Basic ' + Buffer.from(privateKey + ':').toString('base64')

    const searchRes = await fetch(`https://api.imagekit.io/v1/files?searchQuery=name="${fileName}"`, {
      headers: { 'Authorization': authHeader }
    })

    if (!searchRes.ok) return

    const files = await searchRes.json()
    if (Array.isArray(files) && files.length > 0) {
      const fileId = files[0].fileId
      await fetch(`https://api.api.imagekit.io/v1/files/${fileId}`, {
        method: 'DELETE',
        headers: { 'Authorization': authHeader }
      })
    }
  } catch (err) {
    console.error('[deleteImageKitFileByUrl Error]:', err)
  }
}

function handleCORS(response) {
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-user-id')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  
  response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0')
  response.headers.set('Pragma', 'no-cache')
  response.headers.set('Expires', '0')
  response.headers.set('Surrogate-Control', 'no-store')
  return response
}

export async function OPTIONS() {
  return handleCORS(new NextResponse(null, { status: 200 }))
}

async function resolveCategoryIdsForVideo(db, video) {
  const updatedVideo = { ...video };
  
  // 1. Resolve category_id (Kategori Utama)
  if (video.animeTitle) {
    const cleanMain = cleanCatName(video.animeTitle);
    const mainCat = await db.collection('categories').findOne({
      name: { $regex: new RegExp(`^.*${cleanMain}.*$`, 'i') },
      parent_id: { $in: [null, 'none'] }
    });
    if (mainCat) {
      updatedVideo.category_id = String(mainCat.id || mainCat._id);
      updatedVideo.categoryId = updatedVideo.category_id;
    }
  }

  // 2. Resolve sub_category_1_id (Sub-Kategori 1)
  if (video.subCategory && updatedVideo.category_id) {
    const cleanSub1 = cleanCatName(video.subCategory);
    const sub1Cat = await db.collection('categories').findOne({
      name: { $regex: new RegExp(`^.*${cleanSub1}.*$`, 'i') },
      parent_id: updatedVideo.category_id
    });
    if (sub1Cat) {
      updatedVideo.sub_category_1_id = String(sub1Cat.id || sub1Cat._id);
      updatedVideo.subCategoryId = updatedVideo.sub_category_1_id;
      updatedVideo.sub_category_id = updatedVideo.sub_category_1_id;
    }
  }

  // 3. Resolve sub_category_2_id (Sub-Kategori 2)
  if (video.subCategory2 && updatedVideo.sub_category_1_id) {
    const cleanSub2 = cleanCatName(video.subCategory2);
    const sub2Cat = await db.collection('categories').findOne({
      name: { $regex: new RegExp(`^.*${cleanSub2}.*$`, 'i') },
      parent_id: updatedVideo.sub_category_1_id
    });
    if (sub2Cat) {
      updatedVideo.sub_category_2_id = String(sub2Cat.id || sub2Cat._id);
      updatedVideo.subCategory2Id = updatedVideo.sub_category_2_id;
    }
  }

  return updatedVideo;
}

// Catch-all API handler
async function handleRoute(request, { params }) {
  const { path = [] } = await params
  const route = `/${path.join('/')}`
  const method = request.method

  try {
    const db = await connectToMongo()

    // 1. AUTH ROUTES
    if (route === '/auth/register' && method === 'POST') {
      const body = await request.json()
      const { name, email, password } = body

      if (!name || !email || !password) {
        return handleCORS(NextResponse.json({ error: 'Nama, Email, dan Password wajib diisi!' }, { status: 400 }))
      }

      const existingUser = await db.collection('users').findOne({ email })
      if (existingUser) {
        return handleCORS(NextResponse.json({ error: 'Email sudah terdaftar!' }, { status: 400 }))
      }

      const DEFAULT_AVATARS = [
        "https://ik.imagekit.io/shindoranesub/c11d825a820d5a3fc725c0c02fb1d637.jpg",
        "https://ik.imagekit.io/shindoranesub/b109036f0bf49f236b934a70d115fdfc.jpg",
        "https://ik.imagekit.io/shindoranesub/pngegg.png",
        "https://ik.imagekit.io/shindoranesub/sorry.png"
      ];
      const randomAvatar = DEFAULT_AVATARS[Math.floor(Math.random() * DEFAULT_AVATARS.length)];

      const newUser = {
        id: uuidv4(),
        name,
        email,
        password,
        role: 'user',
        avatarUrl: randomAvatar,
        isBanned: false,
        createdAt: new Date()
      }

      await db.collection('users').insertOne(newUser)
      const { password: _, ...userWithoutPassword } = newUser
      return handleCORS(NextResponse.json(userWithoutPassword))
    }

    if (route === '/auth/login' && method === 'POST') {
      const body = await request.json()
      const { email, password, isStaffOnly } = body

      if (!email || !password) {
        return handleCORS(NextResponse.json({ error: 'Email dan password wajib diisi!' }, { status: 400 }))
      }

      const user = await db.collection('users').findOne({ email, password })
      if (!user) {
        return handleCORS(NextResponse.json({ error: 'Email atau password salah!' }, { status: 401 }))
      }

      if (user.isBanned) {
        return handleCORS(NextResponse.json({ error: 'Akun Anda telah dibanned oleh Admin!' }, { status: 403 }))
      }

      if (isStaffOnly && user.role !== 'admin' && user.role !== 'moderator') {
        return handleCORS(NextResponse.json({ error: 'Akses ditolak! Anda bukan Staf/Moderator/Admin.' }, { status: 403 }))
      }

      const { password: _, ...userWithoutPassword } = user
      return handleCORS(NextResponse.json(userWithoutPassword))
    }

    if (route === '/auth/forgot-password' && method === 'POST') {
      const body = await request.json()
      const { email } = body

      if (!email) {
        return handleCORS(NextResponse.json({ error: 'Email wajib diisi!' }, { status: 400 }))
      }

      const user = await db.collection('users').findOne({ email })
      if (!user) {
        return handleCORS(NextResponse.json({ error: 'Email tidak ditemukan!' }, { status: 404 }))
      }

      const settings = await db.collection('settings').findOne({ id: 'site_settings' })
      const credentials = settings?.emailProviderCredentials
      const smtpHost = credentials?.smtpHost || 'mail.shindoranesub.my.id'
      const smtpPort = Number(credentials?.smtpPort || 465)
      const smtpUser = credentials?.smtpUser || 'resend@shindoranesub.my.id'
      const smtpPass = credentials?.smtpPass

      const pinCode = Math.floor(100000 + Math.random() * 900000)

      try {
        await db.collection('users').updateOne(
          { email },
          {
            $set: {
              resetPinCode: pinCode.toString(),
              resetPinExpires: new Date(Date.now() + 15 * 60 * 1000)
            }
          }
        )

        if (!smtpPass) {
          return handleCORS(NextResponse.json({
            success: true,
            message: 'Kode PIN verifikasi telah disimulasikan.',
            pinCode
          }))
        }

        const transporter = nodemailer.createTransport({
          host: smtpHost,
          port: smtpPort,
          secure: smtpPort === 465,
          auth: { user: smtpUser, pass: smtpPass },
          tls: { rejectUnauthorized: false }
        })

        const mailOptions = {
          from: `"ShinDora Nesub" <${smtpUser}>`,
          to: email,
          subject: 'Kode Verifikasi Reset Password - ShinDora Nesub',
          html: `
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <style>
                body {
                  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
                  background-color: #0b0f19;
                  margin: 0;
                  padding: 30px 15px;
                  -webkit-font-smoothing: antialiased;
                }
                .wrapper {
                  max-width: 520px;
                  margin: 0 auto;
                  background: #111827;
                  border: 1px solid #1e293b;
                  border-radius: 16px;
                  overflow: hidden;
                  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
                }
                .header {
                  background: linear-gradient(135deg, #06b6d4 0%, #ec4899 50%, #8b5cf6 100%);
                  padding: 30px 20px;
                  text-align: center;
                }
                .brand-title {
                  color: #ffffff;
                  font-size: 24px;
                  font-weight: 900;
                  letter-spacing: 2px;
                  margin: 0;
                  text-transform: uppercase;
                  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }
                .brand-subtitle {
                  color: rgba(255, 255, 255, 0.9);
                  font-size: 11px;
                  font-weight: 600;
                  letter-spacing: 1px;
                  margin-top: 4px;
                  text-transform: uppercase;
                }
                .content {
                  padding: 32px 28px;
                  color: #cbd5e1;
                  font-size: 14px;
                  line-height: 1.6;
                }
                .greeting {
                  font-size: 16px;
                  color: #f8fafc;
                  margin-bottom: 12px;
                }
                .pin-container {
                  background: #1e293b;
                  border: 1px solid #334155;
                  border-radius: 12px;
                  padding: 20px;
                  text-align: center;
                  margin: 24px 0;
                }
                .pin-label {
                  font-size: 11px;
                  text-transform: uppercase;
                  letter-spacing: 1.5px;
                  color: #94a3b8;
                  font-weight: 700;
                  margin-bottom: 10px;
                }
                .pin-code {
                  font-family: 'Courier New', Courier, monospace;
                  font-size: 36px;
                  font-weight: 800;
                  letter-spacing: 8px;
                  color: #38bdf8;
                  text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
                  margin: 0;
                  padding-left: 8px;
                }
                .alert-box {
                  background: rgba(239, 68, 68, 0.1);
                  border-left: 4px solid #ef4444;
                  padding: 12px 16px;
                  border-radius: 6px;
                  font-size: 12px;
                  color: #fca5a5;
                  margin-bottom: 24px;
                }
                .footer {
                  background: #0f172a;
                  padding: 20px;
                  text-align: center;
                  font-size: 12px;
                  color: #64748b;
                  border-top: 1px solid #1e293b;
                }
              </style>
            </head>
            <body>
              <div class="wrapper">
                <div class="header">
                  <h1 class="brand-title">SHINDORA NESUB</h1>
                  <div class="brand-subtitle">Retro Anime Streaming Platform</div>
                </div>
                <div class="content">
                  <div class="greeting">Halo, <strong>${user.name || 'Kohae'}</strong> 👋</div>
                  <p>Kami menerima permintaan untuk melakukan pengubahan kata sandi akun Anda. Gunakan kode PIN verifikasi di bawah ini untuk melanjutkan:</p>
                  <div class="pin-container">
                    <div class="pin-label">Kode Verifikasi Reset</div>
                    <div class="pin-code">${pinCode}</div>
                  </div>
                  <div class="alert-box">
                    <strong>PENTING:</strong> Kode ini hanya berlaku selama <strong>15 menit</strong>. Jangan berikan kode ini kepada siapa pun demi keamanan akun Anda.
                  </div>
                  <p style="font-size: 12px; color: #64748b; margin-bottom: 0;">Jika Anda tidak merasa meminta reset kata sandi, silakan abaikan email ini secara aman.</p>
                </div>
                <div class="footer">
                  &copy; 2026 <strong>ShinDora Nesub</strong>. All rights reserved.
                </div>
              </div>
            </body>
            </html>
          `
        }

        await transporter.sendMail(mailOptions)

        return handleCORS(NextResponse.json({
          success: true,
          message: 'Kode PIN verifikasi telah dikirim ke email Anda.',
          pinCode
        }))
      } catch (err) {
        console.error('[SMTP Send Error]:', err)
        return handleCORS(NextResponse.json({
          success: true,
          message: 'Kode PIN verifikasi disimulasikan karena masalah SMTP.',
          pinCode
        }))
      }
    }

    if (route === '/auth/reset-password' && method === 'POST') {
      const body = await request.json()
      const { email, pinCode, newPassword } = body

      if (!email || !pinCode || !newPassword) {
        return handleCORS(NextResponse.json({ error: 'Data wajib diisi lengkap!' }, { status: 400 }))
      }

      const user = await db.collection('users').findOne({ email })
      if (!user) {
        return handleCORS(NextResponse.json({ error: 'Email tidak ditemukan!' }, { status: 404 }))
      }

      if (!user.resetPinCode || user.resetPinCode !== pinCode.toString()) {
        return handleCORS(NextResponse.json({ error: 'Kode PIN verifikasi salah!' }, { status: 400 }))
      }

      if (!user.resetPinExpires || new Date() > new Date(user.resetPinExpires)) {
        return handleCORS(NextResponse.json({ error: 'Kode PIN telah kadaluarsa!' }, { status: 400 }))
      }

      await db.collection('users').updateOne(
        { email },
        { 
          $set: { password: newPassword },
          $unset: { resetPinCode: "", resetPinExpires: "" }
        }
      )

      return handleCORS(NextResponse.json({ 
        success: true, 
        message: 'Kata sandi Anda berhasil diperbarui!' 
      }))
    }

    if (route === '/auth/update-avatar' && method === 'POST') {
      const body = await request.json()
      const { userId, avatarUrl } = body

      if (!userId || !avatarUrl) {
        return handleCORS(NextResponse.json({ error: 'ID Pengguna dan Data Avatar wajib dikirim!' }, { status: 400 }))
      }

      await db.collection('users').updateOne({ id: userId }, { $set: { avatarUrl } })
      const updatedUser = await db.collection('users').findOne({ id: userId })
      if (updatedUser) {
        const { password: _, ...userWithoutPassword } = updatedUser
        return handleCORS(NextResponse.json(userWithoutPassword))
      }
      return handleCORS(NextResponse.json({ error: 'Pengguna tidak ditemukan' }, { status: 404 }))
    }

    // 2. SETTINGS ROUTES
    const SENSITIVE_KEYS = [
      'saweriaStreamKey',
      'trakteerStreamKey',
      'takoStreamKey',
      'imagekitPrivateKey',
      'onesignalRestApiKey'
    ];

    function maskSettings(settings) {
      if (!settings) return {};
      const masked = { ...settings };
      SENSITIVE_KEYS.forEach(key => {
        if (masked[key]) {
          masked[key] = '••••••••';
        }
      });
      if (masked.emailProviderCredentials && masked.emailProviderCredentials.smtpPass) {
        masked.emailProviderCredentials = {
          ...masked.emailProviderCredentials,
          smtpPass: '••••••••'
        };
      }
      return masked;
    }

    if (route === '/settings' && method === 'GET') {
      const settings = await db.collection('settings').findOne({ id: 'site_settings' })
      return handleCORS(NextResponse.json(maskSettings(settings) || {}))
    }

    if (route === '/settings' && method === 'POST') {
      const body = await request.json()
      const { _id, ...cleanBody } = body
      
      const existingSettings = await db.collection('settings').findOne({ id: 'site_settings' })
      if (existingSettings) {
        SENSITIVE_KEYS.forEach(key => {
          if (cleanBody[key] === '••••••••' || cleanBody[key] === '********') {
            cleanBody[key] = existingSettings[key];
          }
        });
        if (cleanBody.emailProviderCredentials && 
            (cleanBody.emailProviderCredentials.smtpPass === '••••••••' || 
             cleanBody.emailProviderCredentials.smtpPass === '********')) {
          cleanBody.emailProviderCredentials.smtpPass = existingSettings.emailProviderCredentials?.smtpPass;
        }
      }

      await db.collection('settings').updateOne(
        { id: 'site_settings' },
        { $set: cleanBody },
        { upsert: true }
      )
      const settings = await db.collection('settings').findOne({ id: 'site_settings' })
      return handleCORS(NextResponse.json(maskSettings(settings)))
    }

    if (route === '/imagekit/auth' && method === 'GET') {
      const settings = await db.collection('settings').findOne({ id: 'site_settings' })
      const privateKey = settings?.imagekitPrivateKey
      const publicKey = settings?.imagekitPublicKey

      if (!privateKey || !publicKey) {
        return handleCORS(NextResponse.json({ error: 'Kredensial ImageKit belum dikonfigurasi!' }, { status: 400 }))
      }

      const token = uuidv4()
      const expire = Math.floor(Date.now() / 1000) + 1800

      const crypto = require('crypto')
      const signature = crypto
        .createHmac('sha1', privateKey)
        .update(token + expire.toString())
        .digest('hex')

      return handleCORS(NextResponse.json({
        token,
        expire,
        signature,
        publicKey,
        urlEndpoint: settings?.imagekitUrlEndpoint || ''
      }))
    }

    // 3. VIDEOS ROUTES
    if (route === '/videos' && method === 'GET') {
      const url = new URL(request.url)
      const search = url.searchParams.get('search') || ''
      let category = url.searchParams.get('category') || ''
      const showAll = url.searchParams.get('showAll') === 'true'
      if (category) {
        category = cleanCatName(category)
      }

      // Migration check for video category references
      try {
        const unmigratedVideos = await db.collection('videos').find({
          animeTitle: { $exists: true, $ne: '' },
          category_id: { $exists: false }
        }).toArray();
        if (unmigratedVideos.length > 0) {
          for (const video of unmigratedVideos) {
            const resolved = await resolveCategoryIdsForVideo(db, video);
            const setObj = {};
            if (resolved.category_id) {
              setObj.category_id = resolved.category_id;
              setObj.categoryId = resolved.categoryId;
            }
            if (resolved.sub_category_1_id) {
              setObj.sub_category_1_id = resolved.sub_category_1_id;
              setObj.subCategoryId = resolved.subCategoryId;
              setObj.sub_category_id = resolved.sub_category_id;
            }
            if (resolved.sub_category_2_id) {
              setObj.sub_category_2_id = resolved.sub_category_2_id;
              setObj.subCategory2Id = resolved.subCategory2Id;
            }
            if (Object.keys(setObj).length > 0) {
              await db.collection('videos').updateOne({ id: video.id }, { $set: setObj });
            }
          }
        }
      } catch (migrateErr) {
        console.error('[Category Migration Error]:', migrateErr);
      }

      const query = {}
      const andConditions = []

      const categoryIdParam = url.searchParams.get('category_id') || url.searchParams.get('categoryId')
      const subCategory1IdParam = url.searchParams.get('sub_category_1_id') || url.searchParams.get('subCategory1Id') || url.searchParams.get('sub_category_id') || url.searchParams.get('subCategoryId')
      const subCategory2IdParam = url.searchParams.get('sub_category_2_id') || url.searchParams.get('subCategory2Id')

      if (categoryIdParam) {
        andConditions.push({
          $or: [
            { categoryId: categoryIdParam },
            { category_id: categoryIdParam }
          ]
        })
      }
      if (subCategory1IdParam) {
        andConditions.push({
          $or: [
            { subCategoryId: subCategory1IdParam },
            { sub_category_id: subCategory1IdParam },
            { sub_category_1_id: subCategory1IdParam }
          ]
        })
      }
      if (subCategory2IdParam) {
        andConditions.push({
          $or: [
            { subCategory2Id: subCategory2IdParam },
            { sub_category_2_id: subCategory2IdParam }
          ]
        })
      }

      if (category && category !== 'SEMUA') {
        const cleanCat = cleanCatName(category)
        andConditions.push({
          $or: [
            { animeTitle: { $regex: cleanCat, $options: 'i' } },
            { subCategory: { $regex: cleanCat, $options: 'i' } },
            { sub_category: { $regex: cleanCat, $options: 'i' } },
            { subCategory1: { $regex: cleanCat, $options: 'i' } },
            { sub_category_1: { $regex: cleanCat, $options: 'i' } },
            { subCategory2: { $regex: cleanCat, $options: 'i' } },
            { sub_category_2: { $regex: cleanCat, $options: 'i' } },
            { id: cleanCat },
            { categoryId: cleanCat },
            { category_id: cleanCat },
            { subCategoryId: cleanCat },
            { sub_category_id: cleanCat },
            { subCategory2Id: cleanCat },
            { sub_category_2_id: cleanCat }
          ]
        })
      }

      if (search) {
        const regexSearch = { $regex: new RegExp(search, 'i') }
        andConditions.push({
          $or: [
            { title: regexSearch },
            { slug: regexSearch },
            { animeTitle: regexSearch },
            { episode: regexSearch },
            { id: regexSearch },
            { subCategory: regexSearch },
            { subCategory2: regexSearch }
          ]
        })
      }

      if (andConditions.length > 0) {
        query.$and = andConditions
      }

      if (!showAll) {
        const now = new Date()
        const nowStr = now.toISOString()
        const publicFilter = {
          $or: [
            { status: { $exists: false } },
            { status: "published" },
            { 
              $and: [
                { status: "scheduled" },
                { 
                  $or: [
                    { scheduledAt: { $lte: nowStr } },
                    { scheduledAt: { $lte: now } }
                  ]
                }
              ]
            }
          ]
        }
        
        if (query.$or) {
          const existingOr = query.$or
          delete query.$or
          query.$and = [
            { $or: existingOr },
            publicFilter
          ]
        } else {
          query.$and = query.$and ? [...query.$and, publicFilter] : [publicFilter]
        }
      }

      const videos = await db.collection('videos').find(query).sort({ createdAt: -1 }).toArray()
      return handleCORS(NextResponse.json(videos))
    }

    if (route === '/videos' && method === 'POST') {
      const body = await request.json()
      
      const computedSlug = body.slug && body.slug.trim() !== '' 
        ? generateSlug(body.slug) 
        : generateSlug(body.title)

      let newVideo = {
        ...body,
        id: uuidv4(),
        title: body.title?.trim() || body.title,
        animeTitle: body.animeTitle?.trim() || body.animeTitle,
        episode: body.episode?.trim() || body.episode,
        description: body.description?.trim() || body.description,
        thumbnailUrl: body.thumbnailUrl?.trim() || body.thumbnailUrl,
        videoUrl: body.videoUrl?.trim() || body.videoUrl,
        videoUrl2: body.videoUrl2?.trim() || body.videoUrl2,
        videoUrl3: body.videoUrl3?.trim() || body.videoUrl3,
        slug: computedSlug,
        status: body.status || 'published',
        scheduledAt: body.scheduledAt || null,
        views: Number(body.views || 0),
        likes: Number(body.likes || 0),
        createdAt: new Date()
      }
      
      newVideo = await resolveCategoryIdsForVideo(db, newVideo)
      await db.collection('videos').insertOne(newVideo)
      if (newVideo.status === 'published') {
        await triggerOneSignalNotification(db, newVideo)
      }
      return handleCORS(NextResponse.json(newVideo))
    }

    if (route === '/videos/toggle-like' && method === 'POST') {
      const body = await request.json()
      const { id, action } = body
      if (!action || (action !== 'like' && action !== 'unlike')) {
        return handleCORS(NextResponse.json({ error: 'Aksi tidak valid! Harus "like" atau "unlike"' }, { status: 400 }))
      }
      const incVal = action === 'like' ? 1 : -1
      const video = await db.collection('videos').findOne({ $or: [{ id }, { slug: id }] })
      if (video) {
        const newLikes = Math.max(0, (video.likes || 0) + incVal)
        await db.collection('videos').updateOne({ id: video.id }, { $set: { likes: newLikes } })
        const updated = await db.collection('videos').findOne({ id: video.id })
        return handleCORS(NextResponse.json(updated))
      }
      return handleCORS(NextResponse.json({ error: 'Video tidak ditemukan!' }, { status: 404 }))
    }

    if (route === '/videos/increment-views' && method === 'POST') {
      const body = await request.json()
      const { id } = body
      const video = await db.collection('videos').findOne({ $or: [{ id }, { slug: id }] })
      if (video) {
        await db.collection('videos').updateOne({ id: video.id }, { $inc: { views: 1 } })
        const updated = await db.collection('videos').findOne({ id: video.id })
        return handleCORS(NextResponse.json(updated))
      }
      return handleCORS(NextResponse.json({ error: 'Video tidak ditemukan!' }, { status: 404 }))
    }

    if (route === '/videos' && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body

      if (updateData.slug || updateData.title) {
        updateData.slug = updateData.slug && updateData.slug.trim() !== '' 
          ? generateSlug(updateData.slug) 
          : generateSlug(updateData.title)
      }

      const resolvedData = await resolveCategoryIdsForVideo(db, updateData)
      await db.collection('videos').updateOne({ id }, { $set: resolvedData })
      const updated = await db.collection('videos').findOne({ id })
      if (updated && updated.status === 'published') {
        await triggerOneSignalNotification(db, updated)
      }
      return handleCORS(NextResponse.json(updated))
    }

    if (route === '/videos' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')

      const video = await db.collection('videos').findOne({ id })
      if (video && video.thumbnailUrl) {
        const settings = await db.collection('settings').findOne({ id: 'site_settings' })
        if (settings?.imagekitPrivateKey) {
          await deleteImageKitFileByUrl(video.thumbnailUrl, settings.imagekitPrivateKey)
        }
      }

      await db.collection('videos').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    if (route === '/videos/bulk-csv' && method === 'POST') {
      const body = await request.json()
      const { csvData } = body
      if (!csvData) {
        return handleCORS(NextResponse.json({ error: 'Data CSV kosong!' }, { status: 400 }))
      }

      const lines = csvData.split('\n')
      const imported = []
      for (const line of lines) {
        if (!line.trim()) continue
        const parts = line.split(',')
        if (parts.length < 5) continue

        const [title, animeTitle, episode, thumbnailUrl, videoUrl, ...descParts] = parts
        const description = descParts.join(',') || ''

        const cleanTitle = title.trim()
        let newVideo = {
          id: uuidv4(),
          title: cleanTitle,
          slug: generateSlug(cleanTitle),
          animeTitle: animeTitle.trim(),
          episode: episode.trim(),
          thumbnailUrl: thumbnailUrl.trim(),
          videoUrl: videoUrl.trim(),
          description: description.trim(),
          views: 0,
          likes: 0,
          createdAt: new Date()
        }
        newVideo = await resolveCategoryIdsForVideo(db, newVideo)
        await db.collection('videos').insertOne(newVideo)
        imported.push(newVideo)
      }

      return handleCORS(NextResponse.json({ success: true, count: imported.length, imported }))
    }

    // 4. CATEGORIES ROUTES
    if (route === '/categories' && method === 'GET') {
      const categories = await db.collection('categories').find({}).toArray()
      return handleCORS(NextResponse.json(categories))
    }

    if (route === '/categories' && method === 'POST') {
      const body = await request.json()
      const newCategory = {
        name: body.name ? body.name.trim() : '',
        parent_id: body.parent_id === 'none' || !body.parent_id ? null : String(body.parent_id),
        id: uuidv4(),
        createdAt: new Date()
      }
      await db.collection('categories').insertOne(newCategory)
      return handleCORS(NextResponse.json(newCategory))
    }

    if (route === '/categories' && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body
      if (updateData.parent_id === 'none' || !updateData.parent_id) {
        updateData.parent_id = null
      } else {
        updateData.parent_id = String(updateData.parent_id)
      }
      if (updateData.name) {
        updateData.name = updateData.name.trim()
      }
      await db.collection('categories').updateOne({ id }, { $set: updateData })
      const updated = await db.collection('categories').findOne({ id })
      return handleCORS(NextResponse.json(updated))
    }

    if (route === '/categories' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      if (id) {
        await db.collection('categories').deleteOne({ id })
        // Hapus atau reset relasi anak (Sub-Kategori 1 / Sub-Kategori 2) yang menggunakan ID ini sebagai parent
        await db.collection('categories').updateMany({ parent_id: String(id) }, { $set: { parent_id: null } })
      }
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 5. USERS MANAGEMENT ROUTES
    if (route === '/users' && method === 'GET') {
      const url = new URL(request.url)
      const search = url.searchParams.get('search') || ''
      const query = {}
      if (search) {
        query.$or = [
          { name: { $regex: new RegExp(search, 'i') } },
          { email: { $regex: new RegExp(search, 'i') } }
        ]
      }
      const users = await db.collection('users').find(query).toArray()
      const safeUsers = users.map(({ password, ...rest }) => rest)
      return handleCORS(NextResponse.json(safeUsers))
    }

    if (route === '/users' && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body
      await db.collection('users').updateOne({ id }, { $set: updateData })
      const updated = await db.collection('users').findOne({ id })
      return handleCORS(NextResponse.json(updated))
    }

    if (route === '/users' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      await db.collection('users').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 6. PLAYLISTS ROUTES
    if (route === '/playlists' && method === 'GET') {
      const url = new URL(request.url)
      const userId = url.searchParams.get('userId')
      const search = url.searchParams.get('search') || ''

      const query = {
        $or: [
          { ownerId: null },
          ...(userId ? [{ ownerId: userId }] : [])
        ]
      }

      if (search) {
        query.title = { $regex: new RegExp(search, 'i') }
      }

      const playlists = await db.collection('playlists').find(query).toArray()
      return handleCORS(NextResponse.json(playlists))
    }

    if (route === '/playlists' && method === 'POST') {
      const body = await request.json()
      const newPlaylist = {
        id: uuidv4(),
        title: body.title,
        ownerId: body.ownerId || null,
        videoIds: body.videoIds || [],
        isPrivate: body.isPrivate === undefined ? true : body.isPrivate,
        createdAt: new Date()
      }
      await db.collection('playlists').insertOne(newPlaylist)
      return handleCORS(NextResponse.json(newPlaylist))
    }

    if (route === '/playlists' && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body
      await db.collection('playlists').updateOne({ id }, { $set: updateData })
      const updated = await db.collection('playlists').findOne({ id })
      return handleCORS(NextResponse.json(updated))
    }

    if (route === '/playlists' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      await db.collection('playlists').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 7. COMMENTS & NOTIFICATIONS ROUTES
    if (route === '/comments' && method === 'GET') {
      const url = new URL(request.url)
      const videoId = url.searchParams.get('videoId')
      const search = url.searchParams.get('search') || ''
      const filterEpisode = url.searchParams.get('filterEpisode') || ''

      const query = {}
      if (videoId) {
        const video = await db.collection('videos').findOne({ $or: [{ id: videoId }, { slug: videoId }] })
        if (video) {
          query.videoId = video.id
        } else {
          query.videoId = videoId
        }
      }
      if (search) {
        query.content = { $regex: new RegExp(search, 'i') }
      }

      let comments = await db.collection('comments').find(query).toArray()

      if (filterEpisode && filterEpisode !== 'ALL') {
        comments = comments.filter(c => c.videoId === filterEpisode)
      }

      return handleCORS(NextResponse.json(comments))
    }

    if (route === '/comments' && method === 'POST') {
      const body = await request.json()
      const newComment = {
        id: uuidv4(),
        videoId: body.videoId,
        userId: body.userId,
        userName: body.userName,
        userAvatar: body.userAvatar || 'https://ik.imagekit.io/shindoranesub/c11d825a820d5a3fc725c0c02fb1d637.jpg',
        content: body.content,
        parentId: body.parentId || null,
        createdAt: new Date()
      }
      await db.collection('comments').insertOne(newComment)

      if (body.parentId) {
        const parentComment = await db.collection('comments').findOne({ id: body.parentId })
        if (parentComment && parentComment.userId !== body.userId) {
          const video = await db.collection('videos').findOne({ $or: [{ id: body.videoId }, { slug: body.videoId }] })
          const notification = {
            id: uuidv4(),
            userId: parentComment.userId,
            senderName: body.userName,
            senderAvatar: body.userAvatar || '',
            contentSnippet: body.content.length > 50 ? body.content.substring(0, 50) + '...' : body.content,
            animeTitle: video ? video.animeTitle : 'Anime',
            episodeTitle: video ? video.title : 'Episode',
            videoId: body.videoId,
            isRead: false,
            createdAt: new Date()
          }
          await db.collection('notifications').insertOne(notification)
        }
      }

      return handleCORS(NextResponse.json(newComment))
    }

    if (route === '/comments' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')

      if (!id) {
        return handleCORS(NextResponse.json({ error: 'Comment ID is required' }, { status: 400 }))
      }

      const allComments = await db.collection('comments').find({}).toArray()
      
      const idsToDelete = [id]
      const getChildrenIds = (parentId) => {
        allComments.forEach(c => {
          if (c.parentId === parentId) {
            idsToDelete.push(c.id)
            getChildrenIds(c.id)
          }
        })
      }
      
      getChildrenIds(id)

      await db.collection('comments').deleteMany({ id: { $in: idsToDelete } })
      return handleCORS(NextResponse.json({ success: true, deletedCount: idsToDelete.length }))
    }

    if (route === '/notifications' && method === 'GET') {
      const url = new URL(request.url)
      const userId = url.searchParams.get('userId')
      if (!userId) {
        return handleCORS(NextResponse.json([]))
      }
      const notifications = await db.collection('notifications')
        .find({ userId })
        .sort({ createdAt: -1 })
        .limit(20)
        .toArray()
      return handleCORS(NextResponse.json(notifications))
    }

    if (route === '/notifications' && method === 'PUT') {
      const body = await request.json()
      const { id, userId, markAll } = body

      if (markAll && userId) {
        await db.collection('notifications').updateMany({ userId }, { $set: { isRead: true } })
        return handleCORS(NextResponse.json({ success: true }))
      }

      if (id) {
        await db.collection('notifications').updateOne({ id }, { $set: { isRead: true } })
        return handleCORS(NextResponse.json({ success: true }))
      }

      return handleCORS(NextResponse.json({ error: 'Invalid payload' }, { status: 400 }))
    }

    if (route === '/notifications' && method === 'DELETE') {
      const url = new URL(request.url)
      const userId = url.searchParams.get('userId')
      if (!userId) {
        return handleCORS(NextResponse.json({ error: 'User ID required' }, { status: 400 }))
      }
      await db.collection('notifications').deleteMany({ userId })
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 8. ADS ROUTES
    if ((route === '/ads' || route === '/promo' || route === '/promotions') && method === 'GET') {
      const ads = await db.collection('ads').find({}).toArray()
      return handleCORS(NextResponse.json(ads))
    }

    if ((route === '/ads' || route === '/promo' || route === '/promotions') && method === 'POST') {
      const body = await request.json()
      const newAd = {
        ...body,
        id: uuidv4(),
        isActive: body.isActive === undefined ? true : body.isActive
      }
      await db.collection('ads').insertOne(newAd)
      return handleCORS(NextResponse.json(newAd))
    }

    if ((route === '/ads' || route === '/promo' || route === '/promotions') && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body
      await db.collection('ads').updateOne({ id }, { $set: updateData })
      const updated = await db.collection('ads').findOne({ id })
      return handleCORS(NextResponse.json(updated))
    }

    if ((route === '/ads' || route === '/promo' || route === '/promotions') && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      await db.collection('ads').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 9. PAGES ROUTES
    if (route === '/pages' && method === 'GET') {
      const pages = await db.collection('pages').find({}).toArray()
      return handleCORS(NextResponse.json(pages))
    }

    if (route === '/pages' && method === 'POST') {
      const body = await request.json()
      const newPage = {
        ...body,
        id: uuidv4(),
        createdAt: new Date()
      }
      await db.collection('pages').insertOne(newPage)
      return handleCORS(NextResponse.json(newPage))
    }

    if (route === '/pages' && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body
      await db.collection('pages').updateOne({ id }, { $set: updateData })
      const updated = await db.collection('pages').findOne({ id })
      return handleCORS(NextResponse.json(updated))
    }

    if (route === '/pages' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      await db.collection('pages').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 10. DONATIONS & WEBHOOKS ROUTES
    if (route === '/donations' && method === 'GET') {
      const donations = await db.collection('donations').find({}).sort({ createdAt: -1 }).toArray()
      return handleCORS(NextResponse.json(donations))
    }

    if (route === '/donations' && method === 'POST') {
      const body = await request.json()
      const newDonation = {
        id: uuidv4(),
        name: body.name || body.donatorName || 'Donatur',
        amount: body.amount || 'Rp 0',
        message: body.message || '',
        platform: body.platform || 'Saweria',
        createdAt: new Date()
      }
      await db.collection('donations').insertOne(newDonation)
      return handleCORS(NextResponse.json(newDonation))
    }

    if (route === '/donations' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      await db.collection('donations').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    if (route === '/webhooks/poll' && method === 'GET') {
      const latestDonations = await db.collection('donations').find({}).sort({ createdAt: -1 }).limit(5).toArray()
      return handleCORS(NextResponse.json(latestDonations))
    }

    if (route === '/webhooks/saweria' && method === 'POST') {
      const body = await request.json()
      const rawAmount = body.amount || 0
      const amountStr = typeof rawAmount === 'number'
        ? `Rp ${rawAmount.toLocaleString('id-ID')}`
        : rawAmount
      
      const newDonation = {
        id: uuidv4(),
        name: body.donator_name || body.name || 'Donatur Saweria',
        amount: amountStr,
        message: body.message || '',
        platform: 'Saweria',
        createdAt: new Date()
      }
      await db.collection('donations').insertOne(newDonation)
      return handleCORS(NextResponse.json({ success: true, donation: newDonation }))
    }

    if (route === '/webhooks/trakteer' && method === 'POST') {
      const body = await request.json()
      const rawAmount = body.amount || 0
      const amountStr = typeof rawAmount === 'number'
        ? `Rp ${rawAmount.toLocaleString('id-ID')}`
        : rawAmount

      const newDonation = {
        id: uuidv4(),
        name: body.donator_name || body.name || 'Donatur Trakteer',
        amount: amountStr,
        message: body.message || '',
        platform: 'Trakteer',
        createdAt: new Date()
      }
      await db.collection('donations').insertOne(newDonation)
      return handleCORS(NextResponse.json({ success: true, donation: newDonation }))
    }

    if (route === '/webhooks/tako' && method === 'POST') {
      const body = await request.json()
      const rawAmount = body.amount || 0
      const amountStr = typeof rawAmount === 'number'
        ? `Rp ${rawAmount.toLocaleString('id-ID')}`
        : rawAmount

      const newDonation = {
        id: uuidv4(),
        name: body.donator_name || body.name || 'Donatur Tako.id',
        amount: amountStr,
        message: body.message || '',
        platform: 'Tako.id',
        createdAt: new Date()
      }
      await db.collection('donations').insertOne(newDonation)
      return handleCORS(NextResponse.json({ success: true, donation: newDonation }))
    }

    // 11. POLLING & VOTING ROUTES
    if (route === '/polling' && method === 'GET') {
      const polling = await db.collection('polling').find({}).toArray()
      return handleCORS(NextResponse.json(polling))
    }

    if (route === '/polling' && method === 'POST') {
      const body = await request.json()
      const newPoll = {
        id: uuidv4(),
        title: body.title || 'Vote Terbaru',
        options: body.options || [],
        ownerId: body.ownerId || null,
        isActive: body.isActive === undefined ? true : body.isActive,
        createdAt: new Date()
      }
      await db.collection('polling').insertOne(newPoll)
      return handleCORS(NextResponse.json(newPoll))
    }

    if (route === '/polling/vote' && method === 'POST') {
      const body = await request.json()
      const { pollId, optionId, userId } = body

      if (!pollId || !optionId) {
        return handleCORS(NextResponse.json({ error: 'Poll ID dan Option ID wajib dikirim!' }, { status: 400 }))
      }

      if (userId) {
        const existingVote = await db.collection('user_votes').findOne({ pollId, userId })
        if (existingVote) {
          return handleCORS(NextResponse.json({ error: 'Anda sudah memberikan suara untuk polling ini!' }, { status: 400 }))
        }
      }

      const poll = await db.collection('polling').findOne({ id: pollId })
      if (!poll) {
        return handleCORS(NextResponse.json({ error: 'Polling tidak ditemukan' }, { status: 404 }))
      }

      const updatedOptions = poll.options.map(opt => {
        if (opt.id === optionId) {
          return { ...opt, votes: (opt.votes || 0) + 1 }
        }
        return opt
      })

      if (userId) {
        await db.collection('user_votes').insertOne({
          id: uuidv4(),
          pollId,
          userId,
          optionId,
          createdAt: new Date()
        })
      }

      await db.collection('polling').updateOne({ id: pollId }, { $set: { options: updatedOptions } })
      const updatedPoll = await db.collection('polling').findOne({ id: pollId })
      return handleCORS(NextResponse.json(updatedPoll))
    }

    if (route === '/polling' && method === 'PUT') {
      const body = await request.json()
      const { id, _id, ...updateData } = body
      await db.collection('polling').updateOne({ id }, { $set: updateData })
      const updated = await db.collection('polling').findOne({ id })
      return handleCORS(NextResponse.json(updated))
    }

    if (route === '/polling' && method === 'DELETE') {
      const url = new URL(request.url)
      const id = url.searchParams.get('id')
      await db.collection('polling').deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    // 12. GLOBAL PUBLIC CHAT ROUTES
    if (route === '/chat' && method === 'GET') {
      const messages = await db.collection('global_chat')
        .find({})
        .sort({ createdAt: -1 })
        .limit(100)
        .toArray()
      
      return handleCORS(NextResponse.json(messages.reverse()))
    }

    if (route === '/chat' && method === 'POST') {
      const body = await request.json()
      const { userName, userAvatar, content } = body

      if (!content || !content.trim()) {
        return handleCORS(NextResponse.json({ error: 'Konten pesan wajib diisi!' }, { status: 400 }))
      }

      const settingsObj = await db.collection('settings').findOne({ id: 'site_settings' })
      const blockedWordsStr = settingsObj?.blocked_words || settingsObj?.blockedWords || "anjing, babi, bangsat, anjrit, fuck, shit, kontol, memek, asu, bajingan"
      
      const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

      const censorText = (text, listStr) => {
        if (!text) return ''
        const words = listStr.split(',').map(w => w.trim()).filter(Boolean)
        let censored = text
        words.forEach(word => {
          const escaped = escapeRegExp(word)
          const regex = new RegExp(`\\b${escaped}\\b|${escaped}`, 'gi')
          censored = censored.replace(regex, '*'.repeat(word.length))
        })
        return censored
      }

      const cleanContent = censorText(content, blockedWordsStr)

      const newMsg = {
        id: uuidv4(),
        userName: userName || 'Pengguna',
        userAvatar: userAvatar || 'https://ik.imagekit.io/shindoranesub/c11d825a820d5a3fc725c0c02fb1d637.jpg',
        content: cleanContent.trim(),
        createdAt: new Date()
      }

      await db.collection('global_chat').insertOne(newMsg)
      return handleCORS(NextResponse.json(newMsg))
    }

    // 13. CUSTOM EMOTES ROUTES
    if (route === "/emotes" && method === "GET") {
      const emotes = await db.collection("emotes").find({}).toArray()
      return handleCORS(NextResponse.json(emotes))
    }

    if (route === "/emotes" && method === "POST") {
      const body = await request.json()
      const { code, imageUrl } = body

      if (!code || !code.trim() || !imageUrl || !imageUrl.trim()) {
        return handleCORS(NextResponse.json({ error: "Kode shortcode dan URL wajib diisi!" }, { status: 400 }))
      }

      let formattedCode = code.trim()
      if (!formattedCode.startsWith(":")) formattedCode = ":" + formattedCode
      if (!formattedCode.endsWith(":")) formattedCode = formattedCode + ":"

      const existing = await db.collection("emotes").findOne({ code: formattedCode })
      if (existing) {
        return handleCORS(NextResponse.json({ error: "Kode shortcode tersebut sudah digunakan!" }, { status: 400 }))
      }

      const newEmote = {
        id: uuidv4(),
        code: formattedCode,
        imageUrl: imageUrl.trim(),
        createdAt: new Date()
      }

      await db.collection("emotes").insertOne(newEmote)
      return handleCORS(NextResponse.json(newEmote))
    }

    if (route === "/emotes" && method === "DELETE") {
      const url = new URL(request.url)
      const id = url.searchParams.get("id")
      if (!id) {
        return handleCORS(NextResponse.json({ error: "ID wajib dilampirkan!" }, { status: 400 }))
      }
      await db.collection("emotes").deleteOne({ id })
      return handleCORS(NextResponse.json({ success: true }))
    }

    return handleCORS(NextResponse.json({ error: `Route ${route} not found` }, { status: 404 }))

  } catch (error) {
    console.error('API Error:', error)
    return handleCORS(NextResponse.json({ error: "Internal server error: " + error.message }, { status: 500 }))
  }
}

export const GET = handleRoute
export const POST = handleRoute
export const PUT = handleRoute
export const DELETE = handleRoute
export const PATCH = handleRoute
