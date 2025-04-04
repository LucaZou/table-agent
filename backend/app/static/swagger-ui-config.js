window.onload = function() {
  // 自定义Swagger UI配置
  const ui = SwaggerUIBundle({
    url: "/api/openapi.json",
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ],
    layout: "StandaloneLayout",
    docExpansion: "list",
    defaultModelsExpandDepth: -1,
    displayRequestDuration: true,
    filter: true,
    syntaxHighlight: {
      activate: true,
      theme: "agate"
    },
    tryItOutEnabled: true
  });

  window.ui = ui;
}; 