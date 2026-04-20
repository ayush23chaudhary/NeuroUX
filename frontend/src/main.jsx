import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { NeuroProvider } from "./context/NeuroProvider";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <NeuroProvider>
        <App />
      </NeuroProvider>
    </BrowserRouter>
  </React.StrictMode>
);
