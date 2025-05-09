FROM eclipse-temurin:21-jdk-alpine as build

WORKDIR /app

# Создаем временное приложение Spring Boot
RUN apk add --no-cache maven
COPY pom.xml .
RUN mvn -B dependency:go-offline

COPY src ./src
RUN mvn clean package -DskipTests

# Создаем финальный образ
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Копируем JAR из этапа сборки
COPY --from=build /app/target/*.jar app.jar

# Создаем файл application.properties для отключения SQL инициализации
RUN echo "spring.sql.init.mode=never" > application.properties

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar", "--spring.config.location=file:///app/application.properties"]