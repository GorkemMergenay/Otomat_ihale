"""
Metin içinden ihale tarihleri çıkarma (son başvuru, yayın tarihi).
Türkçe ve yaygın formatları destekler.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

# Yaygın tarih formatları (regex, strptime format)
DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "%Y-%m-%d"),
    (re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b"), "%d.%m.%Y"),
    (re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b"), "%d/%m/%Y"),
    (re.compile(r"\b(\d{1,2})\s*[-/.]\s*(\d{1,2})\s*[-/.]\s*(\d{4})\b"), "%d.%m.%Y"),
]

# Son başvuru / deadline anahtar kelimeleri (öncelikli aranır)
DEADLINE_KEYWORDS = re.compile(
    r"(?:son\s+başvuru|son\s+tarih|deadline|başvuru\s+süresi|teklif\s+tarihi|kapanış)\s*[:\s]*(\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)

# İhale günü / açılış tarihi (ihalenin yapılacağı gün)
TENDER_DATE_KEYWORDS = re.compile(
    r"(?:ihale\s+tarihi|ihale\s+günü|açılış\s+tarihi|teklif\s+açılış|açılış\s+günü|ihale\s+tarih)\s*[:\s]*(\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)

def _parse_flexible_date(s: str) -> Optional[date]:
    """Tek bir tarih string'ini parse et."""
    s = s.strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    if re.match(r"^\d{1,2}[./]\d{1,2}[./]\d{2}$", s):
        parts = re.split(r"[./]", s)
        if len(parts) == 3 and len(parts[2]) == 2:
            y = int(parts[2])
            if y < 50:
                y += 2000
            else:
                y += 1900
            s = f"{parts[0].zfill(2)}.{parts[1].zfill(2)}.{y}"
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except ValueError:
            continue
    if len(s) == 4 and s.isdigit():
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for pattern, fmt in DATE_PATTERNS:
        m = pattern.search(s)
        if m:
            try:
                if fmt == "%d.%m.%Y":
                    d, mo, y = m.group(1), m.group(2), m.group(3)
                    if len(y) == 2:
                        y = "20" + y
                    return datetime.strptime(f"{d}.{mo}.{y}", "%d.%m.%Y").date()
                return datetime.strptime(m.group(0), fmt).date()
            except (ValueError, IndexError):
                continue
    return None


def extract_deadline_from_text(text: Optional[str]) -> Optional[date]:
    """
    Metinden son başvuru tarihini çıkarır.
    Önce 'son tarih', 'deadline' vb. geçen ifadeleri arar, yoksa herhangi bir tarih arar.
    """
    if not text or not text.strip():
        return None
    text = " " + text + " "
    match = DEADLINE_KEYWORDS.search(text)
    if match:
        raw = match.group(1).strip()
        d = _parse_flexible_date(raw)
        if d:
            return d
    for pattern, _ in DATE_PATTERNS:
        for m in pattern.finditer(text):
            raw = m.group(0)
            d = _parse_flexible_date(raw)
            if d and d >= date.today():
                return d
            if d:
                return d
    return None


def extract_tender_date_from_text(text: Optional[str]) -> Optional[date]:
    """
    Metinden ihale gününü (ihalenin yapılacağı tarih) çıkarır.
    'İhale tarihi', 'açılış tarihi', 'ihale günü' vb. ifadeleri arar.
    """
    if not text or not text.strip():
        return None
    text = " " + text + " "
    match = TENDER_DATE_KEYWORDS.search(text)
    if match:
        raw = match.group(1).strip()
        d = _parse_flexible_date(raw)
        if d:
            return d
    return None


def extract_any_date_from_text(text: Optional[str]) -> Optional[date]:
    """Metinden herhangi bir tarih çıkarır (ilk bulunan)."""
    if not text or not text.strip():
        return None
    for pattern, _ in DATE_PATTERNS:
        m = pattern.search(text)
        if m:
            d = _parse_flexible_date(m.group(0))
            if d:
                return d
    return None
