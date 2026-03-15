"use client"
import { useEffect, useState } from "react"
import { getAllRoles } from "../../lib/api/firm_users"

export default function FetchUserRoles() {

  const [roles, setRoles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {

    const fetchRoles = async () => {
      try {
        const res = await getAllRoles()
        setRoles(res.data)
      } catch (err) {
        console.error("Failed to load roles", err)
        setError(err)
      } finally {
        setLoading(false)
      }
    }

    fetchRoles()

  }, [])

  return {
    roles,
    loading,
    error
  }

}