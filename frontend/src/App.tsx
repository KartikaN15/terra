import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Suspense, lazy } from "react";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const ProductionsList = lazy(() => import("./pages/ProductionsList"));
const ProductionDetail = lazy(() => import("./pages/ProductionDetail"));
const UploadCSV = lazy(() => import("./pages/UploadCSV"));
const Documents = lazy(() => import("./pages/Documents"));
const ProductionReport = lazy(() => import("./pages/ProductionReport"));
const EmissionFactors = lazy(() => import("./pages/EmissionFactors"));
const Settings = lazy(() => import("./pages/Settings"));
const ProductionDesigner = lazy(() => import("./pages/ProductionDesigner"));
const GreenlightForecast = lazy(() => import("./pages/GreenlightForecast"));
const Anomalies = lazy(() => import("./pages/Anomalies"));

function AppLayout() {
  return (
    <Layout>
      <Suspense fallback={
        <div className="flex items-center justify-center h-[60vh]">
          <div className="animate-spin w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      }>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/productions" element={<ProductionsList />} />
          <Route path="/productions/:id" element={<ProductionDetail />} />
          <Route path="/productions/:id/report" element={<ProductionReport />} />
          <Route path="/forecast" element={<GreenlightForecast />} />
          <Route path="/anomalies" element={<Anomalies />} />
          <Route path="/upload" element={<UploadCSV />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/factors" element={<EmissionFactors />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/productions/new/designer" element={<ProductionDesigner />} />
          <Route path="/productions/:id/designer" element={<ProductionDesigner />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<AppLayout />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
