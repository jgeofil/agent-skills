---
name: modal-drawer-system
description: >-
  Implements accessible modals and drawers with focus trap, ESC to close, scroll lock, portal rendering, and ARIA attributes. Includes sample implementations for common use cases like edit forms, confirmations, and detail views. Use when building "modals", "dialogs", "drawers", "sidebars", or "overlays".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Modal & Drawer System Generator

Create accessible, polished modal dialogs and drawer components.

## Core Workflow

1. **Choose type**: Modal (center), Drawer (side), Bottom Sheet
2. **Setup portal**: Render outside DOM hierarchy
3. **Focus management**: Focus trap and restoration
4. **Accessibility**: ARIA attributes, keyboard shortcuts
5. **Animations**: Smooth enter/exit transitions
6. **Scroll lock**: Prevent body scroll when open
7. **Backdrop**: Click outside to close

## Base Modal Component

```typescript
"use client";

import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "full";
  closeOnEscape?: boolean;
  closeOnBackdrop?: boolean;
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = "md",
  closeOnEscape = true,
  closeOnBackdrop = true,
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // ESC key handler
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Focus trap
  useEffect(() => {
    if (!isOpen) return;

    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements?.[0] as HTMLElement;
    const lastElement = focusableElements?.[
      focusableElements.length - 1
    ] as HTMLElement;

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;

      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    };

    firstElement?.focus();
    document.addEventListener("keydown", handleTab);
    return () => document.removeEventListener("keydown", handleTab);
  }, [isOpen]);

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    full: "max-w-full mx-4",
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
      aria-describedby={description ? "modal-description" : undefined}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in"
        onClick={closeOnBackdrop ? onClose : undefined}
      />

      {/* Modal */}
      <div
        ref={modalRef}
        className={`relative z-10 w-full ${sizeClasses[size]} animate-in zoom-in-95 slide-in-from-bottom-4 duration-200`}
      >
        <div className="rounded-lg bg-white shadow-xl">
          {/* Header */}
          {(title || description) && (
            <div className="border-b px-6 py-4">
              {title && (
                <h2 id="modal-title" className="text-xl font-semibold">
                  {title}
                </h2>
              )}
              {description && (
                <p
                  id="modal-description"
                  className="mt-1 text-sm text-gray-600"
                >
                  {description}
                </p>
              )}
            </div>
          )}

          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute right-4 top-4 rounded-lg p-1 hover:bg-gray-100"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>

          {/* Content */}
          <div className="p-6">{children}</div>
        </div>
      </div>
    </div>,
    document.body
  );
}
```

## Best Practices

1. **Portal rendering**: Render outside parent DOM
2. **Focus management**: Trap focus, restore on close
3. **Keyboard support**: ESC to close, Tab navigation
4. **ARIA attributes**: role, aria-modal, aria-labelledby
5. **Scroll lock**: Prevent body scroll when open
6. **Backdrop**: Click outside to close (optional)
7. **Animations**: Smooth enter/exit transitions
8. **Mobile responsive**: Full screen on small devices

## Output Checklist

- [ ] Modal component with portal
- [ ] Drawer component (left/right/bottom)
- [ ] Focus trap implementation
- [ ] ESC key handler
- [ ] Scroll lock on body
- [ ] Backdrop with click-to-close
- [ ] ARIA attributes
- [ ] Smooth animations
- [ ] Close button
- [ ] Sample use cases (confirm, edit, detail)


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

