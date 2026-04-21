import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

st.set_page_config(page_title="Semantic RAG UI", layout="wide")
st.title("Semantic RAG")
st.caption("Ingest PDF documents and run semantic search with project-based access control.")

def fetch_projects():
    try:
        resp = requests.get(f"{API_BASE_URL}/projects", timeout=30)
        resp.raise_for_status()
        return resp.json().get("projects", [])
    except Exception as exc:
        st.error(f"Could not load projects: {exc}")
        return []

tab_ingest, tab_search = st.tabs(["Ingest PDFs", "Search"])

with tab_ingest:
    st.subheader("Upload and ingest PDF documents")

    projects = fetch_projects()

    if not projects:
        st.warning("No projects found. Seed projects first before using upload.")
    else:
        project_options = {
            f"{p['name']} (ID: {p['id']})": p["id"]
            for p in projects
        }

        selected_project_label = st.selectbox(
            "Target Project",
            options=list(project_options.keys())
        )
        selected_project_id = project_options[selected_project_label]

        uploaded_files = st.file_uploader(
            "Upload PDF file(s)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Only PDF files are allowed."
        )

        if st.button("Ingest Uploaded PDFs", key="ingest_btn"):
            if not uploaded_files:
                st.warning("Please upload at least one PDF file.")
            else:
                results = []
                progress = st.progress(0)
                status_box = st.empty()

                for idx, uploaded_file in enumerate(uploaded_files, start=1):
                    status_box.info(f"Ingesting {uploaded_file.name} ...")
                    try:
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf"
                            )
                        }
                        data = {
                            "project_id": str(selected_project_id)
                        }

                        resp = requests.post(
                            f"{API_BASE_URL}/ingest/upload",
                            files=files,
                            data=data,
                            timeout=300,
                        )
                        resp.raise_for_status()
                        payload = resp.json()
                        results.append({
                            "filename": uploaded_file.name,
                            "status": "success",
                            "response": payload,
                        })
                    except Exception as exc:
                        results.append({
                            "filename": uploaded_file.name,
                            "status": "failed",
                            "error": str(exc),
                        })

                    progress.progress(idx / len(uploaded_files))

                status_box.success("Upload ingestion finished.")

                success_count = sum(1 for r in results if r["status"] == "success")
                fail_count = len(results) - success_count

                st.write(f"**Success:** {success_count} | **Failed:** {fail_count}")

                for item in results:
                    with st.container(border=True):
                        st.markdown(f"### {item['filename']}")
                        if item["status"] == "success":
                            data = item["response"].get("data", {})
                            st.success("Ingested successfully")
                            st.write(
                                f"**Document ID:** {data.get('document_id')} | "
                                f"**Project ID:** {data.get('project_id')} | "
                                f"**Pages:** {data.get('page_count')} | "
                                f"**Chunks:** {data.get('chunk_count')}"
                            )
                        else:
                            st.error(item["error"])

with tab_search:
    st.subheader("Semantic search")

    with st.form("search_form"):
        col1, col2 = st.columns([1, 3])

        with col1:
            user_id = st.text_input("User ID", value="user_1", placeholder="e.g. user_1")
            top_k = st.slider("Top K", min_value=1, max_value=20, value=5)

        with col2:
            query = st.text_area(
                "Query",
                value="",
                placeholder="Enter your search query here...",
                height=120,
            )

        submitted = st.form_submit_button("Search")

    if submitted:
        if not user_id.strip():
            st.warning("Please enter a user_id.")
        elif not query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Searching..."):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/search",
                        json={
                            "user_id": user_id.strip(),
                            "query": query.strip(),
                            "top_k": top_k,
                        },
                        timeout=60,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    results = data.get("results", [])

                    st.success(f"Found {len(results)} result(s).")

                    if not results:
                        st.info("No results found.")
                    else:
                        for idx, item in enumerate(results, start=1):
                            with st.container(border=True):
                                st.markdown(f"### {idx}. {item['document_name']}")
                                st.markdown(
                                    f"**Page:** {item['page_number']} | "
                                    f"**Project ID:** {item['project_id']} | "
                                    f"**Score:** {item['similarity_score']}"
                                )
                                snippet = item["chunk_text"][:700]
                                if len(item["chunk_text"]) > 700:
                                    snippet += "..."
                                st.write(snippet)

                except requests.HTTPError as exc:
                    st.error(f"API error: {exc.response.status_code} - {exc.response.text}")
                except Exception as exc:
                    st.error(f"Search failed: {exc}")