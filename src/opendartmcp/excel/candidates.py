"""OpenDART XML을 우선하고 DART 첨부 조회로 빠진 문서만 보완한다.

문서의 주소는 접수번호가 아니라 (rcpNo, dcmNo) 쌍이다. 정정 공시는 본문만
재제출하고 첨부는 원본 공시에 남으므로, 후보의 접수번호는 조회에 쓴
접수번호와 다를 수 있다 — 그 경우가 정상이다.

공시 계열의 모든 ZIP XML에서 감사·검토보고서를 먼저 찾는다. OpenDART가
반기·분기 첨부를 ZIP에서 빼는 경우에만 화면의 내부 문서 목록으로 보완한다.
본문은 감사·검토보고서가 실제로 없고 사용자가 승인한 경우에만 후보가 된다.
"""
from __future__ import annotations

import datetime
import html
import re
from urllib.parse import parse_qs

import httpx
from bs4 import BeautifulSoup

from ..errors import DartApiError, DartHttpError
from . import dartdoc

# 화면 제목의 "[정정] 연결감사보고서"처럼 앞에 붙는 표식 — ZIP 제목엔 없다.
_BRACKET_RE = re.compile(r"^\s*(?:\[[^\]]*\]\s*)+")
# 보고서명의 "[기재정정]", "[첨부추가]" 표식.
_MARK_RE = re.compile(r"\[[^\]]*\]")
_RCEPT_RE = re.compile(r"^\d{14}$")
_DCM_RE = re.compile(r"^\d+$")
# ZIP 엔트리명 — 경로 이탈과 구분자 혼입을 막는다.
_ENTRY_RE = re.compile(r"^[\w.\-]+$")
_NODE_RE = re.compile(r"var node[12] = \{\};(.*?)(?=var node[12] = \{\};|//js tree)", re.S)
_FIELD_RE = re.compile(r"node[12]\['([^']+)'\]\s*=\s*\"([^\"]*)\";")
_DATE_RE = re.compile(r"^(\d{4}\.\d{2}\.\d{2})\s*")

BODY_SUFFIX = " (본문)"
_ATTACHMENT_KEYWORDS = ("감사보고서", "검토보고서")
_ATTACHMENT_EXCLUDES = (
    "감사의감사보고서",
    "내부회계관리제도운영보고서",
    "내부감시장치에대한감사의의견서",
)


class CandidateError(ValueError):
    pass


def _viewer_options(page: str) -> list[dict]:
    """첨부 선택 상자의 항목들. value의 rcpNo가 문서의 실제 소속 공시다."""
    soup = BeautifulSoup(page, "html.parser")
    select = soup.find("select", id="att")
    if select is None:
        return []
    result = []
    for option in select.find_all("option"):
        query = parse_qs(html.unescape(option.get("value", "")))
        rcept_no = (query.get("rcpNo") or [""])[0]
        dcm_no = (query.get("dcmNo") or [""])[0]
        if not _RCEPT_RE.fullmatch(rcept_no) or not _DCM_RE.fullmatch(dcm_no):
            continue
        label = re.sub(r"\s+", " ", " ".join(option.stripped_strings)).strip()
        match = _DATE_RE.match(label)
        date = match.group(1).replace(".", "") if match else rcept_no[:8]
        title = label[match.end():].strip() if match else label
        result.append({
            "candidate_id": f"viewer:{rcept_no}:{dcm_no}",
            "rcept_no": rcept_no,
            "date": date,
            "title": title,
        })
    return result


def _report_name(page: str) -> str:
    """화면 title("회사명/보고서명/날짜")에서 보고서명."""
    soup = BeautifulSoup(page, "html.parser")
    if soup.title:
        parts = [p.strip() for p in soup.title.get_text().split("/")]
        if len(parts) >= 2 and parts[1]:
            return parts[1]
    return "본문"


def _title_key(title: str) -> str:
    """같은 문서인지 가리는 열쇠 — 화면 제목의 표식은 ZIP 제목에 없다."""
    return dartdoc.norm(_BRACKET_RE.sub("", title))


