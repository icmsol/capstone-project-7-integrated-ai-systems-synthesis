"""Colab/Jupyter presentation layer for the Project 7 operator workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re

from .operator_workflow import OperatorWorkflow, OperatorWorkflowError


def _file_upload_bytes(upload: Any) -> tuple[str, bytes]:
    value = upload.value
    if not value:
        raise OperatorWorkflowError("Select a solicitation/source file first.")
    if isinstance(value, dict):
        name, metadata = next(iter(value.items()))
        content = metadata["content"]
    else:
        item = value[0]
        name = item["name"]
        content = item["content"]
    return str(name), bytes(content)


def _parse_optional_number(value: str) -> dict[str, Any] | None:
    cleaned = value.strip().replace("$", "").replace(",", "")
    if not cleaned:
        return None
    return {"amount": float(cleaned), "currency": "USD"}


def _parse_optional_int(value: str) -> int | None:
    cleaned = value.strip()
    return int(cleaned) if cleaned else None


def _format_operator_money(value: Any) -> str:
    """Render structured money cleanly without changing the underlying JSON."""
    if value in (None, "", {}):
        return "Not stated"
    if isinstance(value, dict):
        amount = value.get("amount")
        currency = str(value.get("currency") or "USD")
        if isinstance(amount, (int, float)):
            if float(amount).is_integer():
                amount_text = f"${amount:,.0f}"
            else:
                amount_text = f"${amount:,.2f}"
            return f"{amount_text} {currency}"
    return str(value)


def _operator_packet_markdown(packet: dict[str, Any]) -> str:
    """Render a Colab-stable, table-free reviewer view of the packet.

    The canonical packet JSON remains unchanged. This function is presentation-only
    and deliberately avoids Markdown tables because Colab may collapse table headers.
    """
    opportunity = packet["opportunity_summary"]
    alignment = packet["organization_fit_summary"]
    history = packet["historical_context_summary"]
    triage = packet["clause_triage_summary"]
    evidence = packet["evidence_summary"]
    recommendation = packet["recommendation"]

    lines = [
        "# Integrated Human Decision-Support Packet",
        "",
        "## Packet Control",
        f"- **Packet ID:** `{packet['packet_id']}`",
        f"- **Case ID:** `{packet['case_id']}`",
        f"- **Status:** `{packet['packet_status']}`",
        f"- **Generated:** `{packet['generated_at']}`",
        "- **Final decision:** Pending authorized human disposition",
        f"- **External actions:** `{packet['external_actions_performed']}`",
        "",
        "## Executive Summary",
        "",
        packet["executive_summary"],
        "",
        "## Opportunity",
        f"- **Agency:** {opportunity['agency']}",
        f"- **Solicitation:** `{opportunity['solicitation_id']}`",
        f"- **Title:** {opportunity['title']}",
        f"- **Status:** `{opportunity['status']}`",
        f"- **Due:** `{opportunity['due_at']}`",
        f"- **Jurisdiction:** {opportunity['jurisdiction']}",
        f"- **Procurement method:** {opportunity['procurement_method']}",
        f"- **Estimated value:** {_format_operator_money(opportunity.get('estimated_value'))}",
        "",
        "## Configurable Organization Alignment",
        f"- **Alignment:** {alignment['alignment_label']}",
        f"- **Alignment score:** `{alignment['alignment_score']:.2f}`",
        f"- **Staffing families:** {', '.join(alignment['staffing_families']) or 'None mapped'}",
        "",
        "### Matched capabilities",
    ]
    if alignment["matched_capability_ids"]:
        lines.extend(
            f"- `{capability_id}` — {capability_name}"
            for capability_id, capability_name in zip(
                alignment["matched_capability_ids"],
                alignment["matched_capability_names"],
            )
        )
    else:
        lines.append("- No configured capability met the alignment threshold.")
    lines.extend([
        "",
        "> Alignment is screening evidence—not proof of eligibility, capacity, award probability, or final strategic fit.",
        "",
        "## Historical Context",
        f"- **Frozen source period:** `{history['source_period']['start_date']}` through `{history['source_period']['end_date']}`",
        f"- **Source records:** `{history['source_records']:,}`",
        f"- **Matched historical records:** `{history['matched_historical_records']}`",
        "",
        history["interpretation"],
        "",
        "## Clause-Theme Triage",
    ])
    for item in triage["predictions"]:
        reasons = ", ".join(item.get("reason_codes", [])) or "none"
        lines.extend([
            f"### `{item['passage_id']}` — {item['predicted_category']}",
            f"- **Confidence:** `{item['confidence']:.6f}`",
            f"- **Decision:** `{item['decision']}`",
            f"- **Domain warning:** `{item['domain_warning']}`",
            f"- **Truncated:** `{item['truncated']}`",
            f"- **Reason codes:** `{reasons}`",
        ])
    if triage.get("domain_warning_count", 0):
        lines.extend([
            "",
            "> **Domain-shift safeguard active:** confidence does not establish semantic correctness. "
            "Use the classifications only for triage and review the original language with a qualified reviewer.",
        ])
    lines.extend([
        "",
        "## Validated Evidence",
    ])
    if evidence["citations"]:
        for item in evidence["citations"]:
            lines.extend([
                f"- `{item['evidence_id']}` — {item['citation_text']}",
                f"  - Source: {item['source_locator']}",
            ])
    else:
        lines.append("- No registered evidence record met the configured acceptance criteria for the assessed claims.")
    lines.extend([
        f"- **Evidence items:** `{evidence['evidence_item_count']}`",
        f"- **Sufficient assessments:** `{evidence['sufficient_assessment_count']}`",
        f"- **Material conflicts:** `{evidence['material_conflict_count']}`",
        "",
        "> Retrieved evidence is not automatically treated as sufficient support. The registered FAR corpus is bounded and does not replace review of the complete current official acquisition record.",
        "",
        "## Nonbinding Recommendation",
        f"### {recommendation['recommendation_label']}",
        f"- **Recommendation code:** `{recommendation['recommendation_code']}`",
        f"- **Recommendation strength:** `{recommendation['recommendation_strength']:.2f}`",
        f"- **Required reviewer:** {recommendation['required_human_reviewer']['role_name']}",
        f"- **Next action:** {recommendation['recommended_next_action']}",
        "",
        f"> {recommendation['nonbinding_disclosure']}",
        "",
        "### Required conditions",
    ])
    lines.extend(f"- {item}" for item in recommendation["conditions"])
    lines.extend(["", "### Missing information"])
    lines.extend(f"- {item}" for item in recommendation["missing_information"])
    lines.extend(["", "## Unresolved Issues"])
    for item in packet["unresolved_issues"]:
        lines.extend([
            f"### `{item['issue_id']}` — {item['severity'].upper()} / {item['category']}",
            f"- **Description:** {item['description']}",
            f"- **Required action:** {item['required_action']}",
        ])
    lines.extend([
        "",
        "## Authorized Human Disposition — Pending",
        f"- **Required reviewer:** {packet['human_review']['required_reviewer']['role_name']}",
        "- Accept the nonbinding recommendation",
        "- Accept with modified conditions",
        "- Reject the recommendation",
        "- Defer pending information",
        "- Escalate to another authorized reviewer",
        "",
        "**Required disposition record:** reviewer identity and authorized role; selected disposition; rationale of at least 20 characters; modified conditions when applicable; escalation target when applicable; decision timestamp.",
        "",
        "**The original system recommendation remains separate and immutable.**",
        "",
        "## Audit and Integrity",
        f"- **Source case-state SHA-256:** `{packet['source_case_state_sha256']}`",
        f"- **Packet audit events:** `{', '.join(packet['audit_event_ids'][-2:])}`",
        f"- **Total case audit events:** `{len(packet['audit_event_ids'])}`",
        "- **Final decision in packet:** `null`",
        f"- **External actions performed:** `{packet['external_actions_performed']}`",
        "",
        "## Production Boundary",
        "",
        packet["production_boundary"],
    ])
    return "\n".join(lines)


def launch_operator_interface(
    *,
    repo_root: Path,
    workspace_parent: Path = Path("/content/project7_operator_cases"),
) -> None:
    """Render the single-entry-point Project 7 operator interface."""

    import ipywidgets as widgets
    from IPython.display import HTML, Markdown, clear_output, display

    repo_root = Path(repo_root).resolve()
    workspace_parent = Path(workspace_parent).resolve()
    workspace_parent.mkdir(parents=True, exist_ok=True)

    workflow: OperatorWorkflow | None = None
    passage_rows: list[dict[str, Any]] = []

    banner = widgets.HTML(
        value=(
            "<div style='padding:14px;border:1px solid #9fbad0;border-radius:8px;"
            "background:#eef5fb'>"
            "<b>Project 7 — Integrated AI Decision-Support Operator</b><br>"
            "Controlled capstone prototype. Recommendations are nonbinding; "
            "final human authority is required; no autonomous external action is performed."
            "</div>"
        )
    )
    metadata_warning = widgets.HTML(
        value=(
            "<div style='padding:10px;border-left:4px solid #c88a00;background:#fff8e5'>"
            "<b>Operator control:</b> Project 7 does not independently extract or "
            "semantically verify the structured opportunity metadata against the uploaded "
            "PDF. Confirm the fields below against the source before validating intake."
            "</div>"
        )
    )

    status_html = widgets.HTML()
    global_output = widgets.Output(
        layout={"border": "1px solid #ddd", "padding": "8px"}
    )

    def set_status() -> None:
        nonlocal workflow
        if workflow is None:
            status_html.value = (
                "<b>Current status:</b> No active case. Start a new case or restore a bundle."
            )
            return
        summary = workflow.status_summary()
        status_html.value = (
            f"<b>Current status:</b> stage=<code>{summary['operator_stage']}</code> | "
            f"case=<code>{summary['case_id'] or 'pending'}</code> | "
            f"case_status=<code>{summary['case_status'] or 'pending'}</code>"
        )

    # ------------------------------------------------------------------
    # New case / restore
    # ------------------------------------------------------------------
    source_upload = widgets.FileUpload(
        accept=".pdf,.txt,.docx",
        multiple=False,
        description="Select source",
    )
    bundle_upload = widgets.FileUpload(
        accept=".zip",
        multiple=False,
        description="Select bundle",
    )
    restore_button = widgets.Button(
        description="Restore Case Bundle",
        button_style="info",
        icon="upload",
    )
    restore_output = widgets.Output()

    # ------------------------------------------------------------------
    # Intake fields
    # ------------------------------------------------------------------
    source_portal = widgets.Text(
        description="Source:",
        placeholder="e.g., Cal eProcure, email from agency",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    jurisdiction = widgets.Text(
        description="Jurisdiction:",
        value="California",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    agency = widgets.Text(
        description="Issuing agency:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    solicitation_id = widgets.Text(
        description="Solicitation ID:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    title = widgets.Text(
        description="Title:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    description = widgets.Textarea(
        description="Scope description:",
        rows=4,
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    status = widgets.Text(
        description="Status:",
        value="Open",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    posted_at = widgets.Text(
        description="Posted date:",
        placeholder="YYYY-MM-DD",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    due_at = widgets.Text(
        description="Due date:",
        placeholder="YYYY-MM-DD",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    place = widgets.Textarea(
        description="Place of performance:",
        rows=2,
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    procurement = widgets.Text(
        description="Procurement method:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    vehicle = widgets.Text(
        description="Contract vehicle:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    estimated_value = widgets.Text(
        description="Est. value USD:",
        placeholder="Leave blank if unknown",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    freshness = widgets.Text(
        description="Data freshness days:",
        placeholder="Leave blank if unknown",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )

    intake_button = widgets.Button(
        description="1. Validate Intake",
        button_style="primary",
        icon="check",
    )
    intake_output = widgets.Output()

    # ------------------------------------------------------------------
    # Profile / alignment
    # ------------------------------------------------------------------
    profile_options: list[tuple[str, str]] = []
    temp_workflow = OperatorWorkflow(
        repo_root=repo_root,
        workspace_root=workspace_parent / "_profile_discovery",
    )
    for profile in temp_workflow.available_profiles():
        profile_options.append(
            (
                f"{profile['organization_name']} ({profile['organization_id']})",
                profile["path"],
            )
        )
    import shutil
    shutil.rmtree(temp_workflow.workspace_root, ignore_errors=True)

    profile_dropdown = widgets.Dropdown(
        options=profile_options,
        description="Organization:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    alignment_button = widgets.Button(
        description="2. Analyze Organization Fit",
        button_style="primary",
        icon="search",
    )
    alignment_output = widgets.Output()

    # ------------------------------------------------------------------
    # Clause passages
    # ------------------------------------------------------------------
    passage_container = widgets.VBox()

    def refresh_passages() -> None:
        passage_container.children = tuple(
            row["box"] for row in passage_rows
        )

    def add_passage_row(_=None) -> None:
        index = len(passage_rows) + 1
        section = widgets.Text(
            description=f"Section {index}:",
            placeholder="Source section / page reference",
            layout=widgets.Layout(width="95%"),
            style={"description_width": "100px"},
        )
        text = widgets.Textarea(
            description=f"Passage {index}:",
            rows=4,
            placeholder="Paste a relevant source passage here",
            layout=widgets.Layout(width="95%"),
            style={"description_width": "100px"},
        )
        remove = widgets.Button(
            description="Remove",
            button_style="warning",
            icon="trash",
            layout=widgets.Layout(width="110px"),
        )
        box = widgets.VBox([section, text, remove])

        row = {
            "section": section,
            "text": text,
            "remove": remove,
            "box": box,
        }
        passage_rows.append(row)

        def remove_row(_button, row=row) -> None:
            passage_rows.remove(row)
            refresh_passages()

        remove.on_click(remove_row)
        refresh_passages()

    add_passage_button = widgets.Button(
        description="Add Passage",
        icon="plus",
    )
    add_passage_button.on_click(add_passage_row)
    add_passage_row()

    source_domain = widgets.Dropdown(
        options=["public_sector", "commercial_contract"],
        value="public_sector",
        description="Source domain:",
        layout=widgets.Layout(width="60%"),
        style={"description_width": "140px"},
    )
    consequential = widgets.Checkbox(
        value=True,
        description="Consequential procurement/contract use",
        indent=False,
    )
    clause_button = widgets.Button(
        description="3. Run Clause Triage",
        button_style="primary",
        icon="tasks",
    )
    clause_output = widgets.Output()

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------
    evidence_button = widgets.Button(
        description="4. Run Evidence Review",
        button_style="primary",
        icon="book",
    )
    evidence_output = widgets.Output()

    # ------------------------------------------------------------------
    # Packet
    # ------------------------------------------------------------------
    packet_button = widgets.Button(
        description="5. Generate Recommendation & Packet",
        button_style="primary",
        icon="file",
    )
    packet_output = widgets.Output()

    # ------------------------------------------------------------------
    # Human disposition
    # ------------------------------------------------------------------
    roles_config = json.loads(
        (
            repo_root
            / "config"
            / "profiles"
            / "icm_reviewer_roles.json"
        ).read_text(encoding="utf-8")
    )
    role_options = [
        (f"{item['role_name']} ({item['role_id']})", item["role_id"])
        for item in roles_config["roles"]
    ]

    reviewer_identity = widgets.Text(
        description="Reviewer identity:",
        placeholder="Name or unique human identifier",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    reviewer_role = widgets.Dropdown(
        options=role_options,
        description="Reviewer role:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    disposition = widgets.Dropdown(
        options=[
            ("Accept recommendation", "accept"),
            ("Accept with modified conditions", "accept_with_modified_conditions"),
            ("Reject recommendation", "reject"),
            ("Defer pending information", "defer_pending_information"),
            ("Escalate to another reviewer", "escalate"),
        ],
        description="Disposition:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    rationale = widgets.Textarea(
        description="Rationale:",
        rows=4,
        placeholder="Required; at least 20 characters",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    modified = widgets.Textarea(
        description="Modified conditions:",
        rows=2,
        placeholder="Optional; separate multiple conditions with semicolons",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    escalation_target = widgets.Dropdown(
        options=[("Not applicable", "")] + role_options,
        description="Escalation target:",
        layout=widgets.Layout(width="95%"),
        style={"description_width": "170px"},
    )
    record_button = widgets.Button(
        description="6. Record Human Disposition",
        button_style="danger",
        icon="user",
    )
    disposition_output = widgets.Output()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    export_button = widgets.Button(
        description="Export Resumable Case Bundle",
        button_style="success",
        icon="download",
    )
    export_output = widgets.Output()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def show_error(output_widget: Any, exc: Exception) -> None:
        with output_widget:
            clear_output()
            display(
                HTML(
                    "<div style='padding:10px;background:#fdeaea;border-left:4px "
                    "solid #b3261e'><b>Action did not complete.</b><br>"
                    f"{type(exc).__name__}: {exc}</div>"
                )
            )

    def on_restore(_button) -> None:
        nonlocal workflow
        try:
            name, content = _file_upload_bytes(bundle_upload)
            incoming = workspace_parent / "_incoming_bundle.zip"
            incoming.write_bytes(content)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            destination = workspace_parent / f"restored_{stamp}"
            workflow = OperatorWorkflow.restore_case_bundle(
                repo_root=repo_root,
                bundle_path=incoming,
                destination_root=destination,
            )
            incoming.unlink(missing_ok=True)
            with restore_output:
                clear_output()
                display(Markdown(
                    f"**Case bundle restored.**  \n"
                    f"Stage: `{workflow.stage}`  \n"
                    f"Case: `{workflow.case_id}`  \n"
                    f"Workspace: `{workflow.workspace_root}`"
                ))
            set_status()
        except Exception as exc:
            show_error(restore_output, exc)

    def on_intake(_button) -> None:
        nonlocal workflow
        try:
            filename, content = _file_upload_bytes(source_upload)
            required = {
                "Source": source_portal.value,
                "Jurisdiction": jurisdiction.value,
                "Agency": agency.value,
                "Solicitation ID": solicitation_id.value,
                "Title": title.value,
            }
            missing = [label for label, value in required.items() if not value.strip()]
            if missing:
                raise OperatorWorkflowError(
                    "Required intake fields are missing: " + ", ".join(missing)
                )
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            slug = re.sub(
                r"[^A-Za-z0-9_-]+",
                "_",
                solicitation_id.value.strip(),
            ) or "case"
            workflow = OperatorWorkflow(
                repo_root=repo_root,
                workspace_root=workspace_parent / f"{slug}_{stamp}",
            )
            raw = {
                "source_portal": source_portal.value.strip(),
                "jurisdiction": jurisdiction.value.strip(),
                "agency": agency.value.strip(),
                "solicitation_id": solicitation_id.value.strip(),
                "title": title.value.strip(),
                "description": description.value.strip() or None,
                "status": status.value.strip() or None,
                "posted_at": posted_at.value.strip() or None,
                "due_at": due_at.value.strip() or None,
                "place_of_performance": place.value.strip() or None,
                "procurement_method": procurement.value.strip() or None,
                "contract_vehicle": vehicle.value.strip() or None,
                "estimated_value": _parse_optional_number(estimated_value.value),
                "data_freshness_days": _parse_optional_int(freshness.value),
            }
            result = workflow.run_intake(
                source_filename=filename,
                source_bytes=content,
                raw_opportunity=raw,
            )
            opp = result["normalized_opportunity"]
            with intake_output:
                clear_output()
                display(Markdown(
                    "### Intake validated\n"
                    f"- Case: `{result['case_state']['case_id']}`\n"
                    f"- Agency: **{opp['agency']}**\n"
                    f"- Solicitation: **{opp['solicitation_id']}**\n"
                    f"- Status: `{opp['status']}`\n"
                    f"- Source checksum: `{opp['source']['sha256']}`\n"
                    f"- Missing tracked fields: `{len(opp['missing_fields'])}`"
                ))
            set_status()
        except Exception as exc:
            show_error(intake_output, exc)

    def on_alignment(_button) -> None:
        try:
            if workflow is None:
                raise OperatorWorkflowError("Validate intake first.")
            if not profile_dropdown.value:
                raise OperatorWorkflowError("Select an organization profile.")
            result = workflow.run_alignment(
                profile_path=Path(profile_dropdown.value)
            )
            alignment = result["service_alignment"]
            history = result["historical_context"]
            lines = [
                "### Organization alignment",
                f"- Label: **{alignment['alignment_label']}**",
                f"- Score: **{alignment['alignment_score']:.4f}**",
                f"- Historical matches: **{history['matched_historical_records']:,}**",
                "",
                "**Matched capabilities**",
            ]
            for item in alignment["matched_capabilities"]:
                matched_terms = ", ".join(item.get("matched_terms", [])) or "none"
                lines.append(
                    f"- {item['capability_name']} — `{item['match_strength']}` "
                    f"(matched: {matched_terms})"
                )
            lines.extend(
                [
                    "",
                    "> Alignment is screening evidence, not proof of eligibility, "
                    "capacity, award probability, or final pursuit fit.",
                ]
            )
            with alignment_output:
                clear_output()
                display(Markdown("\n".join(lines)))
            set_status()
        except Exception as exc:
            show_error(alignment_output, exc)

    def on_clause(_button) -> None:
        try:
            if workflow is None:
                raise OperatorWorkflowError("Start a case first.")
            passages = []
            for index, row in enumerate(passage_rows, start=1):
                if not row["text"].value.strip():
                    continue
                passages.append(
                    {
                        "passage_id": f"PASSAGE-OPERATOR-{index:03d}",
                        "source_section": row["section"].value.strip(),
                        "text": row["text"].value.strip(),
                    }
                )
            result = workflow.run_clause_triage(
                passages=passages,
                source_domain=source_domain.value,
                consequential_use=consequential.value,
            )
            lines = ["### Clause-theme triage"]
            for item in result["predictions"]:
                lines.append(
                    f"- **{item['predicted_category']}** — "
                    f"confidence `{item['confidence']:.4f}` — "
                    f"`{item['decision']}` — "
                    f"reasons `{', '.join(item['reason_codes'])}`"
                )
            lines.append(
                "\n> Model output is triage only; it is not legal interpretation or approval."
            )
            if any(item.get("domain_warning") for item in result["predictions"]):
                lines.append(
                    "> **Domain-shift safeguard active:** model confidence does not establish "
                    "semantic correctness. Review the original language with a qualified "
                    "reviewer before relying on any predicted theme."
                )
            with clause_output:
                clear_output()
                display(Markdown("\n".join(lines)))
            set_status()
        except Exception as exc:
            show_error(clause_output, exc)

    def on_evidence(_button) -> None:
        try:
            if workflow is None:
                raise OperatorWorkflowError("Start a case first.")
            result = workflow.run_evidence()
            lines = ["### Evidence review"]
            for item in result["results"]:
                assessment = item["assessment"]
                lines.append(
                    f"- `{item['request_id']}` — "
                    f"**{assessment['sufficiency_status']}** — "
                    f"score `{assessment['evidence_score']:.3f}` — "
                    f"accepted items `{len(item['evidence_items'])}`"
                )
            case = result["updated_case_state"]
            lines.extend(
                [
                    "",
                    f"**Case status:** `{case['case_status']}`",
                    "",
                    "> The registered evidence corpus is bounded. No result is treated "
                    "as support merely because a semantically similar record exists.",
                ]
            )
            with evidence_output:
                clear_output()
                display(Markdown("\n".join(lines)))
            set_status()
        except Exception as exc:
            show_error(evidence_output, exc)

    def on_packet(_button) -> None:
        try:
            if workflow is None:
                raise OperatorWorkflowError("Start a case first.")
            result = workflow.run_packet()
            rec = result["recommendation"]
            packet = result["packet"]
            with packet_output:
                clear_output()
                display(Markdown(
                    "### Nonbinding recommendation\n"
                    f"**{rec['recommendation_code']} — "
                    f"{rec['recommendation_label']}**  \n"
                    f"Strength: `{rec['recommendation_strength']:.2f}`  \n"
                    f"Required reviewer: "
                    f"**{rec['required_human_reviewer']['role_name']}**\n\n"
                    "---\n"
                ))
                display(Markdown(_operator_packet_markdown(packet)))
            set_status()
        except Exception as exc:
            show_error(packet_output, exc)

    def on_disposition(_button) -> None:
        try:
            if workflow is None:
                raise OperatorWorkflowError("Start a case first.")
            conditions = [
                item.strip()
                for item in modified.value.split(";")
                if item.strip()
            ]
            result = workflow.record_disposition(
                reviewer_identity=reviewer_identity.value.strip(),
                reviewer_role_id=reviewer_role.value,
                disposition=disposition.value,
                rationale=rationale.value.strip(),
                modified_conditions=conditions,
                escalation_target_role_id=(
                    escalation_target.value or None
                ),
            )
            case = result["updated_case_state"]
            event = result["audit_event"]
            with disposition_output:
                clear_output()
                display(Markdown(
                    "### Authorized human disposition recorded\n"
                    f"- Disposition: **{case['human_disposition']['disposition']}**\n"
                    f"- Case status: **{case['case_status']}**\n"
                    f"- Audit event: `{event['event_id']}`\n"
                    f"- Audit actor: `{event['actor_type']}`\n"
                    f"- Original recommendation unchanged: "
                    f"`{result['recommendation_unchanged']}`\n"
                    f"- External actions: `{result['external_actions_performed']}`"
                ))
            set_status()
        except Exception as exc:
            show_error(disposition_output, exc)

    def on_export(_button) -> None:
        try:
            if workflow is None:
                raise OperatorWorkflowError("There is no active case to export.")
            bundle_path = (
                workspace_parent
                / f"{workflow.case_id or 'project7_case'}_bundle.zip"
            )
            workflow.export_case_bundle(bundle_path)
            with export_output:
                clear_output()
                display(Markdown(
                    f"**Resumable case bundle created:** `{bundle_path}`"
                ))
            try:
                from google.colab import files
                files.download(str(bundle_path))
            except Exception:
                pass
        except Exception as exc:
            show_error(export_output, exc)

    restore_button.on_click(on_restore)
    intake_button.on_click(on_intake)
    alignment_button.on_click(on_alignment)
    clause_button.on_click(on_clause)
    evidence_button.on_click(on_evidence)
    packet_button.on_click(on_packet)
    record_button.on_click(on_disposition)
    export_button.on_click(on_export)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    new_case_panel = widgets.VBox(
        [
            widgets.HTML("<h3>Start a New Case</h3>"),
            source_upload,
            metadata_warning,
            source_portal,
            jurisdiction,
            agency,
            solicitation_id,
            title,
            description,
            status,
            posted_at,
            due_at,
            place,
            procurement,
            vehicle,
            estimated_value,
            freshness,
            intake_button,
            intake_output,
            widgets.HTML("<hr><h3>Or Resume a Saved Case</h3>"),
            bundle_upload,
            restore_button,
            restore_output,
        ]
    )

    alignment_panel = widgets.VBox(
        [
            profile_dropdown,
            alignment_button,
            alignment_output,
        ]
    )
    clause_panel = widgets.VBox(
        [
            widgets.HTML(
                "<b>Paste relevant source passages for bounded clause-theme triage.</b>"
            ),
            source_domain,
            consequential,
            passage_container,
            add_passage_button,
            clause_button,
            clause_output,
        ]
    )
    evidence_panel = widgets.VBox(
        [
            widgets.HTML(
                "Evidence requests are generated automatically from the actual "
                "model predictions and operator-supplied passages."
            ),
            evidence_button,
            evidence_output,
        ]
    )
    packet_panel = widgets.VBox(
        [
            packet_button,
            packet_output,
        ]
    )
    disposition_panel = widgets.VBox(
        [
            widgets.HTML(
                "<b>The AI recommendation remains separate from the human decision.</b>"
            ),
            reviewer_identity,
            reviewer_role,
            disposition,
            rationale,
            modified,
            escalation_target,
            record_button,
            disposition_output,
        ]
    )
    persistence_panel = widgets.VBox(
        [
            widgets.HTML(
                "Export after any completed stage. The ZIP includes source manifest, "
                "structured inputs, outputs, audit evidence, checksums, and current stage."
            ),
            export_button,
            export_output,
        ]
    )

    accordion = widgets.Accordion(
        children=[
            new_case_panel,
            alignment_panel,
            clause_panel,
            evidence_panel,
            packet_panel,
            disposition_panel,
            persistence_panel,
        ],
        selected_index=0,
    )
    titles = [
        "1 — Opportunity Intake",
        "2 — Organization Alignment",
        "3 — Clause Triage",
        "4 — Evidence Review",
        "5 — Recommendation & Packet",
        "6 — Human Disposition",
        "7 — Save / Resume",
    ]
    for index, title_text in enumerate(titles):
        accordion.set_title(index, title_text)

    set_status()
    display(
        widgets.VBox(
            [
                banner,
                status_html,
                accordion,
                global_output,
            ]
        )
    )
