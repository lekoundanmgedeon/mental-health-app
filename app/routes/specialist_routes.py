"""Specialist directory routes."""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.prediction_forms import SpecialistForm
from app.models.specialist import Specialist

specialist_bp = Blueprint("specialists", __name__, url_prefix="/specialists")


@specialist_bp.route("/")
@login_required
def list_specialists():
    """Show specialists and support centers."""
    specialists = Specialist.query.order_by(Specialist.name.asc()).all()
    return render_template("specialists/list.html", title="Find specialists", specialists=specialists)


@specialist_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_specialist():
    """Add a specialist card."""
    form = SpecialistForm()
    if form.validate_on_submit():
        specialist = Specialist(
            name=form.name.data.strip(),
            specialty=form.specialty.data.strip(),
            contact=form.contact.data.strip(),
            location=form.location.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
        )
        db.session.add(specialist)
        db.session.commit()
        flash("Specialist added successfully.", "success")
        return redirect(url_for("specialists.list_specialists"))
    return render_template("specialists/add.html", title="Add specialist", form=form)


@specialist_bp.route("/edit/<int:specialist_id>", methods=["GET", "POST"])
@login_required
def edit_specialist(specialist_id: int):
    """Edit a specialist card."""
    specialist = Specialist.query.get_or_404(specialist_id)
    form = SpecialistForm(obj=specialist)
    if form.validate_on_submit():
        specialist.name = form.name.data.strip()
        specialist.specialty = form.specialty.data.strip()
        specialist.contact = form.contact.data.strip()
        specialist.location = form.location.data.strip()
        specialist.description = form.description.data.strip() if form.description.data else ""
        db.session.commit()
        flash("Specialist updated successfully.", "success")
        return redirect(url_for("specialists.list_specialists"))
    return render_template("specialists/edit.html", title="Edit specialist", form=form, specialist=specialist)


@specialist_bp.post("/delete/<int:specialist_id>")
@login_required
def delete_specialist(specialist_id: int):
    """Delete a specialist card."""
    specialist = Specialist.query.get_or_404(specialist_id)
    db.session.delete(specialist)
    db.session.commit()
    flash("Specialist deleted.", "info")
    return redirect(url_for("specialists.list_specialists"))