def is_financial_attachment(title: str) -> bool:
    """재무제표 원문을 담는 감사·검토보고서인지 제목으로 좁힌다."""
    normalized = dartdoc.norm(_BRACKET_RE.sub("", title))
    return (any(word in normalized for word in _ATTACHMENT_KEYWORDS)
            and not any(word in normalized for word in _ATTACHMENT_EXCLUDES))


def _series_key(report_nm: str) -> str:
    """정정·추가 표식을 뗀 보고서 이름 — 같은 보고서의 제출본들을 묶는 열쇠.

    "[기재정정]사업보고서 (2024.12)" 와 "[첨부추가]사업보고서 (2024.12)" 는
    같은 보고서의 다른 제출본이다.
    """
    return dartdoc.norm(_MARK_RE.sub("", report_nm))


async def _list_page(client, params: dict) -> dict:
    try:
        return await client.get_json("/list.json", params)
    except DartApiError as error:
        if error.status == "013":         # 조회 결과 없음
            return {"list": [], "total_page": 0}
        raise


async def _find_filing(client, rcept_no: str, corp_code: str | None) -> dict:
    """접수번호의 공시 메타. corp_code를 알면 한 번에 끝난다."""
    date = rcept_no[:8]
    # 공시유형을 좁히지 않는다 — 외부감사 단독 공시는 정기공시(A)가 아니다.
    base = {"bgn_de": date, "end_de": date, "page_count": "100"}
    if corp_code:
        base["corp_code"] = corp_code
    page = 1
    while True:
        base["page_no"] = str(page)
        data = await _list_page(client, base)
        for item in data.get("list") or []:
            if item["rcept_no"] == rcept_no:
                return item
        if page >= int(data.get("total_page") or 0):
            raise CandidateError("filing not found")
        page += 1


async def _series_filings(client, filing: dict) -> list[dict]:
    """같은 보고서의 모든 제출본(원본·정정·추가), 최신 제출본이 먼저.

    정정은 몇 달 뒤에도 올라온다 — 접수 연도 앞뒤로 넉넉히 훑는다.
    """
    key = _series_key(filing["report_nm"])
    year = int(filing["rcept_no"][:4])
    end = max(year + 1, datetime.date.today().year)
    params = {"corp_code": filing["corp_code"], "bgn_de": f"{year - 1}0101",
              "end_de": f"{end}1231", "page_count": "100"}
    # 공시가 많은 회사는 한 해 수백 건이라 정기공시로 좁힌다 — 안 좁히면
    # 3월 사업보고서가 1페이지 밖으로 밀려 원본을 놓친다.
    if any(word in key for word in ("사업보고서", "반기보고서", "분기보고서")):
        params["pblntf_ty"] = "A"
    same = []
    page = 1
    while True:
        params["page_no"] = str(page)
        data = await _list_page(client, params)
        same += [item for item in (data.get("list") or [])
                 if _series_key(item["report_nm"]) == key]
        if page >= int(data.get("total_page") or 0):
            break
        page += 1
    if filing["rcept_no"] not in [item["rcept_no"] for item in same]:
        same.append(filing)
    return sorted(same, key=lambda item: item["rcept_no"], reverse=True)


