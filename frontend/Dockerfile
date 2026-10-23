# Serwujemy statyczne pliki przez nginx — lekki, sprawdzony serwer HTTP.
# 🟡 NICE TO KNOW: multi-stage nie jest tu konieczny, bo nie mamy kroku
# "budowania" dla czystego HTML/JS. Gdybyś dodał np. Reacta z `npm run build`,
# dokładnie tak wyglądałby pierwszy stage — build w Node, a potem kopiowanie
# tylko skompilowanych plików do obrazu z nginx.
FROM nginx:1.27-alpine

# Usuwamy domyślną stronę powitalną nginx
RUN rm -rf /usr/share/nginx/html/*

# Kopiujemy nasze pliki statyczne na miejsce domyślnej strony
COPY . /usr/share/nginx/html

# Własna konfiguracja nginx (patrz nginx.conf obok)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
