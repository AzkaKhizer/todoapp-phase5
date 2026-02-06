"use client";

import { useState, useRef, useEffect } from "react";
import type { Tag, TagWithCount } from "@/lib/types";

interface TagInputProps {
  value: string[];
  onChange: (value: string[]) => void;
  suggestions?: TagWithCount[];
  placeholder?: string;
  maxTags?: number;
  className?: string;
  disabled?: boolean;
}

export function TagInput({
  value,
  onChange,
  suggestions = [],
  placeholder = "Add tags...",
  maxTags = 10,
  className = "",
  disabled = false,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Filter suggestions based on input
  const filteredSuggestions = suggestions.filter(
    (tag) =>
      tag.name.toLowerCase().includes(inputValue.toLowerCase()) &&
      !value.includes(tag.name)
  );

  // Close suggestions on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const addTag = (tagName: string) => {
    const trimmed = tagName.trim().toLowerCase();
    if (trimmed && !value.includes(trimmed) && value.length < maxTags) {
      onChange([...value, trimmed]);
      setInputValue("");
      setShowSuggestions(false);
      setHighlightedIndex(-1);
    }
  };

  const removeTag = (tagName: string) => {
    onChange(value.filter((t) => t !== tagName));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      if (highlightedIndex >= 0 && filteredSuggestions[highlightedIndex]) {
        addTag(filteredSuggestions[highlightedIndex].name);
      } else if (inputValue) {
        addTag(inputValue);
      }
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev < filteredSuggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
      setHighlightedIndex(-1);
    }
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div
        className={`
          input-field flex flex-wrap gap-2 p-2 min-h-[42px] cursor-text
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        `}
        onClick={() => !disabled && inputRef.current?.focus()}
      >
        {value.map((tag) => (
          <TagBadge
            key={tag}
            name={tag}
            onRemove={() => removeTag(tag)}
            removable={!disabled}
          />
        ))}
        {value.length < maxTags && (
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setShowSuggestions(true);
              setHighlightedIndex(-1);
            }}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={handleKeyDown}
            placeholder={value.length === 0 ? placeholder : ""}
            disabled={disabled}
            className="flex-1 min-w-[100px] bg-transparent border-none outline-none
                       text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
          />
        )}
      </div>

      {/* Suggestions dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && !disabled && (
        <div
          className="absolute z-50 w-full mt-1 py-1 rounded-lg border
                     border-[var(--border-primary)] bg-[var(--bg-secondary)] shadow-lg"
        >
          {filteredSuggestions.map((tag, index) => (
            <button
              key={tag.id}
              type="button"
              onClick={() => addTag(tag.name)}
              className={`
                w-full px-3 py-2 text-left text-sm flex items-center justify-between
                transition-colors
                ${
                  index === highlightedIndex
                    ? "bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]"
                    : "text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]"
                }
              `}
            >
              <span className="flex items-center gap-2">
                {tag.color && (
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: tag.color }}
                  />
                )}
                {tag.name}
              </span>
              <span className="text-xs text-[var(--text-muted)]">
                {tag.task_count} tasks
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function TagBadge({
  name,
  color,
  onRemove,
  removable = true,
  size = "sm",
}: {
  name: string;
  color?: string | null;
  onRemove?: () => void;
  removable?: boolean;
  size?: "sm" | "md";
}) {
  const sizeClasses = size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-2.5 py-1";

  return (
    <span
      className={`
        inline-flex items-center gap-1 rounded-full font-medium
        bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]
        border border-[var(--accent-primary)]/20
        ${sizeClasses}
      `}
    >
      {color && (
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: color }}
        />
      )}
      <span className="truncate max-w-[100px]">{name}</span>
      {removable && onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-0.5 hover:text-[var(--error)] transition-colors"
          aria-label={`Remove ${name} tag`}
        >
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
}

export function TagList({ tags, size = "sm" }: { tags: Tag[]; size?: "sm" | "md" }) {
  if (!tags || tags.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1">
      {tags.map((tag) => (
        <TagBadge
          key={tag.id}
          name={tag.name}
          color={tag.color}
          removable={false}
          size={size}
        />
      ))}
    </div>
  );
}
