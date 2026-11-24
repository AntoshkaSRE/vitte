"""Служебные адреса: проверка работоспособности, robots.txt и sitemap.xml."""
from xml.sax.saxutils import escape

from flask import Blueprint, Response, jsonify, redirect, url_for

from app import __version__
from app.db import query_all, query_one

bp = Blueprint("ops", __name__)

# Публичные страницы без параметров, попадающие в sitemap.xml
STATIC_PAGES = ("public.index", "public.about", "public.features", "public.indicators",
                "public.faculties", "public.directions", "public.open_stats", "public.news_list",
                "public.faq", "public.docs", "public.contacts", "public.sitemap")


@bp.route("/favicon.ico")
def favicon():
    """Браузеры запрашивают /favicon.ico автоматически: перенаправляем на значок сайта в формате SVG."""
    return redirect(url_for("static", filename="favicon.svg"), code=301)


@bp.route("/robots.txt")
def robots():
    """Правила для поисковых роботов: закрыты личные разделы и панель администратора."""
    lines = ["User-agent: *",
             "Disallow: /admin/", "Disallow: /cabinet/", "Disallow: /api/", "Disallow: /reports/",
             "Disallow: /dashboards/", "Disallow: /login",
             f"Sitemap: {url_for('ops.sitemap_xml', _external=True)}"]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap_xml():
    """Карта сайта в формате XML: статические страницы, факультеты и опубликованные новости."""
    urls = [url_for(endpoint, _external=True) for endpoint in STATIC_PAGES]
    for row in query_all("SELECT code FROM faculties ORDER BY id"):
        urls.append(url_for("public.faculty_detail", code=row["code"], _external=True))
    for row in query_all("SELECT id FROM news WHERE is_published ORDER BY id"):
        urls.append(url_for("public.news_detail", news_id=row["id"], _external=True))
    body = "".join(f"  <url><loc>{escape(url)}</loc></url>\n" for url in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")
    return Response(xml, mimetype="application/xml")


@bp.route("/healthz")
def healthz():
    """Возвращает 200, если приложение запущено и доступна база данных, иначе 503."""
    try:
        query_one("SELECT 1 AS ok")
    except Exception:  # noqa: BLE001 - любая ошибка подключения означает «база недоступна»
        return jsonify(status="error", database="unavailable"), 503
    return jsonify(status="ok", database="ok", version=__version__)
