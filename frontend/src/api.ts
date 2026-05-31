const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

function resumirErroHtml(raw: string): string {
  if (!raw.trim().startsWith("<")) return raw;
  const exc = raw.match(/<pre class="exception_value">([\s\S]*?)<\/pre>/i)?.[1];
  const title = raw.match(/<title>([\s\S]*?)<\/title>/i)?.[1];
  const limpar = (s: string) =>
    s
      .replace(/<[^>]*>/g, " ")
      .replace(/&quot;/g, '"')
      .replace(/&#x27;/g, "'")
      .replace(/&amp;/g, "&")
      .replace(/\s+/g, " ")
      .trim();
  if (exc) return `Erro no servidor: ${limpar(exc)}`;
  if (title) return `Erro no servidor: ${limpar(title)}`;
  return "Erro no servidor ao processar a requisição.";
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${url}`, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(resumirErroHtml(text) || `Erro ${response.status}`);
  }
  if (response.status === 204) {
    return {} as T;
  }
  return (await response.json()) as T;
}

export const api = {
  get: <T>(url: string) => request<T>(url),
  post: <T>(url: string, body?: unknown) =>
    request<T>(url, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined
    }),
  put: <T>(url: string, body: unknown) =>
    request<T>(url, {
      method: "PUT",
      body: JSON.stringify(body)
    }),
  del: <T>(url: string) =>
    request<T>(url, {
      method: "DELETE"
    }),
  fileUrl: (url: string) => `${API_URL}${url}`
};
