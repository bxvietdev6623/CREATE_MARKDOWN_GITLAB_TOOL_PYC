import os
import re
import datetime
import random
import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import zipfile
import io

app = Flask(__name__)
CORS(app)


FIXED_APPS = [
    "91视频", "台湾Swag", "Porn高清", "Pornbest", "Pornhub", "tiktok成人版",
    "50度灰", "黄瓜视频", "香蕉视频", "樱桃视频", "蜜桃视频", "幸福宝",
    "中国X站", "果冻传媒", "麻豆传媒", "天美传媒", "精东传媒", "大象传媒",
]

FIXED_URLS = [
    "最新在线地址", "入口地址发布页", "当前可用地址", "永久地址", "官方最新地址",
    "在线观看入口", "免费观看入口", "不用付费观看", "无广告在线播放", "高清视频免费看",
]


# Load LIST_KEYWORDS from formatted_output.txt if present
def load_list_keywords():
    keywords = []
    try:
        with open("formatted_output.txt", "r", encoding="utf-8") as f:
            for line in f:
                token = line.strip().strip(",").strip()
                if token.startswith('"') and token.endswith('"'):
                    token = token[1:-1]
                if token:
                    keywords.append(token)
    except Exception:
        pass
    return keywords

LIST_KEYWORDS = load_list_keywords()

