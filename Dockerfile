# 🚀 DOCKERFILE FINAL (corrigé) — Substitution du PORT au runtime

# Étape de build
FROM node:20-alpine AS build
WORKDIR /app

# Installer les dépendances (dev inclus pour le build)
ENV NODE_ENV=development
COPY package.json yarn.lock ./
RUN rm -f package-lock.json && yarn install --network-timeout 300000

# Vérification
RUN ls node_modules/@vitejs/plugin-react/package.json && echo "✅ @vitejs/plugin-react installé"

# Copier le code et builder
COPY . .
ENV NODE_ENV=production
RUN yarn build
RUN ls -la dist/index.html && echo "✅ Build réussi"

# Étape de runtime avec Nginx
FROM nginx:alpine

# S'assurer que envsubst est disponible (normalement présent, mais on sécurise)
RUN apk add --no-cache gettext

# Copier le build
COPY --from=build /app/dist /usr/share/nginx/html

# Déposer le template Nginx à l'endroit attendu par l'entrypoint
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Générer la config au runtime avec un PORT par défaut (3000) puis lancer Nginx
CMD ["/bin/sh", "-c", ": ${PORT:=3000}; envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]

# Port par défaut exposé (indicatif)
EXPOSE 3000


