import fetch from "node-fetch";

export async function post(url: string, data: Record<string, unknown>) {
  return await fetch(url, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function get(url: string) {
  return await fetch(url);
}
