/**
 * Tests for task components.
 */

import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { TaskCard } from "@/components/tasks/TaskCard";
import { TaskList } from "@/components/tasks/TaskList";
import { EmptyState } from "@/components/tasks/EmptyState";
import type { Task } from "@/lib/types";

// Mock task data
const mockTask: Task = {
  id: "task-1",
  title: "Test Task",
  description: "Test Description",
  is_complete: false,
  user_id: "user-1",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const mockCompletedTask: Task = {
  ...mockTask,
  id: "task-2",
  title: "Completed Task",
  is_complete: true,
};

describe("TaskCard", () => {
  const mockOnToggle = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    mockOnToggle.mockClear();
    mockOnEdit.mockClear();
    mockOnDelete.mockClear();
  });

  it("renders task title and description", () => {
    render(
      <TaskCard
        task={mockTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
  });

  it("shows incomplete checkbox for incomplete task", () => {
    render(
      <TaskCard
        task={mockTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).not.toBeChecked();
  });

  it("shows checked checkbox for completed task", () => {
    render(
      <TaskCard
        task={mockCompletedTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeChecked();
  });

  it("calls onToggle when checkbox is clicked", async () => {
    const user = userEvent.setup();
    render(
      <TaskCard
        task={mockTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    await user.click(screen.getByRole("checkbox"));
    expect(mockOnToggle).toHaveBeenCalledWith(mockTask.id);
  });

  it("calls onEdit when edit button is clicked", async () => {
    const user = userEvent.setup();
    render(
      <TaskCard
        task={mockTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    await user.click(screen.getByLabelText(/edit/i));
    expect(mockOnEdit).toHaveBeenCalledWith(mockTask);
  });

  it("calls onDelete when delete button is clicked", async () => {
    const user = userEvent.setup();
    render(
      <TaskCard
        task={mockTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    await user.click(screen.getByLabelText(/delete/i));
    expect(mockOnDelete).toHaveBeenCalledWith(mockTask.id);
  });

  it("applies strikethrough styling to completed task", () => {
    render(
      <TaskCard
        task={mockCompletedTask}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const title = screen.getByText("Completed Task");
    expect(title).toHaveClass("line-through");
  });
});

describe("TaskList", () => {
  const mockOnToggle = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  const tasks: Task[] = [mockTask, mockCompletedTask];

  beforeEach(() => {
    mockOnToggle.mockClear();
    mockOnEdit.mockClear();
    mockOnDelete.mockClear();
  });

  it("renders all tasks", () => {
    render(
      <TaskList
        tasks={tasks}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText("Test Task")).toBeInTheDocument();
    expect(screen.getByText("Completed Task")).toBeInTheDocument();
  });

  it("renders empty state when no tasks", () => {
    render(
      <TaskList
        tasks={[]}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText(/no tasks/i)).toBeInTheDocument();
  });

  it("passes event handlers to TaskCard components", async () => {
    const user = userEvent.setup();
    render(
      <TaskList
        tasks={[mockTask]}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    await user.click(screen.getByRole("checkbox"));
    expect(mockOnToggle).toHaveBeenCalledWith(mockTask.id);
  });
});

describe("EmptyState", () => {
  it("renders default message", () => {
    render(<EmptyState />);

    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument();
    expect(screen.getByText(/create your first task/i)).toBeInTheDocument();
  });

  it("renders custom title and description", () => {
    render(
      <EmptyState
        title="Custom Title"
        description="Custom description text"
      />
    );

    expect(screen.getByText("Custom Title")).toBeInTheDocument();
    expect(screen.getByText("Custom description text")).toBeInTheDocument();
  });

  it("renders icon", () => {
    render(<EmptyState />);

    // Check for SVG icon presence
    const svg = document.querySelector("svg");
    expect(svg).toBeInTheDocument();
  });
});
