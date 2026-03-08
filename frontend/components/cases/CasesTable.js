"use client";

import { format } from "date-fns";
import { MoreHorizontal, Pencil, Trash2, Eye } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import StatusBadge from "./StatusBadge";

export default function CasesTable({
  cases,
  isLoading,
  onEdit,
  onDelete,
}) {
  if (isLoading) {
    return (
      <div className="space-y-3 p-6">
        {Array(5)
          .fill(0)
          .map((_, i) => (
            <Skeleton key={i} className="h-12 w-full rounded-lg" />
          ))}
      </div>
    );
  }

  if (!cases?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <p className="text-sm font-medium text-gray-900">
          No cases yet
        </p>
        <p className="text-sm text-gray-400">
          Create your first case to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Case Title</TableHead>
            <TableHead>Client</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="hidden md:table-cell">
              Assigned Lawyer
            </TableHead>
            <TableHead className="hidden lg:table-cell">
              Deadline
            </TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>

        <TableBody>
          {cases.map((c) => (
            <TableRow key={c.id}>
              <TableCell>
                <span className="font-medium">
                  {c.title}
                </span>
              </TableCell>

              <TableCell>{c.client_name}</TableCell>

              <TableCell>
                <StatusBadge status={c.status} />
              </TableCell>

              <TableCell className="hidden md:table-cell">
                {c.assigned_lawyer || "—"}
              </TableCell>

              <TableCell className="hidden lg:table-cell">
                {c.deadline
                  ? format(new Date(c.deadline), "MMM d, yyyy")
                  : "—"}
              </TableCell>

              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>

                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onEdit(c)}>
                      <Eye className="w-4 h-4 mr-2" />
                      View
                    </DropdownMenuItem>

                    <DropdownMenuItem onClick={() => onEdit(c)}>
                      <Pencil className="w-4 h-4 mr-2" />
                      Edit
                    </DropdownMenuItem>

                    <DropdownMenuItem
                      onClick={() => onDelete(c)}
                      className="text-red-600"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}