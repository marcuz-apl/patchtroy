"""Content and structured data extraction engine for Playtrafi."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import urljoin

import trafilatura
from bs4 import BeautifulSoup

logger = logging.getLogger("playtrafi.extractors")


def extract_markdown_and_metadata(
    html: str,
    base_url: str = ''
) -> tuple[str, str, dict[str, Any]]:
    if not html or not html.strip():
        return '', '', {}

    title = ''
    metadata: dict[str, Any] = {}

    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_el = soup.find('title')
        if title_el and title_el.string:
            title = title_el.string.strip()
    except Exception:
        pass

    try:
        meta = trafilatura.extract_metadata(html, default_url=base_url)
        if meta:
            metadata = {
                'title': meta.title,
                'author': meta.author,
                'url': meta.url or base_url,
                'hostname': meta.hostname,
                'description': meta.description,
                'sitename': meta.sitename,
                'date': meta.date,
                'categories': meta.categories,
                'tags': meta.tags,
            }
            if meta.title:
                title = meta.title
    except Exception as exc:
        logger.debug('Trafilatura metadata extraction error: %s', exc)

    markdown = ''
    try:
        extracted = trafilatura.extract(
            html,
            url=base_url,
            output_format='markdown',
            include_links=True,
            include_images=True,
            include_formatting=True,
            include_tables=True,
            favor_recall=True,
        )
        if extracted:
            markdown = extracted.strip()
    except Exception as exc:
        logger.debug('Trafilatura content extraction error: %s', exc)

    if not markdown:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script', 'style', 'noscript', 'svg']):
                tag.decompose()
            body = soup.find('body') or soup
            lines = [line.strip() for line in body.get_text(separator=' ').splitlines()]
            markdown = chr(10).join(line for line in lines if line)
        except Exception:
            markdown = ''

    return markdown, title, metadata


def extract_structured_data(
    html: str,
    source_url: str = '',
    custom_schema: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not html or not html.strip():
        return []

    items: list[dict[str, Any]] = []

    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as exc:
        logger.warning('BeautifulSoup parsing failed: %s', exc)
        return []

    if custom_schema and isinstance(custom_schema, dict) and custom_schema.get('fields'):
        custom_items = _extract_custom_schema(soup, source_url, custom_schema)
        if custom_items:
            return custom_items

    next_data_el = soup.find('script', id='__NEXT_DATA__')
    if next_data_el and next_data_el.string:
        try:
            nd = json.loads(next_data_el.string)
            props = nd.get('props', {}).get('pageProps', {})
            raw_listings = (
                props.get('listings')
                or props.get('products')
                or props.get('items')
                or props.get('data')
            )
            if isinstance(raw_listings, list) and raw_listings:
                for item in raw_listings:
                    if isinstance(item, dict):
                        item['_source_url'] = source_url
                        items.append(item)
                if items:
                    return items
        except Exception:
            pass

    ld_items = _extract_json_ld(soup, source_url)
    if ld_items:
        items.extend(ld_items)

    return items


def extract_links(html: str, base_url: str = '') -> list[dict[str, str]]:
    if not html:
        return []

    links: list[dict[str, str]] = []
    seen: set[str] = set()

    try:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            full_url = urljoin(base_url, href) if base_url else href
            if full_url not in seen:
                seen.add(full_url)
                text = a.get_text(strip=True)
                links.append({'href': full_url, 'text': text})
    except Exception:
        pass

    return links


def _extract_json_ld(soup: BeautifulSoup, source_url: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for tag in soup.find_all('script', type='application/ld+json'):
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string)
            elements = data if isinstance(data, list) else [data]
            for el in elements:
                if not isinstance(el, dict):
                    continue
                if '@graph' in el and isinstance(el['@graph'], list):
                    for sub in el['@graph']:
                        if isinstance(sub, dict):
                            sub['_source_url'] = source_url
                            items.append(sub)
                else:
                    el['_source_url'] = source_url
                    items.append(el)
        except Exception:
            continue

    return items


def _extract_custom_schema(
    soup: BeautifulSoup,
    source_url: str,
    schema: dict[str, Any]
) -> list[dict[str, Any]]:
    item_selector = schema.get('item_selector')
    fields = schema.get('fields', {})
    results: list[dict[str, Any]] = []

    if item_selector:
        containers = soup.select(item_selector)
        for container in containers:
            record: dict[str, Any] = {'_source_url': source_url}
            for field_name, selector in fields.items():
                el = container.select_one(selector)
                record[field_name] = el.get_text(strip=True) if el else None
            results.append(record)
    else:
        record = {'_source_url': source_url}
        for field_name, selector in fields.items():
            el = soup.select_one(selector)
            record[field_name] = el.get_text(strip=True) if el else None
        results.append(record)

    return results
