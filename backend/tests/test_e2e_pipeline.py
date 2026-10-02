"""
Comprehensive end-to-end integration test script for:
- Project Creation
- PDF Upload & Validation
- Background Ingest Pipeline (Parse, Chunk, Embed, Qdrant Index)
- Structured Paper Extraction & Analysis
- PDF File Serving (/api/papers/{id}/file)
- Semantic Literature Search & Grounded Answer Generation
- Research Gap Detection & Evidence Grounding
- Contradiction Analysis
- Landscape Synthesis
- Research Report Generation
"""

import time
import fitz
import httpx

BASE_URL = "http://localhost:8000/api"


def run_e2e_test():
    print("=" * 60)
    print("Starting Comprehensive RAG & Literature Analysis E2E Test")
    print("=" * 60)

    # 1. Create project
    print("\n1. Creating project...")
    r = httpx.post(
        f"{BASE_URL}/projects",
        json={"name": "Medical AI Benchmarks", "description": "Testing full RAG pipeline"},
    )
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    project = r.json()
    project_id = project["project_id"]
    print(f"   Project created: {project_id}")

    # 2. Make synthetic PDF
    print("\n2. Generating synthetic academic PDF with PyMuPDF...")
    doc = fitz.open()
    page1 = doc.new_page(width=595, height=842)
    page1.insert_text((50, 50), "Attention Transformers for Chest X-ray Classification", fontsize=18)
    page1.insert_text((50, 80), "Dr. Alice Smith, Prof. Robert Jones", fontsize=12)
    page1.insert_text((50, 120), "Abstract", fontsize=14)
    page1.insert_textbox(
        fitz.Rect(50, 140, 545, 240),
        "We introduce an attention-guided transformer model for chest radiograph anomaly detection. "
        "Our framework achieves 0.94 AUC on the benchmark dataset.",
        fontsize=10,
    )
    page1.insert_text((50, 260), "1. Introduction", fontsize=14)
    page1.insert_textbox(
        fitz.Rect(50, 280, 545, 380),
        "Accurate chest X-ray diagnosis requires capturing subtle localized opacities and global contextual dependencies. "
        "Prior work relied on standard CNN backbones.",
        fontsize=10,
    )
    page1.insert_text((50, 400), "2. Methodology", fontsize=14)
    page1.insert_textbox(
        fitz.Rect(50, 420, 545, 520),
        "We integrate multi-head cross-attention into a hierarchical vision backbone with cosine annealing schedules.",
        fontsize=10,
    )
    page1.insert_text((50, 540), "3. Limitations", fontsize=14)
    page1.insert_textbox(
        fitz.Rect(50, 560, 545, 660),
        "Our evaluation is restricted to a single hospital cohort and does not account for differences in scanner calibration across institutions.",
        fontsize=10,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    print("   PDF generated successfully.")

    # 3. Upload PDF
    print("\n3. Uploading PDF to /api/projects/{id}/papers/upload...")
    files = {"file": ("radiology_attention.pdf", pdf_bytes, "application/pdf")}
    upload_resp = httpx.post(f"{BASE_URL}/projects/{project_id}/papers/upload", files=files)
    assert upload_resp.status_code == 202, f"Expected 202, got {upload_resp.status_code}: {upload_resp.text}"
    upload_data = upload_resp.json()
    job_id = upload_data["job_id"]
    paper_id = upload_data["paper"]["paper_id"]
    print(f"   Upload accepted. Job ID: {job_id}, Paper ID: {paper_id}")

    # 4. Poll job
    print("\n4. Polling ingestion job status...")
    succeeded = False
    for i in range(25):
        time.sleep(1)
        j_resp = httpx.get(f"{BASE_URL}/jobs/{job_id}")
        j_data = j_resp.json()
        status = j_data["status"]
        stage = j_data.get("stage")
        progress = j_data.get("progress")
        print(f"   Poll {i+1}: status={status}, stage={stage}, progress={progress}")
        if status == "SUCCEEDED":
            succeeded = True
            break
        elif status == "FAILED":
            raise RuntimeError(f"Job failed: {j_data.get('error')}")

    assert succeeded, "Job did not complete in time"
    print("   Ingestion job completed successfully!")

    # 5. Check paper details & analysis
    print("\n5. Checking paper details and structured analysis...")
    p_resp = httpx.get(f"{BASE_URL}/papers/{paper_id}")
    assert p_resp.status_code == 200
    p_json = p_resp.json()
    paper = p_json["paper"]
    analysis = p_json.get("analysis")
    print(f"   Paper status: {paper['status']}, title: '{paper['title']}'")
    assert paper["status"] in ("INDEXED", "ANALYZED")
    assert analysis is not None, "Paper analysis should be present"
    print(f"   Extracted problem: {analysis.get('problem')[:60]}...")
    print(f"   Extracted limitations: {len(analysis.get('limitations', []))} found")
    assert len(analysis.get("limitations", [])) > 0

    # 6. Check chunks
    print("\n6. Checking chunks in database...")
    c_resp = httpx.get(f"{BASE_URL}/papers/{paper_id}/chunks")
    assert c_resp.status_code == 200
    chunks = c_resp.json()
    print(f"   Total chunks extracted and indexed: {len(chunks)}")
    assert len(chunks) >= 3

    # 7. Check PDF file serving
    print("\n7. Checking PDF file serving endpoint...")
    f_resp = httpx.get(f"{BASE_URL}/papers/{paper_id}/file")
    assert f_resp.status_code == 200
    assert f_resp.headers.get("content-type") == "application/pdf"
    assert len(f_resp.content) == len(pdf_bytes)
    print(f"   PDF file downloaded accurately ({len(f_resp.content)} bytes).")

    # 8. Test Search & RAG
    print("\n8. Testing semantic literature search and grounded answer...")
    s_resp = httpx.post(
        f"{BASE_URL}/search",
        json={
            "project_id": project_id,
            "query": "What are the limitations of this model regarding hospital cohort?",
            "generate_answer": True,
        },
    )
    assert s_resp.status_code == 200
    search_res = s_resp.json()
    print(f"   Intent: {search_res.get('intent')}")
    print(f"   Insufficient evidence: {search_res.get('insufficient_evidence')}")
    print(f"   Answer: {search_res.get('answer')[:120]}...")
    print(f"   Sources found: {len(search_res.get('sources', []))}")
    assert len(search_res.get("sources", [])) > 0
    top_source = search_res["sources"][0]
    print(f"   Top source: [Page {top_source['page']}, {top_source['section']}] {top_source['text'][:80]}...")

    # 9. Test Gaps Endpoint
    print("\n9. Testing Research Gaps endpoint...")
    g_resp = httpx.get(f"{BASE_URL}/projects/{project_id}/gaps")
    assert g_resp.status_code == 200
    gaps = g_resp.json()
    print(f"   Gaps found: {len(gaps)}")
    assert len(gaps) > 0
    top_gap = gaps[0]
    print(f"   Top Gap: '{top_gap.get('topic')}' (Confidence: {top_gap.get('confidence')}%)")
    print(f"   Suggested question: {top_gap.get('suggestedQuestion')}")
    assert len(top_gap.get("evidence", [])) > 0
    print(f"   Evidence count: {len(top_gap['evidence'])}")

    # 10. Test Landscape Endpoint
    print("\n10. Testing Landscape endpoint...")
    l_resp = httpx.get(f"{BASE_URL}/projects/{project_id}/landscape")
    assert l_resp.status_code == 200
    landscape = l_resp.json()
    print(f"   Methodologies: {landscape.get('methodologies')}")
    print(f"   Repeated limitations: {len(landscape.get('repeatedLimitations', []))}")
    assert len(landscape.get("methodologies", [])) > 0

    # 11. Test Reports Endpoint
    print("\n11. Testing Report generation and export...")
    rep_resp = httpx.post(f"{BASE_URL}/projects/{project_id}/reports/generate")
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    markdown = rep_data.get("markdown", "")
    assert len(markdown) > 100
    print(f"   Report generated successfully! Length: {len(markdown)} characters.")
    print("   First 150 chars:\n" + markdown[:150])

    print("\n" + "=" * 60)
    print(">>> ALL 11 END-TO-END RAG & PLATFORM TESTS PASSED SUCCESSFULLY! <<<")
    print("=" * 60)


if __name__ == "__main__":
    run_e2e_test()
