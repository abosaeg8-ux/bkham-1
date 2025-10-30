from asyncio import run, sleep, gather
from typing import Dict, Any, List, Union
from aminodorksfix.asyncfix import Client, SubClient
from keep_alive import keep_alive  # ✅ استدعاء الأداة
import random

# --- ⚙️ الإعدادات الأساسية ---
API_KEY = "1bd49e6563fb5b744a999b6c050197a9"
EMAIL = "abosaeg10@gmail.com"
PASSWORD = "foo40k"
TARGET_COMMUNITY_LINK = "http://aminoapps.com/c/anime-empire-1"

# --- 💬 إعدادات العشوائية والتكرار ---
RANDOM_COMMENTS = [
    "هههههه", "يرجال", "هففف", "اها", "شايفك",
    "امااا", "...", "جاري التفكير", "غريب", "وش ذا",
    "قوي!", "طيب", "بفكر", "ممتاز", "واو"
]
MAX_INTERACTION_RETRIES = 3
LAST_KNOWN_POST_ID = None


# --- 🎨 تنسيق المخرجات ---
def colorize(text: str, status: str) -> str:
    return f"\033[94m[\033[0m{status}\033[94m] \033[0m{text}\033[94m"


# --- 🔒 تسجيل الدخول ---
async def login(client: Client) -> None:
    if not all([API_KEY, EMAIL, PASSWORD]):
        raise ValueError("Missing Credentials")

    try:
        print(colorize("جارٍ محاولة تسجيل الدخول...", "*"))
        await client.login(EMAIL, PASSWORD)
        print(colorize("تم تسجيل الدخول بنجاح! 🚀", "+"))
    except Exception as e:
        print(f"\033[0;31m[LoginError]: فشل تسجيل الدخول: {e}\033[0m")
        raise e


# --- ❤️‍🔥 التفاعل مع منشور (إعجاب + تعليق عشوائي) ---
async def interact_with_post(sub_client: SubClient, primary_id: str, post_type: str,
                             post_data: Dict[str, Any],
                             max_retries: int = MAX_INTERACTION_RETRIES) -> None:

    comment_text = random.choice(RANDOM_COMMENTS)
    blog_id = post_data.get("blogId")
    object_id = post_data.get("objectId") or blog_id

    async def attempt_interaction_logic(current_attempt: int):
        # إعجاب
        if post_data.get("type") in [2, 3]:
            await sub_client.like_wiki(objectId=object_id)
        else:
            await sub_client.like_blog(blogId=blog_id)

        print(colorize(f"تم الإعجاب (المحاولة {current_attempt}) على {post_type}: {primary_id}", "👍"))

        # تعليق
        await sub_client.comment(message=comment_text, blogId=blog_id or object_id)
        print(colorize(f"تم التعليق (المحاولة {current_attempt}) على {post_type}: {primary_id} — '{comment_text}'", "💬"))
        return True

    for attempt in range(max_retries):
        try:
            await attempt_interaction_logic(attempt + 1)
            return
        except Exception as e:
            error_msg = str(e)
            if "already been liked" in error_msg or "Comment has already been created" in error_msg:
                print(colorize(f"تم التفاعل مسبقاً مع {primary_id}. تم التخطي.", "-"))
                return
            print(f"\033[0;33m[Retry]: فشل التفاعل مع {primary_id} ({attempt + 1}/{max_retries}): {error_msg}\033[0m")
            await sleep(1)

    print(f"\033[0;31m[Skip-Failed]: فشل التفاعل مع {primary_id} بعد {max_retries} محاولات.\033[0m")


# --- 🔄 مراقبة المجتمع ---
async def monitor_community(sub_client: SubClient, target_com_id: str) -> None:
    global LAST_KNOWN_POST_ID

    while True:
        print("\n" + colorize("جاري فحص أحدث 5 منشورات...", "*"))
        try:
            blogs_response = await sub_client.get_recent_blogs(start=0, size=5)
            response_json: Union[Dict[str, Any], List[Dict[str, Any]]] = blogs_response.json
            posts: List[Dict[str, Any]] = response_json.get("blogList", []) if isinstance(response_json, dict) else response_json

            if not posts:
                print(colorize("لا توجد منشورات حديثة.", "-"))
                await sleep(5)
                continue

            current_latest_post_id = posts[0].get("blogId") or posts[0].get("objectId")

            if LAST_KNOWN_POST_ID is None:
                LAST_KNOWN_POST_ID = current_latest_post_id
                print(colorize(f"تم تسجيل أول معرّف: {LAST_KNOWN_POST_ID}", "✓"))

            elif current_latest_post_id != LAST_KNOWN_POST_ID:
                new_posts_tasks = []
                for post in posts:
                    post_id = post.get("blogId") or post.get("objectId")
                    if post_id == LAST_KNOWN_POST_ID:
                        break
                    post_type = "Wiki" if post.get("type") == 2 else "Blog/Post"
                    print(colorize(f"منشور جديد: {post_id}", "🆕"))
                    new_posts_tasks.append(interact_with_post(sub_client, post_id, post_type, post))

                LAST_KNOWN_POST_ID = current_latest_post_id

                if new_posts_tasks:
                    print(colorize(f"عدد المنشورات الجديدة: {len(new_posts_tasks)} — جاري التفاعل...", "⚡"))
                    await gather(*new_posts_tasks)
                else:
                    print(colorize("تمت معالجة جميع المنشورات الجديدة.", "-"))
            else:
                print(colorize("لا يوجد جديد حالياً. 😴", "-"))

        except Exception as e:
            print(f"\033[0;31m[MonitorError]: {e}\033[0m")

        print(colorize("الانتظار 5 ثوانٍ قبل الفحص التالي...", "⏳"))
        await sleep(5)


# --- 🏁 التشغيل الرئيسي ---
async def main():
    keep_alive()  # ✅ تشغيل الأداة قبل البدء
    client = Client(api_key=API_KEY, socket_enabled=False)

    try:
        await login(client)
    except Exception:
        return

    print(colorize("جاري تحليل رابط المجتمع...", "*"))
    try:
        link_data = await client.get_from_code(TARGET_COMMUNITY_LINK)
        target_com_id = getattr(link_data, 'comId', None)
        if not target_com_id:
            print("\033[0;31m[FATAL]: لم يتم العثور على ComId.\033[0m")
            return
    except Exception as e:
        print(f"\033[0;31m[FATAL]: فشل تحليل الرابط: {e}\033[0m")
        return

    sub_client = SubClient(comId=target_com_id, profile=client.profile)
    print(colorize(f"بدء المراقبة للمجتمع: {target_com_id}", "✅"))
    await monitor_community(sub_client, target_com_id)


if __name__ == "__main__":
    try:
        run(main())
    except Exception as e:
        print(f"\033[0;31m[TERMINATED]: خطأ حاسم: {e}\033[0m")

