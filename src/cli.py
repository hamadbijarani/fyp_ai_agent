from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.adapters.message_schema import Message
from src.adapters.whatsapp_adapter import WhatsAppImporter
from src.config import load_settings
from src.pipeline import Pipeline
from src.retrieval.hybrid import HybridRetriever
from src.security.filesystem_auth import FilesystemAuthorizer


def build_pipeline():
    auth = FilesystemAuthorizer()
    retriever = HybridRetriever(auth)
    # load existing index if present
    cfg = load_settings()
    idx = cfg["retrieval"]["index_path"]
    meta = cfg["retrieval"]["metadata_path"]
    try:
        retriever.load(idx, meta)
    except Exception:
        pass
    return Pipeline(context_builder=__import__("src.context.builder", fromlist=["ContextBuilder"]).ContextBuilder(retriever))


def cmd_ingest(args):
    auth = FilesystemAuthorizer()
    retriever = HybridRetriever(auth, chunk_size=load_settings()["app"]["chunk_size"], overlap=load_settings()["app"]["chunk_overlap"])
    if args.path:
        n = retriever.index_file(args.path)
        print(f"Indexed {n} chunks from {args.path}")
    else:
        n = retriever.index_authorized()
        print(f"Indexed {n} chunks from authorized folders")
    retriever.save(load_settings()["retrieval"]["index_path"], load_settings()["retrieval"]["metadata_path"])


def cmd_search(args):
    pipeline = build_pipeline()
    # reuse retriever via pipeline context builder
    cb = pipeline.context_builder
    hits = cb.retriever.search(args.query)
    print(json.dumps(hits, indent=2, default=str))


def cmd_draft(args):
    msg = Message(id=args.id, source=args.source, sender=args.sender, timestamp=__import__("datetime").datetime.now(), subject=args.subject, body=args.body)
    pipeline = build_pipeline()
    res = pipeline.process(msg)
    print(json.dumps(res["draft"].model_dump(), indent=2, default=str))


def cmd_audit(args):
    from src.storage.audit_log import AuditLog

    log = AuditLog()
    print(json.dumps(log.recent(args.limit), indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(prog="sla")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ingest")
    p.add_argument("--path", help="file or (omit) all authorized")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("search")
    p.add_argument("query")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("draft")
    p.add_argument("--id", default="msg1")
    p.add_argument("--source", choices=["email", "whatsapp"], default="email")
    p.add_argument("--sender", default="unknown")
    p.add_argument("--subject", default=None)
    p.add_argument("--body", required=True)
    p.set_defaults(func=cmd_draft)

    p = sub.add_parser("audit")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
