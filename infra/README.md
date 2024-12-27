# Pipeline Configuration for Serverless Microservices

This directory contains the configuration for the AWS CodePipeline and related resources used to automate deployment for the Serverless Microservices project.

## Pipeline Overview
- **Name**: `ServerlessMicroservicesPipeline`
- **Stages**:
  1. **Source**: Pulls the latest code from the GitHub repository.
  2. **Build**: Uses CodeBuild to package the Lambda function.
  3. **Deploy**: *(Planned)* Deploys resources using CloudFormation.

## Files
1. **`pipeline.json`**: Defines the pipeline configuration, including:
   - Source action from GitHub.
   - Build action using CodeBuild.
   - S3 bucket for artifact storage.

2. **`README.md`**: This documentation file.

## Dependencies
- **AWS Services**:
  - CodePipeline
  - CodeBuild
  - S3 (Artifact storage)
- **IAM Roles**:
  - `CodePipelineServiceRole`: Grants necessary permissions to CodePipeline and CodeBuild.

## Setup Instructions
### Prerequisites
- An S3 bucket (`serverless-microservices-artifacts`).
- A GitHub repository with the required codebase.
- A GitHub Personal Access Token (stored securely in AWS Secrets Manager).

### To Update the Pipeline
1. Modify `pipeline.json` as needed.
2. Recreate the pipeline using:
   ```bash
   aws codepipeline update-pipeline --cli-input-json file://pipeline.json

### To Delete the Pipeline
Run:
   ```bash
   aws codepipeline delete-pipeline --name ServerlessMicroservicesPipeline

### To Delete the Pipeline
Use the AWS Console or CLI:
bash
    aws codepipeline list-pipeline-executions --name ServerlessMicroservicesPipeline

## Future Enhancements
- Add a deploy stage using CloudFormation to provision resources.
- Implement error handling and notifications for pipeline failures.

### Steps to Use in VS Code:
1. Open the `README.md` file in your `infra` folder.
2. Copy and paste the content above.
3. Save the file.
4. Push the changes to GitHub using:
   ```bash
   git add infra/README.md
   git commit -m "Add README for pipeline configuration"
   git push origin main
