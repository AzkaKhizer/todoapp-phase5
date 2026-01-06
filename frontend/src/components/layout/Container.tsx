import type { ReactNode } from "react";

interface ContainerProps {
  children: ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

const sizeClasses = {
  sm: "max-w-2xl",
  md: "max-w-4xl",
  lg: "max-w-6xl",
  xl: "max-w-7xl",
};

export function Container({
  children,
  className = "",
  size = "md",
}: ContainerProps) {
  return (
    <div className={`${sizeClasses[size]} mx-auto px-4 ${className}`}>
      {children}
    </div>
  );
}
