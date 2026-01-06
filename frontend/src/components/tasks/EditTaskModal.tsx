"use client";

import { TaskForm } from "@/components/forms/TaskForm";
import { Modal } from "@/components/ui/Modal";
import type { Task } from "@/lib/types";

interface EditTaskModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (taskId: string, data: { title: string; description: string }) => Promise<void>;
}

export function EditTaskModal({
  task,
  isOpen,
  onClose,
  onSave,
}: EditTaskModalProps) {
  if (!task) return null;

  const handleSubmit = async (data: { title: string; description: string }) => {
    await onSave(task.id, data);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Task">
      <TaskForm
        onSubmit={handleSubmit}
        initialData={{ title: task.title, description: task.description }}
        submitLabel="Save Changes"
      />
    </Modal>
  );
}
