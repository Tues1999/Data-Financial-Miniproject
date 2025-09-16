"""Application views for the finance dashboard and data export."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import BytesIO

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from openpyxl import Workbook
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import FinanceRecord


views_bp = Blueprint("views", __name__)


_CURRENCY_QUANTIZER = Decimal("0.01")
_VALID_RECORD_TYPES = frozenset({"income", "expense"})


def _load_user_records(user_id: int, *, ascending: bool) -> list[FinanceRecord]:
    """Return ordered finance records for *user_id*."""

    ordering = (
        FinanceRecord.record_date.asc() if ascending else FinanceRecord.record_date.desc(),
        FinanceRecord.id.asc() if ascending else FinanceRecord.id.desc(),
    )
    stmt = (
        select(FinanceRecord)
        .where(FinanceRecord.user_id == user_id)
        .order_by(*ordering)
    )
    return list(db.session.scalars(stmt))


def _calculate_totals(user_id: int) -> tuple[Decimal, Decimal, Decimal]:
    """Return total income, expense, and balance for a user."""

    totals = {"income": Decimal("0.00"), "expense": Decimal("0.00")}
    stmt = (
        select(
            FinanceRecord.record_type,
            func.coalesce(func.sum(FinanceRecord.amount), 0),
        )
        .where(FinanceRecord.user_id == user_id)
        .group_by(FinanceRecord.record_type)
    )

    for record_type, total in db.session.execute(stmt):
        if record_type in totals:
            totals[record_type] = Decimal(str(total)).quantize(_CURRENCY_QUANTIZER)

    balance = (totals["income"] - totals["expense"]).quantize(_CURRENCY_QUANTIZER)
    return totals["income"], totals["expense"], balance


def _parse_record_date(raw_date: str) -> date | None:
    """Parse ISO formatted date strings from the dashboard form."""

    try:
        return date.fromisoformat(raw_date)
    except ValueError:
        return None


def _parse_amount(raw_amount: str) -> tuple[Decimal | None, str | None, str | None]:
    """Parse the submitted amount into a positive currency value."""

    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        return None, "จำนวนเงินไม่ถูกต้อง", "danger"

    try:
        amount = amount.quantize(_CURRENCY_QUANTIZER, rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return None, "จำนวนเงินไม่ถูกต้อง", "danger"

    if amount <= 0:
        return None, "จำนวนเงินต้องมากกว่า 0", "warning"

    return amount, None, None


@views_bp.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    """Dashboard for viewing and adding financial records."""

    if request.method == "POST":
        form_date = request.form.get("record_date", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip() or None
        record_type = request.form.get("record_type", "").strip()
        amount_raw = request.form.get("amount", "").strip()

        if record_type not in _VALID_RECORD_TYPES:
            flash("กรุณาเลือกประเภทให้ถูกต้อง", "warning")
        elif not form_date or not category or not amount_raw:
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "warning")
        else:
            amount, amount_error, flash_category = _parse_amount(amount_raw)
            if amount_error:
                flash(amount_error, flash_category or "danger")
            else:
                record_date = _parse_record_date(form_date)
                if not record_date:
                    flash("รูปแบบวันที่ไม่ถูกต้อง", "danger")
                else:
                    record = FinanceRecord(
                        user_id=current_user.id,
                        record_date=record_date,
                        category=category,
                        description=description,
                        amount=amount,
                        record_type=record_type,
                    )

                    try:
                        db.session.add(record)
                        db.session.commit()
                    except SQLAlchemyError:
                        db.session.rollback()
                        current_app.logger.exception("Failed to save finance record")
                        flash(
                            "เกิดข้อผิดพลาดในการบันทึกข้อมูล โปรดลองใหม่อีกครั้ง",
                            "danger",
                        )
                    else:
                        flash("บันทึกข้อมูลเรียบร้อย", "success")
                        return redirect(url_for("views.dashboard"))

    records = _load_user_records(current_user.id, ascending=False)

    income_total, expense_total, balance_total = _calculate_totals(current_user.id)

    return render_template(
        "dashboard.html",
        records=records,
        income_total=income_total,
        expense_total=expense_total,
        balance_total=balance_total,
    )


@views_bp.route("/download", methods=["GET"])
@login_required
def download_excel():
    """Generate an Excel file of the user's financial records."""

    records = _load_user_records(current_user.id, ascending=True)

    income_total, expense_total, balance_total = _calculate_totals(current_user.id)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "ข้อมูลการเงิน"

    headers = [
        "วันที่",
        "ประเภท",
        "หมวดหมู่",
        "รายละเอียด",
        "จำนวนเงิน",
        "วันที่บันทึก",
    ]
    worksheet.append(headers)

    for record in records:
        worksheet.append(
            [
                record.record_date.isoformat(),
                "รายรับ" if record.record_type == "income" else "รายจ่าย",
                record.category,
                record.description or "-",
                float(record.amount),
                record.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    if records:
        worksheet.append([])
        worksheet.append(["", "", "", "รวมรายรับ", float(income_total), ""])
        worksheet.append(["", "", "", "รวมรายจ่าย", float(expense_total), ""])
        worksheet.append(["", "", "", "คงเหลือ", float(balance_total), ""])

    for column_cells in worksheet.columns:
        max_length = max(
            (len(str(cell.value)) for cell in column_cells if cell.value is not None),
            default=0,
        )
        column_letter = column_cells[0].column_letter
        worksheet.column_dimensions[column_letter].width = max(12, max_length + 2)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    filename = f"financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

