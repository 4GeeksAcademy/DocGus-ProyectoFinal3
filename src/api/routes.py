from flask import request, jsonify, Blueprint
from api.utils import patient_required
from api.utils import student_required
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from api.models import (
    db, User, UserRole, EducationLevel, MedicalFile,
    PersonalData, PathologicalBackground, FamilyBackground,
    NonPathologicalBackground, GynecologicalBackground, AuditTrail
)
from api.utils import APIException
from datetime import datetime, timedelta

api = Blueprint('api', __name__)

# REGISTRO
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        raise APIException("El cuerpo de la solicitud debe ser JSON", status_code=400)

    required_fields = [
        "first_name", "last_name", "mother_last_name",
        "email", "password", "role"
    ]
    for field in required_fields:
        if field not in data or not data[field]:
            raise APIException(f"Falta el campo requerido: {field}", status_code=400)

    if User.query.filter_by(email=data["email"]).first():
        raise APIException("El correo ya está registrado", status_code=400)

    hashed_password = generate_password_hash(data["password"])

    try:
        role = UserRole(data["role"])
    except ValueError:
        raise APIException("Rol inválido", status_code=400)

    education_level = data.get("education_level")
    education_level_enum = None
    if education_level:
        try:
            education_level_enum = EducationLevel(education_level)
        except ValueError:
            raise APIException("Nivel educativo inválido", status_code=400)

    birth_date = data.get("birth_date")
    if birth_date:
        try:
            birth_date = datetime.fromisoformat(birth_date)
        except ValueError:
            raise APIException("Formato de fecha inválido. Use YYYY-MM-DD.", status_code=400)

    new_user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        mother_last_name=data["mother_last_name"],
        email=data["email"],
        password=hashed_password,
        birth_date=birth_date,
        sex=data.get("sex"),
        phone=data.get("phone"),
        role=role,
        is_active=True,
        is_validated=False,
        education_level=education_level_enum,
        education_area=data.get("education_area"),
        institution=data.get("institution"),
        registration_number=data.get("registration_number")
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario registrado exitosamente"}), 201

# LOGIN
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        raise APIException("Correo y contraseña son requeridos", status_code=400)

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        raise APIException("Credenciales inválidas", status_code=401)

    access_token = create_access_token(
        identity=str(user.id), expires_delta=timedelta(hours=1))

    return jsonify({"token": access_token, "user": user.serialize()}), 200

# PERFIL DEL USUARIO ACTUAL
@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        raise APIException("Usuario no encontrado", status_code=404)
    return jsonify(user.serialize()), 200

@api.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        raise APIException("Usuario no encontrado", status_code=404)
    data = request.get_json()

    for field in [
        "first_name", "last_name", "mother_last_name", "birth_date", "sex",
        "phone", "education_level", "education_area", "institution", "registration_number"
    ]:
        if field in data:
            if field == "education_level" and data[field]:
                try:
                    setattr(user, field, EducationLevel(data[field]))
                except ValueError:
                    raise APIException("Nivel educativo inválido", status_code=400)
            elif field == "birth_date" and data[field]:
                try:
                    setattr(user, field, datetime.fromisoformat(data[field]))
                except ValueError:
                    raise APIException("Formato de fecha inválido. Use YYYY-MM-DD.", status_code=400)
            else:
                setattr(user, field, data[field])
    db.session.commit()
    return jsonify({"msg": "Perfil actualizado"}), 200

# LISTAR USUARIOS PENDIENTES DE VALIDACIÓN
@api.route('/users/pending', methods=['GET'])
@jwt_required()
def get_pending_users():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise APIException("Usuario no encontrado", status_code=404)

    if user.role == UserRole.ADMIN:
        users = User.query.filter_by(role=UserRole.PROFESSIONAL, is_validated=False).all()
    elif user.role == UserRole.PROFESSIONAL:
        users = User.query.filter_by(role=UserRole.STUDENT, is_validated=False).all()
    else:
        raise APIException("No autorizado", status_code=403)

    return jsonify([u.serialize() for u in users]), 200


# VALIDAR USUARIO
@api.route('/users/<int:id>/validate', methods=['PUT'])
@jwt_required()
def validate_user(id):
    current_user = User.query.get(get_jwt_identity())
    user = User.query.get(id)
    if not user:
        raise APIException("Usuario no encontrado", status_code=404)

    allowed = (
        current_user.role == UserRole.ADMIN and user.role == UserRole.PROFESSIONAL
    ) or (
        current_user.role == UserRole.PROFESSIONAL and user.role == UserRole.STUDENT
    )

    if not allowed:
        raise APIException("No autorizado para validar este usuario", status_code=403)

    user.is_validated = True
    db.session.commit()
    return jsonify({"msg": "Usuario validado"}), 200

