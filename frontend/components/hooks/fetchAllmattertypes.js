"use client"
import { useEffect, useState } from "react"
import { getAllMatterTypes } from "../../lib/api/cases"

export default function FetcAllMatterTypes() {

  const [roles, setMatterType] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {

    const fetchRoles = async () => {
      try {
        const res = await getAllMatterTypes()
        setMatterType(res.data)
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