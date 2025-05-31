import React, { useEffect, useState } from "react";
import axios from "axios";

const ExpedientePaciente = () => {
  const [expediente, setExpediente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mensaje, setMensaje] = useState("");

  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchExpediente = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/patient/medical-file`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setExpediente(response.data);
      } catch (error) {
        console.error("Error al obtener el expediente", error);
        setMensaje("No se pudo cargar el expediente.");
      } finally {
        setLoading(false);
      }
    };

    fetchExpediente();
  }, []);

  const confirmarExpediente = async () => {
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL}/patient/confirm-file`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setMensaje("✔️ Expediente confirmado exitosamente.");
      setExpediente({ ...expediente, status: "confirmed" });
    } catch (error) {
      console.error("Error al confirmar el expediente", error);
      setMensaje("No se pudo confirmar el expediente.");
    }
  };

  const renderSection = (title, data) => {
    if (!data) return null;
    return (
      <div className="card mb-3">
        <div className="card-header bg-primary text-white">
          {title}
        </div>
        <ul className="list-group list-group-flush">
          {Object.entries(data).map(([key, value]) => (
            <li className="list-group-item" key={key}>
              <strong>{key.replace(/_/g, " ")}:</strong> {String(value)}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  if (loading) return <p>Cargando expediente...</p>;
  if (!expediente) return <p>No hay expediente disponible.</p>;

  return (
    <div className="container mt-4">
      <h2 className="mb-3">🗂️ Mi expediente clínico</h2>
      <p><strong>Estado actual:</strong> {expediente.status}</p>

      {expediente.status === "approved" && (
        <button className="btn btn-success mb-3" onClick={confirmarExpediente}>
          Confirmar expediente
        </button>
      )}

      {expediente.status === "confirmed" && (
        <div className="alert alert-success">✔️ Expediente confirmado</div>
      )}

      {mensaje && (
        <div className="alert alert-info">{mensaje}</div>
      )}

      {renderSection("🧍 Datos personales", expediente.personal_data)}
      {renderSection("⚕️ Antecedentes patológicos", expediente.pathological_background)}
      {renderSection("🚭 Antecedentes no patológicos", expediente.non_pathological_background)}
      {renderSection("♀️ Antecedentes ginecológicos", expediente.gynecological_background)}
      {renderSection("👪 Antecedentes familiares", expediente.family_background)}
    </div>
  );
};

export default ExpedientePaciente;
