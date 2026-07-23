import { create } from "zustand";

export type DemoView = "upload" | "docs" | "chat";

interface AppState {
  isMobileNavOpen: boolean;
  toggleMobileNav: () => void;
  closeMobileNav: () => void;

  activeDemoView: DemoView;
  setActiveDemoView: (view: DemoView) => void;
}

/**
 * Client-only UI state that doesn't belong in the URL or server cache —
 * navigation/demo-tab state today, workspace UI state (panels, selection)
 * once the authenticated app is built on top of this foundation.
 */
export const useAppStore = create<AppState>((set) => ({
  isMobileNavOpen: false,
  toggleMobileNav: () => set((state) => ({ isMobileNavOpen: !state.isMobileNavOpen })),
  closeMobileNav: () => set({ isMobileNavOpen: false }),

  activeDemoView: "upload",
  setActiveDemoView: (view) => set({ activeDemoView: view }),
}));
