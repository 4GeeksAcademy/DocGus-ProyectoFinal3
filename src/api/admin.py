import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .models import (
    db,
    User,
    MedicalFile,
    PersonalData,
    PathologicalBackground,
    FamilyBackground,
    GynecologicalBackground,
    NonPathologicalBackground,
    AuditTrail
)

class UserView(ModelView):
    column_list = [
        "id", "email", "role", "is_active", "is_validated",
        "first_name", "last_name", "mother_last_name", "birth_date",
        "sex", "phone", "education_level", "education_area",
        "institution", "registration_number"
    ]
    column_exclude_list = ["password"]

class MedicalFileView(ModelView):
    column_list = [
        "id", "status", "created_at", "updated_at", "patient_id", "student_id"
    ]

class PersonalDataView(ModelView):
    column_list = [
        "id", "medical_file_id", "address", "phone"
    ]

class PathologicalBackgroundView(ModelView):
    column_list = [
        "id", "medical_file_id",
        "personal_diseases", "medications", "hospitalizations",
        "surgeries", "traumatisms", "transfusions",
        "allergies", "others"
    ]

class FamilyBackgroundView(ModelView):
    column_list = [
        "id", "medical_file_id",
        "hypertension", "diabetes", "cancer",
        "heart_disease", "kidney_disease", "liver_disease",
        "mental_illness", "congenital_malformations", "others"
    ]

class GynecologicalBackgroundView(ModelView):
    column_list = [
        "id", "medical_file_id",
        "not_applicable", "menarche_age", "pregnancies", "births",
        "c_sections", "abortions", "contraceptive_method", "others"
    ]

class NonPathologicalBackgroundView(ModelView):
    column_list = [
        "id", "medical_file_id",
        "education_level", "economic_activity", "marital_status",
        "dependents", "occupation", "recent_travels",
        "social_activities", "exercise", "diet_supplements",
        "hygiene", "tattoos", "piercings", "hobbies",
        "tobacco_use", "alcohol_use", "recreational_drugs",
        "addictions", "others"
    ]

class AuditTrailView(ModelView):
    column_list = [
        "id", "medical_file_id", "author_id", "timestamp",
        "change", "reason", "previous_status", "new_status"
    ]

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='DocGus Admin', template_mode='bootstrap3')

    admin.add_view(UserView(User, db.session))
    admin.add_view(MedicalFileView(MedicalFile, db.session))
    admin.add_view(PersonalDataView(PersonalData, db.session))
    admin.add_view(PathologicalBackgroundView(PathologicalBackground, db.session))
    admin.add_view(FamilyBackgroundView(FamilyBackground, db.session))
    admin.add_view(GynecologicalBackgroundView(GynecologicalBackground, db.session))
    admin.add_view(NonPathologicalBackgroundView(NonPathologicalBackground, db.session))
    admin.add_view(AuditTrailView(AuditTrail, db.session))