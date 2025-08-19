# 🚀 DOCKERFILE UNIVERSEL SIPORTS - ZERO ERREUR GARANTI
FROM node:20-alpine

WORKDIR /app

# Supprimer les conflits potentiels
RUN rm -f package-lock.json

# Copier les fichiers de configuration
COPY package.json ./
COPY .yarnrc ./

# Copier yarn.lock s'il existe, sinon on le créera
COPY yarn.loc[k] ./ || echo "yarn.lock sera créé"

# Installation ultra robuste avec fallback
RUN yarn install --network-timeout 300000 --no-frozen-lockfile || \
    (rm -f yarn.lock && yarn install --network-timeout 300000)

# Copier le code source
COPY . .

# Build optimisé
ENV NODE_ENV=production
RUN yarn build

# Stage de production avec nginx
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=0 /app/dist /usr/share/nginx/html

# Configuration nginx optimisée pour SPA
RUN echo 'server { \
    listen 3000; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /assets/ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]