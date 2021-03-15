FROM openjdk:15.0.2-jdk-slim-buster

ADD app/target/example.smallest-0.0.1-SNAPSHOT.war app.war

ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app.war"]
