import React from "react";
import { Outlet } from "react-router-dom";

const AdminDashLayout = () => (
  <div>
    <h1>Tabla de Usuarios</h1>
    <Outlet />
  </div>
);

export default AdminDashLayout;