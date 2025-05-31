# Proyecto: Ecosistema Digital para la Gestión de Expedientes Médicos
# Objetivo: Crear un MVP centrado en el llenado, supervisión y validación de antecedentes clínicos, divididos por rubros.
# Tecnología:
# - Backend: Flask + SQLAlchemy + JWT + PostgreSQL
# - Frontend: React (Vite) + Bootstrap + FontAwesome
# - Sesiones: localStorage (no cookies)
# Estructura del repo: `src/api` para el backend, `src/front` para el frontend.
# Roles del sistema:
# - admin: valida profesionales
# - professional: supervisa estudiantes y valida expedientes
# - student: llena expediente de antecedentes clínicos
# - patient: registra sus datos y confirma su expediente
# Rubros del expediente (cada uno en su tabla):
# - PersonalData
# - PathologicalBackground
# - FamilyBackground
# - NonPathologicalBackground
# - GynecologicalBackground (incluye campo 'no corresponde')
# Flujo de trabajo:
# 1. Paciente se registra.
# 2. Estudiante completa los antecedentes del paciente.
# 3. Profesional autoriza o rechaza.
# 4. Paciente confirma o solicita corrección.
# Estados del expediente:
# 'registrado', 'completado', 'en revisión', 'rechazado', 'autorizado', 'confirmado'
# Protección de rutas con decoradores según rol: @admin_required, @student_required, etc.
# El objetivo del MVP es lograr que todos los flujos estén conectados y funcionales de manera mínima pero clara.
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, DateTime, Enum as PgEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Enums para roles y estados
class UserRole(Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    STUDENT = "student"
    PATIENT = "patient"

class FileStatus(Enum):
    EMPTY = "empty"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    FEEDBACK = "feedback"
    APPROVED = "approved"
    CORRECTION_REQUESTED = "correction_requested"
    CONFIRMED = "confirmed"

class EducationLevel(Enum):
    NONE = "Sin estudios"
    PRIMARY = "Primaria"
    SECONDARY = "Secundaria"
    HIGH_SCHOOL = "Bachillerato"
    TECHNICAL = "Carrera técnica"
    PROFESSIONAL = "Licenciatura/Profesional"
    POSTGRADUATE = "Posgrado"

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    mother_last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    birth_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    sex: Mapped[str] = mapped_column(String(20), nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    is_validated: Mapped[bool] = mapped_column(Boolean(), default=False)
    education_level: Mapped[EducationLevel] = mapped_column(PgEnum(EducationLevel), nullable=True)
    education_area: Mapped[str] = mapped_column(String(120), nullable=True)
    institution: Mapped[str] = mapped_column(String(120), nullable=True)
    registration_number: Mapped[str] = mapped_column(String(60), nullable=True)

    # Relaciones
    medical_file = relationship("MedicalFile", uselist=False, back_populates="patient")
    professional_profile = relationship("ProfessionalProfile", uselist=False, back_populates="user")
    student_profile = relationship("StudentProfile", uselist=False, back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mother_last_name": self.mother_last_name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "sex": self.sex,
            "phone": self.phone,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_validated": self.is_validated,
            "education_level": self.education_level.value if self.education_level else None,
            "education_area": self.education_area,
            "institution": self.institution,
            "registration_number": self.registration_number,
        }

class ProfessionalProfile(db.Model):
    __tablename__ = "professional_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="professional_profile")
    students = relationship("StudentProfile", back_populates="professional")

class StudentProfile(db.Model):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="student_profile")
    professional_id: Mapped[int] = mapped_column(ForeignKey("professional_profiles.id"))
    professional = relationship("ProfessionalProfile", back_populates="students")
    medical_files = relationship("MedicalFile", back_populates="student")

class MedicalFile(db.Model):
    __tablename__ = "medical_files"
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), nullable=True)
    status: Mapped[FileStatus] = mapped_column(PgEnum(FileStatus), default=FileStatus.EMPTY)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    patient = relationship("User", back_populates="medical_file")
    student = relationship("StudentProfile", back_populates="medical_files")
    personal_data = relationship("PersonalData", uselist=False, back_populates="medical_file")
    pathological_background = relationship("PathologicalBackground", uselist=False, back_populates="medical_file")
    family_background = relationship("FamilyBackground", uselist=False, back_populates="medical_file")
    non_pathological_background = relationship("NonPathologicalBackground", uselist=False, back_populates="medical_file")
    gynecological_background = relationship("GynecologicalBackground", uselist=False, back_populates="medical_file")
    audit_trails = relationship("AuditTrail", back_populates="medical_file")

