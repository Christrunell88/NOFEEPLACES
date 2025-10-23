import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { HelmetProvider } from 'react-helmet-async';

const rootElement = document.getElementById("root");

// Support both hydration (for prerendered pages) and render (for SPA)
if (rootElement.hasChildNodes()) {
  // If the root has children, it means the page was prerendered
  // Use hydrateRoot for better performance and SEO
  ReactDOM.hydrateRoot(
    rootElement,
    <React.StrictMode>
      <HelmetProvider>
        <App />
      </HelmetProvider>
    </React.StrictMode>
  );
} else {
  // Otherwise, use regular render
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <HelmetProvider>
        <App />
      </HelmetProvider>
    </React.StrictMode>
  );
}