async def list_candidates(client, rcept_no: str,
                          corp_code: str | None = None,
                          allow_body: bool = False) -> dict:
    """공시 계열의 재무문서 후보. 제목만 반환하고 원문은 반환하지 않는다.

    정정 공시는 본문만 재제출하고 첨부는 원본 제출본에 남는다. 그래서
    한 건이 아니라 같은 보고서의 제출본 전체를 훑어 그 안의 문서를 모은다.
    후보의 접수번호가 넘긴 값과 다른 것은 정상이다.
    """
    if not _RCEPT_RE.fullmatch(rcept_no or ""):
        return {"ok": False, "error": "invalid_rcept_no"}

    attachments: list[dict] = []
    bodies: list[dict] = []
    try:
        filing = await _find_filing(client, rcept_no, corp_code)
        series = await _series_filings(client, filing)
    except (CandidateError, DartApiError, DartHttpError):
        series = []
    for item in series:
        try:
            zip_bytes = await client.download_zip("/document.xml",
                                                  {"rcept_no": item["rcept_no"]})
            with client.open_zip(zip_bytes) as zf:
                documents = client.zip_documents(zf)
        except (DartApiError, DartHttpError):
            continue
        for document in documents:
            candidate = {
                "candidate_id": f"zip:{item['rcept_no']}:{document['filename']}",
                "rcept_no": item["rcept_no"],
                "date": item["rcept_dt"],
                "title": document["title"] or item["report_nm"],
                "source": "opendart_xml",
            }
            if is_financial_attachment(candidate["title"]):
                attachments.append(candidate)
            elif document["filename"] == f"{item['rcept_no']}.xml":
                candidate["candidate_id"] = f"body:{item['rcept_no']}"
                candidate["title"] += BODY_SUFFIX
                bodies.append(candidate)

    # XML에 재무 첨부가 있으면 화면을 보지 않는다. 연간·외감단독의 정상 경로다.
    if attachments:
        return {"ok": True, "candidates": attachments}

    # 반기·분기 검토보고서는 공시 ZIP에 들어 있지 않다 — 화면에만 있다.
    # 내부 조회 실패와 첨부 부재는 구분한다. 전자는 본문 승인 사유가 아니다.
    lookup_failed = False
    try:
        page = await client.get_dart_html("/dsaf001/main.do", {"rcpNo": rcept_no})
        screen = [item for item in _viewer_options(page)
                  if is_financial_attachment(item["title"])]
    except (DartApiError, DartHttpError, httpx.HTTPError):
        screen = []
        lookup_failed = True
    seen = {(item["rcept_no"], _title_key(item["title"]))
            for item in attachments}
    for item in screen:
        if (item["rcept_no"], _title_key(item["title"])) not in seen:
            item["source"] = "dart_attachment"
            attachments.append(item)

    if attachments:
        return {"ok": True, "candidates": attachments}
    if lookup_failed:
        return {"ok": False, "error": "attachment_lookup_failed",
                "body_available": bool(bodies)}
    if bodies and not allow_body:
        return {
            "ok": False,
            "error": "confirmation_required",
            "body_available": True,
            "message": "감사·검토보고서 첨부가 없습니다. 본문을 사용할까요?",
        }
    if bodies:
        # 정정 계열이면 최신 본문 하나만 내놓는다.
        return {"ok": True, "candidates": [max(bodies, key=lambda x: x["date"])],
                "body_approved": True}
    return {"ok": False, "error": "no_documents"}


def parse_candidate_id(candidate_id: str) -> tuple[str, str, str]:
    """candidate_id → (종류, 접수번호, 문서 지시자).

    zip은 ZIP 엔트리명, viewer는 화면 문서번호, body는 빈 문자열이다.
    """
    parts = (candidate_id or "").split(":")
    if len(parts) == 3 and parts[0] in ("zip", "viewer"):
        kind, rcept_no, ref = parts
    elif len(parts) == 2 and parts[0] == "body":
        kind, rcept_no, ref = "body", parts[1], ""
    else:
        raise CandidateError("invalid candidate id")
    if not _RCEPT_RE.fullmatch(rcept_no):
        raise CandidateError("invalid candidate id")
    if kind == "viewer" and not _DCM_RE.fullmatch(ref):
        raise CandidateError("invalid candidate id")
    if kind == "zip" and not _ENTRY_RE.fullmatch(ref):
        raise CandidateError("invalid candidate id")
    return kind, rcept_no, ref


