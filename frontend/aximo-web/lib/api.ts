export function apiBase(): string {
  // Always call our own Next API proxy
  return "/api/proxy";
}

export async function apiFetch(path: string, init?: RequestInit) {
  const url = `${apiBase()}${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      ...(init?.headers || {}),
      "Content-Type": init?.headers && "Content-Type" in (init.headers as any)
        ? (init.headers as any)["Content-Type"]
        : "application/json",
    },
    cache: "no-store",
  });
  return res;
}
