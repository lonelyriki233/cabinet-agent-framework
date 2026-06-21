"""SkillForge: automatic skill discovery, creation, calibration, and iteration.

(C) When a worker has no skill for a domain:
  1. skill_discovery_needed() → detect gap
  2. find_adjacent_skills() → look for similar skills
  3. forge_skill() → create new skill from research + available template
  4. calibrate_skill() → user feedback loop
  5. improve_skill_from_feedback() → self-evolution
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json, re, sys

from .model import (
    ROOT, RUNTIME, SKILLS, OUTPUTS, now, slug, read_json, write_json, write_text,
    TASK_TO_WORKER, WORKERS,
)

SKILL_TEMPLATES = ROOT / "skills"
WORKER_SKILLS = SKILL_TEMPLATES / "worker"
THINKING_SKILLS = SKILL_TEMPLATES / "thinking"

SKILL_MANIFEST_FILE = SKILL_TEMPLATES / "manifest.json"

# Known domains for skill matching
KNOWN_DOMAINS = {
    "writing": ["小说", "写作", "剧本", "故事", "文字", "文学", "创作"],
    "music": ["音乐", "作曲", "编曲", "歌曲", "乐谱", "和声", "旋律"],
    "game_design": ["游戏", "关卡", "玩法", "数值", "平衡", "策划"],
    "code": ["代码", "编程", "开发", "API", "接口", "数据库", "调试"],
    "research": ["研究", "论文", "文献", "调研", "综述", "实验"],
    "art": ["美术", "绘画", "设计", "UI", "视觉", "风格"],
    "data": ["数据", "分析", "统计", "可视化", "训练", "模型"],
    "devops": ["部署", "CI", "测试", "运维", "监控", "配置"],
    "planning": ["规划", "路线", "战略", "方案", "架构"],
    "analysis": ["分析", "审计", "审查", "评估", "评审"],
}


def ensure_skill_registry():
    """Ensure skill directories and manifest exist."""
    for d in [WORKER_SKILLS, THINKING_SKILLS]:
        d.mkdir(parents=True, exist_ok=True)
    if not SKILL_MANIFEST_FILE.exists():
        write_json(SKILL_MANIFEST_FILE, {
            "version": 1,
            "forge_skills": {},
            "last_updated": now(),
        })


def _load_manifest() -> dict:
    ensure_skill_registry()
    return read_json(SKILL_MANIFEST_FILE, {}) or {}


def _save_manifest(manifest: dict):
    manifest["last_updated"] = now()
    write_json(SKILL_MANIFEST_FILE, manifest)


def list_all_skills() -> list[dict]:
    """List all registered worker skills with metadata."""
    ensure_skill_registry()
    manifest = _load_manifest()
    skills = []
    for f in sorted(WORKER_SKILLS.glob("*.md")):
        name = f.stem
        meta = manifest.get("forge_skills", {}).get(name, {})
        skills.append({
            "name": name,
            "path": str(f),
            "forge_version": meta.get("version", 0),
            "domain": meta.get("domain", "general"),
            "task_types": meta.get("task_types", []),
            "created_at": meta.get("created_at", ""),
            "iteration_count": meta.get("iteration_count", 0),
            "usage_count": meta.get("usage_count", 0),
        })
    return skills


def skill_discovery_needed(worker_name: str, task_type: str, title: str, request: str) -> bool:
    """Check if a worker skill needs to be forged for this task.
    
    Returns True if no existing skill covers this request.
    """
    ensure_skill_registry()
    
    # Always forge if no worker skills exist
    existing = list(WORKER_SKILLS.glob("*.md"))
    if not existing:
        return True
    
    # Check if any existing skill's domain/task_types match
    manifest = _load_manifest()
    for_skills = manifest.get("forge_skills", {})
    
    text = f"{title} {request}".lower()
    
    for skill_name, meta in for_skills.items():
        skill_types = meta.get("task_types", [])
        # Exact match on task_type
        if task_type in skill_types:
            return False
        # Domain match
        skill_domain = meta.get("domain", "")
        if skill_domain in KNOWN_DOMAINS:
            keywords = KNOWN_DOMAINS[skill_domain]
            if any(kw in text for kw in keywords):
                return False
    
    return True


def estimate_skill_gap(worker_name: str, task_type: str, title: str) -> dict:
    """Estimate what skill needs to be built: domain, proposed name, description."""
    text = f"{title} {worker_name}".lower()
    
    # Find best domain
    best_domain = "general"
    best_score = 0
    for domain, keywords in KNOWN_DOMAINS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_domain = domain
    
    # Generate skill name
    skill_name = slug(f"forge-{task_type}-{best_domain}")[:48]
    
    return {
        "domain": best_domain,
        "proposed_name": skill_name,
        "description": f"Auto-forged {best_domain} skill for {task_type} tasks ({worker_name})",
        "gap_confidence": min(1.0, 0.3 + best_score * 0.15),
    }


def find_adjacent_skills(task_type: str) -> list[dict]:
    """Find existing skills that could serve as reference/starting point.
    
    Returns a list of skill dicts that are adjacent to the requested task_type.
    """
    ensure_skill_registry()
    manifest = _load_manifest()
    adjacent = []
    
    for skill_name, meta in manifest.get("forge_skills", {}).items():
        if task_type in meta.get("task_types", []):
            # Direct match
            path = WORKER_SKILLS / f"{skill_name}.md"
            if path.exists():
                adjacent.append({
                    "name": skill_name,
                    "path": str(path),
                    "domain": meta.get("domain", ""),
                    "relevance": "direct",
                    "version": meta.get("version", 0),
                })
    
    # Also scan by domain from TASK_TO_WORKER mapping
    from .leader import classify_request
    return adjacent


class SkillForge:
    """Creates, calibrates, and evolves worker skills."""
    
    def forge_skill(self, worker_name: str, task_type: str, task_title: str,
                    request: str, sources: list[dict] = None) -> dict:
        """Create a new skill from scratch or from references.
        
        Returns dict with skill_name and skill_path on success.
        """
        ensure_skill_registry()
        
        gap = estimate_skill_gap(worker_name, task_type, task_title)
        skill_name = gap["proposed_name"]
        domain = gap["domain"]
        
        # Check if already exists with this name
        skill_path = WORKER_SKILLS / f"{skill_name}.md"
        manifest = _load_manifest()
        forge_skills = manifest.setdefault("forge_skills", {})
        
        if skill_path.exists():
            return {"skill_name": skill_name, "skill_path": str(skill_path), "existing": True}
        
        # Build skill content from request + task info
        skill_content = self._build_skill_md(
            skill_name=skill_name,
            domain=domain,
            task_type=task_type,
            worker_name=worker_name,
            request=request,
            sources=sources or [],
        )
        
        write_text(skill_path, skill_content)
        
        # Register in manifest
        forge_skills[skill_name] = {
            "version": 1,
            "domain": domain,
            "task_types": [task_type, slug(domain)],
            "worker": worker_name,
            "description": gap["description"],
            "created_at": now(),
            "iteration_count": 0,
            "usage_count": 0,
        }
        _save_manifest(manifest)
        
        return {"skill_name": skill_name, "skill_path": str(skill_path), "existing": False}
    
    def _build_skill_md(self, skill_name: str, domain: str, task_type: str,
                        worker_name: str, request: str, sources: list[dict]) -> str:
        """Build a SKILL.md document for the forged skill."""
        refs = ""
        if sources:
            refs = "**References:**\n"
            for s in sources[:3]:
                refs += f"- {s.get('name', 'source')} ({s.get('relevance', 'general')})\n"
        
        return f"""---