async def load_zip_document(client, rcept_no: str, filename: str) -> tuple[str, str]:
    """공시 ZIP 안의 문서 하나. 정식 XML이라 손질이 필요 없다."""
    zip_bytes = await client.download_zip("/document.xml",
                                          {"rcept_no": rcept_no})
    with client.open_zip(zip_bytes) as zf:
        documents = {item["filename"]: item for item in client.zip_documents(zf)}
        if filename not in documents:
            raise CandidateError("document not in filing")
        return (client._decode_document(zf.read(filename)),
                documents[filename]["title"])


def _viewer_nodes(page: str, dcm_no: str) -> list[dict]:
    nodes = []
    for block in _NODE_RE.findall(page):
        node = dict(_FIELD_RE.findall(block))
        if (node.get("dcmNo") == dcm_no and node.get("offset", "").isdigit()
                and node.get("length", "").isdigit()):
            nodes.append(node)
    return nodes


def _pick_node(nodes: list[dict], scope: str) -> dict:
    """재무제표 덩어리 중 하나. 요청 범위와 맞는 것이 있으면 그것을 쓴다.

    범위를 거르지 않고 선호만 한다 — 한 문서에 한 범위만 들어 있는 것이
    보통이고, 걸러버리면 멀쩡한 문서를 못 쓰게 된다.
    """
    labelled = [(node, dartdoc.norm(html.unescape(node.get("text", ""))))
                for node in nodes]
    financial = [(node, "연결" in text) for node, text in labelled
                 if "재무제표" in text and "보고서" not in text]
    if not financial:
        # 목차가 평평한 문서(외국법인 공시 등)는 재무제표가 하위 노드로
        # 나뉘어 있지 않다. 문서 전체를 받는다 — 첫 재무제표 제목 앞부분은
        # 파서가 어차피 버린다.
        financial = [(node, "연결" in text) for node, text in labelled]
    if not financial:                     # 목차 자체가 없는 문서
        raise CandidateError("financial statement section not found")
    wanted = scope == dartdoc.CONSOLIDATED
    preferred = [node for node, consolidated in financial
                 if consolidated == wanted] or [node for node, _ in financial]
    return max(preferred, key=lambda item: int(item["length"]))


def _mark_notes_title(soup) -> None:
    """주석 섹션 제목을 파서가 아는 TITLE 경계로 바꾼다.

    문단으로 쓰는 문서도 있고 테두리 없는 표의 셀로 쓰는 문서도 있다.
    표 셀이면 그 표를 통째로 TITLE로 바꾼다 — 셀만 바꾸면 표 안에 갇혀
    최상위 흐름에서 경계로 보이지 않는다.

    재무제표에도 `주석`이라는 글자가 열 머리글로 등장하므로, 머리글 안의
    문단과 테두리 있는 표(=수치 표)는 후보에서 뺀다.
    """
    for element in soup.find_all(["p", "td"]):
        if dartdoc.norm(element.get_text()) != "주석":
            continue
        holder = element
        if element.name == "p":
            if element.find_parent(["th", "td"]):
                continue          # 재무제표의 `주석` 열 머리글 안이다
        else:
            table = element.find_parent("table")
            if table is None or dartdoc.norm(table.get_text()) != "주석":
                continue          # 다른 내용이 섞인 표는 건드리지 않는다
            if str(table.get("border", "")).strip() not in ("", "0"):
                continue          # 수치 표는 제목 표가 아니다
            holder = table
        marker = soup.new_tag("TITLE")
        marker.string = "주석"
        holder.replace_with(marker)
        return
    raise CandidateError("notes section not found")


def _zip_document(client, zip_bytes: bytes, title: str) -> str | None:
    """공시 ZIP에서 제목이 같은 문서 하나. 없거나 여럿이면 None."""
    wanted = dartdoc.norm(_BRACKET_RE.sub("", title))
    with client.open_zip(zip_bytes) as zf:
        matches = [document for document in client.zip_documents(zf)
                   if dartdoc.norm(document["title"]) == wanted]
        if len(matches) != 1:
            return None
        return client._decode_document(zf.read(matches[0]["filename"]))


