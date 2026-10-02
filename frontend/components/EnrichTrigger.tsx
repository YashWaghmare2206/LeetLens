"use client";

import { useEffect } from "react";
import { ensureEnriched } from "@/lib/api";

export default function EnrichTrigger({ username }: { username: string }) {
  useEffect(() => {
    if (username) {
      ensureEnriched(username);
    }
  }, [username]);

  return null;
}