name: {skill_name}
description: Auto-forged {domain} skill for {task_type} tasks ({worker_name})
version: 1.0.0
author: SkillForge (Cabinet Agent Framework)
forge:
  domain: {domain}
  task_type: {task_type}
  worker: {worker_name}
  source_request: |
    {request[:200]}
  adjacent_skills: {len(sources)}
  iteration_count: 0
  auto_created: true
---

# {skill_name}

## Overview

Auto-forged skill for domain **{domain}** via {worker_name}.
Created from user request: "{request[:100]}"

{refs}
## Input

- Task packet from framework dispatch
- User request context
- Existing project memory and state

## Process

1. Analyze the incoming task context
2. Map to {domain} domain operations
3. Execute with worker guidelines and gate constraints
4. Output structured results

## Output

- Task outputs in `runtime/outputs/`
- Updated state and memory
- Audit entries

## Quality Gates

- [ ] Output exists and is parseable
- [ ] Acceptance criteria met
- [ ] No forbidden paths touched
- [ ] Source attribution clear

## Pitfalls

- Initial version: may need calibration
- User feedback loop: expect iterations
"""
    
    def improve_skill_from_feedback(self, skill_name: str, feedback: str, task: dict) -> dict:
        """Improve a forged skill based on user feedback and task results."""
        ensure_skill_registry()
        skill_path = WORKER_SKILLS / f"{skill_name}.md"
        if not skill_path.exists():
            return {"error": "skill_not_found"}
        
        manifest = _load_manifest()
        meta = manifest.get("forge_skills", {}).get(skill_name, {})
        meta["iteration_count"] = meta.get("iteration_count", 0) + 1
        meta["last_feedback"] = feedback[:200]
        meta["last_improved"] = now()
        manifest["forge_skills"][skill_name] = meta
        _save_manifest(manifest)
        
        # Append feedback note to skill
        content = skill_path.read_text(encoding="utf-8")
        note = f"\n## Iteration {meta['iteration_count']}\n- User feedback: {feedback}\n- Timestamp: {now()}\n- Refined via: {task.get('task_id', 'unknown')}\n"
        content += note
        skill_path.write_text(content, encoding="utf-8")
        
        return {
            "skill_name": skill_name,
            "iteration": meta["iteration_count"],
            "version": meta.get("version", 1),
        }
    
    def calibrate_skill(self, skill_name: str, corrections: dict) -> dict:
        """Apply structured corrections to a skill's metadata and behavior.
        
        corrections can include:
        - name: rename skill
        - domain: change domain
        - task_types: update task type list
        - process: replace process steps
        - criteria: update quality gates
        """
        ensure_skill_registry()
        skill_path = WORKER_SKILLS / f"{skill_name}.md"
        if not skill_path.exists():
            return {"error": "skill_not_found"}
        
        manifest = _load_manifest()
        meta = manifest.get("forge_skills", {}).get(skill_name, {})
        
        if "domain" in corrections:
            meta["domain"] = corrections["domain"]
        if "task_types" in corrections:
            meta["task_types"] = corrections["task_types"]
        meta["calibrated_at"] = now()
        manifest["forge_skills"][skill_name] = meta
        _save_manifest(manifest)
        
        content = skill_path.read_text(encoding="utf-8")
        cal_note = f"\n## Calibration\n- Applied: {json.dumps(corrections, ensure_ascii=False)}\n- Timestamp: {now()}\n"
        content += cal_note
        skill_path.write_text(content, encoding="utf-8")
        
        return {"skill_name": skill_name, "calibrated": True}