# LISTAR TODOS LOS USUARIOS (SOLO ADMIN)
@api.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != UserRole.ADMIN:
        raise APIException("Acceso no autorizado", status_code=403)
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# ELIMINAR USUARIO (SOLO ADMIN)
@api.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = User.query.get(get_jwt_identity())
    if current_user.role != UserRole.ADMIN:
        raise APIException("Acceso no autorizado", status_code=403)
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "Usuario no encontrado"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"}), 200

# OBTENER EXPEDIENTE MÉDICO POR USUARIO
@api.route('/medical-file/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_medical_file_by_user(user_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user:
        raise APIException("Usuario no encontrado", status_code=404)

    medical_file = MedicalFile.query.filter_by(patient_id=user_id).first()
    if not medical_file:
        raise APIException("Expediente médico no encontrado", status_code=404)

    allowed = False
    if current_user.id == user_id:
        allowed = True
    elif current_user.role == UserRole.STUDENT and medical_file.student_id == current_user.student_profile.id:
        allowed = True
    elif current_user.role == UserRole.PROFESSIONAL:
        allowed = True  # Puedes agregar lógica extra si lo deseas
    elif current_user.role == UserRole.ADMIN:
        allowed = True

    if not allowed:
        raise APIException("No tienes permisos para ver este expediente", status_code=403)

    result = {
        "medical_file": {
            "id": medical_file.id,
            "status": medical_file.status.value,
            "patient_id": medical_file.patient_id,
            "student_id": medical_file.student_id,
            "created_at": medical_file.created_at.isoformat(),
            "updated_at": medical_file.updated_at.isoformat()
        },
        "personal_data": medical_file.personal_data.serialize() if medical_file.personal_data else None,
"pathological_background": medical_file.pathological_background.serialize() if medical_file.pathological_background else None,
"family_background": medical_file.family_background.serialize() if medical_file.family_background else None,
"non_pathological_background": medical_file.non_pathological_background.serialize() if medical_file.non_pathological_background else None,
"gynecological_background": medical_file.gynecological_background.serialize() if medical_file.gynecological_background else None,
    }
    return jsonify(result), 200

# ENDPOINTS PARA RUBROS DEL EXPEDIENTE Y AUDITORÍA
@api.route('/medical-files/<int:file_id>/personal-data', methods=['GET', 'PUT'])
@jwt_required()
def personal_data(file_id):
    personal_data = PersonalData.query.filter_by(medical_file_id=file_id).first()
    if request.method == 'GET':
        if not personal_data:
            raise APIException("Datos personales no encontrados", status_code=404)
        return jsonify({
            "id": personal_data.id,
            "address": personal_data.address,
            "phone": personal_data.phone
        }), 200
    else:
        data = request.get_json()
        if not personal_data:
            raise APIException("Datos personales no encontrados", status_code=404)
        for field in ["address", "phone"]:
            if field in data:
                setattr(personal_data, field, data[field])
        db.session.commit()
        return jsonify({"msg": "Datos personales actualizados"}), 200

@api.route('/medical-files/<int:file_id>/pathological-background', methods=['GET', 'PUT'])
@jwt_required()
def pathological_background(file_id):
    pb = PathologicalBackground.query.filter_by(medical_file_id=file_id).first()
    if request.method == 'GET':
        if not pb:
            raise APIException("Antecedentes patológicos no encontrados", status_code=404)
        return jsonify({
            "id": pb.id,
            "personal_diseases": pb.personal_diseases,
            "medications": pb.medications,
            "hospitalizations": pb.hospitalizations,
            "surgeries": pb.surgeries,
            "traumatisms": pb.traumatisms,
            "transfusions": pb.transfusions,
            "allergies": pb.allergies,
            "others": pb.others
        }), 200
    else:
        data = request.get_json()
        if not pb:
            raise APIException("Antecedentes patológicos no encontrados", status_code=404)
        for field in [
            "personal_diseases", "medications", "hospitalizations", "surgeries",
            "traumatisms", "transfusions", "allergies", "others"
        ]:
            if field in data:
                setattr(pb, field, data[field])
        db.session.commit()
        return jsonify({"msg": "Antecedentes patológicos actualizados"}), 200

@api.route('/medical-files/<int:file_id>/family-background', methods=['GET', 'PUT'])
@jwt_required()
def family_background(file_id):
    fb = FamilyBackground.query.filter_by(medical_file_id=file_id).first()
    if request.method == 'GET':
        if not fb:
            raise APIException("Antecedentes familiares no encontrados", status_code=404)
        return jsonify(fb.serialize()), 200
    else:
        data = request.get_json()
        if not fb:
            raise APIException("Antecedentes familiares no encontrados", status_code=404)
        for field in ["hereditary_diseases", "mental_illnesses", "substance_abuse", "other_family_background"]:
            if field in data:
                setattr(fb, field, data[field])
        db.session.commit()
        return jsonify({"msg": "Antecedentes familiares actualizados"}), 200


@api.route('/medical-files/<int:file_id>/non-pathological-background', methods=['GET', 'PUT'])
@jwt_required()
def non_pathological_background(file_id):
    npb = NonPathologicalBackground.query.filter_by(medical_file_id=file_id).first()
    if request.method == 'GET':
        if not npb:
            raise APIException("Antecedentes no patológicos no encontrados", status_code=404)
        return jsonify(npb.serialize()), 200
    else:
        data = request.get_json()
        if not npb:
            raise APIException("Antecedentes no patológicos no encontrados", status_code=404)
        for field in ["lifestyle", "exercise", "diet", "sleep", "toxic_habits"]:
            if field in data:
                setattr(npb, field, data[field])
        db.session.commit()
        return jsonify({"msg": "Antecedentes no patológicos actualizados"}), 200


@api.route('/medical-files/<int:file_id>/gynecological-background', methods=['GET', 'PUT'])
@jwt_required()
def gynecological_background(file_id):
    gb = GynecologicalBackground.query.filter_by(medical_file_id=file_id).first()
    if request.method == 'GET':
        if not gb:
            raise APIException("Antecedentes ginecológicos no encontrados", status_code=404)
        return jsonify(gb.serialize()), 200
    else:
        data = request.get_json()
        if not gb:
            raise APIException("Antecedentes ginecológicos no encontrados", status_code=404)
        for field in ["menarche", "menstrual_cycle", "last_menstruation", "pregnancies", "contraceptive_use"]:
            if field in data:
                setattr(gb, field, data[field])
        db.session.commit()
        return jsonify({"msg": "Antecedentes ginecológicos actualizados"}), 200


# AUDITORÍA DEL EXPEDIENTE
@api.route('/medical-files/<int:file_id>/audit-trail', methods=['GET'])
@jwt_required()
def get_audit_trail(file_id):
    audits = AuditTrail.query.filter_by(medical_file_id=file_id).order_by(AuditTrail.timestamp.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "author_id": a.author_id,
            "timestamp": a.timestamp.isoformat(),
            "change": a.change,
            "reason": a.reason,
            "previous_status": a.previous_status.value if a.previous_status else None,
            "new_status": a.new_status.value if a.new_status else None
        }
        for a in audits
    ]), 200


