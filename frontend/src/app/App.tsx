import "@/app/styles.css";

import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AdminAIProvidersPage } from "@/app/AdminAIProvidersPage";
import { AuthPage } from "@/app/AuthPage";
import { ChannelsCallbackPage } from "@/app/ChannelsCallbackPage";
import { ChannelsPage } from "@/app/ChannelsPage";
import { DashboardPage } from "@/app/DashboardPage";
import { LandingPage } from "@/app/LandingPage";
import { SettingsPage } from "@/app/SettingsPage";
import { AppProviders } from "@/app/providers/AppProviders";

export function App() {
  return (
    <BrowserRouter>
      <AppProviders>
        <div className="page-shell">
          <div className="ambient ambient-left" />
          <div className="ambient ambient-right" />
          <div className="grain" />

          <Routes>
            <Route element={<LandingPage />} path="/" />
            <Route element={<ChannelsCallbackPage />} path="/dashboard/channels/callback" />
            <Route element={<ChannelsPage />} path="/channels" />
            <Route element={<DashboardPage />} path="/dashboard" />
            <Route element={<SettingsPage />} path="/settings" />
            <Route element={<AdminAIProvidersPage />} path="/admin/ai-providers" />
            <Route element={<AuthPage mode="login" />} path="/login" />
            <Route element={<AuthPage mode="register" />} path="/register" />
            <Route element={<Navigate replace to="/" />} path="*" />
          </Routes>
        </div>
      </AppProviders>
    </BrowserRouter>
  );
}
