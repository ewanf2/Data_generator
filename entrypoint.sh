#!/bin/sh
if [ ! -f /app/schemas/schemas.json ]; then
  mkdir -p /app/schemas
  echo '{}' > /app/schemas/schemas.json
fi
exec waitress-serve --listen=0.0.0.0:80 App:App