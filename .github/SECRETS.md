# GitHub Secrets Configuration

This document describes the GitHub secrets required for CI/CD workflows.

## Required Secrets

### Azure Authentication

#### `AZURE_CREDENTIALS`
Azure service principal credentials in JSON format. Used for authenticating with Azure services.

```json
{
  "clientId": "<service-principal-app-id>",
  "clientSecret": "<service-principal-password>",
  "subscriptionId": "<azure-subscription-id>",
  "tenantId": "<azure-ad-tenant-id>"
}
```

**How to create:**
```bash
az ad sp create-for-rbac \
  --name "github-actions-todoapp" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/<resource-group> \
  --sdk-auth
```

#### `AZURE_SUBSCRIPTION_ID`
Your Azure subscription ID.

### Database

#### `DATABASE_URL`
PostgreSQL connection string for the deployed database.

Format: `postgresql://user:password@host:5432/dbname?sslmode=require`

### Application Secrets

#### `BETTER_AUTH_SECRET`
JWT secret for Better Auth authentication. Should be a strong random string.

Generate with: `openssl rand -base64 32`

## Repository Variables (Non-Sensitive)

These can be stored as repository variables instead of secrets:

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_RESOURCE_GROUP` | Azure resource group name | `todoapp-dev-rg` |
| `AKS_CLUSTER_NAME` | AKS cluster name | `todoapp-dev-aks` |
| `ACR_NAME` | Azure Container Registry name | `todoappdevacr` |
| `API_URL` | Public API URL | `https://api.todoapp.example.com` |
| `WS_URL` | WebSocket URL | `wss://api.todoapp.example.com` |

## Environment-Specific Secrets

For multi-environment deployments, create GitHub environments with their own secrets:

### Development (`dev`)
- Uses development Azure resources
- Auto-deploys on push to main

### Staging (`staging`)
- Uses staging Azure resources
- Manual deployment trigger

### Production (`prod`)
- Uses production Azure resources
- Requires manual approval
- Has its own set of secrets

## Setting Secrets

### Via GitHub UI
1. Go to repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Add secret name and value

### Via GitHub CLI
```bash
# Set a secret
gh secret set AZURE_CREDENTIALS < azure-credentials.json

# Set from environment variable
echo "$MY_SECRET" | gh secret set MY_SECRET_NAME

# List secrets
gh secret list
```

## Security Best Practices

1. **Rotate secrets regularly** - Update secrets every 90 days
2. **Use least privilege** - Service principals should have minimal required permissions
3. **Audit access** - Review who has access to secrets
4. **Never log secrets** - Ensure workflows don't expose secrets in logs
5. **Use environments** - Isolate production secrets with environment protection rules