async def load_attachment(client, rcept_no: str, dcm_no: str,
                          scope: str) -> tuple[str, str]:
    """첨부 문서 원문과 제목.

    공시 ZIP에 그 문서가 있으면 정식 XML을 쓴다 — 화면 조각과 달리 목차
    좌표도, 주석 제목 손질도 필요 없다. 2014년 이전 공시는 화면 목차가
    비어 있어 이 경로로만 열린다. ZIP에 없는 첨부만 화면에서 긁는다.
    """
    page = await client.get_dart_html(
        "/dsaf001/main.do", {"rcpNo": rcept_no, "dcmNo": dcm_no})
    options = [item for item in _viewer_options(page)
               if item["rcept_no"] == rcept_no
               and item["candidate_id"].endswith(f":{dcm_no}")]
    title = options[0]["title"] if options else "DART 첨부문서"

    try:
        zip_bytes = await client.download_zip("/document.xml",
                                              {"rcept_no": rcept_no})
        content = _zip_document(client, zip_bytes, title)
    except (DartApiError, DartHttpError):
        content = None          # 열람 불가·API 장애 — 화면으로 넘어간다
    if content is not None:
        return content, title
    return await _viewer_fallback(client, page, title, dcm_no, scope), title


async def load_viewer_document(client, rcept_no: str, scope: str, *,
                               dcm_no: str = "", title: str = "") -> str:
    """DART 화면 HTML을 재무문서 모양으로 반환.

    ZIP XML은 일부 문서에서 화면의 BR을 잃는다. 주석 문단만 화면 구조로
    교체할 때 쓰며, viewer 후보는 dcm_no로, ZIP 후보는 문서 제목으로 찾는다.
    """
    page = await client.get_dart_html(
        "/dsaf001/main.do", {"rcpNo": rcept_no, **(
            {"dcmNo": dcm_no} if dcm_no else {})})
    options = [item for item in _viewer_options(page)
               if item["rcept_no"] == rcept_no]
    if dcm_no:
        options = [item for item in options
                   if item["candidate_id"].endswith(f":{dcm_no}")]
    else:
        wanted = _title_key(title)
        options = [item for item in options
                   if _title_key(item["title"]) == wanted]
    if len(options) != 1:
        raise CandidateError("viewer document not found")
    _, _, viewer_dcm = parse_candidate_id(options[0]["candidate_id"])
    if not dcm_no:
        page = await client.get_dart_html(
            "/dsaf001/main.do", {"rcpNo": rcept_no, "dcmNo": viewer_dcm})
    return await _viewer_fallback(
        client, page, options[0]["title"], viewer_dcm, scope)


async def _viewer_fallback(client, page: str, title: str, dcm_no: str,
                           scope: str) -> str:
    """화면 문서의 재무제표 덩어리를 공시 원문과 같은 모양으로 감싸 반환한다."""
    node = _pick_node(_viewer_nodes(page, dcm_no), scope)
    fragment = await client.get_dart_html("/report/viewer.do", {
        key: node[key] for key in
        ("rcpNo", "dcmNo", "eleId", "offset", "length", "dtd")
    })

    soup = BeautifulSoup(fragment, "html.parser")
    for table in soup.find_all("table"):
        if "nb" in (table.get("class") or []):
            table["border"] = "0"
    _mark_notes_title(soup)

    company = ""
    if soup_page := BeautifulSoup(page, "html.parser").title:
        company = soup_page.get_text(strip=True).split("/", 1)[0]
    body = soup.body.decode_contents() if soup.body else str(soup)
    node_text = dartdoc.norm(html.unescape(node.get("text", "")))
    fs_title = "(첨부)연결재무제표" if "연결" in node_text else "(첨부)재무제표"
    content = (
        "<DOCUMENT>"
        f"<DOCUMENT-NAME>{html.escape(title)}</DOCUMENT-NAME>"
        f"<COMPANY-NAME>{html.escape(company)}</COMPANY-NAME>"
        f"<BODY><TITLE>{fs_title}</TITLE>{body}</BODY>"
        "</DOCUMENT>"
    )
    return content
