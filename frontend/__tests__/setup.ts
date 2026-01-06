/**
 * Jest/Vitest test setup for frontend components.
 */

import "@testing-library/jest-dom";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

// Mock fetch
global.fetch = jest.fn();

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
});

// Helper to mock successful API responses
export function mockApiResponse<T>(data: T) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => data,
  });
}

// Helper to mock failed API responses
export function mockApiError(status: number, message: string) {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: false,
    status,
    json: async () => ({ detail: message }),
  });
}

// Helper to create mock user
export function createMockUser(overrides = {}) {
  return {
    id: "test-user-id",
    email: "test@example.com",
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

// Helper to create mock task
export function createMockTask(overrides = {}) {
  return {
    id: "test-task-id",
    title: "Test Task",
    description: "Test Description",
    is_complete: false,
    user_id: "test-user-id",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
}

// Helper to create mock auth response
export function createMockAuthResponse(overrides = {}) {
  return {
    user: createMockUser(),
    token: "mock-jwt-token",
    ...overrides,
  };
}
