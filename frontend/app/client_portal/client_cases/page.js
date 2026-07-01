"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function ClientCasesPage() {
  console.log("ClientCasesPage rendered")  // add this line to check if the component is rendering
  const router = useRouter()

  useEffect(() => {
    router.replace("/client_portal/dashboard")
  }, [])

  return null
}

