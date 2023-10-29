FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS build
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
RUN pnpm deploy --filter=client --prod /prod/client
RUN pnpm deploy --filter=client-server --prod /prod/client-server

FROM base AS client
COPY --from=build /prod/client /prod/client
WORKDIR /prod/client
EXPOSE 5173
CMD [ "pnpm", "run", "dev" ]

FROM base AS client-server
COPY --from=build /prod/client-server /prod/client-server
WORKDIR /prod/client-server
EXPOSE 8001
CMD [ "pnpm", "start" ]
