from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)
from flask_login import login_required, current_user
from openpyxl import Workbook
from sqlalchemy import func

from . import db
from .models import FinanceRecord


views_bp = Blueprint("views", __name__)


def _calculate_totals(user_id: int) -> tuple[Decimal, Decimal, Decimal]:
    """Return total income, expense, and balance for a user."""

    totals = {"income": Decimal("0"), "expense": Decimal("0")}
    rows = (
        db.session.query(
            FinanceRecord.record_type,
            func.coalesce(func.sum(FinanceRecord.amount), 0),
        )
        .filter(FinanceRecord.user_id == user_id)
        .group_by(FinanceRecord.record_type)
        .all()
    )

    for record_type, total in rows:
        totals[record_type] = Decimal(str(total))

    balance = totals["income"] - totals["expense"]
    return totals["income"], totals["expense"], balance


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

        if record_type not in {"income", "expense"}:
            flash("กรุณาเลือกประเภทให้ถูกต้อง", "warning")
        elif not form_date or not category or not amount_raw:
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "warning")
        else:
            try:
                amount = Decimal(amount_raw)
            except InvalidOperation:
                flash("จำนวนเงินไม่ถูกต้อง", "danger")
            else:
                if amount <= 0:
                    flash("จำนวนเงินต้องมากกว่า 0", "warning")
                else:
                    try:
                        record_date = datetime.strptime(form_date, "%Y-%m-%d").date()
                    except ValueError:
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
                        db.session.add(record)
                        db.session.commit()
                        flash("บันทึกข้อมูลเรียบร้อย", "success")
                        return redirect(url_for("views.dashboard"))

    records = (
        FinanceRecord.query.filter_by(user_id=current_user.id)
        .order_by(FinanceRecord.record_date.desc(), FinanceRecord.id.desc())
        .all()
    )

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
    records = (
        FinanceRecord.query.filter_by(user_id=current_user.id)
        .order_by(FinanceRecord.record_date.asc(), FinanceRecord.id.asc())
        .all()
    )

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
                record.record_date.strftime("%Y-%m-%d"),
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
        max_length = max(len(str(cell.value)) for cell in column_cells)
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
