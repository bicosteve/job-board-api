import type { ReactElement } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./layout/Layout";
import HomePage from "./pages/HomePage";
import JobDetailPage from "./pages/JobDetailPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import VerifyPage from "./pages/VerifyPage";
import DashboardPage from "./pages/DashboardPage";
import ProfileOnboardingPage from "./pages/ProfileOnboardingPage";
import EducationOnboardingPage from "./pages/EducationOnboardingPage";
import AdminLoginPage from "./pages/AdminLoginPage";
import AdminJobsPage from "./pages/AdminJobsPage";
import RegisterAdminPage from "./pages/RegisterAdminPage";

function RequireUser({ children }: { children: ReactElement }) {
  const { userToken } = useAuth();
  if (!userToken) return <Navigate to="/login" replace />;
  return children;
}

function RequireAdmin({ children }: { children: ReactElement }) {
  const { adminToken } = useAuth();
  if (!adminToken) return <Navigate to="/admin/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="jobs/:jobId" element={<JobDetailPage />} />

        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="verify" element={<VerifyPage />} />

        <Route
          path="dashboard"
          element={
            <RequireUser>
              <DashboardPage />
            </RequireUser>
          }
        />
        <Route
          path="onboarding/profile"
          element={
            <RequireUser>
              <ProfileOnboardingPage />
            </RequireUser>
          }
        />
        <Route
          path="onboarding/education"
          element={
            <RequireUser>
              <EducationOnboardingPage />
            </RequireUser>
          }
        />

        <Route path="admin/login" element={<AdminLoginPage />} />
        <Route path="admin/register" element={<RegisterAdminPage />} />

        <Route
          path="admin/jobs"
          element={
            <RequireAdmin>
              <AdminJobsPage />
            </RequireAdmin>
          }
        />
      </Route>
    </Routes>
  );
}
