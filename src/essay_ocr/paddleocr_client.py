#!/usr/bin/env python3
"""Run PaddleOCR AIStudio OCR for one local file or URL.

Usage:
  export PADDLEOCR_TOKEN='your-token'
  python ocr_paddle_aistudio.py papers/学生/A.jpg --out output/ocr_test

The token can also be passed with --token for a quick local test, but the
preferred path is the PADDLEOCR_TOKEN environment variable.
"""

import argparse
import json
import os
from pathlib import Path
import sys
import time

import requests

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
DEFAULT_MODEL = "PP-OCRv6"

DEFAULT_OPTIONAL_PAYLOAD = {
    "markdownIgnoreLabels": [],
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useTextlineOrientation": False,
    "textDetLimitType": "min",
    "textDetLimitSideLen": 64,
    "textDetThresh": 0.3,
    "textDetBoxThresh": 0.6,
    "textDetUnclipRatio": 1.5,
    "textRecScoreThresh": 0,
}

VL_OPTIONAL_PAYLOAD = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}


def optional_payload_for_model(model: str) -> dict:
    if model == "PaddleOCR-VL-1.6":
        return VL_OPTIONAL_PAYLOAD
    return DEFAULT_OPTIONAL_PAYLOAD


def submit_job(file_path: str, token: str, optional_payload: dict, model: str = DEFAULT_MODEL) -> str:
    headers = {"Authorization": f"bearer {token}"}

    if file_path.startswith("http://") or file_path.startswith("https://"):
        headers["Content-Type"] = "application/json"
        payload = {
            "fileUrl": file_path,
            "model": model,
            "optionalPayload": optional_payload,
        }
        response = requests.post(JOB_URL, json=payload, headers=headers, timeout=60)
    else:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        data = {
            "model": model,
            "optionalPayload": json.dumps(optional_payload, ensure_ascii=False),
        }
        with path.open("rb") as f:
            response = requests.post(
                JOB_URL,
                headers=headers,
                data=data,
                files={"file": f},
                timeout=120,
            )

    if response.status_code != 200:
        raise RuntimeError(f"Submit failed: HTTP {response.status_code}: {response.text}")

    payload = response.json()
    try:
        return payload["data"]["jobId"]
    except KeyError as exc:
        raise RuntimeError(f"Submit response missing jobId: {payload}") from exc


def poll_job(job_id: str, token: str, interval: int, timeout_seconds: int) -> str:
    headers = {"Authorization": f"bearer {token}"}
    deadline = time.time() + timeout_seconds

    while True:
        if time.time() > deadline:
            raise TimeoutError(f"OCR job timed out after {timeout_seconds}s: {job_id}")

        response = requests.get(f"{JOB_URL}/{job_id}", headers=headers, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Poll failed: HTTP {response.status_code}: {response.text}")

        payload = response.json()
        data = payload.get("data", {})
        state = data.get("state")

        if state == "pending":
            print("state=pending")
        elif state == "running":
            progress = data.get("extractProgress", {})
            total_pages = progress.get("totalPages")
            extracted_pages = progress.get("extractedPages")
            if total_pages is not None and extracted_pages is not None:
                print(f"state=running pages={extracted_pages}/{total_pages}")
            else:
                print("state=running")
        elif state == "done":
            progress = data.get("extractProgress", {})
            print(
                "state=done "
                f"pages={progress.get('extractedPages')} "
                f"start={progress.get('startTime')} "
                f"end={progress.get('endTime')}"
            )
            result_url = data.get("resultUrl", {}).get("jsonUrl")
            if not result_url:
                raise RuntimeError(f"Done response missing resultUrl.jsonUrl: {payload}")
            return result_url
        elif state == "failed":
            raise RuntimeError(f"OCR job failed: {data.get('errorMsg')}")
        else:
            raise RuntimeError(f"Unknown OCR job state: {payload}")

        time.sleep(interval)


def download_results(jsonl_url: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "result.jsonl"
    text_path = out_dir / "text.txt"
    images_dir = out_dir / "images"
    images_dir.mkdir(exist_ok=True)

    response = requests.get(jsonl_url, timeout=120)
    response.raise_for_status()
    jsonl_path.write_text(response.text, encoding="utf-8")

    text_lines = []
    page_num = 0
    for line_num, line in enumerate(response.text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            result = json.loads(line)["result"]
        except (json.JSONDecodeError, KeyError) as exc:
            raise RuntimeError(f"Invalid JSONL at line {line_num}: {line[:200]}") from exc

        for res in result.get("layoutParsingResults", []):
            markdown = res.get("markdown", {})
            markdown_text = markdown.get("text") if isinstance(markdown, dict) else None
            if markdown_text:
                md_path = out_dir / f"doc_{page_num}.md"
                md_path.write_text(markdown_text, encoding="utf-8")
                text_lines.append(markdown_text)

            image_items = markdown.get("images", {}).items() if isinstance(markdown, dict) else []
            for img_path, img_url in image_items:
                image_path = out_dir / img_path
                image_path.parent.mkdir(parents=True, exist_ok=True)
                img_response = requests.get(img_url, timeout=120)
                if img_response.status_code == 200:
                    image_path.write_bytes(img_response.content)
                    print(f"image_saved={image_path}")

            for img_name, img_url in res.get("outputImages", {}).items():
                img_response = requests.get(img_url, timeout=120)
                if img_response.status_code == 200:
                    image_path = images_dir / f"{img_name}_{page_num}.jpg"
                    image_path.write_bytes(img_response.content)
                    print(f"image_saved={image_path}")
                else:
                    print(f"image_download_failed status={img_response.status_code} url={img_url}")
            page_num += 1

        for res in result.get("ocrResults", []):
            if "markdown" in res and res["markdown"]:
                text_lines.append(res["markdown"])
            elif "texts" in res and res["texts"]:
                text_lines.extend(str(item) for item in res["texts"])
            else:
                pruned_result = res.get("prunedResult", {})
                rec_texts = pruned_result.get("rec_texts", [])
                if rec_texts:
                    text_lines.extend(str(item) for item in rec_texts)

            image_url = res.get("ocrImage")
            if image_url:
                img_response = requests.get(image_url, timeout=120)
                if img_response.status_code == 200:
                    image_path = images_dir / f"img_output_{page_num}.jpg"
                    image_path.write_bytes(img_response.content)
                    print(f"image_saved={image_path}")
                else:
                    print(f"image_download_failed status={img_response.status_code} url={image_url}")
            page_num += 1

    text_path.write_text("\n\n".join(text_lines), encoding="utf-8")
    print(f"jsonl_saved={jsonl_path}")
    print(f"text_saved={text_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PaddleOCR AIStudio OCR.")
    parser.add_argument("file", help="Local file path or http(s) file URL")
    parser.add_argument("--out", default="output/ocr", help="Output directory")
    parser.add_argument("--token", default=os.environ.get("PADDLEOCR_TOKEN"), help="API token; prefer PADDLEOCR_TOKEN env var")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=["PP-OCRv6", "PaddleOCR-VL-1.6"], help="OCR model")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--timeout", type=int, default=600, help="OCR job timeout in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.token:
        print("Error: missing token. Set PADDLEOCR_TOKEN or pass --token.", file=sys.stderr)
        return 2

    print(f"processing={args.file}")
    print(f"model={args.model}")
    optional_payload = optional_payload_for_model(args.model)
    job_id = submit_job(args.file, args.token, optional_payload, args.model)
    print(f"job_id={job_id}")
    jsonl_url = poll_job(job_id, args.token, args.interval, args.timeout)
    download_results(jsonl_url, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
