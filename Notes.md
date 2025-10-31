# Password Reset

## Generate the reset token and store

1. Generate token and nullify any reset-token on the profile table.
2. Set it in redis db for 1 hour.
3. Store it on profile table reset_token.

## Retrieve the reset token

1. Check if redis has the reset token
2. If not available in Redis, check on the profile table
3. Check the expiry of the reset token in UserService
4. If expired return an error to generate a new reset token

## Rate limit generating reset token

1. While generating reset token, store in redis and profile table the generated time
2. Any attempt to generate another reset token within 5 mins should be restricted

## Writing Unit Test

1. Write unit tests for utilities.
2. Write unit tests for services.
3. Write unit tests for repository.
4. Write unit tests for controllers.

## Swagger Documentation

1. we are going to use flasgger library for documentation.
2. install with `pipenv install flasgger`.
3. add to the requirements.txt with `pip freeze | grep flasgger >> requirements.txt`.
4. integrate it to your main file by initializing `swagger = Swagger(app, template={})`.
5. check the endpoint using `http://127.0.0.1:5005/apidocs/`
