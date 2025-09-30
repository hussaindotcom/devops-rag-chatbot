from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document  # Import Document class
import os

# Sample docs (one per microservice)
DOCS = {
    "UserAuthService": """# UserAuthService Deployment Guide (EKS)

## Prerequisites
- EKS cluster v1.28+ with IAM roles for service accounts (IRSA).
- Helm 3.10+ installed.
- kubectl configured with cluster access.
- Docker image built and pushed to ECR: `your-account.dkr.ecr.us-east-1.amazonaws.com/user-auth:v1.2.0`.

## Deployment Steps
1. Add Helm repo: `helm repo add bitnami https://charts.bitnami.com/bitnami`.
2. Create namespace: `kubectl create namespace auth`.
3. Install via Helm:
helm install user-auth bitnami/spring-boot -n auth \
--set image.repository=your-account.dkr.ecr.us-east-1.amazonaws.com/user-auth \
--set image.tag=v1.2.0 \
--set service.type=ClusterIP \
--set ingress.enabled=true \
--set ingress.hosts[0].host=auth.example.com
4. Verify: `kubectl get pods -n auth` (wait for READY=1/1).
5. Scale: `kubectl scale deployment user-auth -n auth --replicas=3`.

## Rollback
- `helm rollback user-auth 0 -n auth`.
- Monitor logs: `kubectl logs -f deployment/user-auth -n auth`.

## Troubleshooting
- Pod crashes: Check events with `kubectl describe pod <pod-name> -n auth`.
- Ingress issues: Ensure ALB controller is installed.
- Secrets: Use `kubectl create secret generic db-creds --from-literal=password=secret -n auth`.""",

 "OrderProcessingService": """# OrderProcessingService Deployment Guide (EKS)

## Prerequisites
- EKS cluster with autoscaling group.
- Image in ECR: `order-process:v2.1.0`.
- RabbitMQ installed in cluster.

## Deployment Steps
1. Namespace: `kubectl create ns orders`.
2. Helm install:
helm install order-process ./charts/order-chart \
--set image.tag=v2.1.0 --namespace orders
3. HPA: `kubectl autoscale deployment order-process --cpu-percent=50 --min=2 --max=10 -n orders`.
4. Test: `kubectl port-forward svc/order-process 8080:80 -n orders`.

## Rollback
- `helm rollback order-process`.

## Troubleshooting
- Queue backlog: Check RabbitMQ dashboard.
- OOM: Increase resources in values.yaml.""",

 "PaymentGatewayService": """# PaymentGatewayService Deployment Guide (EKS)

## Prerequisites
- Stripe API keys as Kubernetes secrets.
- Image: `payment-gateway:v1.0.0`.

## Deployment Steps
1. Create secret: `kubectl create secret generic stripe-keys --from-literal=secret_key=sk_test_... -n payments`.
2. Deploy: `kubectl apply -f payment-deployment.yaml -n payments`.
3. Expose: `kubectl expose deployment payment-gateway --type=LoadBalancer -n payments`.

## Rollback
- `kubectl rollout undo deployment/payment-gateway -n payments`.

## Troubleshooting
- Webhook failures: Verify ingress annotations for HTTPS.""",

 "InventoryManagementService": """# InventoryManagementService Deployment Guide (EKS)

## Prerequisites
- Redis cluster in EKS.
- Image: `inventory-mgmt:v3.0`.

## Deployment Steps
1. Deploy StatefulSet: `kubectl apply -f inventory-statefulset.yaml`.
2. Service: `kubectl apply -f inventory-service.yaml`.
3. Init data: Use job to seed Redis.

## Rollback
- Scale to 0 then back.

## Troubleshooting
- Cache misses: Monitor Redis metrics via Prometheus.""",

 "NotificationService": """# NotificationService Deployment Guide (EKS)

## Prerequisites
- SES verified domain.
- Image: `notifications:v1.5`.

## Deployment Steps
1. ConfigMap for SES creds: `kubectl create configmap ses-config --from-literal=region=us-east-1 -n notifs`.
2. Deploy: `helm upgrade --install notifs ./notification-chart`.

## Rollback
- Helm rollback.

## Troubleshooting
- Delivery failures: Check SES sandbox limits.""",

 "FileUploadService": """# FileUploadService Deployment Guide (S3/Lambda)

## Prerequisites
- S3 bucket: `devops-uploads-bucket`.
- IAM role for Lambda with S3 put permissions.

## Deployment Steps
1. Zip code: Include handler.py with boto3 upload logic.
2. Create Lambda: AWS CLI `aws lambda create-function --function-name file-upload --runtime python3.9 --role arn:aws:iam::...:role/lambda-role --handler handler.upload --zip-file fileb://code.zip`.
3. Trigger: Add S3 event notification for bucket uploads.
4. Test: Upload file to S3, check CloudWatch logs.

## Rollback
- `aws lambda delete-function --function-name file-upload`.

## Troubleshooting
- Permissions: Validate IAM policy for s3:PutObject.""",

 "ImageProcessingService": """# ImageProcessingService Deployment Guide (S3/Lambda)

## Prerequisites
- Pillow library in Lambda layer.
- S3 bucket for processed images.

## Deployment Steps
1. Build layer: Include Pillow in zip.
2. Deploy Lambda: `aws lambda update-function-code --function-name image-process --zip-file fileb://code.zip`.
3. Event source: S3 notification on raw-images bucket.
4. Output: Move to processed-images bucket.

## Rollback
- Revert code zip.

## Troubleshooting
- Format errors: Log with print() to CloudWatch.""",

 "BackupService": """# BackupService Deployment Guide (S3/Lambda + Glacier)

## Prerequisites
- Cron via EventBridge.
- IAM for Glacier vault access.

## Deployment Steps
1. Create Glacier vault: `aws glacier create-vault --vault-name backups`.
2. Lambda: Handler zips DB dumps and uploads.
3. Schedule: EventBridge rule triggers daily at 2AM.
4. Test: Manual invoke `aws lambda invoke --function-name backup-service output.json`.

## Rollback
- Disable rule.

## Troubleshooting
- Vault locks: Check compliance settings.""",

 "DatabaseService": """# DatabaseService Deployment Guide (EC2)

## Prerequisites
- EC2 t3.medium in private subnet.
- Security group allowing port 5432 from app subnets.
- AMI: Amazon Linux 2 with PostgreSQL.

## Deployment Steps
1. Launch EC2: Use user-data script to install Postgres:
#!/bin/bash
yum update -y
amazon-linux-extras install postgresql14
postgresql-setup initdb
systemctl start postgresql
systemctl enable postgresql
su - postgres -c "psql -c "ALTER USER postgres PASSWORD 'strongpass';""
2. EBS volume: Attach 20GB gp3.
3. RDS alternative? No, stick to EC2 for custom.

## Rollback
- Snapshot EBS, terminate, relaunch.

## Troubleshooting
- Connection refused: Check SG inbound rules.""",

 "MonitoringService": """# MonitoringService Deployment Guide (EC2)

## Prerequisites
- EC2 m5.large.
- Prometheus binary downloaded.

## Deployment Steps
1. User-data:
#!/bin/bash
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-.tar.gz
cd prometheus-/
./prometheus --config.file=prometheus.yml &
2. Grafana: Install via yum, port 3000.
3. Expose: ELB in front.

## Rollback
- Stop process, revert user-data.

## Troubleshooting
- Scraping fails: Verify targets in prometheus.yml.""",

    "TalosService": """# TalosService Deployment Guide (EC2 / App Servers)

## Overview
Talos is deployed on multiple EC2 instances (production fleet labeled `talos-prod`). Deploy flow:
- Merge feature branch into `master`.
- SSH into each talos-prod instance, pull latest code, and restart process manager (pm2).

## Merge to master (example)
On your CI machine or local dev where you do merges:
1. Ensure branch is up to date and tests pass.
2. Merge:
git checkout master
git pull origin master
git merge --no-ff <feature-branch>
git push origin master
(If you use PRs, complete the PR merge via GitHub/GitLab UI instead.)

## Rolling update on talos-prod machines
You can run these commands manually for each host or loop over an inventory.

Manual (single host):
ssh ubuntu@<talos-host-ip>
cd /home/ubuntu/talos
git fetch --all
git reset --hard origin/master
pm2 restart all

Notes:
- Use `git reset --hard origin/master` to ensure working tree matches master (careful: discards local changes).
- Prefer using an automation tool (Ansible or AWS SSM Run Command) to run the above across all hosts safely and idempotently.
- If using AWS SSM: `aws ssm send-command --document-name "AWS-RunShellScript" --targets Key=tag:Role,Values=talos-prod --parameters commands=["cd /home/ubuntu/talos","git fetch --all","git reset --hard origin/master","pm2 restart all"]`.""",

    "BelazService": """# BelazService Deployment Guide (Host: 192.2.32.21 / Docker)

## Overview
Belaz is built and deployed on a single host (bashion host). Steps:
- Merge code to `master`.
- SSH into host `192.2.32.21`, update repo, build docker image, push to registry.
- Sync ArgoCD application to pick up new image / manifests.

## Merge to master (example)
git checkout master
git pull origin master
git merge --no-ff <feature-branch>
git push origin master
Or complete the PR in your Git provider.

## On the bashion host (192.2.32.21)
ssh ubuntu@192.2.32.21
cd /home/ubuntu/belaz-prod
git fetch --all
git reset --hard origin/master

Build image (example)

docker build -t your-registry.example.com/belaz:latest .
docker push your-registry.example.com/belaz:latest

Replace `your-registry.example.com/belaz:latest` with your actual registry and tag. Authenticate to the registry beforehand (`docker login` or use an ECR credential helper).

## Sync ArgoCD application
After pushing the image, if your manifests are configured to track `latest` or the specific tag:
argocd app sync belaz-app
Or update the image tag in the Git repo (preferred) and let ArgoCD auto-sync or use argocd-image-updater.

Notes:
- Prefer immutable tags (e.g., `:20250930-build123`) to avoid image caching issues.
- If using ECR, use `aws ecr get-login-password` piped into `docker login` for auth in CI/host.""",

    "BSSService": """# BSSService Deployment Guide (EC2: bss-v2)

## Overview
BSS frontend is built on the `bss-v2` EC2 machine and deployed to the web root `/var/www/html`.

## Build & deploy steps on bss-v2
SSH into the machine, build the frontend, backup the current deployed build and copy the new build in place:

ssh ubuntu@<bss-v2-host-ip>
cd /home/ubuntu/bss-v2

build (try npm first, fallback to npx if necessary)

npm run build || npx run build

ensure build completed

ls -la build

backup current web content and replace

sudo mkdir -p /var/www/html
cd /var/www/html
sudo mv build build-bk-$(date +%Y%m%d%H%M%S) || true

copy new build to web root

sudo cp -r /home/ubuntu/bss-v2/build /var/www/html/

set ownership/permissions if needed

sudo chown -R www-data:www-data /var/www/html/build
sudo chmod -R 755 /var/www/html/build
Notes:
- Replace `<bss-v2-host-ip>` with the real EC2 IP or use an inventory.
- If the web server serves `/var/www/html/index.html`, ensure the new `build` contains that file.
- Keep multiple backups (e.g., `build-bk-YYYYMMDDHHMMSS`) to allow quick rollbacks.
- Consider using rsync over SSH for large builds: `rsync -avz --delete /home/ubuntu/bss-v2/build/ ubuntu@webhost:/var/www/html/build/`.""",

}

# Text splitter for chunking docs
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Prepare documents
documents = []
for service_name, doc_text in DOCS.items():
 chunks = splitter.split_text(doc_text)
 for i, chunk in enumerate(chunks):
     # Create Document objects instead of dictionaries
     documents.append(Document(
         page_content=chunk,
         metadata={"service": service_name, "chunk_id": i}
     ))

# Initialize or load Chroma DB
persist_directory = "./chroma_db"
if os.path.exists(persist_directory):
 vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
 print("Loaded existing Chroma DB.")
else:
 vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
 print("Initialized new Chroma DB with docs.")

# Add new docs if any (for future updates)
# vectorstore.add_documents(new_docs)

print(f"Embedded {len(documents)} chunks for {len(DOCS)} services.") 
