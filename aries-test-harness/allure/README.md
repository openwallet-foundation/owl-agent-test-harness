# ALLURE Reporting with Aries Agent Test Harness

## USAGE
Execute Allure Docker Service from this directory
```sh
docker-compose up -d allure allure-ui
```

- Verify if Allure API is working. Go to -> http://localhost:5050/allure-docker-service/latest-report

- Verify if Allure UI is working. Go to -> http://localhost:5252/allure-docker-service-ui/

Each time tests are executed with the -r allure option, and those results need to be pushed to an official service for tracking test execution history you will need to send those results up to the Allure Service to the appropriate project. 
```sh
./send_results.sh -d ../results -s http://localhost:5050 -p ACAPY
```

See documentation here:
- https://github.com/fescobar/allure-docker-service
- https://github.com/fescobar/allure-docker-service-ui
