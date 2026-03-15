'use client'

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button";


export function ManageUserMenu({ user, onView, onToggleStatus }) {
  return (
    <DropdownMenu>

      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          Manage
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">

        <DropdownMenuItem
          onClick={() => onView(user)}
        >
          View Details
        </DropdownMenuItem>

        <DropdownMenuItem 
          onClick={() => onToggleStatus(user.id)}
        >
          {user.is_active ? "Deactivate" : "Activate"}
        </DropdownMenuItem>

      </DropdownMenuContent>

    </DropdownMenu>
  )
}