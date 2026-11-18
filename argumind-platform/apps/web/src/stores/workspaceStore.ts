import { create } from "zustand";

export interface ErrorToastItem {
  readonly id: string;
  readonly code: string;
  readonly detail: string;
  readonly traceId: string;
}

interface WorkspaceState {
  readonly selectedNodeId: string | null;
  readonly hoveredSpanRange: readonly [number, number] | null;
  readonly activeSeverityFilter: string | null;
  readonly isDarkMode: boolean;
  readonly toasts: readonly ErrorToastItem[];
  selectNode: (nodeId: string | null) => void;
  hoverSpan: (range: readonly [number, number] | null) => void;
  setSeverityFilter: (severity: string | null) => void;
  toggleTheme: () => void;
  pushErrorToast: (toast: Omit<ErrorToastItem, "id">) => void;
  dismissToast: (id: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  selectedNodeId: null,
  hoveredSpanRange: null,
  activeSeverityFilter: null,
  isDarkMode: false,
  toasts: [],
  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),
  hoverSpan: (range) => set({ hoveredSpanRange: range }),
  setSeverityFilter: (severity) => set({ activeSeverityFilter: severity }),
  toggleTheme: () =>
    set((state) => {
      const next = !state.isDarkMode;
      if (typeof document !== "undefined") {
        document.documentElement.classList.toggle("dark", next);
      }
      return { isDarkMode: next };
    }),
  pushErrorToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id: `${Date.now()}-${Math.random()}` }],
    })),
  dismissToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
