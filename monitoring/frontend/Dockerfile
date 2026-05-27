FROM node:24-alpine AS builder
WORKDIR /app

ARG VITE_POLL_INTERVAL=10
ENV VITE_POLL_INTERVAL=$VITE_POLL_INTERVAL

COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80