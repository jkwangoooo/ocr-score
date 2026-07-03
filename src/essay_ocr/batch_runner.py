#!/usr/bin/env python3
"""Batch OCR paper B-side images with configurable glob pattern."""

import argparse
import csv
from pathlib import Path
import sys
import traceback

import ocr_paddle_aistudio as paddle_ocr


def parse_student(folder_name: str) -> tuple[str, str]:
    if "_" not in folder_name:
        return folder_name, ""
    return folder_name.rsplit("_", 1)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def write_manifest(rows: list[dict], out_path: Path) -> None:
    fieldnames = ["name", "studentNo", "sourceFile", "outputDir", "status", "jobId", "textChars", "error"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text_summary(rows: list[dict], out_path: Path) -> None:
    fieldnames = ["name", "studentNo", "status", "text"]
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            text = read_text(Path(row["outputDir"]) / "text.txt") if row["status"] in {"ok", "skipped"} else ""
            writer.writerow({"name": row["name"], "studentNo": row["studentNo"], "status": row["status"], "text": text})


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch OCR B-side essay pages.")
    parser.add_argument("--input", required=True, help="Base directory, e.g. exam_x/papers")
    parser.add_argument("--pattern", default="*/B.jpg", help="Glob pattern under --input")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--token", default=None, help="API token; falls back to PADDLEOCR_TOKEN")
    parser.add_argument("--model", default=paddle_ocr.DEFAULT_MODEL, choices=["PP-OCRv6", "PaddleOCR-VL-1.6"])
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    token = args.token or paddle_ocr.os.environ.get("PADDLEOCR_TOKEN")
    if not token:
        print("Error: missing token. Set PADDLEOCR_TOKEN or pass --token.", file=sys.stderr)
        return 2

    input_dir = Path(args.input)
    out_root = Path(args.out)
    files = sorted(input_dir.glob(args.pattern))
    if not files:
        print(f"Error: no files matching {input_dir / args.pattern}", file=sys.stderr)
        return 1

    rows = []
    for index, source in enumerate(files, start=1):
        name, student_no = parse_student(source.parent.name)
        out_dir = out_root / source.parent.name
        text_path = out_dir / "text.txt"
        row = {
            "name": name,
            "studentNo": student_no,
            "sourceFile": str(source),
            "outputDir": str(out_dir),
            "status": "pending",
            "jobId": "",
            "textChars": "0",
            "error": "",
        }
        print(f"[{index}/{len(files)}] {source}")
        try:
            if text_path.exists() and read_text(text_path) and not args.force:
                text = read_text(text_path)
                row["status"] = "skipped"
                row["textChars"] = str(len(text))
                print(f"  skipped existing text.txt chars={row['textChars']}")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                optional_payload = paddle_ocr.optional_payload_for_model(args.model)
                job_id = paddle_ocr.submit_job(str(source), token, optional_payload, args.model)
                row["jobId"] = job_id
                print(f"  job_id={job_id}")
                jsonl_url = paddle_ocr.poll_job(job_id, token, args.interval, args.timeout)
                paddle_ocr.download_results(jsonl_url, out_dir)
                text = read_text(text_path)
                row["status"] = "ok"
                row["textChars"] = str(len(text))
                print(f"  ok chars={row['textChars']}")
        except Exception as exc:
            row["status"] = "failed"
            row["error"] = f"{type(exc).__name__}: {exc}"
            print(f"  failed: {row['error']}")
            traceback.print_exc()
        rows.append(row)
        write_manifest(rows, out_root / "manifest.csv")
        write_text_summary(rows, out_root / "essay_texts.csv")

    ok_count = sum(1 for r in rows if r["status"] in {"ok", "skipped"})
    failed_count = sum(1 for r in rows if r["status"] == "failed")
    print(f"done total={len(rows)} ok_or_skipped={ok_count} failed={failed_count}")
    print(f"manifest={out_root / 'manifest.csv'}")
    print(f"texts={out_root / 'essay_texts.csv'}")
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