# Enpoint para registrar pacientes y crear automáticamente un expediente médico en blanco
@api.route("/api/register", methods=["POST"])
def register_patient():
    data = request.get_json()
    # ... lógica para crear el paciente ...
    new_patient = User(...)  # con rol = 'patient'
    db.session.add(new_patient)
    db.session.commit()

    # Crear automáticamente el expediente en blanco
    medical_file = MedicalFile(
        patient_id=new_patient.id,
        status=FileStatus.EMPTY  # Enum de tu modelo
    )
    db.session.add(medical_file)
    db.session.commit()

    return jsonify({"msg": "Paciente registrado", "user_id": new_patient.id}), 201

# Enpoint para obtener el expediente médico del paciente actual
@api.route("/api/patient/medical-file", methods=["GET"])
@jwt_required()
@patient_required
def get_my_medical_file():
    current_user_id = get_jwt_identity()
    file = MedicalFile.query.filter_by(patient_id=current_user_id).first()
    if not file:
        return jsonify({"msg": "No hay expediente aún"}), 404
    return jsonify(file.serialize()), 200

# Enpoint para obtener todos los pacientes y sus expedientes médicos
@api.route("/api/student/patients", methods=["GET"])
@jwt_required()
@student_required
def get_all_patients():
    patients = User.query.filter_by(role=UserRole.PATIENT).all()
    result = []
    for p in patients:
        file = MedicalFile.query.filter_by(patient_id=p.id).first()
        result.append({
            "patient_id": p.id,
            "patient_name": p.full_name,
            "email": p.email,
            "file_status": file.status.value if file else "no_file"
        })
    return jsonify(result), 200

# Enpoint para editar el expediente médico de un paciente
@api.route("/api/student/edit-patient-file/<int:patient_id>", methods=["PUT"])
@jwt_required()
@student_required
def edit_patient_file(patient_id):
    file = MedicalFile.query.filter_by(patient_id=patient_id).first()
    if not file:
        return jsonify({"msg": "Expediente no encontrado"}), 404

    data = request.get_json()
    # ... llenar los campos del expediente con lo recibido ...
    file.status = FileStatus.IN_PROGRESS
    db.session.commit()
    return jsonify({"msg": "Expediente actualizado"}), 200