TEMPLATES = [
    """# {title}

🎉 欢迎来到 {app}{url} 官方导航页！

尊敬的用户您好！为了让您能够轻松、快速地找到 {app} 的最新地址，我们特地建立了本官方导航页面。无论您是首次访问，还是长期使用我们的老用户，都能在这里第一时间获取最新、最稳定的访问链接。

关键词：{keywords_text}  
更新时间：{date}  

以下是您当前可用的访问入口，强烈建议收藏多个备用链接，以防主链路出现故障：

- [👉👉主站入口👈👈]({domain})  
- [👉👉备用链接一👈👈]({domain})  
- [👉👉备用链接二👈👈]({domain})  

📌 我们的优势：
- 实时监测所有链接状态，确保每条链接均可正常访问，杜绝失效情况。
- 支持各种设备，包括手机、平板和电脑，跨平台无缝体验。
- 无需注册，无需登录，完全免费，保护用户隐私安全。
- 提供简洁清爽的界面，无任何弹窗和广告打扰。

⚙️ 遇到访问问题怎么办？
- 首先尝试刷新页面或关闭浏览器缓存，清除旧数据。
- 尝试切换不同浏览器访问，比如 Chrome、Firefox 或 Edge。
- 使用浏览器隐身模式，避免浏览器扩展或缓存干扰访问。
- 如果网络环境有限制，建议使用 VPN 或代理服务，突破地理屏蔽。
- 确认您的网络连接正常，必要时切换至数据流量或其他网络环境。

✨ 我们一直致力于为用户打造安全稳定的访问环境，您的支持是我们前进的动力。请务必收藏本页面，以便随时找到最新链接。如有任何疑问或建议，欢迎通过官方联系方式反馈，我们将竭诚为您服务。

感谢您的信赖，祝您访问顺利，使用愉快！
""",

    """# {title}

🔥 {app} - {url} 最新可用地址合集！

随着网络限制日益增多，保证稳定访问优质内容成为我们最重要的目标。为此，我们精心整理并持续更新本页面，确保您可以第一时间获得 {app} 的最新可用地址。

关键词：{keywords_text}  
页面更新日期：{date}  

🔗 当前可访问地址：
- [👉👉主入口👈👈]({domain})  
- [👉👉备用入口一👈👈]({domain})  
- [👉👉备用入口二👈👈]({domain})  

为什么选择我们？
- 多线路保障，确保任一线路出现故障时能迅速切换，不影响您的观看体验。
- 采用先进的服务器集群技术，极大提升访问速度和稳定性。
- 定期更新内容，保证资源丰富多样，满足不同用户需求。
- 严格无广告政策，杜绝一切骚扰弹窗和弹广告，专注提升用户体验。
- 完全匿名访问，绝不收集任何个人信息，保护您的隐私安全。

🌟 使用技巧：
- 请尽量收藏多个链接，预防主链接偶尔因维护或封锁而暂时无法访问。
- 遇到无法访问或加载缓慢时，可尝试清理浏览器缓存或切换网络环境。
- 推荐使用最新版主流浏览器，如 Chrome、Firefox 以获得最佳性能。
- 若您身处网络受限区域，建议配合 VPN 使用，保障访问畅通。

💬 用户支持：
如您遇到任何问题或需要协助，请通过我们的官方反馈渠道联系我们。我们拥有专业的技术团队，致力于快速响应并解决访问相关问题。

感谢您一直以来的支持和理解，愿您有一个愉快的浏览体验！
""",

    """# {title}

🚀 {app} 官方跳转入口说明 - {url}

您好，欢迎访问由我们精心维护的 {app} 官方导航页面。本页面专门提供当前最新、最安全、最稳定的访问入口，确保您能顺畅浏览所有内容。

关键词聚合：{keywords_text}  
日期：{date}  

🌍 可用地址一览：
- [👉👉主站点👈👈]({domain})  
- [👉👉备用站点A👈👈]({domain})  
- [👉👉备用站点B👈👈]({domain})  

📢 访问建议：
- 移动设备推荐使用 Chrome 或 Safari 浏览器，获得最佳兼容性和体验。
- 如果您在 WiFi 网络下遇到访问障碍，建议切换到 4G/5G 移动网络或使用 VPN。
- 浏览时开启无痕/隐身模式，避免浏览器缓存对页面加载造成影响。
- 遇到页面显示异常或链接无法访问，尝试清理浏览器缓存和 Cookie。

⚙️ 技术保障：
- 本导航页面为唯一官方入口，所有链接均经过严格检测，杜绝失效和安全隐患。
- 绝无任何弹窗、广告或恶意插件，确保用户安全无忧。
- 我们每日对链接状态进行检测并及时更新，保障链接实时有效。
- 任何访问问题均可通过官方渠道反馈，获得快速专业支持。

❤️ 用户隐私：
我们尊重您的隐私，绝不追踪任何访问行为，所有访问均匿名处理。

请务必收藏本页面，确保每次访问都能快速找到有效链接。感谢您的支持和信任！
""",

    """# {title}

🌟 {app} 永久导航页 - {url}

感谢您长期以来对 {app} 的信赖与支持。由于域名被封、访问限制频发，我们特别打造本永久导航页面，集中发布每日最新、稳定可用的访问地址，确保您畅享无忧。

关键词：{keywords_text}  
最后更新：{date}  

🔗 推荐访问链接：
- [👉👉主域名👈👈]({domain})  
- [👉👉备用1👈👈]({domain})  
- [👉👉备用2👈👈]({domain})  

技术说明：
- 我们采用先进的自动监控系统，实时检测所有链接可用状态。
- 一旦发现链接失效，立即替换为最新有效地址，完全无需用户操作。
- 支持多节点服务器，保障访问速度和稳定性。

用户体验：
- 本页面无任何广告和弹窗，界面简洁清爽。
- 访问无需注册或下载安装任何软件，直接打开即可使用。
- 完全匿名访问，保障用户隐私安全。

友情提示：
- 建议您将多个备用链接收藏，以便在某条线路出现问题时，快速切换。
- 保持浏览器更新，确保兼容性。
- 若遇访问困难，可尝试使用 VPN 或切换网络环境。

感谢您的支持与配合，我们会持续优化服务，带给您更加流畅的使用体验！
""",

    """# {title}

📘 {app} - {url} 全新访问指南

网络限制日益加剧，想要稳定访问 {app} 优质内容，必须掌握正确的访问方法。本页面将为您详细介绍最有效的访问策略及资源获取渠道。

关键词聚焦：{keywords_text}  
更新时间：{date}  

推荐收藏的访问链接：
- [👉👉主入口地址👈👈]({domain})
- [👉👉备用镜像1👈👈]({domain})
- [👉👉备用镜像2👈👈]({domain})

访问受限时的解决方案：
1. 首先刷新页面或尝试更换不同的主流浏览器。
2. 检查是否启用了代理工具，尝试关闭后重新访问。
3. 切换至手机数据流量，有时运营商网络会更通畅。
4. 使用稳定的 VPN 服务，突破地域限制。

访问小贴士：
- 我们每日检测更新所有链接，确保99.99%的可用率。
- 本站不存储任何用户数据，保护您的隐私安全。
- 提供超清播放体验，兼顾流畅和清晰度。

技术支持：
如您在访问过程中遇到任何问题，请及时反馈给我们。我们拥有专门的技术团队，保障您的访问畅通无阻。

感谢您选择我们的服务，祝您体验愉快！
""",

    """# {title}

🌐 {app} 多线路访问保障 - {url}

为了满足不同地区和网络环境的访问需求，我们特意准备了多条线路供您自由选择，确保您在任何时间都能顺畅访问 {app}。

关键词：{keywords_text}  
更新日期：{date}  
推荐收藏的访问链接：
- [👉👉主入口地址👈👈]({domain})
- [👉👉备用镜像1👈👈]({domain})
- [👉👉备用镜像2👈👈]({domain})
访问优势：
- 多线路切换，避免单点故障，保障访问连续性。
- 支持各种设备及主流浏览器，无论电脑还是手机均适用。
- 免注册登录，无任何广告干扰，尊重您的隐私。

实用建议：
- 收藏所有推荐链接，遇到访问异常时及时切换。
- 尽量使用最新版本浏览器，提升兼容性和安全性。
- 定期清理浏览器缓存，减少访问异常。
- 若网络受限严重，建议搭配 VPN 进行访问。

问题反馈：
如发现任何异常或疑问，请通过官方渠道联系我们。我们将第一时间协助解决，保障您的正常访问。
""",

    """# {title}

📢 {app} 官方推荐访问方式 - {url}

为了确保每位用户都能享受高效稳定的访问体验，我们提供了多个官方认证的访问入口，随时满足您的访问需求。

关键词汇总：{keywords_text}  
最后更新时间：{date}  

访问链接：
- [👉👉主入口👈👈]({domain})
- [👉👉备用入口1👈👈]({domain})
- [👉👉备用入口2👈👈]({domain})

选择我们的理由：
- 高速服务器，支持全天候无间断访问。
- 节点遍布多地，提升访问速度和稳定性。
- 访问免安装，打开即用，操作简单。

访问提示：
- 推荐使用隐身模式访问，避免缓存导致访问失败。
- 遇到加载缓慢或无法访问时，尝试更换线路或刷新页面。
- 网络不佳时，可切换至移动数据流量，提高访问成功率。

您的满意是我们的动力，感谢您的支持与信任！
""",

    """# {title}

🔗 {app} 最佳访问导航 - {url}

欢迎来到官方导航页面！为了让您畅享 {app} 的所有精彩内容，我们每日更新多个有效访问链接，保障您的使用无忧。

关键词：{keywords_text}  
更新日期：{date}  

主要访问入口：
- [👉👉主链接👈👈]({domain})
- [👉👉备用链接一👈👈]({domain})
- [👉👉备用链接二👈👈]({domain})

平台特色：
- 访问稳定安全，杜绝病毒和广告骚扰。
- 支持多设备多浏览器，跨平台无障碍。
- 全免费使用，零门槛零限制。

访问建议：
- 访问时遇到问题，建议先清理浏览器缓存或切换链接。
- 保持浏览器版本更新，提升兼容性。
- 定期关注导航页面更新信息，确保链接有效。

感谢您的选择与支持，祝您浏览愉快！
""",

    """# {title}

🛠️ {app} 用户访问指南 - {url}

为了让您顺畅访问平台，我们精心整理了详细的访问说明和常见问题解答，助您无忧使用。

关键词汇总：{keywords_text}  
更新日期：{date}  
- [👉👉主链接👈👈]({domain})
- [👉👉备用链接一👈👈]({domain})
- [👉👉备用链接二👈👈]({domain})
访问方法：
- 直接使用本页面提供的主入口或备用入口访问。
- 推荐使用 Chrome、Firefox 等主流浏览器，确保兼容性。
- 建议开启浏览器隐私/无痕模式，避免缓存影响。

常见问题解决：
- 页面加载慢或无法访问时，尝试刷新页面或切换网络环境。
- 链接失效时，优先尝试备用链接。
- 网络限制严重时，使用 VPN 是有效手段。

请务必收藏本页面，保证每次访问都顺畅无阻。

感谢您的支持，我们会持续优化，提供最优质的服务体验！
"""
]
def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", text)

