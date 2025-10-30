# -*- coding: utf-8 -*-
from asyncio import run, sleep, gather
from aminodorksfix.asyncfix import Client, SubClient
from keep_alive import keep_alive  # 🔗 ربط مع الأداة

# -------------------- الإعدادات --------------------
API_KEY = "1bd49e6563fb5b744a999b6c050197a9"
EMAIL = "abosaeg6@gmail.com"
PASSWORD = "abosaeg@1"
LINK = "http://aminoapps.com/c/anime-empire-1"
LAST_ID = None
TYPES = {1: "مدونة", 2: "ويكي", 3: "اختبار", 4: "سؤال", 5: "رابط"}
# ---------------------------------------------------

def c(t, s): 
    return f"\033[94m[\033[0m{s}\033[94m] \033[0m{t}\033[94m"

async def login(cn):
    print(c("تسجيل الدخول...", "*"))
    await cn.login(EMAIL, PASSWORD)
    print(c("تم الدخول بنجاح!", "+"))

async def like(sub, pid, pt):
    for _ in range(3):
        try:
            await sub.like_blog(blogId=pid)
            print(c(f"اعجاب على {pt} {pid}", "👍"))
            return
        except Exception as e:
            print(c(f"فشل {pid}: {e}", "-"))
            await sleep(1)

async def monitor(sub, com):
    global LAST_ID
    liked_ids = set()  # 🧠 لمنع تكرار الإعجابات

    while True:
        try:
            r = await sub.get_recent_blogs(start=0, size=10)
            data = r.json
            posts = (data.get("blogList") if isinstance(data, dict) else data) or []

            if not posts:
                await sleep(5)
                continue

            nid = posts[0].get("blogId")

            if LAST_ID is None:
                LAST_ID = nid
                print(c("بدء المراقبة...", "✓"))

            elif nid != LAST_ID:
                tasks = []
                for p in posts:
                    pid = p.get("blogId")
                    if pid == LAST_ID or pid in liked_ids:
                        continue

                    if p.get("isLiked"):
                        liked_ids.add(pid)
                        continue

                    pt = TYPES.get(p.get("type", 1), "غير معروف")
                    print(c(f"جديد {pt}: {pid}", "🆕"))
                    tasks.append(like(sub, pid, pt))
                    liked_ids.add(pid)

                LAST_ID = nid
                if tasks:
                    await gather(*tasks)

        except Exception as e:
            print(c(f"خطأ: {e}", "!"))

        await sleep(5)

async def main():
    keep_alive()  # 🚀 إبقاء السيرفر شغال
    c1 = Client(api_key=API_KEY, socket_enabled=False)
    await login(c1)
    l = await c1.get_from_code(LINK)
    com = getattr(l, "comId", None)
    if not com:
        return print("❌ فشل解析 الرابط")
    sub = SubClient(comId=com, profile=c1.profile)
    print(c(f"بدء الإعجابات للمجتمع {com}", "✅"))
    await monitor(sub, com)

if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        print(f"\033[0;31mخطأ: {e}\033[0m")
