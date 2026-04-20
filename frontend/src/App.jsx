import React from "react";
import { useNeuro } from "./context/NeuroProvider";
import { useNeuroTracker } from "./hooks/useNeuroTracker";
import { motion } from "framer-motion";
import { AdaptiveText, AdaptiveGrid, DensityWrapper } from "./components/AdaptiveUI";
import { AdminPanel } from "./components/AdminPanel";
import SecurityOverlay from "./components/SecurityOverlay";
import { useLocation } from "react-router-dom";

/**
 * Navbar Component
 */
function Navbar() {
  const { uiDensity, isConnected, suspicionScore } = useNeuro();

  return (
    <nav className="bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-2"
        >
          <span className="text-2xl font-bold"> NeuroUX</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              isConnected
                ? "bg-green-400 text-gray-900"
                : "bg-red-400 text-white"
            }`}
          >
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </motion.div>

        <div className="flex items-center gap-4">
          <div className="text-sm">
            <span>Density: </span>
            <span className="font-bold">{uiDensity}</span>
          </div>
          <div className="text-sm">
            <span>Risk: </span>
            <span
              className={`font-bold ${
                suspicionScore > 0.7
                  ? "text-red-300"
                  : suspicionScore > 0.3
                    ? "text-yellow-300"
                    : "text-green-300"
              }`}
            >
              {(suspicionScore * 100).toFixed(0)}%
            </span>
          </div>
          <a
            href="/admin"
            className="px-3 py-1 bg-gray-700 hover:bg-gray-800 rounded-lg text-sm font-semibold transition"
            title="Open Admin Dashboard (God-View)"
          >
            🧠 Admin
          </a>
        </div>
      </div>
    </nav>
  );
}

/**
 * Hero Section Component
 */
function HeroSection() {
  const { uiDensity } = useNeuro();

  return (
    <section className="py-16 bg-gradient-to-b from-purple-50 to-white">
      <div className="max-w-6xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <AdaptiveText variant="h1">
            Self-Adapting Intelligent Interface
          </AdaptiveText>

          <p
            className={`mt-4 ${
              uiDensity === "SIMPLE"
                ? "text-xl"
                : uiDensity === "EXPERT"
                  ? "text-xs"
                  : "text-lg"
            } text-gray-600`}
          >
            Experience UI that learns your behavior and adapts in real-time
          </p>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            id="hero-cta-button"
            onClick={() => console.log("Navigating to explore...")}
            className={`mt-8 font-bold text-white bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg hover:shadow-lg transition-all ${
              uiDensity === "SIMPLE"
                ? "px-8 py-4 text-2xl"
                : uiDensity === "EXPERT"
                  ? "px-3 py-1 text-xs"
                  : "px-6 py-3 text-lg"
            }`}
          >
            Explore Now →
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
}

/**
 * Product Card Component
 */
function ProductCard({ title, description, id }) {
  const { uiDensity } = useNeuro();

  return (
    <motion.div
      layout
      whileHover={{ y: -5 }}
      id={`product-card-${id}`}
      className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow border border-gray-200"
    >
      <div className="w-full h-32 bg-gradient-to-br from-purple-200 to-blue-200 rounded-md mb-4" />

      <AdaptiveText variant="h2">{title}</AdaptiveText>

      <p
        className={`mt-2 text-gray-600 ${
          uiDensity === "SIMPLE"
            ? "text-lg"
            : uiDensity === "EXPERT"
              ? "text-xs"
              : "text-sm"
        }`}
      >
        {description}
      </p>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        id={`product-button-${id}`}
        onClick={() => console.log(`Viewing details for ${title}...`)}
        className={`mt-4 font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded transition ${
          uiDensity === "SIMPLE"
            ? "px-6 py-3 text-lg"
            : uiDensity === "EXPERT"
              ? "px-2 py-1 text-xs"
              : "px-4 py-2 text-sm"
        }`}
      >
        View Details
      </motion.button>
    </motion.div>
  );
}

/**
 * Product Grid Section
 */
function ProductSection() {
  const products = [
    {
      id: "prod1",
      title: "Smart Tracking",
      description: "Real-time behavior analysis",
    },
    {
      id: "prod2",
      title: "Fraud Detection",
      description: "Impossible path identification",
    },
    {
      id: "prod3",
      title: "UI Adaptation",
      description: "Context-aware interface",
    },
    {
      id: "prod4",
      title: "Session Analytics",
      description: "Deep user insights",
    },
    {
      id: "prod5",
      title: "Risk Scoring",
      description: "Real-time anomaly detection",
    },
    {
      id: "prod6",
      title: "Flow Validation",
      description: "DAG-based path checking",
    },
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          <AdaptiveText variant="h2">Features</AdaptiveText>
          <p className="mt-2 text-gray-600">
            Explore the core capabilities of NeuroUX
          </p>
        </motion.div>

        <AdaptiveGrid>
          {products.map((product) => (
            <ProductCard
              key={product.id}
              id={product.id}
              title={product.title}
              description={product.description}
            />
          ))}
        </AdaptiveGrid>
      </div>
    </section>
  );
}

/**
 * Footer Component
 */
function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-8 mt-16">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-sm text-gray-400">
          🧠 NeuroUX Phase 1 - The Foundation | Hackathon 2026
        </p>
      </div>
    </footer>
  );
}

/**
 * Main App Component
 */
export default function App() {
  // Initialize behavior tracking
  useNeuroTracker();
  const location = useLocation();
  const isAdminPath = location.pathname === "/admin";

  // Render admin dashboard if on admin route
  if (isAdminPath) {
    return <AdminPanel />;
  }

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <HeroSection />
      <ProductSection />
      <SecurityOverlay />
      <Footer />
    </div>
  );
}
