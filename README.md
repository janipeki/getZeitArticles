# get latest news of zeit.de

It just works™.

## Do I need it?

Not at all, it just some playing around with AWS and python3.

## Features

* Downloads the newest articles from zeit.de to S3

* Returns this list 
 
## How to use
* Create a zip file after navigating to the src-directory: 
  > zip -r ../function.zip <files to add>

* Upload to AWS Lambda:
  Assuming that the current user has upload right granted.
  > aws lambda update-function-code --function-name zeit --zip-file fileb://function.zip

* Run the code:
  Assuming that the current user has function invoke right granted.
  > aws lambda invoke --function-name zeit out.json 
  
