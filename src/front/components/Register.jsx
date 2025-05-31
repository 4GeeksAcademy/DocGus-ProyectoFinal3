import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const Register = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const roleFromURL = queryParams.get("rol") || "";

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    mother_last_name: "",
    birth_date: "",
    sex: "",
    role: roleFromURL,
    education_level: "",
    education_area: "",
    institution: "",
    registration_number: "",
    phone: "",
    email: "",
    password: ""
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.msg || data.message || "Error al registrar");
      } else {
        setSuccess("Registro exitoso. Redirigiendo al inicio de sesión...");
        setTimeout(() => navigate("/login"), 2000);
      }
    } catch (err) {
      setError("Ocurrió un error en el servidor.");
    }
  };

  const inputStyle = {
    backgroundColor: "#495057",
    color: "#fff",
    border: "1px solid #fff"
  };

  // Opciones para los campos select
  const sexOptions = ["masculino", "femenino", "otro"];
  const educationLevelOptions = [
    "",
    "LICENCIATURA",
    "MAESTRIA",
    "DOCTORADO",
    "TECNICO",
    "BACHILLERATO"
  ];

  return (
    <div className="container-fluid min-vh-100 d-flex align-items-center justify-content-center px-3" style={{ backgroundColor: "#800000", color: "#fff" }}>
      <div className="card p-4 w-100" style={{ maxWidth: "900px", backgroundColor: "#343a40", border: "1px solid #fff" }}>
        <div className="d-flex align-items-start mb-2">
          {formData.role && (
            <div
              style={{
                background: "#6c757d",
                color: "#fff",
                padding: "6px 18px",
                borderRadius: "8px",
                fontWeight: "bold",
                fontSize: "1rem",
                marginRight: "auto"
              }}
            >
              {formData.role.toUpperCase()}
            </div>
          )}
        </div>
        <h2 className="text-center text-white mb-4">Registro de Usuario</h2>

        <form onSubmit={handleSubmit}>
          <div className="row g-3">
            {/* Nombres */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Nombre(s)</label>
              <input
                type="text"
                name="first_name"
                className="form-control"
                style={inputStyle}
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </div>
            {/* Primer Apellido */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Primer Apellido</label>
              <input
                type="text"
                name="last_name"
                className="form-control"
                style={inputStyle}
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </div>
            {/* Segundo Apellido */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Segundo Apellido</label>
              <input
                type="text"
                name="mother_last_name"
                className="form-control"
                style={inputStyle}
                value={formData.mother_last_name}
                onChange={handleChange}
                required
              />
            </div>
            {/* Fecha de Nacimiento */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Fecha de Nacimiento</label>
              <input
                type="date"
                name="birth_date"
                className="form-control"
                style={inputStyle}
                value={formData.birth_date}
                onChange={handleChange}
              />
            </div>
            {/* Sexo */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Sexo</label>
              <select
                name="sex"
                className="form-select"
                style={inputStyle}
                value={formData.sex}
                onChange={handleChange}
              >
                <option value="">Selecciona</option>
                {sexOptions.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
            {/* Rol */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Rol</label>
              <input
                type="text"
                name="role"
                className="form-control"
                style={inputStyle}
                value={formData.role}
                readOnly
              />
            </div>
            {/* Nivel educativo */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Nivel Educativo</label>
              <select
                name="education_level"
                className="form-select"
                style={inputStyle}
                value={formData.education_level}
                onChange={handleChange}
              >
                {educationLevelOptions.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
            {/* Área educativa */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Área Educativa</label>
              <input
                type="text"
                name="education_area"
                className="form-control"
                style={inputStyle}
                value={formData.education_area}
                onChange={handleChange}
              />
            </div>
            {/* Institución */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Institución</label>
              <input
                type="text"
                name="institution"
                className="form-control"
                style={inputStyle}
                value={formData.institution}
                onChange={handleChange}
              />
            </div>
            {/* Matrícula/Cédula */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Matrícula/Cédula</label>
              <input
                type="text"
                name="registration_number"
                className="form-control"
                style={inputStyle}
                value={formData.registration_number}
                onChange={handleChange}
              />
            </div>
            {/* Teléfono */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Teléfono</label>
              <input
                type="tel"
                name="phone"
                className="form-control"
                style={inputStyle}
                value={formData.phone}
                onChange={handleChange}
              />
            </div>
            {/* Correo Electrónico */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Correo Electrónico</label>
              <input
                type="email"
                name="email"
                className="form-control"
                style={inputStyle}
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            {/* Contraseña */}
            <div className="col-12 col-md-6 col-lg-4">
              <label className="form-label text-white">Contraseña</label>
              <input
                type="password"
                name="password"
                className="form-control"
                style={inputStyle}
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {error && <div className="alert alert-danger mt-4">{error}</div>}
          {success && <div className="alert alert-success mt-4">{success}</div>}

          <div className="text-center mt-4">
            <button type="submit" className="btn btn-light btn-lg text-dark w-100">Registrarme</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;