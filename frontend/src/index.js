import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress ResizeObserver errors (known issue with Radix UI/Shadcn)
const suppressResizeObserverError = () => {
  const resizeObserverErr = window.console.error;
  window.console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('ResizeObserver loop')
    ) {
      return;
    }
    resizeObserverErr(...args);
  };
};

suppressResizeObserverError();

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
