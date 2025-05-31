import React from "react";
import { Outlet } from "react-router-dom";

const AdminDashLayout = () => (
  <div>
    <h1>Dashboard Paciente</h1>
    <Outlet />
  </div>
);

export default AdminDashLayout;