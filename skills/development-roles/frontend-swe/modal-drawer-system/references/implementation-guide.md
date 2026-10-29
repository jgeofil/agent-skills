# Modal & Drawer System Generator - Implementation Guide & Code Recipes

## Drawer Component

```typescript
interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  position?: "left" | "right" | "bottom";
  title?: string;
  children: React.ReactNode;
}

export function Drawer({
  isOpen,
  onClose,
  position = "right",
  title,
  children,
}: DrawerProps) {
  // Similar hooks as Modal (ESC, focus trap, scroll lock)

  const positionClasses = {
    left: "left-0 top-0 h-full w-80 animate-in slide-in-from-left",
    right: "right-0 top-0 h-full w-80 animate-in slide-in-from-right",
    bottom: "bottom-0 left-0 right-0 h-96 animate-in slide-in-from-bottom",
  };

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50" role="dialog" aria-modal="true">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={`absolute ${positionClasses[position]} bg-white shadow-xl`}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b px-6 py-4">
            <h2 className="text-xl font-semibold">{title}</h2>
            <button onClick={onClose} aria-label="Close drawer">
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-6">{children}</div>
        </div>
      </div>
    </div>,
    document.body
  );
}
```

## Common Use Cases

### Confirmation Dialog

```typescript
interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "default";
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default",
}: ConfirmDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="mt-2 text-sm text-gray-600">{description}</p>
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            {cancelText}
          </Button>
          <Button
            variant={variant === "danger" ? "destructive" : "default"}
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
```

### Edit Form Modal

```typescript
export function EditUserModal({ user, isOpen, onClose }: EditUserModalProps) {
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    // Save logic
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit User" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input id="name" defaultValue={user.name} />
        </div>
        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" defaultValue={user.email} />
        </div>
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSaving}>
            Save Changes
          </Button>
        </div>
      </form>
    </Modal>
  );
}
```

### Detail View Drawer

```typescript
export function UserDetailDrawer({
  user,
  isOpen,
  onClose,
}: UserDetailDrawerProps) {
  return (
    <Drawer isOpen={isOpen} onClose={onClose} title={user.name}>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Avatar src={user.avatar} size="lg" />
          <div>
            <h3 className="font-semibold">{user.name}</h3>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700">Role</h4>
            <p className="mt-1">{user.role}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700">Department</h4>
            <p className="mt-1">{user.department}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700">Joined</h4>
            <p className="mt-1">{formatDate(user.joinedAt)}</p>
          </div>
        </div>
      </div>
    </Drawer>
  );
}
```
