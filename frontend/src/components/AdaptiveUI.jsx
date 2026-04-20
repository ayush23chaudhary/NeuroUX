import React from "react";
import { useNeuro } from "../context/NeuroProvider";

/**
 * DensityWrapper Component
 * Applies conditional Tailwind classes based on uiDensity
 */
export function DensityWrapper({ children, component: Component = "div" }) {
  const { uiDensity } = useNeuro();

  const getDensityClasses = () => {
    switch (uiDensity) {
      case "SIMPLE":
        return "max-w-2xl mx-auto text-2xl gap-12";
      case "EXPERT":
        return "max-w-full text-xs grid-cols-6 gap-2";
      case "STANDARD":
      default:
        return "max-w-4xl mx-auto text-base gap-6";
    }
  };

  return React.createElement(
    Component,
    { className: getDensityClasses() },
    children
  );
}

/**
 * AdaptiveGrid Component
 * Grid that adapts columns based on density
 */
export function AdaptiveGrid({ children }) {
  const { uiDensity } = useNeuro();

  const getGridClasses = () => {
    switch (uiDensity) {
      case "SIMPLE":
        return "grid grid-cols-1 gap-12";
      case "EXPERT":
        return "grid grid-cols-6 gap-2";
      case "STANDARD":
      default:
        return "grid grid-cols-3 gap-6";
    }
  };

  return (
    <div neuro-component="adaptive-grid" className={getGridClasses()}>
      {children}
    </div>
  );
}

/**
 * AdaptiveText Component
 * Text that adapts size and weight based on density
 */
export function AdaptiveText({ children, variant = "body" }) {
  const { uiDensity } = useNeuro();

  const getTextClasses = () => {
    const baseClasses = {
      SIMPLE: "text-2xl font-bold",
      STANDARD: "text-lg font-semibold",
      EXPERT: "text-xs font-normal",
    };

    const variantClasses = {
      h1: {
        SIMPLE: "text-5xl font-bold",
        STANDARD: "text-4xl font-bold",
        EXPERT: "text-2xl font-bold",
      },
      h2: {
        SIMPLE: "text-4xl font-bold",
        STANDARD: "text-3xl font-bold",
        EXPERT: "text-xl font-bold",
      },
      body: baseClasses,
      caption: {
        SIMPLE: "text-xl",
        STANDARD: "text-sm",
        EXPERT: "text-xs",
      },
    };

    return variantClasses[variant]?.[uiDensity] || variantClasses.body[uiDensity];
  };

  return (
    <span neuro-component="adaptive-text" className={getTextClasses()}>
      {children}
    </span>
  );
}
