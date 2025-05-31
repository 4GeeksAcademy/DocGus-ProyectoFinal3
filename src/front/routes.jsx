import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";
import { Layout } from "./pages/Layout";
import { Home } from "./pages/Home";
import { Single } from "./pages/Single";
import { Demo } from "./pages/Demo";
import Register from "./components/Register.jsx";
import Login from "./components/Login.jsx";
import AdminDashLayout from "./pages/AdminDashLayout.jsx";
import UsersTable from "./pages/UsersTable.jsx";
import ProfeDashLayout from "./pages/ProfeDashLayout.jsx";
import StudentDashLayout from "./pages/StudentDashLayout.jsx";
import PatientDashLayout from "./pages/PatientDashLayout.jsx";
import MedicalFile from "./pages/MedicalFile.jsx";
import MedicalFileViewer from "./pages/MedicalFileViewer.jsx";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Layout />} errorElement={<h1>Not found!</h1>} >
      <Route path="/" element={<Home />} />
      <Route path="/single/:theId" element={<Single />} />
      <Route path="/demo" element={<Demo />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />

      {/* Admin Dashboard */}
      <Route path="/admin" element={<AdminDashLayout />} >
        <Route path="/admin" element={<UsersTable />} />
      </Route>

      {/* Professional Dashboard */}
      <Route path="/profe" element={<ProfeDashLayout />} >
        <Route path="/profe" element={<h1>Listas del profesor</h1>} />
      </Route>
      
      {/* Student Dashboard */}
      <Route path="/student" element={<StudentDashLayout />} >
        <Route path="/student" element={<MedicalFileViewer />} />
      </Route>

      {/* Patient Dashboard */}
      <Route path="/patient" element={<PatientDashLayout />} >
        <Route path="/patient" element={<h1>Expediente Propio</h1>} />
      </Route>
    </Route>
  )
);