import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress ResizeObserver errors (known issue with Radix UI/Shadcn)
const suppressResizeObserverError = () => {
  // Save original console.error
  const originalError = window.console.error;

  // Override console.error
  window.console.error = (...args) => {
    // Check if it's a ResizeObserver error
    const errorMessage = args[0]?.toString() || '';
    if (
      errorMessage.includes('ResizeObserver loop') ||
      errorMessage.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      return; // Suppress this specific error
    }
    // Call original error for all other errors
    originalError.apply(console, args);
  };

  // Also handle uncaught errors in error event handler
  window.addEventListener('error', (event) => {
    if (
      event.message?.includes('ResizeObserver loop') ||
      event.message?.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      event.stopImmediatePropagation();
      event.preventDefault();
    }
  });
};

// Apply the suppression before anything else
suppressResizeObserverError();

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
