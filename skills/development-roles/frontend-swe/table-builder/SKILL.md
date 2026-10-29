---
name: table-builder
description: >-
  Creates data table patterns with filtering, sorting, pagination, row actions, column configuration, server/client rendering modes, and empty/loading states. Use when building "data tables", "list views", "admin tables", or "data grids".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Table Builder

Generate production-ready data tables with sorting, filtering, and pagination.

## Core Workflow

1. **Define columns**: Column configuration with types
2. **Choose mode**: Server-side or client-side rendering
3. **Add features**: Sorting, filtering, pagination, search
4. **Row actions**: Edit, delete, view actions
5. **Empty states**: No data and error views
6. **Loading states**: Skeletons and suspense
7. **Mobile responsive**: Stack columns or horizontal scroll

## Column Configuration

```typescript
import { ColumnDef } from "@tanstack/react-table";

export const columns: ColumnDef<User>[] = [
  {
    accessorKey: "id",
    header: "ID",
    cell: ({ row }) => (
      <span className="font-mono text-sm">{row.original.id}</span>
    ),
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Name
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="font-medium">{row.getValue("name")}</div>
    ),
  },
  {
    accessorKey: "email",
    header: "Email",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge variant={status === "active" ? "success" : "secondary"}>
          {status}
        </Badge>
      );
    },
  },
  {
    id: "actions",
    cell: ({ row }) => <RowActions row={row} />,
  },
];
```

## Best Practices

- Use TanStack Table for complex features
- Server-side pagination for large datasets
- Debounce search inputs
- Persist sorting/filtering in URL params
- Mobile: Horizontal scroll or card view
- Accessibility: Keyboard navigation, ARIA

## Output Checklist

- [ ] Column definitions with types
- [ ] Sorting functionality
- [ ] Filtering/search
- [ ] Pagination controls
- [ ] Row actions menu
- [ ] Empty state component
- [ ] Loading skeleton
- [ ] Mobile responsive
- [ ] URL state persistence
- [ ] Accessibility attributes


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

