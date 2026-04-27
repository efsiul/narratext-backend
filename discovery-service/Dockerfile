FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY target/discovery-service-1.0-SNAPSHOT.jar app.jar
EXPOSE 8760
ENTRYPOINT ["java", "-jar", "app.jar"]