class PersonalData(db.Model):
    __tablename__ = "personal_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    medical_file_id: Mapped[int] = mapped_column(ForeignKey("medical_files.id"))
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    medical_file = relationship("MedicalFile", back_populates="personal_data")

class PathologicalBackground(db.Model):
    __tablename__ = "pathological_background"
    id: Mapped[int] = mapped_column(primary_key=True)
    medical_file_id: Mapped[int] = mapped_column(ForeignKey("medical_files.id"))
    personal_diseases: Mapped[str] = mapped_column(Text, nullable=True)
    medications: Mapped[str] = mapped_column(Text, nullable=True)
    hospitalizations: Mapped[str] = mapped_column(Text, nullable=True)
    surgeries: Mapped[str] = mapped_column(Text, nullable=True)
    traumatisms: Mapped[str] = mapped_column(Text, nullable=True)
    transfusions: Mapped[str] = mapped_column(Text, nullable=True)
    allergies: Mapped[str] = mapped_column(Text, nullable=True)
    others: Mapped[str] = mapped_column(Text, nullable=True)

    medical_file = relationship("MedicalFile", back_populates="pathological_background")

class FamilyBackground(db.Model):
    __tablename__ = "family_background"
    id: Mapped[int] = mapped_column(primary_key=True)
    medical_file_id: Mapped[int] = mapped_column(ForeignKey("medical_files.id"))
    hypertension: Mapped[str] = mapped_column(Text, nullable=True)
    diabetes: Mapped[str] = mapped_column(Text, nullable=True)
    cancer: Mapped[str] = mapped_column(Text, nullable=True)
    heart_disease: Mapped[str] = mapped_column(Text, nullable=True)
    kidney_disease: Mapped[str] = mapped_column(Text, nullable=True)
    liver_disease: Mapped[str] = mapped_column(Text, nullable=True)
    mental_illness: Mapped[str] = mapped_column(Text, nullable=True)
    congenital_malformations: Mapped[str] = mapped_column(Text, nullable=True)
    others: Mapped[str] = mapped_column(Text, nullable=True)

    medical_file = relationship("MedicalFile", back_populates="family_background")

class NonPathologicalBackground(db.Model):
    __tablename__ = "non_pathological_background"
    id: Mapped[int] = mapped_column(primary_key=True)
    medical_file_id: Mapped[int] = mapped_column(ForeignKey("medical_files.id"))
    education_level: Mapped[str] = mapped_column(String(60), nullable=True)
    economic_activity: Mapped[str] = mapped_column(String(120), nullable=True)
    housing_type: Mapped[str] = mapped_column(String(60), nullable=True)
    services: Mapped[str] = mapped_column(Text, nullable=True)
    lifestyle: Mapped[str] = mapped_column(Text, nullable=True)
    nutrition: Mapped[str] = mapped_column(Text, nullable=True)
    habits: Mapped[str] = mapped_column(Text, nullable=True)
    physical_activity: Mapped[str] = mapped_column(Text, nullable=True)

    medical_file = relationship("MedicalFile", back_populates="non_pathological_background")

class GynecologicalBackground(db.Model):
    __tablename__ = "gynecological_background"
    id: Mapped[int] = mapped_column(primary_key=True)
    medical_file_id: Mapped[int] = mapped_column(ForeignKey("medical_files.id"))
    not_applicable: Mapped[bool] = mapped_column(Boolean, default=False)
    menarche: Mapped[str] = mapped_column(String(20), nullable=True)
    cycle: Mapped[str] = mapped_column(String(60), nullable=True)
    pregnancies: Mapped[int] = mapped_column(Integer, nullable=True)
    births: Mapped[int] = mapped_column(Integer, nullable=True)
    abortions: Mapped[int] = mapped_column(Integer, nullable=True)
    last_menstruation: Mapped[str] = mapped_column(String(30), nullable=True)
    last_pap: Mapped[str] = mapped_column(String(30), nullable=True)
    contraceptive_method: Mapped[str] = mapped_column(String(120), nullable=True)
    others: Mapped[str] = mapped_column(Text, nullable=True)

    medical_file = relationship("MedicalFile", back_populates="gynecological_background")

class AuditTrail(db.Model):
    __tablename__ = "audit_trails"
    id: Mapped[int] = mapped_column(primary_key=True)
    medical_file_id: Mapped[int] = mapped_column(ForeignKey("medical_files.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    performed_by: Mapped[str] = mapped_column(String(120), nullable=False)

    medical_file = relationship("MedicalFile", back_populates="audit_trails")
