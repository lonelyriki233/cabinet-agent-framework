
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib, re
import numpy as np

from .model import ROOT, read_json, write_json, write_text, now
from .governance import WORKER_TO_BUREAU

ARCHIVE_ROOT = ROOT / "runtime" / "archive"
META_DIR = ARCHIVE_ROOT / "meta"
INDEX_FILE = ARCHIVE_ROOT / "index.json"
EMBED_DIM = 256

@dataclass
class ArchiveRecord:
    bureau: str
    task_id: str
    task_type: str
    worker: str
    title: str
    source_path: str
    content_path: str
    summary: str
    tags: list[str]
    created_at: str
    embedding_path: str

    def to_dict(self):
        return asdict(self)


def ensure_archive() -> None:
    for d in [ARCHIVE_ROOT, META_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        write_json(INDEX_FILE, {"records": [], "updated_at": None})


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]+|[a-z0-9_]+", text.lower())[:4096]


def _embed(text: str) -> np.ndarray:
    vec = np.zeros(EMBED_DIM, dtype=np.float32)
    for tok in _tokenize(text):
        h = int(hashlib.blake2b(tok.encode('utf-8'), digest_size=8).hexdigest(), 16)
        vec[h % EMBED_DIM] += 1.0
    n = float(np.linalg.norm(vec))
    return vec / n if n else vec


def _record_dir(bureau: str, task_type: str, task_id: str) -> Path:
    return ARCHIVE_ROOT / bureau / task_type / task_id


def _read_preview(path: Path, limit: int = 4000) -> str:
    try:
        return path.read_text(encoding='utf-8')[:limit]
    except Exception:
        return ""


def _rel_or_abs(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def index_artifact(*, bureau: str, task_id: str, task_type: str, worker: str, title: str, source_path: str, artifact_path: str, tags: list[str] | None = None, summary: str | None = None) -> ArchiveRecord:
    ensure_archive()
    tags = tags or []
    artifact = ROOT / artifact_path if not Path(artifact_path).is_absolute() else Path(artifact_path)
    preview = _read_preview(artifact)
    payload = f"{title}\n{task_id}\n{task_type}\n{worker}\n{summary or ''}\n{preview}"
    emb = _embed(payload)

    rec_dir = _record_dir(bureau, task_type, task_id)
    rec_dir.mkdir(parents=True, exist_ok=True)
    emb_path = rec_dir / "embedding.npy"
    np.save(emb_path, emb)

    content_path = _rel_or_abs(artifact)
    meta = ArchiveRecord(
        bureau=bureau,
        task_id=task_id,
        task_type=task_type,
        worker=worker,
        title=title,
        source_path=source_path,
        content_path=content_path,
        summary=summary or preview[:500],
        tags=tags,
        created_at=now(),
        embedding_path=str(emb_path.relative_to(ROOT)),
    )
    write_json(rec_dir / "meta.json", meta.to_dict())
    write_text(rec_dir / "content.txt", preview)
    write_json(META_DIR / f"{bureau}__{task_type}__{task_id}.json", meta.to_dict())

    idx = read_json(INDEX_FILE, {"records": [], "updated_at": None}) or {"records": [], "updated_at": None}
    idx["records"] = [r for r in idx.get("records", []) if not (r.get("task_id") == task_id and r.get("artifact_path") == content_path)]
    idx["records"].append({
        "bureau": bureau,
        "task_id": task_id,
        "task_type": task_type,
        "worker": worker,
        "title": title,
        "artifact_path": content_path,
        "embedding_path": str(emb_path.relative_to(ROOT)),
        "created_at": meta.created_at,
        "tags": tags,
    })
    idx["updated_at"] = meta.created_at
    write_json(INDEX_FILE, idx)
    return meta


def index_task_outputs(task: dict) -> list[ArchiveRecord]:
    bureau = WORKER_TO_BUREAU.get(task.get("worker", ""), "knowledge_skills_bureau")
    recs: list[ArchiveRecord] = []
    for out in task.get("required_outputs", []):
        path = ROOT / out
        if path.exists():
            recs.append(index_artifact(
                bureau=bureau,
                task_id=task["task_id"],
                task_type=task.get("task_type", "unknown"),
                worker=task.get("worker", "unknown"),
                title=task.get("title", task.get("task_id", "task")),
                source_path=out,
                artifact_path=out,
                tags=["required_output", task.get("task_type", "unknown")],
                summary=f"Indexed from task output {out}",
            ))
    for key in ["worker_prompt", "hermes_log"]:
        if task.get(key):
            p = ROOT / task[key]
            if p.exists():
                index_artifact(
                    bureau=bureau,
                    task_id=task["task_id"],
                    task_type=task.get("task_type", "unknown"),
                    worker=task.get("worker", "unknown"),
                    title=f"{task.get('title', task.get('task_id'))} [{key}]",
                    source_path=task[key],
                    artifact_path=task[key],
                    tags=[key],
                    summary=f"Indexed from {key}",
                )
    return recs


def search(query: str, bureau: str | None = None, task_type: str | None = None, top_k: int = 5) -> list[dict]:
    ensure_archive()
    idx = read_json(INDEX_FILE, {"records": []}) or {"records": []}
    qv = _embed(query)
    scored = []
    for r in idx.get("records", []):
        if bureau and r.get("bureau") != bureau:
            continue
        if task_type and r.get("task_type") != task_type:
            continue
        emb_path = ROOT / r["embedding_path"]
        if not emb_path.exists():
            continue
        rv = np.load(emb_path)
        denom = (np.linalg.norm(rv) * np.linalg.norm(qv)) or 1.0
        score = float(np.dot(rv, qv) / denom)
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{**r, "score": round(score, 4)} for score, r in scored[:top_k]]


def tree_view() -> dict:
    ensure_archive()
    tree: dict = {}
    for path in ARCHIVE_ROOT.rglob("meta.json"):
        rel = path.relative_to(ARCHIVE_ROOT)
        parts = rel.parts
        if len(parts) >= 4:
            bureau, task_type, task_id = parts[0], parts[1], parts[2]
            tree.setdefault(bureau, {}).setdefault(task_type, []).append(task_id)
    return tree
