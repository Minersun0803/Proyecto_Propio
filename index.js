export default {
  async fetch(request) {
    return new Response("Hola desde Cloudflare Worker!", {
      headers: { "content-type": "text/plain" },
    });
  },
};