def generate_md_content(title, keyword_list, domain_link, app, url):
    date_now = datetime.datetime.now().strftime("%Y-%m-%d")
    keywords_text = "，".join(keyword_list)
    template = random.choice(TEMPLATES)
    return template.format(
        title=title,
        keywords_text=keywords_text,
        domain=domain_link,
        date=date_now,
        app=app,
        url=url
    )

@app.route("/generate_batch", methods=["POST"])
def generate_batch_markdown():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        primary_keywords = data.get("primary_keywords")
        sub_keywords = data.get("sub_keywords")
        if not isinstance(primary_keywords, list) or not all(isinstance(k, str) for k in primary_keywords):
            return jsonify({"error": "Invalid or missing 'primary_keywords' list"}), 400
        if not isinstance(sub_keywords, list) or not all(isinstance(k, str) for k in sub_keywords):
            return jsonify({"error": "Invalid or missing 'sub_keywords' list"}), 400

        unique_primary_keywords = list(dict.fromkeys([k.strip() for k in primary_keywords if k.strip()]))
        if not unique_primary_keywords:
            return jsonify({"error": "primary_keywords list is empty after deduplication"}), 400
        if len(sub_keywords) < 3:
            return jsonify({"error": "Need at least 3 sub_keywords"}), 400

        memory_zip = io.BytesIO()
        with zipfile.ZipFile(memory_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            manifest_title_lines = []
            total_count = len(unique_primary_keywords)
            stt_width = len(str(total_count)) if total_count > 0 else 1
            stt_counter = 1
            for pk in unique_primary_keywords:
                app_fixed = random.choice(FIXED_APPS)
                url_fixed = random.choice(FIXED_URLS)
                subdomain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=3))
                domain_link = f"https://{subdomain}.zaixianyule.top/"

                # Build 3 unique sub keywords (not equal to primary) from user list, top up from LIST_KEYWORDS if needed
                filtered_unique = list(dict.fromkeys([kw.strip() for kw in sub_keywords if kw.strip() and kw.strip() != pk]))
                if len(filtered_unique) >= 3:
                    chosen_subs = random.sample(filtered_unique, 3)
                else:
                    chosen_subs = filtered_unique.copy()
                    if len(chosen_subs) < 3:
                        fallback_pool = [k for k in LIST_KEYWORDS if k not in chosen_subs and k != pk]
                        need = 3 - len(chosen_subs)
                        if fallback_pool:
                            chosen_subs.extend(random.sample(fallback_pool, min(need, len(fallback_pool))))
                    if len(chosen_subs) < 3:
                        remaining = [k for k in filtered_unique if k not in chosen_subs]
                        for k in remaining:
                            if len(chosen_subs) == 3:
                                break
                            chosen_subs.append(k)
                title = f"{pk} - {app_fixed} - {url_fixed} - {'-'.join(chosen_subs)}"
                # Đặt tên file: STT - từ khóa chính.md
                filename = f"{stt_counter} - {sanitize_filename(pk)}.md"
                content = generate_md_content(title, chosen_subs, domain_link, app_fixed, url_fixed)
                zf.writestr(filename, content)
                # Ghi manifest (chỉ STT - title), STT căn thẳng hàng bằng zero-pad
                manifest_title_lines.append(f"{str(stt_counter).zfill(stt_width)} - {title}")
                stt_counter += 1

            # Thêm file danh sách vào ZIP (mỗi dòng: STT - title)
            manifest_content = "\n".join(manifest_title_lines) + "\n"
            zf.writestr("danh_sach.txt", manifest_content)
        memory_zip.seek(0)
        out_zip_name = f"Markdown-Batch-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
        return send_file(
            memory_zip,
            as_attachment=True,
            download_name=out_zip_name,
            mimetype="application/zip"
        )

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e), "trace": traceback.format_exc()}), 500

@app.route("/", methods=["GET"])
def root():
    return jsonify({"msg": "Batch Markdown Generator is running."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)