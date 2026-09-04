#!/usr/bin/env python3
import os

def update_env_file():
    env_path = "/app/.env"
    if not os.path.exists(env_path):
        print(".env not found")
        return False
        
    with open(env_path, "r") as f:
        content = f.read()

    # Append new variables if they do not exist
    new_vars = []
    if "NEXT_PUBLIC_ONESIGNAL_APP_ID" not in content:
        new_vars.append("NEXT_PUBLIC_ONESIGNAL_APP_ID=5c15e8c1-d41c-4fe8-ab53-347e5410e060")
    if "ONESIGNAL_REST_API_KEY" not in content:
        new_vars.append("ONESIGNAL_REST_API_KEY=onesignal-rest-key-123")

    if new_vars:
        with open(env_path, "a") as f:
            f.write("\n" + "\n".join(new_vars) + "\n")
        print("✓ env: OneSignal keys appended successfully")
    else:
        print("✓ env: OneSignal keys already exist")
    return True

def edit_route_onesignal():
    route_path = "/app/app/api/[[...path]]/route.js"
    if not os.path.exists(route_path):
        print("route.js not found")
        return False
        
    with open(route_path, "r") as f:
        content = f.read()

    old_payload = """    const payload = {
      app_id: onesignalAppId,
      included_segments: ["Subscribed Users"],
      headings: { en: "Episode Baru Dirilis! 🎬" },
      contents: { en: `${video.title} - ${video.episode || ""} telah rilis. Yuk tonton sekarang!` },
      big_picture: video.thumbnailUrl,
      url: `${baseUrl}/watch/${video.slug}`
    }"""

    new_payload = """    const payload = {
      app_id: onesignalAppId,
      included_segments: ["Subscribed Users"],
      headings: { en: `Episode Baru: ${video.animeTitle || "Retro Anime"} 🎬` },
      contents: { en: `Tonton ${video.title} (${video.episode || "Eps 1"}) sekarang!` },
      big_picture: video.thumbnailUrl,
      url: `${baseUrl}/watch/${video.slug}`
    }"""

    if old_payload in content:
        content = content.replace(old_payload, new_payload)
        print("✓ route: OneSignal payload updated with explicit animeTitle and episode")
    else:
        print("✗ route: OneSignal payload block not matched")

    with open(route_path, "w") as f:
        f.write(content)
    return True

if __name__ == "__main__":
    update_env_file()
    edit_route_onesignal()
    print("SUCCESS: OneSignal integration finalized!")
