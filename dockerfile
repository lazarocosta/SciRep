FROM node:latest
WORKDIR /backend
COPY . .
RUN npm install
EXPOSE 3000
ENTRYPOINT ["node", "index.ts"]
