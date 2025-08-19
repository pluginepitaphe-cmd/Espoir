# 🚀 DOCKERFILE FINAL SIPORTS - SYNTAXE YARN CORRECTE
FROM node:20-alpine

WORKDIR /app

# NODE_ENV=development pour installer devDependencies automatiquement
ENV NODE_ENV=development

# Copier package.json et yarn.lock
COPY package.json yarn.lock ./

# Installation simple sans options compliquées
RUN rm -f package-lock.json && yarn install --network-timeout 300000

# Vérifier installation
RUN ls node_modules/@vitejs/plugin-react/package.json && echo "✅ @vitejs/plugin-react installé"

# Copier le code source
COPY . .

# Build avec NODE_ENV=production pour optimisation
ENV NODE_ENV=production
RUN yarn build

# Vérifier que dist/ existe
RUN ls -la dist/index.html && echo "✅ Build réussi"

# Stage production avec nginx
FROM nginx:alpine

# Installer envsubst
RUN apk add --no-cache gettext

COPY --from=0 /app/dist /usr/share/nginx/html

# Créer un template de configuration Nginx
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template

# Utiliser envsubst pour remplacer la variable PORT
RUN envsubst '${PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

EXPOSE ${PORT}
CMD ["nginx", "-g", "daemon off;"]


